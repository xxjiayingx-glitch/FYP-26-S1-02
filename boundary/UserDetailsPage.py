from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from control.UserDetailsCTL import UserDetailsCTL
from control.AdminDashboardCTL import AdminDashboardControl
from control.ActionOnUserCTL import ActionOnUserCTL

user_details_bp = Blueprint("user_details", __name__)

@user_details_bp.route("/admin/user-accounts/<int:user_id>")
def view_user_details_page(user_id):
    if "userID" not in session:
        return redirect(url_for("login.login"))
    
    if session.get("userType") != "system admin":
        return redirect("login.login")
    
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
    if "userID" not in session:
        return redirect(url_for("login.login"))
    
    if session.get("userType") != "system admin":
        return redirect("login.login")
    
    admin_id = session["userID"]
    
    action = request.form.get("action", "").strip()

    control = ActionOnUserCTL()
    result = control.updateUserStatus(user_id, action, admin_id)

    if result["success"] and action == 'suspend':
        flash("User suspended successfully.", "success")
    elif result["success"] and action == 'unsuspend':
        flash("User unsuspended successfully.", "success")
    else:
        flash(result["message"], "error")

    return redirect(url_for("view_users.view_users_page"))

@user_details_bp.route("/admin/user-accounts/delete/<int:user_id>", methods=["POST"])
def delete_user(user_id):
    if "userID" not in session:
        return redirect(url_for("login.login"))
    
    if session.get("userType") != "system admin":
        return redirect("login.login")
    
    admin_id = session["userID"]

    control = ActionOnUserCTL()

    result = control.delete_user(user_id, admin_id)

    if result["success"]:
        flash("User deleted successfully.", "success")
    else:
        flash(result["message"], "error")

    return redirect(url_for("view_users.view_users_page"))