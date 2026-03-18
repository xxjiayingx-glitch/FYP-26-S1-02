from flask import Blueprint, render_template, request, redirect, url_for, session
from control.AdminDashboardCTL import AdminDashboardControl

admin_dashboard_bp = Blueprint("admin_dashboard", __name__)

@admin_dashboard_bp.route("/admin/dashboard")
def admin_dashboard():
    if "userID" not in session:
        return redirect(url_for("login.login"))
    
    admin = {
        "userID": session.get("userID"),
        "username": session.get("username"),
        "userType": session.get("userType"),
        "profileImage": session.get("profileImage")
    }

    control = AdminDashboardControl()
    dashboard_data = control.get_dashboard_data()

    return render_template(
        "admin_dashboard.html",
        admin=admin,
        stats=dashboard_data["stats"],
        reported_list=dashboard_data["reported_list"],
        recent_logs=dashboard_data["recent_logs"]
    )

@admin_dashboard_bp.route("/admin/upload-profile-picture", methods=["POST"])
def upload_profile_picture():
    control = AdminDashboardControl()
    file = request.files.get("profileImage")

    result = control.upload_profile_picture(file)
    
    return redirect(url_for("admin_dashboard.admin_dashboard"))
