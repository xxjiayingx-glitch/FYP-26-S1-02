from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from entity.db_connection import get_db_connection
import os

editor_applications_page_bp = Blueprint("editor_applications_page_bp", __name__)


@editor_applications_page_bp.route("/admin/editor-applications")
def editor_applications_page():
    if "userID" not in session:
        return redirect(url_for("login.login"))

    admin = {
        "userID": session.get("userID"),
        "username": session.get("username"),
        "userType": session.get("userType"),
        "profileImage": session.get("profileImage")
    }

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            userID,
            username,
            email,
            first_name,
            last_name,
            editorApprovalStatus,
            expertiseArea,
            yearsExperience,
            editorBio,
            portfolioLink,
            supportingDocument,
            editorAdminRemarks,
            updated_at,
            created_at
        FROM UserAccount
        WHERE editorApprovalStatus IS NOT NULL
        ORDER BY userID DESC
    """)
    rows = cursor.fetchall()

    applications = []

    for row in rows:
        user_id = row.get("userID")
        username = row.get("username")
        email = row.get("email")
        first_name = row.get("first_name")
        last_name = row.get("last_name")
        approval_status = row.get("editorApprovalStatus")
        expertise_area = row.get("expertiseArea")
        years_experience = row.get("yearsExperience")
        editor_bio = row.get("editorBio")
        portfolio_link = row.get("portfolioLink")
        supporting_document = row.get("supportingDocument")
        editor_admin_remarks = row.get("editorAdminRemarks")
        updated_at = row.get("updated_at")
        created_at = row.get("created_at")

        full_name = f"{first_name or ''} {last_name or ''}".strip()
        if not full_name:
            full_name = username or "Unknown User"

        applied_at_raw = updated_at or created_at
        if applied_at_raw:
            try:
                applied_at_display = applied_at_raw.strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                applied_at_display = str(applied_at_raw)
        else:
            applied_at_display = "-"

        resume_file_name = ""
        resume_file_path = ""

        if supporting_document:
            resume_file_path = supporting_document
            resume_file_name = os.path.basename(supporting_document)

        applications.append({
            "applicationID": user_id,
            "userID": user_id,
            "fullName": full_name,
            "email": email or "-",
            "expertiseArea": expertise_area or "-",
            "yearsOfExperience": str(years_experience) if years_experience is not None else "-",
            "editorBio": editor_bio or "-",
            "portfolioLink": portfolio_link or "",
            "resumeFileName": resume_file_name,
            "resumeFilePath": resume_file_path,
            "applicationStatus": (approval_status or "pending").lower(),
            "adminRemarks": editor_admin_remarks or "",
            "applied_at": applied_at_display
        })

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM UserAccount
        WHERE editorApprovalStatus = 'pending'
    """)
    pending_count = cursor.fetchone().get("total", 0)

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM UserAccount
        WHERE editorApprovalStatus = 'approved'
    """)
    approved_count = cursor.fetchone().get("total", 0)

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM UserAccount
        WHERE editorApprovalStatus = 'rejected'
    """)
    rejected_count = cursor.fetchone().get("total", 0)

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM UserAccount
        WHERE editorApprovalStatus IS NOT NULL
    """)
    total_count = cursor.fetchone().get("total", 0)

    cursor.close()
    conn.close()

    return render_template(
        "editor_applications.html",
        admin=admin,
        applications=applications,
        pending_count=pending_count,
        approved_count=approved_count,
        rejected_count=rejected_count,
        total_count=total_count
    )


@editor_applications_page_bp.route("/admin/editor-applications/approve/<int:user_id>", methods=["POST"])
def approve_editor_application(user_id):
    if "userID" not in session:
        return redirect(url_for("login.login"))

    admin_remarks = request.form.get("adminRemarks", "").strip()

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE UserAccount
        SET editorApprovalStatus = %s,
            editorAdminRemarks = %s,
            updated_at = CURRENT_TIMESTAMP
        WHERE userID = %s
    """, ("approved", admin_remarks if admin_remarks else None, user_id))

    conn.commit()
    cursor.close()
    conn.close()

    flash("Application approved successfully.", "success")
    return redirect(url_for("editor_applications_page_bp.editor_applications_page"))


@editor_applications_page_bp.route("/admin/editor-applications/reject/<int:user_id>", methods=["POST"])
def reject_editor_application(user_id):
    if "userID" not in session:
        return redirect(url_for("login.login"))

    admin_remarks = request.form.get("adminRemarks", "").strip()

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE UserAccount
        SET editorApprovalStatus = %s,
            editorAdminRemarks = %s,
            updated_at = CURRENT_TIMESTAMP
        WHERE userID = %s
    """, ("rejected", admin_remarks if admin_remarks else None, user_id))

    conn.commit()
    cursor.close()
    conn.close()

    flash("Application rejected successfully.", "success")
    return redirect(url_for("editor_applications_page_bp.editor_applications_page"))
