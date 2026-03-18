from flask import Blueprint, render_template, session, redirect, url_for

edit_subscription_plans_bp = Blueprint("edit_subscription_plans", __name__)

@edit_subscription_plans_bp.route("/admin/edit-subscription-plans")
def edit_subscription_plans_page():
    if "userID" not in session:
        return redirect(url_for("login"))
    return render_template("EditSubscriptionPlans.html")
