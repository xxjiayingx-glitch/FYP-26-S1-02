from flask import Blueprint, render_template, session, jsonify, request
from control.ArticleController import ArticleController
from control.TestimonialsCTL import TestimonialController
from control.UnregisteredUser.FeaturesCTL import FeaturesController
from control.UnregisteredUser.ViewCompanyProfileCTL import CompanyProfileController
from control.UnregisteredUser.SubscriptionCTL import SubscriptionCTL

home_bp = Blueprint("home", __name__)
articleCTL = ArticleController()
featuresCTL = FeaturesController()
testimonialCTL = TestimonialController()
companyProfileCTL = CompanyProfileController()
subscriptionCTL = SubscriptionCTL()

@home_bp.route("/")
def unreg_home():
    # For articles, to display latest and 3 article on guest homepage on load
    headline = articleCTL.get_home_headline()

    if headline:
        latest_articles = articleCTL.get_home_latest_articles(
            limit=3, offset=0,
            exclude_id=headline["articleID"]
        )

    else:
        latest_articles = articleCTL.get_home_latest_articles(limit=3, offset=0)
    
    # Display testimonial
    testimonials=testimonialCTL.getHomeTestimonials()

    # For product features, to display 4 on guest homepage on load
    features = featuresCTL.get_features(offset=0, limit=4)

    # Display company profile
    profile = companyProfileCTL.getCompanyProfile()

    plans = subscriptionCTL.getSubscriptionPlans()

    categories = articleCTL.get_categories()

    visible_count = 8
    visible_categories = categories[:visible_count]
    more_categories = categories[visible_count:]

    category_featured_articles = []

    exclude_id = headline["articleID"] if headline else None

    for category in categories:
        article = articleCTL.get_featured_article_by_category(
            category["categoryID"],
            exclude_id=exclude_id
        )

        if article:
            category_featured_articles.append({
                "category": category,
                "article": article
            })

    return render_template(
        "Unregistered/UnregHome.html",
        categories=categories,
        visible_categories=visible_categories,
        more_categories=more_categories,
        headline=headline,
        articles=latest_articles,
        category_featured_articles=category_featured_articles,
        testimonials=testimonials,
        features=features,
        profile=profile,
        plans=plans["plans"]
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
            "imageURL": a['imageURL'],
            "views": a['views']
        }
        for a in articles
    ]
    
    return jsonify(articles_json)

# Function for getting more testimonials 
# @home_bp.route("/load-more-testimonials")
# def load_more_testimonials():

#     offset = int(request.args.get("offset", 4))  # default 3
#     limit = 8

#     testimonials = testimonialCTL.getHomeTestimonials(offset=offset, limit=limit + 1)

#     has_more = len(testimonials) > limit
#     testimonials = testimonials[:limit]

#     return jsonify({
#         "testimonials": testimonials,
#         "has_more": has_more
#     })

# Function for getting more product features 
@home_bp.route("/load_more_features")
def load_more_features():

    offset = request.args.get("offset", 0, type=int)
    limit = request.args.get("limit", 4, type=int)

    features = featuresCTL.get_features(offset=offset, limit=limit + 1)

    has_more = len(features) > limit
    features = features[:limit]

    return jsonify({
        "features": features,
        "has_more": has_more
    })

@home_bp.route("/article/<int:article_id>")
def unreg_article_detail(article_id):
    article = articleCTL.get_article(article_id)
    articleCTL.increment_view_count(article_id)

    if not article:
        return "Article not found", 404

    comments = articleCTL.get_comments_for_article(article_id)

    user_id = session.get("userID")
    user_type = session.get("userType", "").strip().lower()

    is_premium = "premium" in user_type
    is_saved = articleCTL.is_article_saved(user_id, article_id) if user_id else False

    return render_template(
        "article_detail.html",
        article=article,
        comments=comments,
        is_saved=is_saved,
        is_premium=is_premium
    )

@home_bp.route("/all-articles")
def all_articles():
    categories = articleCTL.get_categories()
    visible_count = 8
    visible_categories = categories[:visible_count]
    more_categories = categories[visible_count:]

    headline = articleCTL.get_home_headline()
    articles = articleCTL.get_home_latest_articles(
        limit=12,
        exclude_id=headline["articleID"] if headline else None
    )

    return render_template(
        "Unregistered/category_articles.html",
        categories=categories,
        visible_categories=visible_categories,
        more_categories=more_categories,
        selected_category=None,
        headline=headline,
        articles=articles,
        is_all_page=True
    )

@home_bp.route("/category/<int:category_id>")
def category_articles(category_id):
    categories = articleCTL.get_categories()
    visible_count = 8
    visible_categories = categories[:visible_count]
    more_categories = categories[visible_count:]

    selected_category = None
    for category in categories:
        if category["categoryID"] == category_id:
            selected_category = category
            break

    if not selected_category:
        return "Category not found", 404

    headline = articleCTL.get_featured_article_by_category(category_id)

    if headline:
        articles = articleCTL.home_article_by_category(
            category_id=category_id,
            limit=6,
            exclude_id=headline["articleID"]
        )
    else:
        articles = articleCTL.home_article_by_category(
            category_id=category_id,
            limit=6
        )

    return render_template(
        "Unregistered/category_articles.html",
        categories=categories,
        visible_categories=visible_categories,
        more_categories=more_categories,
        selected_category=selected_category,
        headline=headline,
        articles=articles,
        is_all_page=False
    )
