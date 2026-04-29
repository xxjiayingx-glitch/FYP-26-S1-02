from flask import Blueprint, render_template, request, redirect, url_for, session
from control.RegisterCTL import RegisterController
from entity.Article import Article

register_bp = Blueprint("register", __name__)

registerCTL = RegisterController()

article_entity = Article()
def get_categories():
    return article_entity.get_categories()

@register_bp.route("/register", methods=["GET", "POST"])
def register():
    selected_plan = request.args.get("plan") or request.form.get("selected_plan")

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
            firstName, lastName, phone, username, email, password, retypePassword, interests=interests, pending_plan=selected_plan
        )

        if result["success"]:
            return render_template(
                "Unregistered/UnregRegAcc.html",
                categories=get_categories(),
                selected_plan=selected_plan,
                success="Registration successful! Please check your email to verify your account.",
                form_data={}
            )

        return render_template(
            "Unregistered/UnregRegAcc.html",
            categories=get_categories(),
            selected_plan=selected_plan,
            error=result["message"],
            form_data=request.form
        )


    return render_template(
        "Unregistered/UnregRegAcc.html",
        categories=get_categories(),
        selected_plan=selected_plan,
        form_data={}
    )


@register_bp.route("/verify", methods=["GET"])
def verify():
    token = request.args.get("token")
    if not token:
        return render_template("Unregistered/UnregRegAcc.html", categories=get_categories(), error="Missing token")

    success = registerCTL.user_entity.verify_user(token)
    if success:
        return redirect(url_for("login.login"))
    return render_template("Unregistered/UnregRegAcc.html", categories=get_categories(), error="Invalid or expired verification link.")
