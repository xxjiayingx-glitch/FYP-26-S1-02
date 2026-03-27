from flask import Blueprint, render_template, session, redirect, url_for

web_management_bp = Blueprint("web_management", __name__)

@web_management_bp.route("/admin/edit-key-product-features")
def edit_key_features():
    if "userID" not in session:
        return redirect(url_for("login.login"))
    
    if session.get("userType") != "system admin":
        return redirect("login.login")

    admin = {
        "username": session.get("username"),
        "profileImage": session.get("profileImage"),
        "userType": session.get("userType")
    }

    return render_template(
        "edit_key_product_features.html",
        admin=admin
    )

@web_management_bp.route("/admin/edit-key-product-features/update", methods=["POST"])
def update_key_feature():
    return redirect(url_for("web_management.edit_key_product_features"))