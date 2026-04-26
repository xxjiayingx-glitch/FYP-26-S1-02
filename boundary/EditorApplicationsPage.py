from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from entity.db_connection import get_db_connection
from control.AdminDashboardCTL import AdminDashboardControl
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

editor_applications_page_bp = Blueprint("editor_applications_page_bp", __name__)

@editor_applications_page_bp.route("/admin/editor-applications")
def manage_applications_pg():
    if "userID" not in session:
        return redirect(url_for("login.login"))
    
    if session.get("userType") != "system admin":
        return redirect("login.login")
    
    dashboard_control = AdminDashboardControl()
    admin_data = dashboard_control.get_dashboard_data()
    
    return render_template("admin_applications_mgmt.html", admin=admin_data["admin"])

@editor_applications_page_bp.route("/admin/view-editor-applications")
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
        "admin_view_editor_applications.html",
        admin=admin,
        applications=applications,
        pending_count=pending_count,
        approved_count=approved_count,
        rejected_count=rejected_count,
        total_count=total_count
    )


@editor_applications_page_bp.route("/admin/view-editor-applications/approve/<int:user_id>", methods=["POST"])
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

    cursor.execute("""
        SELECT username, first_name, last_name, email
        FROM UserAccount
        WHERE userID = %s
    """, (user_id,))

    user = cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()

    if user and user.get("email"):
        full_name = f"{user.get('first_name') or ''} {user.get('last_name') or ''}".strip()
        if not full_name:
            full_name = user.get("username") or "Applicant"

        email_sent = send_editor_application_decision_email(
            to_email=user["email"],
            full_name=full_name,
            decision="approved",
            remarks=admin_remarks
        )

        if email_sent:
            flash("Application approved successfully. Email notification sent.", "success")
        else:
            flash("Application approved successfully, but email could not be sent.", "warning")
    else:
        flash("Application approved successfully, but applicant email was not found.", "warning")

    return redirect(url_for("editor_applications_page_bp.editor_applications_page"))


@editor_applications_page_bp.route("/admin/view-editor-applications/reject/<int:user_id>", methods=["POST"])
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

    cursor.execute("""
        SELECT username, first_name, last_name, email
        FROM UserAccount
        WHERE userID = %s
    """, (user_id,))

    user = cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()

    if user and user.get("email"):
        full_name = f"{user.get('first_name') or ''} {user.get('last_name') or ''}".strip()
        if not full_name:
            full_name = user.get("username") or "Applicant"

        email_sent = send_editor_application_decision_email(
            to_email=user["email"],
            full_name=full_name,
            decision="rejected",
            remarks=admin_remarks
        )

        if email_sent:
            flash("Application rejected successfully. Email notification sent.", "success")
        else:
            flash("Application rejected successfully, but email could not be sent.", "warning")
    else:
        flash("Application rejected successfully, but applicant email was not found.", "warning")

    return redirect(url_for("editor_applications_page_bp.editor_applications_page"))

def send_editor_application_decision_email(to_email, full_name, decision, remarks=""):
    smtp_email = os.getenv("FROM_EMAIL")
    smtp_password = os.getenv("EMAIL_APP_PASSWORD")   # Gmail app password
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))

    if not smtp_email or not smtp_password:
        print("Email not sent: missing FROM_EMAIL or EMAIL_APP_PASSWORD")
        return False

    decision_text = "approved" if decision == "approved" else "rejected"
    subject = f"Your Editor Application Has Been {decision_text.title()}"

    remarks_html = ""
    if remarks:
        remarks_html = f"""
            <p><strong>Admin comments:</strong></p>
            <p>{remarks}</p>
        """

    if decision == "approved":
        body_html = f"""
        <html>
            <body>
                <p>Dear {full_name},</p>

                <p>We are pleased to inform you that your editor application has been <strong>approved</strong>.</p>

                {remarks_html}

                <p>You may now log in to your account and access editor features.</p>

                <p>Best regards,<br>System Administration Team</p>
            </body>
        </html>
        """
    else:
        body_html = f"""
        <html>
            <body>
                <p>Dear {full_name},</p>

                <p>We regret to inform you that your editor application has been <strong>rejected</strong>.</p>

                {remarks_html}

                <p>You may review the feedback and submit a new application if allowed by the system.</p>

                <p>Best regards,<br>System Administration Team</p>
            </body>
        </html>
        """

    try:
        msg = MIMEMultipart()
        msg["From"] = smtp_email
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body_html, "html"))

        server = smtplib.SMTP(smtp_host, smtp_port)
        server.starttls()
        server.login(smtp_email, smtp_password)
        server.send_message(msg)
        server.quit()

        return True

    except Exception as e:
        print("Failed to send editor application email:", e)
        return False


@editor_applications_page_bp.route("/admin/change-requests")
def change_requests_page():
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
            r.requestID,
            ua.username,
            ua.email,
            ua.first_name,
            ua.last_name,
            r.currentExpertise,
            r.requestedExpertise,
            r.status,
            r.requested_at
        FROM EditorExpertiseRequest r
        LEFT JOIN UserAccount ua ON r.userID = ua.userID
        WHERE status = "pending"
        ORDER BY r.requested_at ASC
    """)
    rows = cursor.fetchall()

    applications = []

    for row in rows:
        requestID = row.get("requestID")
        username = row.get("username")
        email = row.get("email")
        first_name = row.get("first_name")
        last_name = row.get("last_name")
        current_expertise = row.get("currentExpertise")
        new_expertise = row.get("requestedExpertise")
        status = row.get("status")
        requested_at = row.get("requested_at")

        full_name = f"{first_name or ''} {last_name or ''}".strip()
        if not full_name:
            full_name = username or "Unknown User"

        applied_at = requested_at
        if applied_at:
            try:
                applied_at_display = applied_at.strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                applied_at_display = str(applied_at)
        else:
            applied_at_display = "-"

        # resume_file_name = ""
        # resume_file_path = ""

        # if supporting_document:
        #     resume_file_path = supporting_document
        #     resume_file_name = os.path.basename(supporting_document)

        # applications.append({
        #     # "applicationID": user_id,
        #     # "userID": user_id,
        #     "fullName": full_name,
        #     "email": email or "-",
        #     "currentExpertise": current_expertise,
        #     # "yearsOfExperience": str(years_experience) if years_experience is not None else "-",
        #     # "editorBio": editor_bio or "-",
        #     # "portfolioLink": portfolio_link or "",
        #     # "resumeFileName": resume_file_name,
        #     # "resumeFilePath": resume_file_path,
        #     "status": status.lower(),
        #     # "adminRemarks": editor_admin_remarks or "",
        #     "newExpertise": new_expertise,
        #     "requested_at": applied_at_display
        # })

        applications.append({
            "requestID": requestID,
            "fullName": full_name,
            "email": email or "-",
            "currentExpertise": current_expertise or "-",
            "newExpertise": new_expertise or "-",
            "status": status.lower(),
            "requested_at": applied_at_display
        })

    # cursor.execute("""
    #     SELECT COUNT(*) AS total
    #     FROM UserAccount
    #     WHERE editorApprovalStatus = 'pending'
    # """)
    # pending_count = cursor.fetchone().get("total", 0)

    # cursor.execute("""
    #     SELECT COUNT(*) AS total
    #     FROM UserAccount
    #     WHERE editorApprovalStatus = 'approved'
    # """)
    # approved_count = cursor.fetchone().get("total", 0)

    # cursor.execute("""
    #     SELECT COUNT(*) AS total
    #     FROM UserAccount
    #     WHERE editorApprovalStatus = 'rejected'
    # """)
    # rejected_count = cursor.fetchone().get("total", 0)

    # cursor.execute("""
    #     SELECT COUNT(*) AS total
    #     FROM UserAccount
    #     WHERE editorApprovalStatus IS NOT NULL
    # """)
    # total_count = cursor.fetchone().get("total", 0)

    cursor.execute("""
        SELECT categoryID, categoryName
        FROM ArticleCategory
        WHERE categoryStatus = 'active'
        ORDER BY categoryName ASC
    """)
    expertise_categories = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "admin_view_change_requests.html",
        admin=admin,
        applications=applications,
        expertise_categories=expertise_categories
        # pending_count=pending_count,
        # approved_count=approved_count,
        # rejected_count=rejected_count,
        # total_count=total_count
    )


@editor_applications_page_bp.route("/admin/change-requests/approve/<int:request_id>", methods=["POST"])
def approve_change(request_id):
    if "userID" not in session:
        return redirect(url_for("login.login"))

    # admin_remarks = request.form.get("adminRemarks", "").strip()

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE EditorExpertiseRequest
        SET status = %s,
            reviewed_at = CURRENT_TIMESTAMP
        WHERE requestID = %s
    """, ("approved", request_id))

    # cursor.execute("""
    #     SELECT username, first_name, last_name, email
    #     FROM UserAccount
    #     WHERE userID = %s
    # """, (user_id,))

    # user = cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()

    # if user and user.get("email"):
    #     full_name = f"{user.get('first_name') or ''} {user.get('last_name') or ''}".strip()
    #     if not full_name:
    #         full_name = user.get("username") or "Applicant"

    #     email_sent = send_editor_application_decision_email(
    #         to_email=user["email"],
    #         full_name=full_name,
    #         decision="approved",
    #         remarks=admin_remarks
    #     )

    #     if email_sent:
    #         flash("Application approved successfully. Email notification sent.", "success")
    #     else:
    #         flash("Application approved successfully, but email could not be sent.", "warning")
    flash("Chnage request approved successfully")

    return redirect(url_for("editor_applications_page_bp.change_requests_page"))


@editor_applications_page_bp.route("/admin/change-requests/reject/<int:request_id>", methods=["POST"])
def reject_change(request_id):
    if "userID" not in session:
        return redirect(url_for("login.login"))

    # admin_remarks = request.form.get("adminRemarks", "").strip()

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE EditorExpertiseRequest
        SET status = %s,
            reviewed_at = CURRENT_TIMESTAMP
        WHERE requestID = %s
    """, ("rejected", request_id))

    # cursor.execute("""
    #     SELECT username, first_name, last_name, email
    #     FROM UserAccount
    #     WHERE userID = %s
    # """, (user_id,))

    # user = cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()

    # if user and user.get("email"):
    #     full_name = f"{user.get('first_name') or ''} {user.get('last_name') or ''}".strip()
    #     if not full_name:
    #         full_name = user.get("username") or "Applicant"

    #     email_sent = send_editor_application_decision_email(
    #         to_email=user["email"],
    #         full_name=full_name,
    #         decision="rejected",
    #         remarks=admin_remarks
    #     )

    #     if email_sent:
    #         flash("Application rejected successfully. Email notification sent.", "success")
    #     else:
    #         flash("Application rejected successfully, but email could not be sent.", "warning")

    flash("Application rejected successfully, but applicant email was not found.", "warning")

    return redirect(url_for("editor_applications_page_bp.change_requests_page"))