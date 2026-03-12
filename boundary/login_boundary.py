from flask import Blueprint,render_template,request,redirect,session
from control.auth_controller import AuthController

login_bp = Blueprint('login',__name__)

auth = AuthController()

@login_bp.route("/",methods=["GET","POST"])
def login():

    if request.method=="POST":

        email = request.form["email"]
        pwd = request.form["password"]

        user = auth.login(email,pwd)

        if user:
            session["userID"] = user["userID"]
            return redirect("/dashboard")

    return render_template("login.html")