from flask import Blueprint, render_template, session, redirect, url_for, request
from control.SystemLogCTL import SystemLogCTL
from control.AdminDashboardCTL import AdminDashboardControl
import math

system_monitoring_bp = Blueprint("system_monitoring", __name__)

@system_monitoring_bp.route("/admin/system-monitoring")
def system_monitoring_pg():
    if "userID" not in session:
        return redirect(url_for("login.login"))
    
    if session.get("userType") != "system admin":
        return redirect("login.login")
    
    dashboard_control = AdminDashboardControl()
    admin_data = dashboard_control.get_dashboard_data()
    
    return render_template("admin_system_monitoring.html", admin=admin_data["admin"])

@system_monitoring_bp.route("/admin/system-monitoring/view-logs", methods=["GET"])
def view_logs_page():
    if "userID" not in session:
        return redirect(url_for("login.login"))

    if session.get("userType") != "system admin":
        return redirect(url_for("login.login"))
    
    dashboard_control = AdminDashboardControl()
    admin_data = dashboard_control.get_dashboard_data()
    
    page = request.args.get("page", 1, type=int)
    per_page = 20

    q = request.args.get("q", "").strip()
    search_by = request.args.get("search_by", "").strip()
    start_date = request.args.get("start_date", "")
    end_date = request.args.get("end_date", "")

    if q or start_date or end_date:
        all_logs = SystemLogCTL.get_logs(
            q=q,
            search_by=search_by,
            start_date=start_date,
            end_date=end_date
        )

        total_logs = SystemLogCTL.count_logs(
        q=q,
        search_by=search_by,
        start_date=start_date,
        end_date=end_date
    )
    else:
        all_logs = SystemLogCTL.viewLogs(page)
        total_logs = SystemLogCTL.count_logs()

    total_pages = math.ceil(total_logs/per_page) if total_logs > 0 else 1

    if q or start_date or end_date:
        start = (page - 1) * per_page
        end = start + per_page
        logs = all_logs[start:end]
    else:
        logs = all_logs

    return render_template("admin_view_logs.html", admin=admin_data["admin"],logs=logs, page=page, total_pages=total_pages, q=q,
    search_by=search_by,  start_date=start_date, end_date=end_date)