from flask import Blueprint,render_template,request
from control.article_controller import ArticleController

article_bp = Blueprint('article',__name__)

article_controller = ArticleController()

@article_bp.route("/dashboard")
def dashboard():

    articles = article_controller.get_articles()

    return render_template("articles.html",articles=articles)


@article_bp.route("/search",methods=["POST"])
def search():

    keyword = request.form["keyword"]

    articles = article_controller.search(keyword)

    return render_template("articles.html",articles=articles)