from flask import Blueprint, render_template, request, redirect, session
from control.UpdateProfileCTL import update_user_profile

profile_bp = Blueprint('profile', __name__)

@profile_bp.route("/profile")
def profile():

    return render_template("profile.html")


@profile_bp.route("/update_profile", methods=["POST"])
def update_profile():

    userID = session["userID"]

    first = request.form["first_name"]
    last = request.form["last_name"]
    phone = request.form["phone"]

    update_user_profile(userID, first, last, phone)

    return redirect("/profile")