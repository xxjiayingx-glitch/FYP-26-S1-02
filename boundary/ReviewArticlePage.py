from flask import Blueprint, render_template, request, redirect, session, url_for
from control.ReportDetailsCTL import ReportDetails
from control.ActionOnArticleCTL import ActionOnArticle
from control.AdminDashboardCTL import AdminDashboardControl

review_article_bp = Blueprint("review_article", __name__)

@review_article_bp.route("/admin/article-reported/<int:report_id>")
def review_article_details(report_id):
    if "userID" not in session:
        return redirect(url_for("login.login"))

    if session.get("userType") != "system admin":
        return redirect(url_for("login.login"))
    
    control = ReportDetails()
    report_details = control.list_report_details(report_id)

    dashboard_control = AdminDashboardControl()
    admin_data = dashboard_control.get_dashboard_data()

    return render_template(
        "admin_review_article.html",
        report=report_details,
        admin=admin_data["admin"]
    )

@review_article_bp.route("/admin/article-reported/<int:articleID>/status", methods=["POST"])
def suspend_or_unsuspend(articleID):
    action = request.form.get("action", "").strip()
    control = ActionOnArticle()
    result = control.updateArticleStatus(articleID, action)

    if result:
        message = "User status updated successfully"
    else:
        message = "Failed to update user status"

    return redirect(url_for("article_reported.article_reported_page", message=message))
    