import os
import uuid

from flask import Blueprint, render_template, request, redirect, session, url_for, flash, current_app
from werkzeug.utils import secure_filename

from control.UpdateProfileCTL import UpdateProfileCTL
from entity.UserAccount import UserAccount


profile_bp = Blueprint("profile", __name__)

@profile_bp.route("/")
def profile_page():
    if "userID" not in session:
        return redirect(url_for("login.login"))

    user = UserAccount().get_profile(session["userID"])

    if not user:
        flash("User profile not found.")
        return redirect(url_for("login.login"))

    interests_raw = user.get("interests") or ""
    user["selected_interests"] = [
        i.strip().lower()
        for i in interests_raw.split(",")
        if i.strip()
    ]

    eligible_article_count = UpdateProfileCTL.verify_count(session["userID"])

    return render_template("profile.html", user=user, eligible_article_count=eligible_article_count)

@profile_bp.route("/update", methods=["POST"])
def update_profile():
    if "userID" not in session:
        return redirect(url_for("login.login"))

    selected_interests = request.form.getlist("interests[]")

    if len(selected_interests) > 5:
        flash("You can select up to 5 interests only.")
        return redirect(url_for("profile.profile_page"))

    try:
        UpdateProfileCTL.update_profile(
            session["userID"],
            request.form
        )

        updated_user = UserAccount().get_profile(session["userID"])
        if updated_user:
            updated_user["selected_interests"] = [
                i.strip().lower()
                for i in (updated_user.get("interests") or "").split(",")
                if i.strip()
            ]
            session["user"] = updated_user

        flash("Profile updated successfully")

    except ValueError as e:
        flash(str(e))

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

    try:
        UpdateProfileCTL.change_password(
            session["userID"],
            current_password,
            new_password
        )
        flash("Password updated successfully.")
    except ValueError as e:
        flash(str(e))

    return redirect(url_for("profile.profile_page"))

@profile_bp.route("/upload-photo", methods=["POST"])
def upload_photo():
    if "userID" not in session:
        return redirect(url_for("login.login"))

    file = request.files.get("profile_pic")

    if file and file.filename != "":
        filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
        path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
        file.save(path)

        UpdateProfileCTL.update_profile_photo(
            session["userID"],
            filename
        )

        updated_user = UserAccount().get_profile(session["userID"])
        if updated_user:
            updated_user["selected_interests"] = [
                i.strip().lower()
                for i in (updated_user.get("interests") or "").split(",")
                if i.strip()
            ]
            session["user"] = updated_user

        flash("Profile photo updated successfully.")
    else:
        flash("No file selected.")

    return redirect(url_for("profile.profile_page"))

@profile_bp.route("/apply-verified-badge", methods=["POST"])
def apply_verified_badge():
    if "userID" not in session:
        return redirect(url_for("login.login"))

    try:
        UpdateProfileCTL.apply_verified_badge(session["userID"])

        updated_user = UserAccount().get_profile(session["userID"])
        if updated_user:
            updated_user["selected_interests"] = [
                i.strip().lower()
                for i in (updated_user.get("interests") or "").split(",")
                if i.strip()
            ]
            session["user"] = updated_user

        flash("Verification request submitted successfully.")
    except ValueError as e:
        flash(str(e))

    return redirect(url_for("profile.profile_page"))