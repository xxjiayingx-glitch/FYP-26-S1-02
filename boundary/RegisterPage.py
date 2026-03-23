from flask import Blueprint, render_template, request, redirect, url_for
from control.RegisterCTL import RegisterController
from entity.Article import Article

register_bp = Blueprint("register", __name__)

registerCTL = RegisterController()

article_entity = Article()
def get_categories():
    return article_entity.get_categories()

@register_bp.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":
        firstName = request.form["firstName"]
        lastName = request.form["lastName"]
        phone = request.form["phone"]
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        retypePassword = request.form["retypePassword"]
        interests = request.form.getlist("interests")

        result = registerCTL.register(
            firstName, lastName, phone, username, email, password, retypePassword, interests=interests
        )

        if result["success"]:
            return render_template(
                "Unregistered/UnregRegAcc.html",
                categories=get_categories(), 
                success="Registration successful! Please check your email to verify your account."
            )

        return render_template("Unregistered/UnregRegAcc.html", categories=get_categories(), error=result["message"])

    return render_template("Unregistered/UnregRegAcc.html", categories=get_categories())

@register_bp.route("/verify", methods=["GET"])
def verify():
    token = request.args.get("token")
    if not token:
        return render_template("Unregistered/UnregRegAcc.html", categories=get_categories(), error="Missing token")

    success = registerCTL.user_entity.verify_user(token)
    if success:
        return redirect(url_for("login.login", success="Account verified! You can now log in."))
    return render_template("Unregistered/UnregRegAcc.html", categories=get_categories(), error="Invalid or expired verification link.")
