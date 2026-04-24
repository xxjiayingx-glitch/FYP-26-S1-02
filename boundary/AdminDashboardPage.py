from flask import Blueprint, render_template, request, redirect, url_for, session
from control.AdminDashboardCTL import AdminDashboardControl

admin_dashboard_bp = Blueprint("admin_dashboard", __name__)

@admin_dashboard_bp.route("/admin/dashboard")
def admin_dashboard():
    if "userID" not in session:
        return redirect(url_for("login.login"))
    
    if session.get("userType") != "system admin":
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
        application_list=dashboard_data["application_list"],
        recent_logs=dashboard_data["recent_logs"]
    )