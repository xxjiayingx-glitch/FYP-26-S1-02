from flask import Blueprint, render_template, session, redirect, url_for, request
from boundary.WebAdminAPI import get_key_features_paginated

web_management_bp = Blueprint("web_management", __name__)

@web_management_bp.route("/admin/edit-key-product-features")
def edit_key_product_features_page():
    if "userID" not in session:
        return redirect(url_for("login.login"))

    admin = {
        "userID": session.get("userID"),
        "username": session.get("username"),
        "userType": session.get("userType"),
        "profileImage": session.get("profileImage")
    }

    page = request.args.get("page", 1, type=int)
    features, pagination = get_key_features_paginated(page=page, per_page=3)

    return render_template(
    "edit_key_product_features.html",
    admin=admin,
    features=features,
    pagination=pagination
)

