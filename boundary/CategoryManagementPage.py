from flask import Blueprint, render_template, session, redirect, url_for

category_management_bp = Blueprint("category_management", __name__)

@category_management_bp.route("/admin/category-management")
def category_management_page():
    if "userID" not in session:
        return redirect(url_for("login"))
    return render_template("CategoryManagementMain.html")
