from flask import Blueprint, render_template, session, redirect, url_for, request
from entity.db_connection import get_db_connection

edit_subscription_plans_bp = Blueprint(
    "edit_subscription_plans_bp",
    __name__
)

@edit_subscription_plans_bp.route("/admin/edit-subscription-plans")
def edit_subscription_plans_page():

    if "userID" not in session:
        return redirect(url_for("login.login"))

    admin = {
        "userID": session.get("userID"),
        "username": session.get("username"),
        "userType": session.get("userType"),
        "profileImage": session.get("profileImage")
    }

    selected_plan_id = request.args.get("planID", 8, type=int)

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM SubscriptionPlan
        WHERE planID = %s
        LIMIT 1
    """, (selected_plan_id,))
    plan = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template(
        "EditSubscriptionPlans.html",
        admin=admin,
        plan=plan,
        selected_plan_id=selected_plan_id
    )
