from flask import Blueprint, render_template, request, redirect, session, url_for
from werkzeug.security import generate_password_hash
from entity.UserAccount import UserAccount
from control.LoginCTL import AuthController
from control.SystemLogCTL import SystemLogCTL
import secrets
from server.email_service import send_forgot_password_email
from entity.db_connection import get_db_connection
import os
from werkzeug.utils import secure_filename

login_bp = Blueprint("login", __name__)
auth = AuthController()


@login_bp.route("/login", methods=["GET", "POST"])
def login():
    success_msg = request.args.get("success")

    if request.method == "POST":
        email = request.form["email"]
        pwd = request.form["password"]

        user = auth.login(email, pwd)

        if user == "pending":
            return render_template("login.html", pending=True)

        if user:
            # Extra check for editor approval flow
            user_type = (user.get("userType") or "").strip().lower()
            editor_status = (user.get("editorApprovalStatus") or "").strip().lower()

            # If this is an editor account but not yet approved
            if user_type == "editor":
                if editor_status == "pending":
                    return render_template(
                        "login.html",
                        error="Your editor application is still pending admin approval."
                    )
                elif editor_status == "rejected":
                    return render_template(
                        "login.html",
                        error="Your editor application was rejected. Please contact the admin or reapply."
                    )

            session["userID"] = user["userID"]
            session["username"] = user["username"]
            session["userType"] = user["userType"]
            session["profileImage"] = user.get("profileImage")
            session["profileCompleted"] = user.get("profileCompleted", 0)
            session["editorApprovalStatus"] = user.get("editorApprovalStatus", "")
            session["expertiseArea"] = user.get("expertiseArea")

            SystemLogCTL.logAction(
                accountID=user["userID"],
                action="Logged In",
                targetID=user["userID"],
                targetType="UserAccount"
            )

            # Redirect by role
            if user_type == "system admin":
                return redirect("/admin/dashboard")

            if user_type == "editor":
                return redirect("/editor/dashboard")

            if user.get("profileCompleted") == 0:
                return redirect(url_for("profile.complete_profile"))
            else:
                return redirect("/dashboard")

        return render_template("login.html", error="Invalid email or password")

    return render_template("login.html", success=success_msg)


@login_bp.route("/editor-applicant", methods=["GET", "POST"])
def editor_applicant():
    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT categoryID, categoryName
            FROM ArticleCategory
            WHERE categoryStatus = 'active'
        """)
        categories = cursor.fetchall()

        if request.method == "POST":
            full_name = request.form.get("full_name", "").strip()
            username = request.form.get("username", "").strip()
            email = request.form.get("email", "").strip()
            phone = request.form.get("phone", "").strip()
            password = request.form.get("password", "").strip()
            expertise_area = request.form.get("expertise_area", "").strip()
            years_experience = request.form.get("years_experience", "").strip()
            bio = request.form.get("bio", "").strip()
            portfolio_link = request.form.get("portfolio_link", "").strip()

            # supporting_document = request.files.get("supporting_document")
            # document_filename = None

            # if supporting_document and supporting_document.filename:
            #     document_filename = supporting_document.filename

            # Basic validation
            if not all([full_name, username, email, phone, password, expertise_area, years_experience, bio]):
                return render_template(
                    "editor_applicant.html",
                    error="Please fill in all required fields."
                )

            if len(password) < 10:
                return render_template(
                    "editor_applicant.html",
                    error="Password must be at least 10 characters."
                )
            
            name_parts = full_name.split()
            first_name = name_parts[0] if len(name_parts) > 0 else ""
            last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""

            UPLOAD_FOLDER = os.path.join("static", "uploads", "editor_documents")
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)

            supporting_document = request.files.get("supporting_document")
            document_filename = None

            if supporting_document and supporting_document.filename:
                safe_filename = secure_filename(supporting_document.filename)
                file_path = os.path.join(UPLOAD_FOLDER, safe_filename)
                supporting_document.save(file_path)
                document_filename = f"uploads/editor_documents/{safe_filename}"

            # Check if email or username already exists
            cursor.execute("""
                SELECT userID, email, username, editorApprovalStatus, supportingDocument
                FROM UserAccount
                WHERE email = %s OR username = %s
            """, (email, username))
            existing_user = cursor.fetchone()

            if existing_user:
                existing_status = (existing_user.get("editorApprovalStatus") or "").strip().lower()
                existing_user_id = existing_user.get("userID")
                existing_email = (existing_user.get("email") or "").strip().lower()
                existing_username = (existing_user.get("username") or "").strip().lower()
                existing_document = existing_user.get("supportingDocument")

                if existing_status == "rejected" and existing_email == email.lower() and existing_username == username.lower():
                    hashed_password = generate_password_hash(password, method="pbkdf2:sha256")
                    final_document = document_filename if document_filename else existing_document

                    update_sql = """
                        UPDATE UserAccount
                        SET
                            pwd = %s,
                            first_name = %s,
                            last_name = %s,
                            phone = %s,
                            userType = %s,
                            accountStatus = %s,
                            editorApprovalStatus = %s,
                            expertiseArea = %s,
                            yearsExperience = %s,
                            editorBio = %s,
                            portfolioLink = %s,
                            supportingDocument = %s,
                            editorAdminRemarks = NULL,
                            profileCompleted = %s,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE userID = %s
                    """

                    cursor.execute(
                        update_sql,
                        (
                            hashed_password,
                            first_name,
                            last_name,
                            phone,
                            "editor",
                            "active",
                            "pending",
                            expertise_area,
                            years_experience,
                            bio,
                            portfolio_link,
                            final_document,
                            1,
                            existing_user_id
                        )
                    )

                    conn.commit()

                    return redirect(
                        url_for(
                            "login.login",
                            success="Editor application resubmitted successfully. Please wait for admin approval.We will notify you by email."
                        )
                    )

                return render_template(
                    "editor_applicant.html",
                    categories=categories,
                    error="Email or username already exists."
                )

            # Split full name into first_name and last_name
            # name_parts = full_name.split()
            # first_name = name_parts[0] if len(name_parts) > 0 else ""
            # last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""

            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

            # Insert editor applicant into UserAccount
            # Make sure your UserAccount table has these columns:
            # first_name, last_name, phone, userType, accountStatus,
            # editorApprovalStatus, expertiseArea, yearsExperience,
            # editorBio, portfolioLink, supportingDocument, profileCompleted
            cursor.execute("""
                INSERT INTO UserAccount
                (
                    username,
                    email,
                    pwd,
                    first_name,
                    last_name,
                    phone,
                    userType,
                    accountStatus,
                    editorApprovalStatus,
                    expertiseArea,
                    yearsExperience,
                    editorBio,
                    portfolioLink,
                    supportingDocument,
                    profileCompleted
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,(
                username,
                email,
                hashed_password,
                first_name,
                last_name,
                phone,
                "editor",
                "active",
                "pending",
                expertise_area,
                years_experience,
                bio,
                portfolio_link,
                document_filename,
                1
                ))

            conn.commit()

            return redirect(
                url_for(
                    "login.login",
                    success="Editor application submitted successfully. Please wait for admin approval.We will notify you by email."
                )
            )
        
        return render_template("editor_applicant.html", categories=categories)

    except Exception as e:
        if conn:
            conn.rollback()
        print("EDITOR APPLICATION ERROR:", e)
        return render_template(
            "editor_applicant.html",
            categories=categories if 'categories' in locals() else [],
            error="Something went wrong while submitting your application."
        )

    finally:
        if cursor:
            cursor.close()
        if conn and conn.open:
            conn.close()


@login_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form["email"]
        user = auth.find_by_email(email)

        if user:
            token = secrets.token_urlsafe(32)
            UserAccount.set_password_reset_token(user["userID"], token)
            send_forgot_password_email(email, token)

        return render_template("forgot_password.html", success=True)

    return render_template("forgot_password.html")


@login_bp.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    token = request.args.get("token")

    if not token:
        return redirect(url_for("login.login"))

    if not UserAccount.check_reset_token_valid(token):
        return render_template("reset_password.html", token=token, error="Invalid or expired reset link.")

    if request.method == "POST":
        new_password = request.form["new_password"]
        confirm_password = request.form["confirm_password"]

        if new_password != confirm_password:
            return render_template("reset_password.html", token=token, error="Passwords do not match.")

        if len(new_password) < 10:
            return render_template("reset_password.html", token=token, error="Password must be at least 10 characters.")

        success = UserAccount.reset_password_by_token(
            token,
            generate_password_hash(new_password, method='pbkdf2:sha256')
        )

        if success:
            return redirect(url_for("login.login", success="Password reset successfully. Please log in."))
        else:
            return render_template("reset_password.html", token=token, error="Invalid or expired reset link.")

    return render_template("reset_password.html", token=token)