from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from entity.db_connection import get_db_connection

subscription_bp = Blueprint("subscription", __name__)

# -------------------------
# LOAD PLANS
# -------------------------
@subscription_bp.route("/")
def subscription_page():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM SubscriptionPlan")
    plans = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("subscription.html", plans=plans)


# -------------------------
# SUBSCRIBE
# -------------------------
@subscription_bp.route("/subscribe", methods=["POST"])
def subscribe():
    if "userID" not in session:
        return redirect(url_for("login.login"))

    user_id = session["userID"]
    plan_id = request.form.get("plan_id")

    conn = get_db_connection()
    cursor = conn.cursor()

    # Get selected plan
    cursor.execute("SELECT * FROM SubscriptionPlan WHERE planID = %s", (plan_id,))
    plan = cursor.fetchone()

    if not plan:
        flash("Invalid plan selected", "error")
        return redirect(url_for("subscription.subscription_page"))

    # Update user in DB
    cursor.execute("""
        UPDATE UserAccount
        SET subscriptionID = %s,
            userType = %s
        WHERE userID = %s
    """, (plan_id, plan["planName"].lower(), user_id))

    conn.commit()
    cursor.close()
    conn.close()

    # ✅ IMPORTANT: update session
    session["userType"] = plan["planName"].lower()

    flash("Subscription successful!", "success")
    return redirect(url_for("subscription.subscription_page"))


# -------------------------
# CHANGE PLAN
# -------------------------
@subscription_bp.route("/change-plan", methods=["POST"])
def change_plan():
    if "userID" not in session:
        return redirect(url_for("login.login"))

    user_id = session["userID"]
    plan_id = request.form.get("plan_id")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM SubscriptionPlan WHERE planID = %s", (plan_id,))
    plan = cursor.fetchone()

    if not plan:
        flash("Invalid plan", "error")
        return redirect(url_for("subscription.subscription_page"))

    cursor.execute("""
        UPDATE UserAccount
        SET subscriptionID = %s,
            userType = %s
        WHERE userID = %s
    """, (plan_id, plan["planName"].lower(), user_id))

    conn.commit()
    cursor.close()
    conn.close()

    # ✅ update session
    session["userType"] = plan["planName"].lower()

    flash("Plan updated!", "success")
    return redirect(url_for("subscription.subscription_page"))