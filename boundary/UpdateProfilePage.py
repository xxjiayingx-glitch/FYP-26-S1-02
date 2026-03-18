import os
from flask import request, redirect, session, url_for, current_app
from flask import Blueprint, flash, render_template, request, redirect, session
from control.UpdateProfileCTL import UpdateProfileCTL
from werkzeug.utils import secure_filename

profile_bp = Blueprint("profile", __name__)


@profile_bp.route("/profile")
def profile_page():
    if "userID" not in session:
        return redirect(url_for("login"))

    user = UserAccount().get_profile(session["userID"])
    user["selected_interests"] = user["interests"].split(",") if user.get("interests") else []

    return render_template("profile.html", user=user)


@profile_bp.route("/update", methods=["POST"])
def update_profile():

    UpdateProfileCTL.update_profile(
        session["userID"],
        request.form
    )

    flash("Profile updated successfully")
    return redirect("/profile")

@profile_bp.route("/change-password", methods=["POST"])
def change_password():

    password = request.form["password"]
    new_password = request.form["new_password"]

    UpdateProfileCTL.change_password(
        session["userID"],
        password,
        new_password
    )

    flash("Password updated")
    return redirect("/profile")

@profile_bp.route("/upload-photo", methods=["POST"])
def upload_photo():

    if "userID" not in session:
        return redirect(url_for("login"))

    file = request.files.get("profile_pic")

    if file and file.filename != "":
        filename = secure_filename(file.filename)

        path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
        file.save(path)

        # update database
        UpdateProfileCTL.update_profile_photo(
            session["userID"],
            filename
        )

    return redirect("/profile")