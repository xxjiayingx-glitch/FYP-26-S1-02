from flask import Blueprint, render_template, session

home_bp = Blueprint("home", __name__)

@home_bp.route("/")
def unreg_home():

    user_type = session.get("userType")

    if user_type is None:
        return render_template("Unregistered/UnregHome.html")

    if user_type == "free":
        return render_template("free_homepage.html")

    if user_type == "premium":
        return render_template("premium_homepage.html")

    return render_template("Unregistered/UnregHome.html")
