from flask import Blueprint, render_template, session, redirect, url_for

article_category_page_bp = Blueprint(
    "article_category_page_bp",
    __name__,
    template_folder="../templates"
)

@article_category_page_bp.route("/admin/article-category-page")
def article_category_page():

    admin = {
        "username": "TEST ADMIN",
        "profileImage": None,
        "userType": "System Admin"
    }

    return render_template(
        "ArticleCategory.html",
        admin=admin
    )
