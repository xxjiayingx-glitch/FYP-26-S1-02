from flask import Blueprint, render_template, session, redirect, url_for

edit_company_profile_bp = Blueprint("edit_company_profile", __name__)

@edit_company_profile_bp.route("/admin/edit-company-profile")
def edit_company_profile_page():
    if "userID" not in session:
        return redirect(url_for("login"))
    return render_template("EditCompanyProfile.html")
