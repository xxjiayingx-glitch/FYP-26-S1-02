@category_management_bp.route("/admin/category-management")
def category_management_page():

    if "userID" not in session:
        return redirect(url_for("login"))

    return render_template(
        "CategoryManagementMain.html",
        admin=session   
    )
