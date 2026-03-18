from flask import Blueprint, render_template, session, redirect, url_for

article_category_page_bp = Blueprint("article_category_page", __name__)

@article_category_page_bp.route("/admin/article-category")
def article_category_page():
    if "userID" not in session:
        return redirect(url_for("login"))
    return render_template("ArticleCategory.html")
