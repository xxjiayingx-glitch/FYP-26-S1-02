from flask import Blueprint, render_template, session, redirect, url_for, flash,request
from control.ArticleController import ArticleController
from control.ActionOnArticleCTL import ActionOnArticle
from control.AdminDashboardCTL import AdminDashboardControl
from control.SystemLogCTL import SystemLogCTL

all_articles_bp = Blueprint("all_articles", __name__)

@all_articles_bp.route("/admin/view-all-articles")
def admin_view_all_articles():
    if "userID" not in session:
        return redirect(url_for("login.login"))

    user_type = (session.get("userType") or "").strip().lower()

    if user_type != "system admin":
        flash("Access denied.", "danger")
        return redirect(url_for("login.login"))
    
    dashboard_control = AdminDashboardControl()
    admin_data = dashboard_control.get_dashboard_data()

    articles = ArticleController.list_all_articles()

    return render_template(
        "admin_view_all_articles.html",
        articles=articles,
        admin=admin_data["admin"]
    )

@all_articles_bp.route("/admin/view-article-details/<int:article_id>")
def view_article_details(article_id):
    if "userID" not in session:
        return redirect(url_for("login.login"))

    user_type = (session.get("userType") or "").strip().lower()

    if user_type != "system admin":
            flash("Access denied.", "danger")
            return redirect(url_for("login.login"))
    
    dashboard_control = AdminDashboardControl()
    admin_data = dashboard_control.get_dashboard_data()

    control = ArticleController()
    article = control.get_article_details(article_id)

    return render_template(
        "admin_view_article_details.html",
        article=article,
        admin=admin_data["admin"],
    )

@all_articles_bp.route("/admin/view-article-details/<int:articleID>/status", methods=["POST"])
def suspend_or_unsuspend(articleID):
    if "userID" not in session:
        return redirect(url_for("login.login"))

    user_type = (session.get("userType") or "").strip().lower()

    if user_type != "system admin":
        flash("Access denied.", "danger")
        return redirect(url_for("login.login"))

    action = request.form.get("action", "").strip()
    reviewed_by = session.get("userID")

    control = ActionOnArticle()
    result = control.update_status(articleID, action)

    if result:
        flash("Article status updated successfully", "success")

        if action == "suspend":
            SystemLogCTL.logAction(
                accountID=reviewed_by,
                action=f"System Admin reviewed and suspended article {articleID}",
                targetID=articleID,
                targetType="Article"
            )

        else:
            SystemLogCTL.logAction(
                accountID=reviewed_by,
                action=f"System Admin reviewed and unsuspended article {articleID}",
                targetID=articleID,
                targetType="Article"
            )
    else:
        flash("Failed to update article status", "danger")


    return redirect(url_for("all_articles.admin_view_all_articles"))

