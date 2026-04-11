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
    
    if session.get("profileCompleted") == 0:
        flash("Please complete your profile before accessing this page.")
        return redirect(url_for("profile.complete_profile"))

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

    categories = UserAccount.get_all_categories()
    
    return render_template("profile.html", user=user, eligible_article_count=eligible_article_count, force_complete=False, categories=categories)


@profile_bp.route("/update", methods=["POST"])
def update_profile():
    if "userID" not in session:
        return redirect(url_for("login.login"))

    selected_interests = request.form.getlist("interests[]")

    if len(selected_interests) > 5:
        flash("You can select up to 5 interests only.")
        return redirect(url_for("profile.profile_page"))

    try:
        result = UpdateProfileCTL.update_profile(
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

        flash(result["message"])

    except ValueError as e:
        flash(str(e))

    return redirect(url_for("profile.profile_page"))


# EMAIL VERIFICATION
@profile_bp.route("/verify-email-change", methods=["GET"])
def verify_email_change():
    token = request.args.get("token")

    if not token:
        flash("Missing email verification token.")
        return redirect(url_for("profile.profile_page"))

    success = UserAccount.verify_pending_email_change(token)

    if success:
        flash("Your new email has been verified and updated successfully.")
    else:
        flash("Invalid or expired email verification link.")

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



@profile_bp.route("/resend-email-verification", methods=["POST"])
def resend_email_verification():
    if "userID" not in session:
        return redirect(url_for("login.login"))

    user = UserAccount().get_profile(session["userID"])

    if not user or not user.get("pendingEmail"):
        flash("No pending email to verify.")
        return redirect(url_for("profile.profile_page"))

    import secrets
    from server.email_service import send_email_change_verification_email

    new_token = secrets.token_urlsafe(32)

    UserAccount.start_email_change_request(
        session["userID"],
        user["pendingEmail"],
        new_token
    )

    try:
        send_email_change_verification_email(user["pendingEmail"], new_token)
        flash("Verification email resent successfully.")
    except Exception as e:
        print("Resend email failed:", e)
        flash("Failed to resend email.")

    return redirect(url_for("profile.profile_page"))

@profile_bp.route("/complete-profile", methods=["GET", "POST"])
def complete_profile():
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

    if request.method == "POST":
        gender = request.form.get("gender", "").strip()
        dob = request.form.get("dateOfBirth", "").strip()
        interests = request.form.getlist("interests[]")

        form_user = dict(user)
        form_user["gender"] = gender
        form_user["dateOfBirth"] = dob
        form_user["interests"] = interests
        form_user["selected_interests"] = [i.strip().lower() for i in interests if i.strip()]

        if not gender:
            flash("Please select your gender.", "error")
            return render_template(
                "profile.html",
                user=form_user,
                force_complete=True,
                categories=UserAccount.get_all_categories()
            )

        if not dob:
            flash("Please select your date of birth.", "error")
            return render_template(
                "profile.html",
                user=form_user,
                force_complete=True,
                categories=UserAccount.get_all_categories()
            )

        if not interests:
            flash("Please select at least one interest.", "error")
            return render_template(
                "profile.html",
                user=form_user,
                force_complete=True,
                categories=UserAccount.get_all_categories()
            )

        control = UpdateProfileCTL()
        control.update_required_fields(session["userID"], gender, dob, interests)

        session["profileCompleted"] = 1

        return redirect(url_for("dashboard"))
    
    categories = UserAccount.get_all_categories()
    
    return render_template(
        "profile.html",
        user=user,
        force_complete=True,
        categories=categories
    )
