from flask import Blueprint, render_template

home_bp = Blueprint('home', __name__)

@home_bp.route("/home")
def unreg_home():
    return render_template("Unregistered/UnregHome.html")