from flask import Blueprint, render_template, session, jsonify, request
from control.ArticleController import ArticleController
from control.TestimonialsCTL import TestimonialController
from control.UnregisteredUser.FeaturesCTL import FeaturesController

home_bp = Blueprint("home", __name__)
articleCTL = ArticleController()
featuresCTL = FeaturesController()
testimonialCTL = TestimonialController()

@home_bp.route("/")
def unreg_home():

    # Ensure user is not signed in otherwise redirect to the respective homepage
    user_type = session.get("userType")

    if user_type == "free":
        return render_template("free_homepage.html")

    if user_type == "premium":
        return render_template("premium_homepage.html")

    # For articles, to display latest and 3 article on guest homepage on load
    headline = articleCTL.get_home_headline()

    if headline:
        latest_articles = articleCTL.get_home_latest_articles(
            limit=3, offset=1 
        )

    else:
        latest_articles = articleCTL.get_home_latest_articles(limit=3, offset=0)
    
    # For testimonials, to display 3 on guest homepage on load
    testimonials=testimonialCTL.getHomeTestimonials(offset=0, limit=3)

    # For product features, to display 4 on guest homepage on load
    features = featuresCTL.get_features(offset=0, limit=4)

    return render_template(
        "Unregistered/UnregHome.html",
        headline=headline,
        articles=latest_articles,
        testimonials=testimonials,
        features=features
    )

@home_bp.route("/load_more_articles")
def load_more_articles():
   
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

# Function for getting more testimonials 
@home_bp.route("/load-more-testimonials")
def load_more_testimonials():

    offset = int(request.args.get("offset", 3))  # default 3
    limit = 6

    testimonials = testimonialCTL.getHomeTestimonials(offset=offset, limit=limit)

    return jsonify(testimonials)

# Function for getting more product features 
@home_bp.route("/load_more_features")
def load_more_features():

    offset = request.args.get("offset", type=int)
    limit = request.args.get("limit", type=int)

    features = featuresCTL.get_features(offset=offset, limit=limit)
    
    return jsonify(features)

@home_bp.route("/article/<int:article_id>")
def unreg_article_detail(article_id):
    article = articleCTL.get_article(article_id)
    if not article:
        return "Article not found", 404

    comments = articleCTL.get_comments_for_article(article_id)

    return render_template(
        "article_detail.html",
        article=article,
        comments=comments,
        is_saved=False,
        is_premium=False
    )