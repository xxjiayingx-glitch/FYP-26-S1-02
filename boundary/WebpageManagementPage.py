from flask import Blueprint, render_template, session, redirect, url_for

webpage_management_bp = Blueprint(
    "webpage_management_bp",
    __name__,
    template_folder="../templates"
)

@webpage_management_bp.route("/admin/webpage-management")
def webpage_management_page():

    if "userID" not in session:
        return redirect(url_for("login.login"))

    admin = {
        "username": session.get("username"),
        "profileImage": session.get("profileImage"),
        "userType": session.get("userType")
    }

    return render_template(
        "WebpageManagement.html",
        admin=admin
    )
