from flask import Blueprint, render_template, session, jsonify, request
from control.ArticleController import ArticleController

home_bp = Blueprint("home", __name__)
articleCTL = ArticleController()

@home_bp.route("/")
def unreg_home():

    user_type = session.get("userType")

    if user_type is None:
        # Get headline article
        headline = articleCTL.get_headline()
    
    # Get latest 3 articles
    latest_articles = []
    if headline:
        latest_articles = articleCTL.get_home_latest_articles(limit=3, offset=0, exclude_id=headline['articleID'])
    else:
        latest_articles = articleCTL.get_home_latest_articles(limit=3, offset=0)        
    
    if user_type == "free":
        return render_template("free_homepage.html")

    if user_type == "premium":
        return render_template("premium_homepage.html")

    return render_template("Unregistered/UnregHome.html", headline=headline, articles=latest_articles)
@home_bp.route("/load_more_articles")
def load_more_articles():
    """
    AJAX route to fetch more articles for homepage.
    Parameters:
        - offset: number of articles to skip
        - limit: number of articles to return
    Excludes headline article from results.
    """
    try:
        offset = int(request.args.get('offset', 0))
        limit = int(request.args.get('limit', 6))
    except ValueError:
        offset = 0
        limit = 6

    headline = articleCTL.get_headline()
    exclude_id = headline['articleID'] if headline else None

    articles = articleCTL.get_home_latest_articles(limit=limit, offset=offset, exclude_id=exclude_id)

    # Convert to JSON
    articles_json = [
        {
            "articleID": a['articleID'],
            "articleTitle": a['articleTitle'],
            "content": a['content'][:150],  # short preview
            "imageURL": a['imageURL']
        }
        for a in articles
    ]

    return jsonify(articles_json)