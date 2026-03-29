from flask import Blueprint, render_template, request, redirect, session, url_for
from werkzeug.security import generate_password_hash
from entity.UserAccount import UserAccount
from control.LoginCTL import AuthController
from control.SystemLogCTL import SystemLogCTL
import secrets
from server.email_service import send_forgot_password_email 

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
            session["userID"] = user["userID"]
            session["username"] = user["username"]
            session["userType"] = user["userType"]
            session["profileImage"] = user["profileImage"]
            session["profileCompleted"] = user["profileCompleted"]

            SystemLogCTL.logAction(
                accountID=user["userID"],
                action="Logged In",
                targetID=user["userID"],
                targetType="UserAccount"
            )

            if user["userType"] == "system admin":
                return redirect("/admin/dashboard")

            if user["profileCompleted"] == 0:
                return redirect(url_for("profile.complete_profile"))
            else:
                return redirect("/dashboard")

        return render_template("login.html", error="Invalid email or password")

    return render_template("login.html", success=success_msg)

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

        success = UserAccount.reset_password_by_token(token, generate_password_hash(new_password, method='pbkdf2:sha256'))

        if success:
            return redirect(url_for("login.login", success="Password reset successfully. Please log in."))
        else:
            return render_template("reset_password.html", token=token, error="Invalid or expired reset link.")

    return render_template("reset_password.html", token=token)