from flask import Blueprint, render_template, request, redirect, session, url_for
from werkzeug.security import generate_password_hash
from entity.UserAccount import UserAccount
from control.LoginCTL import AuthController
from control.SystemLogCTL import SystemLogCTL
import secrets
from server.email_service import send_forgot_password_email
from entity.db_connection import get_db_connection

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

        supporting_document = request.files.get("supporting_document")
        document_filename = None

        if supporting_document and supporting_document.filename:
            document_filename = supporting_document.filename

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

        try:
            # Check if email or username already exists
            check_sql = """
                SELECT userID
                FROM UserAccount
                WHERE email = %s OR username = %s
            """
            cursor.execute(check_sql, (email, username))
            existing_user = cursor.fetchone()

            if existing_user:
                cursor.close()
                conn.close()
                return render_template(
                    "editor_applicant.html",
                    error="Email or username already exists."
                )

            # Split full name into first_name and last_name
            name_parts = full_name.split()
            first_name = name_parts[0] if len(name_parts) > 0 else ""
            last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""

            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

            # Insert editor applicant into UserAccount
            # Make sure your UserAccount table has these columns:
            # first_name, last_name, phone, userType, accountStatus,
            # editorApprovalStatus, expertiseArea, yearsExperience,
            # editorBio, portfolioLink, supportingDocument, profileCompleted
            insert_sql = """
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
            """

            cursor.execute(
                insert_sql,
                (
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
                )
            )

            conn.commit()

            return redirect(
                url_for(
                    "login.login",
                    success="Editor application submitted successfully. Please wait for admin approval."
                )
            )

        except Exception as e:
            conn.rollback()
            print("EDITOR APPLICATION ERROR:", e)
            return render_template(
                "editor_applicant.html",
                error="Something went wrong while submitting your application."
            )

        finally:
            cursor.close()
            conn.close()
            
    conn = get_db_connection()
    cursor = conn.cursor()
    
    return render_template("editor_applicant.html",categories=categories)


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