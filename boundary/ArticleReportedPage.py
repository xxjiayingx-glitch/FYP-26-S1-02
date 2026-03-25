from flask import Blueprint, render_template, request, session, redirect, url_for
from control.ArticleReportedCTL import ArticleReported
from control.AdminDashboardCTL import AdminDashboardControl
import math

article_reported_bp = Blueprint("article_reported", __name__)

@article_reported_bp.route("/admin/article-reported", methods=["GET"])
def article_reported_page():
    if "userID" not in session:
        return redirect(url_for("login"))
    
    if session.get("userType") != "system admin":
        return redirect("/login")
    
    dashboard_control = AdminDashboardControl()
    admin_data = dashboard_control.get_dashboard_data()

    page = request.args.get("page", 1, type=int)
    per_page = 10

    reported_control = ArticleReported()
    all_report = reported_control.list_article_reported()

    total_report = len(all_report)
    total_pages = math.ceil(total_report/per_page) if total_report > 0 else 1

    start = (page-1) * per_page
    end = start + per_page
    reportedArticles = all_report[start:end]

    return render_template(
        "article_reported.html",
        admin=admin_data["admin"],
        reportedArticles=reportedArticles,
        page=page,
        total_pages=total_pages
    )
        


