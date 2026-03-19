import os
from flask import Blueprint, render_template, request, redirect, session, url_for, flash, current_app
from werkzeug.utils import secure_filename

from control.UpdateProfileCTL import UpdateProfileCTL
from entity.UserAccount import UserAccount

profile_bp = Blueprint("profile", __name__)


@profile_bp.route("/profile")
def profile_page():
    if "userID" not in session:
        return redirect(url_for("login.login"))

    user = UserAccount().get_profile(session["userID"])

    if not user:
        flash("User profile not found.")
        return redirect(url_for("login.login"))

    user["selected_interests"] = user["interests"].split(",") if user.get("interests") else []
    print("Session userID:", session.get("userID"))
    print("Raw interests from DB:", user.get("interests"))

    user["selected_interests"] = user["interests"].split(",") if user.get("interests") else []

    print("Selected interests list:", user["selected_interests"])
    return render_template("profile.html", user=user)


@profile_bp.route("/update", methods=["POST"])
def update_profile():
    if "userID" not in session:
        return redirect(url_for("login.login"))

    UpdateProfileCTL.update_profile(
        session["userID"],
        request.form
    )

    flash("Profile updated successfully")
    return redirect(url_for("profile.profile_page"))


@profile_bp.route("/change-password", methods=["POST"])
def change_password():
    if "userID" not in session:
        return redirect(url_for("login.login"))

    current_password = request.form.get("current_password")
    new_password = request.form.get("new_password")
    confirm_password = request.form.get("confirm_password")

    if not current_password or not new_password or not confirm_password:
        flash("Please fill in all password fields.")
        return redirect(url_for("profile.profile_page"))

    if new_password != confirm_password:
        flash("New password and confirm password do not match.")
        return redirect(url_for("profile.profile_page"))

    UpdateProfileCTL.change_password(
        session["userID"],
        current_password,
        new_password
    )

    flash("Password updated successfully")
    return redirect(url_for("profile.profile_page"))


@profile_bp.route("/upload-photo", methods=["POST"])
def upload_photo():
    if "userID" not in session:
        return redirect(url_for("login.login"))

    file = request.files.get("profile_pic")

    if file and file.filename != "":
        filename = secure_filename(file.filename)
        path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
        file.save(path)

        UpdateProfileCTL.update_profile_photo(
            session["userID"],
            filename
        )

        flash("Profile photo updated successfully.")
    else:
        flash("No file selected.")

    return redirect(url_for("profile.profile_page"))