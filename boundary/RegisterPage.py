from flask import Blueprint, render_template, request, redirect, url_for
from control.RegisterCTL import RegisterController

register_bp = Blueprint('register', __name__)

registerCTL = RegisterController()

@register_bp.route("/register", methods=["GET","POST"])
def register():

    if request.method == "POST":
        firstName = request.form["firstName"]
        lastName = request.form["lastName"]
        phone = request.form["phone"]
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        retypePassword = request.form["retypePassword"]

        result = registerCTL.register(firstName, lastName, phone, username, email, password, retypePassword)

        if result["success"]:
            return redirect(url_for("login.login"))

        return render_template(
            "Unregistered/UnregRegAcc.html",
            error=result["message"]
        )

    return render_template("Unregistered/UnregRegAcc.html")