from flask import Blueprint, render_template, request, redirect, url_for
from control.UserDetailsCTL import UserDetailsCTL
from control.AdminDashboardCTL import AdminDashboardControl
from control.ActionOnUserCTL import ActionOnUserCTL

user_details_bp = Blueprint("user_details", __name__)

@user_details_bp.route("/admin/user-accounts/<int:user_id>")
def view_user_details_page(user_id):
    admin_control = AdminDashboardControl()
    admin_data = admin_control.get_dashboard_data()

    control = UserDetailsCTL()
    user_data = control.getUserDetails(user_id)

    return render_template(
        "user_details.html",
        admin=admin_data["admin"],
        user=user_data["user"],
        subscription_status=user_data["subscription_status"],
        interests=user_data["interests"]
    )


@user_details_bp.route("/admin/user-accounts/<int:user_id>/status", methods=["POST"])
def update_user_status(user_id):
    action = request.form.get("action", "").strip()

    control = ActionOnUserCTL()
    success = control.updateUserStatus(user_id, action)

    if success:
        message = "User status updated successfully"
    else:
        message = "Failed to update user status"

    return redirect(url_for("view_users.view_users_page", message=message))