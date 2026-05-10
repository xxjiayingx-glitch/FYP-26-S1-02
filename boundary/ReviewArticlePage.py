from flask import Blueprint, render_template, request, redirect, session, url_for, flash
from control.ReportDetailsCTL import ReportDetails
from control.ActionOnArticleCTL import ActionOnArticle
from control.AdminDashboardCTL import AdminDashboardControl
from control.SystemLogCTL import SystemLogCTL

review_article_bp = Blueprint("review_article", __name__)

# @review_article_bp.route("/editor/article-reported/<int:report_id>")
# def review_article_details(report_id):
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
    
#     control = ReportDetails()
#     report_details = control.list_report_details(report_id)

#     dashboard_control = AdminDashboardControl()
#     admin_data = dashboard_control.get_dashboard_data()

#     return render_template(
#         "editor_review_reported_article.html",
#         report=report_details,
#         admin=admin_data["admin"]
#     )


@review_article_bp.route("/editor/article-reported/<int:report_id>")
@review_article_bp.route("/admin/article-reported/<int:report_id>")
def review_article_details(report_id):
    if "userID" not in session:
        return redirect(url_for("login.login"))

    user_type = (session.get("userType") or "").strip().lower()
    editor_status = (session.get("editorApprovalStatus") or "").strip().lower()

    # Only editor and system admin can access this page
    if user_type not in ["editor", "system admin"]:
        flash("Access denied.", "danger")
        return redirect(url_for("login.login"))

    # Editor must be approved
    if user_type == "editor" and editor_status != "approved":
        flash("Your editor account is not approved yet.", "warning")
        return redirect(url_for("login.login"))

    control = ReportDetails()
    report_details = control.list_report_details(report_id)

    # If system admin, render admin HTML
    if user_type == "system admin":
        dashboard_control = AdminDashboardControl()
        admin_data = dashboard_control.get_dashboard_data()

        return render_template(
            "admin_review_reported_article.html",
            report=report_details,
            admin=admin_data["admin"],
            active_page="reported"
        )

    # If editor, render editor HTML
    return render_template(
        "editor_review_reported_article.html",
        report=report_details,
        active_page="reported"
    )


@review_article_bp.route("/editor/article-reported/<int:articleID>/status", methods=["POST"])
@review_article_bp.route("/admin/article-reported/<int:articleID>/status", methods=["POST"])
def suspend_or_unsuspend(articleID):
    if "userID" not in session:
        return redirect(url_for("login.login"))

    user_type = (session.get("userType") or "").strip().lower()
    editor_status = (session.get("editorApprovalStatus") or "").strip().lower()

    # Allow both editor and system admin
    if user_type not in ["editor", "system admin"]:
        flash("Access denied.", "danger")
        return redirect(url_for("login.login"))

    # Only editor needs approval status check
    if user_type == "editor" and editor_status != "approved":
        flash("Your editor account is not approved yet.", "warning")
        return redirect(url_for("login.login"))

    action = request.form.get("action", "").strip()
    reviewed_by = session.get("userID")

    control = ActionOnArticle()
    result = control.update_article_and_report_status(articleID, action, reviewed_by)

    if result:
        flash("Article status updated successfully", "success")

        role_label = "System admin" if user_type == "system admin" else "Editor"

        if action == "suspend":
            SystemLogCTL.logAction(
                accountID=reviewed_by,
                action=f"{role_label} reviewed and suspended article {articleID}",
                targetID=articleID,
                targetType="Article"
            )

        elif action == "unsuspend":
            SystemLogCTL.logAction(
                accountID=reviewed_by,
                action=f"{role_label} reviewed and unsuspended article {articleID}",
                targetID=articleID,
                targetType="Article"
            )

        else:
            SystemLogCTL.logAction(
                accountID=reviewed_by,
                action=f"{role_label} reviewed article {articleID} without suspending/unsuspending",
                targetID=articleID,
                targetType="Article"
            )

    else:
        flash("Failed to update article status", "danger")

    # Redirect back based on role
    if user_type == "system admin":
        return redirect(url_for("article_reported.article_reported_page"))

    return redirect(url_for("article_reported.article_reported_page"))

# @review_article_bp.route("/editor/article-reported/<int:articleID>/status", methods=["POST"])
# def suspend_or_unsuspend(articleID):
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
    
#     action = request.form.get("action", "").strip()
#     reviewed_by = session.get("userID")

#     control = ActionOnArticle()
#     result = control.update_article_and_report_status(articleID, action, reviewed_by)

#     if result:
#         flash("Article status updated successfully")
#         if action == "suspend":
#             SystemLogCTL.logAction(
#                 accountID=reviewed_by,
#                 action=f"Reviewed and suspended article {articleID}",
#                 targetID=articleID,
#                 targetType="Article"
#             )
#         elif action == "unsuspend":
#             SystemLogCTL.logAction(
#                 accountID=reviewed_by,
#                 action=f"Reviewed and unsuspend article {articleID}",
#                 targetID=articleID,
#                 targetType="Article"
#             )
#         else:
#             SystemLogCTL.logAction(
#                 accountID=reviewed_by,
#                 action=f"Reviewed article {articleID} without suspending/unsuspending ",
#                 targetID=articleID,
#                 targetType="Article"
#             )
            
#     else:
#         flash("Failed to update article status")

#     return redirect(url_for("article_reported.article_reported_page"))
    