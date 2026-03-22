from flask import Blueprint, render_template, session, redirect, url_for

article_category_page_bp = Blueprint(
    "article_category_page_bp",
    __name__,
    template_folder="../templates"
)


@article_category_page_bp.route("/admin/article-category-page")
def article_category_page_view():

    if "userID" not in session:
        return redirect(url_for("login.login"))

    admin = {
        "username": session.get("username"),
        "profileImage": session.get("profileImage"),
        "userType": session.get("userType")
    }

    return render_template(
        "ArticleCategory.html",
        admin=admin
    )
