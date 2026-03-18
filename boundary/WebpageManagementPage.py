from flask import Blueprint, render_template, session, redirect, url_for

webpage_management_bp = Blueprint("webpage_management", __name__)

@webpage_management_bp.route("/admin/webpage-management")
def webpage_management_page():
    if "userID" not in session:
        return redirect(url_for("login"))
    return render_template("WebpageManagement.html")
