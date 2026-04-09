from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from entity.db_connection import get_db_connection

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
            ea.applicationID,
            ea.userID,
            CONCAT(
                COALESCE(u.first_name, ''),
                CASE
                    WHEN u.first_name IS NOT NULL AND u.last_name IS NOT NULL THEN ' '
                    ELSE ''
                END,
                COALESCE(u.last_name, '')
            ) AS fullName,
            u.email,
            ea.expertiseArea,
            ea.yearsOfExperience,
            ea.editorBio,
            ea.portfolioLink,
            ea.resumeFileName,
            ea.resumeFilePath,
            ea.applicationStatus,
            ea.adminRemarks,
            ea.applied_at
        FROM EditorApplication ea
        JOIN UserAccount u
            ON ea.userID = u.userID
        ORDER BY ea.applied_at DESC
    """)
    applications = cursor.fetchall()

    cursor.execute("""
        SELECT COUNT(*) AS pending_count
        FROM EditorApplication
        WHERE applicationStatus = 'pending'
    """)
    pending_count = cursor.fetchone()["pending_count"]

    cursor.execute("""
        SELECT COUNT(*) AS approved_count
        FROM EditorApplication
        WHERE applicationStatus = 'approved'
    """)
    approved_count = cursor.fetchone()["approved_count"]

    cursor.execute("""
        SELECT COUNT(*) AS rejected_count
        FROM EditorApplication
        WHERE applicationStatus = 'rejected'
    """)
    rejected_count = cursor.fetchone()["rejected_count"]

    cursor.execute("""
        SELECT COUNT(*) AS total_count
        FROM EditorApplication
    """)
    total_count = cursor.fetchone()["total_count"]

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

@editor_applications_page_bp.route("/admin/editor-applications/approve/<int:application_id>", methods=["POST"])
def approve_editor_application(application_id):
    if "userID" not in session:
        return redirect(url_for("login.login"))

    reviewed_by = session.get("userID")
    admin_remarks = request.form.get("adminRemarks", "").strip()

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT applicationID
        FROM EditorApplication
        WHERE applicationID = %s
    """, (application_id,))
    application = cursor.fetchone()

    if not application:
        cursor.close()
        conn.close()
        flash("Application not found.", "error")
        return redirect(url_for("editor_applications_page_bp.editor_applications_page"))

    cursor.execute("""
        UPDATE EditorApplication
        SET applicationStatus = %s,
            adminRemarks = %s,
            reviewed_by = %s,
            reviewed_at = CURRENT_TIMESTAMP
        WHERE applicationID = %s
    """, ("approved", admin_remarks if admin_remarks else None, reviewed_by, application_id))

    conn.commit()
    cursor.close()
    conn.close()

    flash("Application approved successfully.", "success")
    return redirect(url_for("editor_applications_page_bp.editor_applications_page"))


@editor_applications_page_bp.route("/admin/editor-applications/reject/<int:application_id>", methods=["POST"])
def reject_editor_application(application_id):
    if "userID" not in session:
        return redirect(url_for("login.login"))

    reviewed_by = session.get("userID")
    admin_remarks = request.form.get("adminRemarks", "").strip()

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT applicationID
        FROM EditorApplication
        WHERE applicationID = %s
    """, (application_id,))
    application = cursor.fetchone()

    if not application:
        cursor.close()
        conn.close()
        flash("Application not found.", "error")
        return redirect(url_for("editor_applications_page_bp.editor_applications_page"))

    cursor.execute("""
        UPDATE EditorApplication
        SET applicationStatus = %s,
            adminRemarks = %s,
            reviewed_by = %s,
            reviewed_at = CURRENT_TIMESTAMP
        WHERE applicationID = %s
    """, ("rejected", admin_remarks if admin_remarks else None, reviewed_by, application_id))

    conn.commit()
    cursor.close()
    conn.close()

    flash("Application rejected successfully.", "success")
    return redirect(url_for("editor_applications_page_bp.editor_applications_page"))
