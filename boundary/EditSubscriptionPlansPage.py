from flask import Blueprint, render_template, session, redirect, url_for

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

    return render_template(
        "EditSubscriptionPlans.html",
        admin=admin
    )
