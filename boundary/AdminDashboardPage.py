from flask import Blueprint, render_template
from control.AdminDashboardCTL import AdminDashboardControl

admin_dashboard_bp = Blueprint("admin_dashboard", __name__)

@admin_dashboard_bp.route("/admin/dashboard")
def admin_dashboard():
    control = AdminDashboardControl()
    dashboard_data = control.get_dashboard_data()

    return render_template(
        "admin_dashboard.html",
        admin=dashboard_data["admin"],
        stats=dashboard_data["stats"],
        reported_list=dashboard_data["reported_list"],
        recent_logs=dashboard_data["recent_logs"]
    )