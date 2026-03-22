from flask import Blueprint, request, redirect, session, url_for
from control.AdminUploadImageCTL import AdminUploadImageCTL

admin_profile_bp = Blueprint("admin_profile", __name__)

@admin_profile_bp.route("/admin/upload-profile-picture", methods=["POST"])
def upload_profile_picture():
    if "userID" not in session:
        return redirect(url_for("login.login"))

    file = request.files.get("profileImage")

    control = AdminUploadImageCTL()
    result = control.upload_profile_picture(file, session["userID"])

    if result["success"]:
        session["profileImage"] = result["filename"]

    return redirect(request.referrer or url_for("admin_dashboard.admin_dashboard"))