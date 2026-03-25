from flask import Blueprint, render_template, session, redirect, url_for

edit_company_profile_bp = Blueprint(
    "edit_company_profile_bp",
    __name__,
    template_folder="../templates"
)

@edit_company_profile_bp.route("/admin/edit-company-profile")
def edit_company_profile_page():

    if "userID" not in session:
        return redirect(url_for("login.login"))

    admin = {
        "username": session.get("username"),
        "profileImage": session.get("profileImage"),
        "userType": session.get("userType")
    }

    return render_template(
        "EditCompanyProfile.html",
        admin=admin
    )
