from flask import Blueprint, render_template, request, redirect, url_for
from control.ReportDetailsCTL import ReportDetails
from control.ActionOnArticleCTL import ActionOnArticle

review_article_bp = Blueprint("review_article", __name__)

@review_article_bp.route("/admin/article-reported/<int:report_id>")
def review_article_details(report_id):
    control = ReportDetails()
    report_details = control.list_report_details(report_id)

    return render_template(
        "review_article.html",
        report=report_details
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
    