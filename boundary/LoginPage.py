from flask import Blueprint,render_template,request,redirect,session
from control.LoginCTL import AuthController

login_bp = Blueprint('login',__name__)

auth = AuthController()

@login_bp.route("/login",methods=["GET","POST"])
def login():

    if request.method=="POST":

        email = request.form["email"]
        pwd = request.form["password"]

        user = auth.login(email,pwd)

        if user:
            session["userID"] = user["userID"]
            session["username"] = user["username"]
            session["userType"] = user["userType"]
            session["profileImage"] = user["profileImage"]

            if user["userType"] == "system admin":
                return redirect("/admin/dashboard")
            else:
                return redirect("/dashboard")

    return render_template("login.html")