from flask import Blueprint, render_template, session, redirect, url_for, request
from control.SystemLogCTL import SystemLogCTL
from control.AdminDashboardCTL import AdminDashboardControl
import math

system_monitoring_bp = Blueprint("system_monitoring", __name__)

@system_monitoring_bp.route("/admin/system-monitoring")
def system_monitoring_pg():
    if "userID" not in session:
        return redirect(url_for("login"))
    
    if session.get("userType") != "system admin":
        return redirect("/login")
    
    dashboard_control = AdminDashboardControl()
    admin_data = dashboard_control.get_dashboard_data()
    
    return render_template("admin_system_monitoring.html", admin=admin_data["admin"])

@system_monitoring_bp.route("/admin/system-monitoring/view-logs", methods=["GET"])
def view_logs_page():
    if "userID" not in session:
        return redirect("/login")

    if session.get("userType") != "system admin":
        return redirect("/login")
    
    dashboard_control = AdminDashboardControl()
    admin_data = dashboard_control.get_dashboard_data()
    
    page = request.args.get("page", 1, type=int)
    per_page = 10

    q = request.args.get("q", "").strip()
    search_by = request.args.get("search_by", "").strip()
    log_date = request.args.get("log_date", "").strip()

    if q or log_date:
        all_logs = SystemLogCTL.get_logs(q=q, search_by=search_by, log_date=log_date)
    else:
        all_logs = SystemLogCTL.viewLogs()


    total_logs = len(all_logs)
    total_pages = math.ceil(total_logs/per_page) if total_logs > 0 else 1

    start = (page-1) * per_page
    end = start + per_page
    logs = all_logs[start:end]

    return render_template("admin_view_logs.html", admin=admin_data["admin"],logs=logs, page=page, total_pages=total_pages, q=q,
    search_by=search_by, log_date=log_date)