from flask import Blueprint, render_template, request, redirect, session, url_for
from control.LoginCTL import AuthController
from control.SystemLogCTL import SystemLogCTL

login_bp = Blueprint("login", __name__)
auth = AuthController()

@login_bp.route("/login", methods=["GET", "POST"])
def login():
    success_msg = request.args.get("success")
    if request.method == "POST":
        email = request.form["email"]
        pwd = request.form["password"]

        user = auth.login(email, pwd)

        if user == "pending_verification":
            return render_template("login.html", error="Please verify your email before logging in")
        
        if user:
            session["userID"] = user["userID"]
            session["username"] = user["username"]
            session["userType"] = user["userType"]
            session["profileImage"] = user["profileImage"]
            session["profileCompleted"] = user["profileCompleted"]

            # Logs login record
            SystemLogCTL.logAction(
            accountID=user["userID"],
            action="Logged In",
            targetID=user["userID"],
            targetType="UserAccount"
            )

            if user["userType"] == "system admin":
                return redirect("/admin/dashboard")

            # First-time login if gender, DOB, and interests are all null
            # is_first_login = (
            #     not user.get("gender") and
            #     not user.get("dateOfBirth") and
            #     not user.get("interests")
            # )

            # if is_first_login:
            #     return redirect("/profile?first_login=1")

            if user["profileCompleted"] == 0:
                return redirect(url_for("profile.complete_profile"))
            else:
                return redirect("/dashboard")

        return render_template("login.html", error="Invalid email or password")

    return render_template("login.html", success=success_msg)