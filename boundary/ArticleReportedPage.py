from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from control.ArticleReportedCTL import ArticleReported
from control.AdminDashboardCTL import AdminDashboardControl
import math

article_reported_bp = Blueprint("article_reported", __name__)

# @article_reported_bp.route("/editor/article-reported", methods=["GET"])
# def article_reported_page():
#     if "userID" not in session:
#         return redirect(url_for("login.login"))

#     user_type = (session.get("userType") or "").strip().lower()
#     editor_status = (session.get("editorApprovalStatus") or "").strip().lower()

#     if user_type != "editor":
#         flash("Access denied.", "danger")
#         return redirect(url_for("login.login"))

#     if editor_status != "approved":
#         flash("Your editor account is not approved yet.", "warning")
#         return redirect(url_for("login.login"))

#     page = request.args.get("page", 1, type=int)
#     per_page = 10

#     expertise_category = session.get("expertiseArea")  
#     print("SESSION expertiseArea =", expertise_category)

#     reported_control = ArticleReported()
#     all_report = all_report = reported_control.list_article_reported(expertise_category=expertise_category, admin_fallback_only=False)

#     total_report = len(all_report)
#     total_pages = math.ceil(total_report/per_page) if total_report > 0 else 1

#     start = (page-1) * per_page
#     end = start + per_page
#     reportedArticles = all_report[start:end]

#     print("SESSION expertiseArea =", session.get("expertiseArea"))
#     print("SESSION expertiseCategoryID =", session.get("expertiseCategoryID"))

#     return render_template(
#         "editor_articles_reported.html",
#         # admin=admin_data["admin"],
#         reportedArticles=reportedArticles,
#         page=page,
#         total_pages=total_pages,
#         active_page="reported"
#     )

# @article_reported_bp.route("/admin/article-reported", methods=["GET"])
# def admin_article_reported_page():
#     if "userID" not in session:
#         return redirect(url_for("login.login"))

#     user_type = (session.get("userType") or "").strip().lower()

#     if user_type != "system admin":
#         flash("Access denied.", "danger")
#         return redirect(url_for("login.login"))

#     page = request.args.get("page", 1, type=int)
#     per_page = 10

#     dashboard_control = AdminDashboardControl()
#     admin_data = dashboard_control.get_dashboard_data()

#     reported_control = ArticleReported()

#     # Admin only sees reported articles whose category has NO approved editor
#     all_report = reported_control.list_article_reported(expertise_category=None,admin_fallback_only=True)

#     total_report = len(all_report)
#     total_pages = math.ceil(total_report / per_page) if total_report > 0 else 1

#     start = (page - 1) * per_page
#     end = start + per_page
#     reportedArticles = all_report[start:end]

#     return render_template(
#         "article_reported.html",
#         admin=admin_data["admin"],
#         reportedArticles=reportedArticles,
#         page=page,
#         total_pages=total_pages,
#         active_page="reported"
#     )
        

@article_reported_bp.route("/editor/article-reported", methods=["GET"])
@article_reported_bp.route("/admin/article-reported", methods=["GET"])
def article_reported_page():
    if "userID" not in session:
        return redirect(url_for("login.login"))

    user_type = (session.get("userType") or "").strip().lower()
    editor_status = (session.get("editorApprovalStatus") or "").strip().lower()

    if user_type not in ["editor", "system admin"]:
        flash("Access denied.", "danger")
        return redirect(url_for("login.login"))

    if user_type == "editor" and editor_status != "approved":
        flash("Your editor account is not approved yet.", "warning")
        return redirect(url_for("login.login"))

    page = request.args.get("page", 1, type=int)
    per_page = 10

    reported_control = ArticleReported()

    admin_data = None

    if user_type == "editor":
        expertise_category = session.get("expertiseArea")

        print("SESSION expertiseArea =", expertise_category)
        print("SESSION expertiseCategoryID =", session.get("expertiseCategoryID"))

        all_report = reported_control.list_article_reported(
            expertise_category=expertise_category,
            admin_fallback_only=False
        )

        template_name = "editor_articles_reported.html"

    else:
        dashboard_control = AdminDashboardControl()
        admin_data = dashboard_control.get_dashboard_data()

        # Admin only sees reported articles whose category has no approved editor
        all_report = reported_control.list_article_reported(
            expertise_category=None,
            admin_fallback_only=True
        )

        template_name = "admin_article_reported.html"

    total_report = len(all_report)
    total_pages = math.ceil(total_report / per_page) if total_report > 0 else 1

    start = (page - 1) * per_page
    end = start + per_page
    reportedArticles = all_report[start:end]

    if user_type == "system admin":
        return render_template(
            template_name,
            admin=admin_data["admin"],
            reportedArticles=reportedArticles,
            page=page,
            total_pages=total_pages,
            active_page="reported"
        )

    return render_template(
        template_name,
        reportedArticles=reportedArticles,
        page=page,
        total_pages=total_pages,
        active_page="reported"
    )
