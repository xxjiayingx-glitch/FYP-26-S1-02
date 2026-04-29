import os
import stripe
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from entity.db_connection import get_db_connection
from dotenv import load_dotenv

load_dotenv()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

subscription_bp = Blueprint("subscription", __name__)


def normalize_plan_name(value):
    """
    Convert DB/session values like:
    'Free Plan', 'free', ' premium plan '
    into:
    'free', 'premium', 'basic'
    """
    if not value:
        return ""

    value = str(value).strip().lower()
    value = value.replace("plan", "").strip()
    return value


# -------------------------
# LOAD PLANS
# -------------------------
@subscription_bp.route("/")
def subscription_page():
    if "userType" in session:
        session["userType"] = normalize_plan_name(session.get("userType"))

    auto_plan = request.args.get("auto_plan")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM SubscriptionPlan
        WHERE planStatus = 'active' OR planStatus IS NULL
        ORDER BY planID ASC
    """)
    plans = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("subscription.html", plans=plans, auto_plan=auto_plan)


# -------------------------
# CHANGE NON-PREMIUM PLAN DIRECTLY
# -------------------------
@subscription_bp.route("/change-plan", methods=["POST"])
def change_plan():
    if "userID" not in session:
        return redirect(url_for("login.login"))

    user_id = session["userID"]
    plan_id = request.form.get("plan_id")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM SubscriptionPlan WHERE planID = %s", (plan_id,))
    plan = cursor.fetchone()

    if not plan:
        cursor.close()
        conn.close()
        flash("Invalid plan selected.", "error")
        return redirect(url_for("subscription.subscription_page"))

    plan_name = normalize_plan_name(plan["planName"])

    # Premium must go through Stripe payment
    if plan_name == "premium":
        cursor.close()
        conn.close()
        flash("Premium plan requires payment.", "error")
        return redirect(url_for("subscription.subscription_page"))

    cursor.execute("""
        UPDATE UserAccount
        SET userType = %s
        WHERE userID = %s
    """, (plan_name, user_id))

    conn.commit()
    cursor.close()
    conn.close()

    session["userType"] = plan_name

    flash("Plan updated successfully.", "success")
    return redirect(url_for("subscription.subscription_page"))


# -------------------------
# CREATE STRIPE CHECKOUT SESSION
# -------------------------
@subscription_bp.route("/create-checkout-session", methods=["POST"])
def create_checkout_session():
    if "userID" not in session:
        return redirect(url_for("login.login"))

    user_id = session["userID"]
    plan_id = request.form.get("plan_id")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM SubscriptionPlan WHERE planID = %s", (plan_id,))
    plan = cursor.fetchone()

    if not plan:
        cursor.close()
        conn.close()
        flash("Invalid plan selected.", "error")
        return redirect(url_for("subscription.subscription_page"))

    raw_plan_name = plan["planName"]
    plan_name = normalize_plan_name(raw_plan_name)

    if plan_name != "premium":
        cursor.close()
        conn.close()
        flash(f"Only premium plan requires payment. Detected plan: {raw_plan_name}", "error")
        return redirect(url_for("subscription.subscription_page"))

    try:
        amount_cents = int(float(plan["price"]) * 100)

        BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:5000")

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="payment",
            line_items=[
                {
                    "price_data": {
                        "currency": "sgd",
                        "product_data": {
                            "name": raw_plan_name,
                            "description": f"{raw_plan_name} access"
                        },
                        "unit_amount": amount_cents,
                    },
                    "quantity": 1,
                }
            ],
            success_url=f"{BASE_URL}/subscription/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{BASE_URL}/subscription/cancel",
            metadata={
                "user_id": str(user_id),
                "plan_name": plan_name
            }
        )

        cursor.close()
        conn.close()

        return redirect(checkout_session.url, code=303)

    except Exception as e:
        cursor.close()
        conn.close()
        print("Stripe error:", str(e))  # 👈 important debug
        flash(f"Payment setup failed: {str(e)}", "error")
        return redirect(url_for("subscription.subscription_page"))

# -------------------------
# PAYMENT SUCCESS
# -------------------------
@subscription_bp.route("/success")
def payment_success():
    if "userID" not in session:
        return redirect(url_for("login.login"))

    session_id = request.args.get("session_id")

    if not session_id:
        flash("Missing payment session.", "error")
        return redirect(url_for("subscription.subscription_page"))

    try:
        checkout_session = stripe.checkout.Session.retrieve(session_id)

        if checkout_session.payment_status != "paid":
            flash("Payment not completed.", "error")
            return redirect(url_for("subscription.subscription_page"))

        user_id = int(checkout_session.metadata["user_id"])
        plan_name = normalize_plan_name(checkout_session.metadata["plan_name"])

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE UserAccount
            SET userType = %s,
                       pendingPlan = NULL
            WHERE userID = %s
        """, (plan_name, user_id))

        cursor.execute("""
            SELECT profileCompleted
            FROM UserAccount
            WHERE userID = %s
        """, (user_id,))
        update_profile = cursor.fetchone()

        conn.commit()
        cursor.close()
        conn.close()

        session["userType"] = plan_name

        if update_profile and update_profile.get("profileCompleted") == 0:
            flash("Payment successful! Please complete your profile.", "success")
            return redirect(url_for("profile.complete_profile"))

        flash("Payment successful! You are now a Premium user.", "success")
        return redirect("/dashboard")

    except Exception as e:
        flash(f"Unable to verify payment: {str(e)}", "error")
        return redirect(url_for("subscription.subscription_page"))


# -------------------------
# PAYMENT CANCEL
# -------------------------
@subscription_bp.route("/cancel")
def payment_cancel():
    flash("Payment cancelled.", "error")
    return redirect(url_for("subscription.subscription_page"))