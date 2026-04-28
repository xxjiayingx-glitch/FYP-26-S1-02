from flask import Flask, render_template, request, redirect, session, url_for, jsonify

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    session,
    url_for,
    flash,
    jsonify,
)
from dotenv import load_dotenv
load_dotenv()
import os
import nltk

NLTK_DATA_DIR = os.path.join(os.getcwd(), "nltk_data")
os.makedirs(NLTK_DATA_DIR, exist_ok=True)

if NLTK_DATA_DIR not in nltk.data.path:
    nltk.data.path.insert(0, NLTK_DATA_DIR)

def ensure_nltk():
    resources = [
        ("punkt", "tokenizers/punkt"),
        ("punkt_tab", "tokenizers/punkt_tab"),
        ("stopwords", "corpora/stopwords")
    ]

    for resource_name, resource_path in resources:
        try:
            nltk.data.find(resource_path)
            print(f"NLTK resource already exists: {resource_name}", flush=True)
        except LookupError:
            print(f"Downloading NLTK resource: {resource_name}", flush=True)
            nltk.download(resource_name, download_dir=NLTK_DATA_DIR)

ensure_nltk()
print("NLTK DATA PATHS:", nltk.data.path, flush=True)

from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash

from entity.db_connection import get_db_connection
from routes.fact_check_routes import fact_check_bp

# timestamp
from datetime import datetime

from boundary.AdminDashboardPage import admin_dashboard_bp
from boundary.ViewUsersPage import view_users_bp
from boundary.LoginPage import login_bp
from boundary.UserDetailsPage import user_details_bp
from boundary.ArticleReportedPage import article_reported_bp
from boundary.ReviewArticlePage import review_article_bp
from boundary.AutoPublishSettingPage import auto_publish_bp
from boundary.UpdateProfilePage import profile_bp
from boundary.SearchPage import article_bp
from boundary.ArticlePage import comment_bp
from boundary.ViewandManagePage import subscription_bp
from boundary.TestimonialPage import testimonial_bp
from boundary.HomePage import home_bp
# from boundary.CompanyProfilePage import companyprof_bp
from boundary.UnregSubscriptionPage import unregSub_bp
from boundary.RegisterPage import register_bp
from boundary.CategoryManagementPage import category_management_bp
from boundary.ArticleCategoryPage import article_category_page_bp
from boundary.CategoryAPI import category_bp
from boundary.WebpageManagementPage import webpage_management_bp
from boundary.EditCompanyProfilePage import edit_company_profile_bp
from boundary.EditSubscriptionPlansPage import edit_subscription_plans_bp
from boundary.WebAdminAPI import web_admin_api_bp
from boundary.AdminVerifyBadgePage import admin_verified_bp
from boundary.AdminUploadImage import admin_profile_bp
from boundary.AdminViewLogsPage import system_monitoring_bp
from boundary.EditKeyProductFeatures import web_management_bp
from boundary.CategoryReportedPage import category_reported_page_bp
from boundary.EditorApplicationsPage import editor_applications_page_bp

# Controllers
from control.ArticleController import ArticleController
from control.SystemLogCTL import SystemLogCTL
from control.ArticleController import ArticleController
article_controller = ArticleController()


# Flask App
app = Flask(__name__)
app.secret_key = "secretkey"

# Register Blueprints
app.register_blueprint(admin_dashboard_bp)
app.register_blueprint(view_users_bp)
app.register_blueprint(login_bp)
app.register_blueprint(user_details_bp)
app.register_blueprint(article_reported_bp)
app.register_blueprint(review_article_bp)
app.register_blueprint(auto_publish_bp)
app.register_blueprint(profile_bp, url_prefix="/profile")
app.register_blueprint(article_bp, url_prefix="/articles")
app.register_blueprint(comment_bp, url_prefix="/comments")
app.register_blueprint(subscription_bp, url_prefix="/subscription")
app.register_blueprint(testimonial_bp, url_prefix="/testimonial")
app.register_blueprint(home_bp)
# app.register_blueprint(companyprof_bp, url_prefix="/company")
app.register_blueprint(unregSub_bp, url_prefix="/subscribe")
app.register_blueprint(register_bp)
app.register_blueprint(category_management_bp)
app.register_blueprint(article_category_page_bp)
app.register_blueprint(category_bp)
app.register_blueprint(webpage_management_bp)
app.register_blueprint(edit_company_profile_bp)
app.register_blueprint(edit_subscription_plans_bp)
app.register_blueprint(web_admin_api_bp)
app.register_blueprint(fact_check_bp)
app.register_blueprint(admin_verified_bp)
app.register_blueprint(admin_profile_bp)
app.register_blueprint(system_monitoring_bp)
app.register_blueprint(web_management_bp)
app.register_blueprint(category_reported_page_bp)
app.register_blueprint(editor_applications_page_bp)

# Image File Size
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024

# Upload image
app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, "static", "uploads")
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

@app.route('/info/<page>')
def info(page):
    valid_pages = ['contact', 'about', 'help', 'privacy', 'terms', 'advertise']
    if page not in valid_pages:
        return "Page not found", 404
    return render_template('info.html', page=page)

# Login
# @app.route("/", methods=["GET", "POST"])
# def login():
#     if "userID" in session:
#         # redirect based on user type
#         if session.get("userType", "").lower() == "premium":
#             return redirect(url_for("premium_homepage"))
#         else:
#             return redirect(url_for("free_homepage"))

#     if request.method == "POST":
#         email = request.form["email"]
#         password = request.form["password"]

#         conn = get_db_connection()
#         cursor = conn.cursor()
#         query = """
#             SELECT * FROM UserAccount
#             WHERE email = %s AND pwd = %s AND accountStatus = 'active'
#         """
#         cursor.execute(query, (email, password))
#         user = cursor.fetchone()
#         cursor.close()
#         conn.close()

#         if user:
#             # set session
#             session["userID"] = user["userID"]
#             session["username"] = user["username"]
#             session["userType"] = user["userType"].lower().strip()

#             print("[LOGIN DEBUG] Session:", session)
#             print("[LOGIN DEBUG] Session after login:", session)

#             # redirect based on user type
#             if "premium" in session.get("userType", "").lower():
#                 return redirect(url_for("premium_homepage"))
#             else:
#                 return redirect(url_for("free_homepage"))

#         return render_template("login.html", error="Invalid email or password")

#     return render_template("login.html")

# Free Registered User Homepage 
@app.route("/free_homepage", methods=["GET", "POST"])
def free_homepage():
    user_id = session.get("userID")
    search_query = request.args.get("q", "").strip()

    # get all categories
    categories = article_controller.get_categories()
    visible_count = 8
    visible_categories = categories[:visible_count]
    more_categories = categories[visible_count:]

    # Top viewed (HEADER)
    headline = article_controller.get_home_headline()

   
    # First top viewed article used as headline/exclude reference
    # top_headline = top_viewed[0] if top_viewed else None
    

    # Latest and Top viewed by category (HEADER)
    category_featured_articles = []

    exclude_id = headline["articleID"] if headline else None
    exclude_category_id = headline["categoryID"] if headline else None

    for category in categories:
        if exclude_category_id and category["categoryID"] == exclude_category_id:
            continue

        article = article_controller.get_featured_article_by_category(
            category["categoryID"],
            exclude_id=exclude_id
        )

        if article:
            category_featured_articles.append({
                "category": category,
                "article": article
            })

    # User interest category top articles
    interest_names = article_controller.get_user_interests(user_id)
    category_ids = article_controller.get_category_ids_from_names(interest_names)

    if category_ids:
        category_top_articles = article_controller.get_articles_by_multiple_categories(
            category_ids, limit=12,  exclude_id=exclude_id
        )
    else:
        category_top_articles = []

    
    
    # Latest articles
    if search_query:
        latest_articles = article_controller.search(search_query) 
    else:
        latest_articles = article_controller.get_home_latest_articles(exclude_id=exclude_id)

    for article in latest_articles:
            article["featured_image"] = article.get("imageURL")

    return render_template(
        "free_homepage.html",
        categories=categories,
        visible_categories=visible_categories,
        more_categories=more_categories,
        search_query=search_query,
        headline=headline,
        category_featured_articles=category_featured_articles,
        category_top_articles=category_top_articles,
        latest_articles=latest_articles
    )

@app.route("/premium_homepage", methods=["GET", "POST"])
def premium_homepage():
    user_id = session.get("userID")
    search_query = request.args.get("q")

    # get all categories
    categories = article_controller.get_categories()
    visible_count = 8
    visible_categories = categories[:visible_count]
    more_categories = categories[visible_count:]
    
    # Top viewed articles
    headline = article_controller.get_home_headline()

    # First top viewed article used as headline/exclude reference
    # top_headline = top_viewed[0] if top_viewed else None
    # exclude_id = top_headline["articleID"] if top_headline else None

    # Latest and top viewed by category
    category_featured_articles = []

    exclude_id = headline["articleID"] if headline else None
    exclude_category_id = headline["categoryID"] if headline else None


    for category in categories:
        if exclude_category_id and category["categoryID"] == exclude_category_id:
            continue

        article = article_controller.get_featured_article_by_category(
            category["categoryID"],
            exclude_id=exclude_id
        )

        if article:
            category_featured_articles.append({
                "category": category,
                "article": article
            })
    
    # User saved articles 
    saved_articles = article_controller.get_user_saved_articles(user_id)
    user_top_category_id = saved_articles[0]["categoryID"] if saved_articles else None

    # User interest category top articles
    interest_names = article_controller.get_user_interests(user_id)
    category_ids = article_controller.get_category_ids_from_names(interest_names)

    if category_ids:
        category_top_articles = article_controller.get_articles_by_multiple_categories(
            category_ids, limit=12, exclude_id=exclude_id
        )
    else:
        category_top_articles = []

    # Latest articles
    if search_query:
        latest_articles = article_controller.search(search_query) 
    else:
        latest_articles = article_controller.get_home_latest_articles(exclude_id=exclude_id)

    # Map imageURL → featured_image
    for article in latest_articles:
        article["featured_image"] = article.get("imageURL")
    
    return render_template(
        "premium_homepage.html",
        categories=categories,
        visible_categories=visible_categories,
        more_categories=more_categories,
        search_query=search_query,
        headline=headline,
        category_featured_articles=category_featured_articles,
        category_top_articles=category_top_articles,
        saved_articles=saved_articles,
        latest_articles=latest_articles
    )


@app.route("/user/articles", defaults={"category_id": None})
@app.route("/user/articles/category/<int:category_id>")
def user_category_articles(category_id=None):
    if "userID" not in session:
        return redirect(url_for("login.login"))

    search_query = request.args.get("q", "").strip()

    categories = article_controller.get_categories()

    visible_count = 8
    visible_categories = categories[:visible_count]
    more_categories = categories[visible_count:]

    selected_category = None
    headline = None
    articles = []
    is_all_page = category_id is None

    if category_id is not None:
        for category in categories:
            if category["categoryID"] == category_id:
                selected_category = category
                break

        if not selected_category:
            return "Category not found", 404

        if search_query:
            articles = article_controller.search_article_in_category(
                keyword=search_query,
                category_id=category_id,
                limit=12
            )
            headline = None
        else:
            headline = article_controller.get_featured_article_by_category(category_id)

            articles = article_controller.home_article_by_category(
                category_id=category_id,
                exclude_id=headline["articleID"] if headline else None
            )

    else:
        if search_query:
            articles = article_controller.search_article_in_category(
                keyword=search_query,
                category_id=None,
                limit=12
            )
            headline = None
        else:
            headline = article_controller.get_home_headline()
            articles = article_controller.get_home_latest_articles(exclude_id=headline["articleID"] if headline else None)

    return render_template(
        "free_premium_category_articles.html",
        categories=categories,
        visible_categories=visible_categories,
        more_categories=more_categories,
        selected_category=selected_category,
        headline=headline,
        articles=articles,
        is_all_page=is_all_page,
        search_query=search_query
    )

@app.route("/dashboard")
def dashboard():
    if "userID" not in session:
        return redirect(url_for("login.login"))

    if session.get("profileCompleted") == 0:
        flash("Please complete your profile before accessing this page.")
        return redirect(url_for("profile.complete_profile"))
   
    user_type = session.get("userType", "").lower()

    if "premium" in user_type:
        return redirect(url_for("premium_homepage"))
    else:
        return redirect(url_for("free_homepage"))

# Article detail page
@app.route("/article/<int:article_id>")
def article_detail(article_id):
    print("ARTICLE ROUTE FILE:", __file__, flush=True)

    user_id = session.get("userID")

    # Increase view first so updated count can be fetched
    article_controller.increment_view_count(article_id)

    article = article_controller.get_article(article_id)
    comments = article_controller.get_comments_for_article(article_id)

    # Safely check if the article is saved
    is_saved = article_controller.is_article_saved(user_id, article_id)

    # Make premium check robust
    user_type = session.get("userType", "").strip().lower()
    is_premium = "premium" in user_type

    print("ARTICLE DETAIL session userID:", session.get("userID"), flush=True)
    print("ARTICLE DETAIL article_id:", article_id, flush=True)
    print("ARTICLE DETAIL is_saved:", is_saved, flush=True)
    print("ARTICLE DETAIL views:", article.get("views") if article else None, flush=True)
    print("ARTICLE DETAIL likes:", article.get("likes") if article else None, flush=True)
    print("ARTICLE DETAIL ROUTE HIT", flush=True)

    return render_template(
        "article_detail.html",
        article=article,
        comments=comments,
        is_saved=is_saved,
        is_premium=is_premium
    )

# Add comment route
@app.route("/add_comment", methods=["POST"])
def add_comment_route():
    if "userID" not in session:
        return redirect(url_for("login.login"))

    article_id = request.form.get("articleID")
    comment_text = request.form.get("commentText")
    user_id = session["userID"]

    article_controller.add_comment(user_id, article_id, comment_text)

    # redirect back to the same article page
    return redirect(url_for("article_detail", article_id=article_id))


# Save article route
@app.route("/toggle_save_article", methods=["POST"])
def toggle_save_article():
    if "userID" not in session:
        return jsonify({"status": "error", "message": "Please log in first."}), 403

    user_type = session.get("userType", "").strip().lower()

    # more robust premium check
    if "premium" not in user_type:
        return jsonify({
            "status": "premium_only",
            "message": "This is a Premium feature. Upgrade your account to save articles and view them later anytime."
        }), 403

    article_id = request.form.get("articleID")
    if not article_id:
        return jsonify({"status": "error", "message": "Missing article ID."}), 400

    article_id = int(article_id)
    user_id = session["userID"]

    now_saved = article_controller.toggle_save_article(user_id, article_id)
    print("SAVE ROUTE userID:", session.get("userID"))
    print("SAVE ROUTE articleID:", request.form.get("articleID"))
    
    return jsonify({
        "status": "saved" if now_saved else "unsaved"
    })

# Report article route
@app.route("/report_article/<int:article_id>", methods=["POST"])
def report_article_route(article_id):
    user_id = session.get("userID")  # Get the logged-in user ID from session
    if not user_id:
        flash("You need to be logged in to report an article.", "warning")
        return redirect(url_for("login.login"))  # Redirect to login page if not logged in
    
    optional_comment = request.form.get('optionalComment', '')
    report_category_id = request.form.get('report_category_id')  # Get the category ID from the form
    
    # Validate the report category
    if not is_valid_report_category(report_category_id):
        flash("Invalid or inactive category", "error")
        return redirect(url_for('article_detail', article_id=article_id))
    
    # Report the article
    article_controller.report_article(article_id, user_id, optional_comment, report_category_id)
    
    flash("Article reported successfully!", "success")
    return redirect(url_for('article_detail', article_id=article_id))

def is_valid_report_category(report_category_id):
    # Query the ReportCategory table to ensure the category exists and is active
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM ReportCategory WHERE reportCategoryID = %s AND categoryStatus = 'active'", (report_category_id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result is not None

# My Articles Route
@app.route("/my_articles", methods=["GET"])
def my_articles():
    user_id = session.get("userID")
    if not user_id:
        return redirect(url_for("login"))
    
    if session.get("profileCompleted") == 0:
        flash("Please complete your profile before accessing this page.")
        return redirect(url_for("profile.complete_profile"))

    keyword = request.args.get("keyword", "").strip()
    category_id = request.args.get("category_id", "").strip()
    status = request.args.get("status", "").strip()   # ✅ ADD THIS

    categories = article_controller.get_categories()

    if keyword or category_id or status:
        articles = article_controller.search_my_articles(
            user_id, keyword, category_id, status   # ✅ PASS IT
        )
    else:
        articles = article_controller.get_my_articles(user_id)

    return render_template(
        "my_articles.html",
        articles=articles,
        keyword=keyword,
        category_id=category_id,
        status=status,   # ✅ SEND TO TEMPLATE
        categories=categories
    )
    
@app.route("/create_article", methods=["GET", "POST"])
def create_article():
    user_id = session.get("userID")
    if not user_id:
        return redirect(url_for("login.login"))

    if request.method == "POST":
        title = request.form.get("title")
        category_id = request.form.get("category")
        content = request.form.get("content")
        ai_fact_check_score = request.form.get("ai_fact_check_score", 0)
        ai_fact_check_status = request.form.get("ai_fact_check_status")

        submit_action = request.form.get("submit_action", "").strip().lower()

        if submit_action == "submit":
            status = "pending review"
        else:
            status = "draft"


        featured_image = request.files.get("featured_image")
        image_filename = None

        if featured_image and featured_image.filename:
            image_filename = secure_filename(featured_image.filename)
            save_path = os.path.join(app.config["UPLOAD_FOLDER"], image_filename)
            featured_image.save(save_path)

        articleID = article_controller.create_article(
            user_id=user_id,
            title=title,
            category_id=category_id,
            content=content,
            status=status,
            featured_image=image_filename,
            ai_fact_check_score=ai_fact_check_score,
            ai_fact_check_status=ai_fact_check_status
        )

        print("FREE USER article created with ID =", articleID, flush=True)

        if articleID:
            SystemLogCTL.logAction(
                accountID=session["userID"],
                action="Created Article",
                targetID=articleID,
                targetType="Article"
            )

            if status == "pending review":
                flash("Article submitted for review successfully!", "success")
            else:
                flash("Article saved as draft successfully!", "success")

            return redirect(url_for("my_articles"))

    categories = article_controller.get_categories()
    current_time = datetime.now().strftime("%d %b %Y %H:%M:%S")

    return render_template(
        "create_article.html",
        categories=categories,
        current_time=current_time
    )

# Edit Article Route
@app.route("/edit_article/<int:article_id>", methods=["GET", "POST"])
def edit_article(article_id):
    user_id = session.get("userID")
    if not user_id:
        return redirect(url_for("login.login"))

    article = article_controller.get_article(article_id)

    if not article or article["created_by"] != user_id:
        flash("You do not have permission to edit this article.", "error")

        if (session.get("userType") or "").strip().lower() == "editor":
            return redirect(url_for("editor_my_articles"))
        return redirect(url_for("my_articles"))

    categories = article_controller.get_categories()

    if request.method == "POST":
        title = request.form.get("title")
        category_id = request.form.get("category")
        content = request.form.get("content")
        ai_fact_check_score = request.form.get("ai_fact_check_score", 0)
        ai_fact_check_status = request.form.get("ai_fact_check_status")

        submit_action = request.form.get("submit_action", "").strip().lower()
        status_from_form = request.form.get("status", "").strip().lower()

        if (session.get("userType") or "").strip().lower() == "editor":
            status = status_from_form if status_from_form else article.get("articleStatus", "draft")
        else:
            if submit_action == "submit":
                status = "pending review"
            else:
                status = "draft"

        featured_image = request.files.get("featured_image")
        image_filename = None

        if featured_image and featured_image.filename:
            image_filename = secure_filename(featured_image.filename)
            save_path = os.path.join(app.config["UPLOAD_FOLDER"], image_filename)
            featured_image.save(save_path)

        updated = article_controller.update_article(
            article_id=article_id,
            title=title,
            category_id=category_id,
            content=content,
            status=status,
            ai_fact_check_score=ai_fact_check_score,
            ai_fact_check_status=ai_fact_check_status
        )

        if updated and image_filename:
            article_controller.update_article_image(article_id, image_filename)

        if updated:
            SystemLogCTL.logAction(
                accountID=session["userID"],
                action="Updated Article",
                targetID=article_id,
                targetType="Article"
            )

            if (session.get("userType") or "").strip().lower() == "editor":
                flash("Article updated successfully!", "success")
                return redirect("/editor/my_articles")

            if status == "pending review":
                flash("Article updated and resubmitted for review successfully!", "success")
            else:
                flash("Article updated and saved as draft successfully!", "success")

            return redirect(url_for("my_articles"))

        else:
            flash("Failed to update article.", "error")

    if (session.get("userType") or "").strip().lower() == "editor":
        return render_template(
            "editor_edit_article.html",
            article=article,
            categories=categories,
            active_page="my_articles"
        )

    return render_template(
        "edit_article.html",
        article=article,
        categories=categories
    )

# Delete Article Route
@app.route("/delete_article/<int:article_id>", methods=["GET"])
def delete_article(article_id):
    user_id = session.get("userID")
    if not user_id:
        return redirect(url_for("login.login"))

    article = article_controller.get_article(article_id)

    if not article or article["created_by"] != user_id:
        flash("You do not have permission to delete this article.", "error")

        if (session.get("userType") or "").strip().lower() == "editor":
            return redirect(url_for("editor_my_articles"))
        return redirect(url_for("my_articles"))

    deleted = article_controller.delete_article(article_id)

    if deleted:
        flash("Article deleted successfully!", "success")
        SystemLogCTL.logAction(
            accountID=session["userID"],
            action="Deleted Article",
            targetID=article_id,
            targetType="Article"
        )
    else:
        flash("Failed to delete article.", "error")

    if (session.get("userType") or "").strip().lower() == "editor":
        return redirect(url_for("editor_my_articles"))
    return redirect(url_for("my_articles"))



@app.route("/saved-articles")
def saved_articles():
    if "userID" not in session:
        return redirect(url_for("login"))
    if "premium" not in session.get("userType", "").lower():
        return redirect(url_for("dashboard"))
    return render_template("saved_articles.html")

# Insight Page - Premium Only
@app.route("/insight")
def insight():
    # --- Access Control ---
    if "userID" not in session:
        return redirect(url_for("login.login"))

    if "premium" not in session.get("userType", "").lower():
        return redirect(url_for("dashboard"))

    if session.get("profileCompleted") == 0:
        flash("Please complete your profile before accessing this page.")
        return redirect(url_for("profile.complete_profile"))

    user_id = session.get("userID")
    article_id = request.args.get("article_id")

    # --- Fetch User Articles ---
    articles = article_controller.get_my_articles(user_id)

    selected_article = None
    analytics = {"views": 0, "likes": 0}

    # --- Helper Function: Calculate Credibility ---
    def attach_credibility(article, analytics):
        views = analytics.get("views", 0)
        likes = analytics.get("likes", 0)
        ai_score = article.get("aiFactCheckScore", 0)

        credibility = article_controller.calculate_credibility(
            ai_score,
            views,
            likes
        )

        article["credibilityScore"] = round(credibility, 2)  # Round for frontend display
        return article

    # --- Case 1: User Selected an Article ---
    if article_id:
        try:
            article_id = int(article_id)
            selected_article = article_controller.get_article_insight(article_id)

            if selected_article:
                analytics = article_controller.get_article_analytics(article_id)
                selected_article = attach_credibility(selected_article, analytics)
            else:
                flash("Selected article not found.", "warning")
        except ValueError:
            flash("Invalid article ID.", "error")

    # --- Case 2: Auto-select First Article if none selected ---
    if not selected_article and articles:
        first_id = articles[0]["articleID"]
        selected_article = article_controller.get_article_insight(first_id)
        analytics = article_controller.get_article_analytics(first_id)
        selected_article = attach_credibility(selected_article, analytics)

    # --- Render Insight Page ---
    return render_template(
        "insight.html",
        articles=articles,
        selected_article=selected_article,
        analytics=analytics
    )

# Generate AI Review (AJAX)
@app.route("/generate_ai_review_ajax/<int:article_id>")
def generate_ai_review_ajax(article_id):
    article = article_controller.get_article_insight(article_id)

    if not article:
        return jsonify({"success": False, "message": "Article not found"})

    try:
        import re
        from collections import Counter
        import textstat

        title = (article.get("articleTitle") or "").strip()
        content = (article.get("content") or "").strip()
        ai_score = float(article.get("aiFactCheckScore", 0) or 0)
        views = int(article.get("views", 0) or 0)
        likes = int(article.get("likes", 0) or 0)

        if not content:
            return jsonify({"success": False, "message": "No article content found"})

        # -----------------------------
        # Basic text preparation
        # -----------------------------
        clean_content = re.sub(r"\s+", " ", content).strip()
        paragraphs = [p.strip() for p in content.split("\n") if p.strip()]
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', clean_content) if s.strip()]
        words = re.findall(r"\b[a-zA-Z][a-zA-Z'-]*\b", clean_content.lower())
        word_count = len(words)
        sentence_count = max(len(sentences), 1)
        avg_sentence_len = round(word_count / sentence_count, 1)

        # -----------------------------
        # Summary
        # -----------------------------
        summary = " ".join(sentences[:2]).strip()
        if not summary:
            summary = clean_content[:250] + "..." if len(clean_content) > 250 else clean_content

        # -----------------------------
        # Readability
        # -----------------------------
        readability = round(textstat.flesch_reading_ease(clean_content), 1)
        grade_level = round(textstat.flesch_kincaid_grade(clean_content), 1)

        # -----------------------------
        # Keyword extraction
        # -----------------------------
        simple_words = [w for w in words if len(w) > 4]
        keywords = [w for w, _ in Counter(simple_words).most_common(5)]
        keyword_text = ", ".join(keywords) if keywords else "No strong keywords detected"

        # -----------------------------
        # Evidence / source signals
        # -----------------------------
        evidence_terms = [
            "according to", "reported", "source", "sources", "data", "study", "studies",
            "research", "survey", "official", "ministry", "agency", "statistic", "statistics"
        ]
        evidence_hits = [term for term in evidence_terms if term in clean_content.lower()]
        evidence_score = min(len(evidence_hits) * 15, 100)

        # -----------------------------
        # Repetition check
        # -----------------------------
        common_words = [w for w in words if len(w) > 4]
        repeated = [w for w, c in Counter(common_words).most_common(5) if c >= 4]
        repetition_flag = len(repeated) > 0

        # -----------------------------
        # Title quality check
        # -----------------------------
        title_words = title.split()
        title_score = 100

        if len(title_words) < 5:
            title_score -= 25
        if len(title_words) > 16:
            title_score -= 15
        if not any(ch.isalpha() for ch in title):
            title_score -= 20
        if ":" in title or "-" in title:
            title_score += 5

        title_score = max(min(title_score, 100), 0)

        # -----------------------------
        # Structure check
        # -----------------------------
        structure_score = 100
        if len(paragraphs) < 2:
            structure_score -= 25
        if sentence_count < 3:
            structure_score -= 20
        if avg_sentence_len > 30:
            structure_score -= 20
        if avg_sentence_len < 8:
            structure_score -= 10

        structure_score = max(min(structure_score, 100), 0)

        # -----------------------------
        # Tone / professionalism signals
        # -----------------------------
        informal_terms = ["very very", "super", "damn", "omg", "lol", "u ", "ur ", "wanna", "gonna"]
        tone_score = 100
        if any(term in clean_content.lower() for term in informal_terms):
            tone_score -= 25
        if "!" in clean_content:
            tone_score -= 10
        tone_score = max(min(tone_score, 100), 0)

        # -----------------------------
        # Local AI quality score
        # -----------------------------
        readability_score = 100
        if readability < 30:
            readability_score = 55
        elif readability < 50:
            readability_score = 75
        elif readability <= 80:
            readability_score = 95
        else:
            readability_score = 80

        local_quality_score = round(
            (readability_score * 0.20) +
            (evidence_score * 0.25) +
            (title_score * 0.15) +
            (structure_score * 0.20) +
            (tone_score * 0.20),
            1
        )

        # -----------------------------
        # Strengths
        # -----------------------------
        strengths = []

        if word_count >= 150:
            strengths.append("The article contains a useful amount of detail.")
        if evidence_hits:
            strengths.append("The content includes evidence-related language that improves credibility.")
        if 50 <= readability <= 80:
            strengths.append("The article is reasonably readable for general audiences.")
        if len(paragraphs) >= 2:
            strengths.append("The article has acceptable paragraph structure.")
        if title_score >= 80:
            strengths.append("The headline is reasonably clear and focused.")

        if not strengths:
            strengths.append("The article has a clear topic and a usable starting structure.")

        # -----------------------------
        # Issues found
        # -----------------------------
        issues = []

        if word_count < 120:
            issues.append("The article is short and may need more context or supporting detail.")
        if not evidence_hits:
            issues.append("There are no strong source or evidence signals in the writing.")
        if len(paragraphs) < 2:
            issues.append("The content is not well separated into paragraphs.")
        if avg_sentence_len > 30:
            issues.append("Some sentences may be too long and harder to read.")
        if avg_sentence_len < 8:
            issues.append("The writing may be too fragmented and abrupt.")
        if repetition_flag:
            issues.append(f"Some words appear repeatedly, such as: {', '.join(repeated[:3])}.")
        if title_score < 70:
            issues.append("The headline could be more specific or informative.")

        if not issues:
            issues.append("No major structural issues were detected.")

        # -----------------------------
        # Suggestions
        # -----------------------------
        suggestions = []

        if word_count < 120:
            suggestions.append("Add more background details, explanation, or examples.")
        if not evidence_hits:
            suggestions.append("Include facts, sources, quoted information, or statistics to strengthen trust.")
        if len(paragraphs) < 2:
            suggestions.append("Break the article into smaller paragraphs to improve readability.")
        if avg_sentence_len > 30:
            suggestions.append("Split long sentences into shorter ones for clarity.")
        if repetition_flag:
            suggestions.append("Replace repeated words with more varied vocabulary.")
        if title_score < 70:
            suggestions.append("Rewrite the title so it is more specific and descriptive.")
        if readability < 40:
            suggestions.append("Use simpler wording to make the article easier for readers to understand.")
        elif readability > 85:
            suggestions.append("Add slightly more professional detail so the article feels stronger and more informative.")

        if not suggestions:
            suggestions.append("The article is fairly balanced overall. Focus on adding stronger supporting evidence for even better credibility.")

        # -----------------------------
        # Credibility explanation
        # -----------------------------
        engagement_score = 0 if views < 10 else min((likes / views) * 100, 100)
        credibility_explanation = (
            f"The article currently has an AI fact-check score of {ai_score}/100. "
            f"The local content quality score is {local_quality_score}/100, based on readability, evidence signals, title quality, structure, and tone. "
            f"Engagement is based on {views} views and {likes} likes, giving an engagement score of {round(engagement_score, 1)}/100. "
            f"Credibility can be improved most by strengthening sources, clarity, and specificity."
        )

        # -----------------------------
        # Final review output
        # -----------------------------
        review = (
            f"Summary:\n{summary}\n\n"
            f"Content analytics:\n"
            f"- Word count: {word_count}\n"
            f"- Sentence count: {sentence_count}\n"
            f"- Average sentence length: {avg_sentence_len} words\n"
            f"- Readability score: {readability}\n"
            f"- Estimated grade level: {grade_level}\n"
            f"- Top keywords: {keyword_text}\n"
            f"- Local quality score: {local_quality_score}/100\n\n"
            f"Strengths:\n- " + "\n- ".join(strengths) + "\n\n"
            f"Issues found:\n- " + "\n- ".join(issues) + "\n\n"
            f"Suggestions to improve:\n- " + "\n- ".join(suggestions) + "\n\n"
            f"Credibility explanation:\n{credibility_explanation}"
        )

        article_controller.save_ai_review(article_id, review)

        return jsonify({"success": True, "review": review})

    except Exception as e:
        import traceback
        print("LOCAL AI REVIEW ERROR:", str(e), flush=True)
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": "AI review temporarily unavailable. Please try again later."
        })
    
# ----------------------------
# ---------- EDITOR ----------
# ----------------------------

@app.route("/editor/dashboard")
def editor_dashboard():
    if "userID" not in session:
        return redirect(url_for("login.login"))

    user_type = (session.get("userType") or "").strip().lower()
    editor_status = (session.get("editorApprovalStatus") or "").strip().lower()

    if user_type != "editor" or editor_status != "approved":
        return redirect(url_for("login.login"))

    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT expertiseArea
        FROM UserAccount
        WHERE userID = %s
    """, (session["userID"],))
    editor = cursor.fetchone()
    expertise = editor["expertiseArea"] if editor else None 

    # ===== TOTAL =====
    cursor.execute("SELECT COUNT(articleID) AS total FROM Article")
    total_articles = cursor.fetchone()["total"]

    # ===== PENDING (own category only) =====
    cursor.execute("""
        SELECT a.articleID, a.articleTitle, a.articleStatus, a.created_at
        FROM Article a
        JOIN ArticleCategory c ON a.categoryID = c.categoryID
        WHERE a.articleStatus = 'pending review'
        AND c.categoryName = %s
        ORDER BY a.created_at DESC
        LIMIT 5
    """, (expertise,))
    pending_articles = cursor.fetchall()
    pending_count = len(pending_articles)

    # ===== APPROVED COUNT =====
    cursor.execute("SELECT COUNT(*) AS count FROM Article WHERE articleStatus = 'published'")
    approved_count = cursor.fetchone()["count"]

    # ===== PENDING REVIEW COUNT =====
    cursor.execute("""
        SELECT COUNT(DISTINCT r.articleID) AS count
        FROM ReportedArticle r
        JOIN Article a ON r.articleID = a.articleID
        JOIN ArticleCategory c ON a.categoryID = c.categoryID
        WHERE r.reportStatus = 'pending review'
        AND c.categoryName = %s
    """, (expertise,))

    reported_count = cursor.fetchone()["count"]
    
    cursor.execute("""
        SELECT expertiseArea
        FROM UserAccount
        WHERE userID = %s
    """, (session["userID"],))
    editor = cursor.fetchone()
    expertise = editor["expertiseArea"] if editor else None
    
    # ===== REPORTED ARTICLES (own category + pending only) =====
    cursor.execute("""
        SELECT 
            MIN(r.reportID) AS reportID,
            r.articleID,
            a.articleTitle,
            c.categoryName AS category,
            COUNT(r.reportID) AS totalReports,
            MAX(r.reported_at) AS latestReportDate,
            a.articleStatus,
            CASE 
                WHEN SUM(CASE WHEN r.reportStatus = 'pending review' THEN 1 ELSE 0 END) > 0 
                THEN 'pending review'
                ELSE 'completed'
            END AS reportStatus
        FROM ReportedArticle r
        JOIN Article a ON r.articleID = a.articleID
        JOIN ArticleCategory c ON a.categoryID = c.categoryID
        WHERE r.reportStatus = 'pending review'
        AND c.categoryName = %s
        GROUP BY r.articleID, a.articleTitle, c.categoryName, a.articleStatus
        ORDER BY latestReportDate DESC
    """, (expertise,))
    reported_articles = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "editor_dashboard.html",
        active_page="dashboard",
        total_articles=total_articles,
        pending_articles=pending_articles,
        pending_count=pending_count,
        approved_count=approved_count,
        reported_count=reported_count,
        reported_articles=reported_articles
    )
    
@app.route("/editor/category_articles")
def editor_category_articles():
    if "userID" not in session:
        return redirect(url_for("login.login"))

    user_id = session["userID"]

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT expertiseArea
        FROM UserAccount
        WHERE userID = %s
    """, (user_id,))
    editor = cursor.fetchone()

    expertise = editor["expertiseArea"] if editor else None

    cursor.execute("""
        SELECT categoryID
        FROM ArticleCategory
        WHERE categoryName = %s AND categoryStatus = 'active'
    """, (expertise,))
    category = cursor.fetchone()

    category_id = category["categoryID"] if category else None

    if category_id:
        cursor.execute("""
            SELECT a.articleID,
                   a.articleTitle,
                   c.categoryName,
                   a.created_by,
                   a.created_at,
                   a.approved_at
            FROM Article a
            JOIN ArticleCategory c ON a.categoryID = c.categoryID
            WHERE a.categoryID = %s
            ORDER BY a.created_at DESC
        """, (category_id,))
        articles = cursor.fetchall()
    else:
        articles = []

    cursor.close()
    conn.close()

    return render_template(
        "editor_category_articles.html",
        active_page="category",
        articles=articles,
        expertise=expertise
    )

@app.route("/editor/article_preview/<int:article_id>")
def editor_article_preview(article_id):
    if "userID" not in session:
        return redirect(url_for("login.login"))

    user_type = (session.get("userType") or "").strip().lower()
    editor_status = (session.get("editorApprovalStatus") or "").strip().lower()

    if user_type != "editor" or editor_status != "approved":
        return redirect(url_for("login.login"))

    article = article_controller.get_article(article_id)

    if not article:
        flash("Article not found.", "error")
        return redirect(url_for("editor_category_articles"))

    return render_template(
        "editor_article_preview.html",
        article=article,
        active_page="category"
    )

@app.route("/editor/my_articles")
def editor_my_articles():
    if "userID" not in session:
        return redirect(url_for("login.login"))

    user_id = session.get("userID")

    keyword = request.args.get("keyword", "").strip()
    status = request.args.get("status", "").strip()

    if keyword or status:
        articles = article_controller.search_my_articles(
            user_id, keyword, None, status
        )
    else:
        articles = article_controller.get_my_articles(user_id)

    return render_template(
        "editor_my_articles.html",
        articles=articles,
        keyword=keyword,
        status=status,
        active_page="my_articles"
    )

@app.route("/editor/create_article", methods=["GET", "POST"])
def editor_create_article():
    if "userID" not in session:
        return redirect(url_for("login.login"))

    user_type = (session.get("userType") or "").strip().lower()
    editor_status = (session.get("editorApprovalStatus") or "").strip().lower()

    if user_type != "editor":
        flash("Access denied.", "danger")
        return redirect(url_for("login.login"))

    if editor_status != "approved":
        flash("Your editor account is not approved yet.", "warning")
        return redirect(url_for("login.login"))

    user_id = session.get("userID")

    if request.method == "POST":
        title = request.form.get("title")
        category_id = request.form.get("category")
        content = request.form.get("content")
        ai_fact_check_score = request.form.get("ai_fact_check_score", 0)
        ai_fact_check_status = request.form.get("ai_fact_check_status")

        submit_action = request.form.get("submit_action", "").strip().lower()

        if submit_action == "submit":
            status = "published"
        else:
            status = "draft"

        featured_image = request.files.get("featured_image")
        image_filename = None

        if featured_image and featured_image.filename:
            image_filename = secure_filename(featured_image.filename)
            save_path = os.path.join(app.config["UPLOAD_FOLDER"], image_filename)
            featured_image.save(save_path)

        articleID = article_controller.create_article(
            user_id=user_id,
            title=title,
            category_id=category_id,
            content=content,
            status=status,
            featured_image=image_filename,
            ai_fact_check_score=ai_fact_check_score,
            ai_fact_check_status=ai_fact_check_status
        )

        if articleID:
            SystemLogCTL.logAction(
                accountID=session["userID"],
                action="Created Article",
                targetID=articleID,
                targetType="Article"
            )

            if status == "published":
                flash("Article published successfully!", "success")
            else:
                flash("Article saved as draft successfully!", "success")

            return redirect(url_for("editor_my_articles"))

    categories = article_controller.get_categories()
    current_time = datetime.now().strftime("%d %b %Y %H:%M:%S")

    return render_template(
        "editor_create_article.html",
        categories=categories,
        current_time=current_time,
        active_page="my_articles"
    )


@app.route("/editor/approval_articles")
def editor_approval_articles():
    if "userID" not in session:
        return redirect(url_for("login.login"))

    user_type = (session.get("userType") or "").strip().lower()
    editor_status = (session.get("editorApprovalStatus") or "").strip().lower()

    if user_type != "editor" or editor_status != "approved":
        return redirect(url_for("login.login"))

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT a.articleID,
               a.articleTitle,
               a.articleStatus,
               a.created_by,
               a.created_at,
               c.categoryName
        FROM Article a
        JOIN ArticleCategory c ON a.categoryID = c.categoryID
        WHERE a.articleStatus = 'pending review'
        ORDER BY a.created_at DESC
    """)
    articles = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "editor_approval_articles.html",
        active_page="approval",
        articles=articles
    )

@app.route("/editor/approve_article", methods=["POST"])
def approve_article():
    if "userID" not in session:
        return redirect(url_for("login.login"))

    user_type = (session.get("userType") or "").strip().lower()
    editor_status = (session.get("editorApprovalStatus") or "").strip().lower()

    if user_type != "editor" or editor_status != "approved":
        return redirect(url_for("login.login"))

    article_id = request.form.get("article_id")

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE Article
            SET articleStatus = 'published',
                approved_at = NOW(),
                updated_at = NOW()
            WHERE articleID = %s
        """, (article_id,))
        conn.commit()
        flash("Article approved successfully.", "success")

    except Exception as e:
        conn.rollback()
        print("APPROVE ARTICLE ERROR:", e)
        flash("Failed to approve article.", "error")

    finally:
        cursor.close()
        conn.close()

    return redirect(url_for("editor_approval_articles"))


@app.route("/editor/reject_article", methods=["POST"])
def reject_article():
    if "userID" not in session:
        return redirect(url_for("login.login"))

    user_type = (session.get("userType") or "").strip().lower()
    editor_status = (session.get("editorApprovalStatus") or "").strip().lower()

    if user_type != "editor" or editor_status != "approved":
        return redirect(url_for("login.login"))

    article_id = request.form.get("article_id")

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE Article
            SET articleStatus = 'rejected',
                updated_at = NOW()
            WHERE articleID = %s
        """, (article_id,))
        conn.commit()
        flash("Article rejected successfully.", "warning")

    except Exception as e:
        conn.rollback()
        print("REJECT ARTICLE ERROR:", e)
        flash("Failed to reject article.", "error")

    finally:
        cursor.close()
        conn.close()

    return redirect(url_for("editor_approval_articles"))
    
@app.route("/editor/manage_profile", methods=["GET", "POST"])
def editor_manage_profile():
    if "userID" not in session:
        return redirect(url_for("login.login"))

    user_type = (session.get("userType") or "").strip().lower()
    editor_status = (session.get("editorApprovalStatus") or "").strip().lower()

    if user_type != "editor" or editor_status != "approved":
        return redirect(url_for("login.login"))

    user_id = session.get("userID")

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        if request.method == "POST":
            form_type = request.form.get("form_type")

            if form_type == "profile":
                full_name = request.form.get("full_name", "").strip()
                username = request.form.get("username", "").strip()
                email = request.form.get("email", "").strip()
                phone = request.form.get("phone", "").strip()
                years_experience = request.form.get("years_experience", "").strip()
                editor_bio = request.form.get("editor_bio", "").strip()
                portfolio_link = request.form.get("portfolio_link", "").strip()

                name_parts = full_name.split()
                first_name = name_parts[0] if len(name_parts) > 0 else ""
                last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""

                update_sql = """
                    UPDATE UserAccount
                    SET first_name = %s,
                        last_name = %s,
                        username = %s,
                        email = %s,
                        phone = %s,
                        yearsExperience = %s,
                        editorBio = %s,
                        portfolioLink = %s,
                        updated_at = NOW()
                    WHERE userID = %s
                """

                cursor.execute(update_sql, (
                    first_name,
                    last_name,
                    username,
                    email,
                    phone,
                    years_experience if years_experience else None,
                    editor_bio,
                    portfolio_link,
                    user_id
                ))
                conn.commit()

                session["username"] = username
                flash("Profile updated successfully.", "success")

            elif form_type == "password":
                current_password = request.form.get("current_password", "").strip()
                new_password = request.form.get("new_password", "").strip()
                confirm_new_password = request.form.get("confirm_new_password", "").strip()

                if not current_password or not new_password or not confirm_new_password:
                    flash("Please fill in all password fields.", "error")
                else:
                    cursor.execute(
                        "SELECT pwd FROM UserAccount WHERE userID = %s",
                        (user_id,)
                    )
                    user = cursor.fetchone()

                    if not user:
                        flash("User account not found.", "error")
                    elif not check_password_hash(user["pwd"], current_password):
                        flash("Current password is incorrect.", "error")
                    elif new_password != confirm_new_password:
                        flash("New password and confirm password do not match.", "error")
                    elif len(new_password) < 10:
                        flash("New password must be at least 10 characters.", "error")
                    elif current_password == new_password:
                        flash("New password cannot be the same as your current password.", "error")
                    else:
                        hashed_new_password = generate_password_hash(
                            new_password,
                            method='pbkdf2:sha256'
                        )

                        cursor.execute("""
                            UPDATE UserAccount
                            SET pwd = %s,
                                updated_at = NOW()
                            WHERE userID = %s
                        """, (hashed_new_password, user_id))
                        conn.commit()

                        flash("Password changed successfully.", "success")

        cursor.execute("SELECT * FROM UserAccount WHERE userID = %s", (user_id,))
        profile = cursor.fetchone()

        cursor.execute("""
            SELECT categoryID, categoryName
            FROM ArticleCategory
            WHERE categoryStatus = 'active'
            ORDER BY categoryName ASC
        """)
        categories = cursor.fetchall()

        cursor.execute("""
            SELECT requestID, currentExpertise, requestedExpertise, status, requested_at, reviewed_at
            FROM EditorExpertiseRequest
            WHERE userID = %s
            ORDER BY requested_at DESC
            LIMIT 1
        """, (user_id,))
        latest_expertise_request = cursor.fetchone()

        return render_template(
            "editor_manage_profile.html",
            active_page="profile",
            profile=profile,
            categories=categories,
            latest_expertise_request=latest_expertise_request
        )

    except Exception as e:
        conn.rollback()
        print("EDITOR MANAGE PROFILE ERROR:", e)
        flash("Something went wrong. Please try again.", "error")

        cursor.execute("SELECT * FROM UserAccount WHERE userID = %s", (user_id,))
        profile = cursor.fetchone()

        cursor.execute("""
            SELECT categoryID, categoryName
            FROM ArticleCategory
            WHERE categoryStatus = 'active'
            ORDER BY categoryName ASC
        """)
        categories = cursor.fetchall()

        cursor.execute("""
            SELECT requestID, currentExpertise, requestedExpertise, status, requested_at, reviewed_at
            FROM EditorExpertiseRequest
            WHERE userID = %s
            ORDER BY requested_at DESC
            LIMIT 1
        """, (user_id,))
        latest_expertise_request = cursor.fetchone()

        return render_template(
            "editor_manage_profile.html",
            active_page="profile",
            profile=profile,
            categories=categories,
            latest_expertise_request=latest_expertise_request
        )

    finally:
        cursor.close()
        conn.close()

@app.route("/editor/request_expertise", methods=["POST"])
def request_expertise():
    if "userID" not in session:
        return redirect(url_for("login.login"))

    user_type = (session.get("userType") or "").strip().lower()
    editor_status = (session.get("editorApprovalStatus") or "").strip().lower()

    if user_type != "editor" or editor_status != "approved":
        return redirect(url_for("login.login"))

    user_id = session.get("userID")
    new_expertise = request.form.get("new_expertise", "").strip()

    if not new_expertise:
        flash("Please select a new expertise area.", "error")
        return redirect(url_for("editor_manage_profile"))

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT expertiseArea
            FROM UserAccount
            WHERE userID = %s
        """, (user_id,))
        user = cursor.fetchone()

        current_expertise = user["expertiseArea"] if user else None

        if current_expertise == new_expertise:
            flash("Requested expertise cannot be the same as your current expertise.", "warning")
            return redirect(url_for("editor_manage_profile"))

        cursor.execute("""
            SELECT *
            FROM EditorExpertiseRequest
            WHERE userID = %s
              AND requestedExpertise = %s
              AND status = 'pending'
            ORDER BY requested_at DESC
            LIMIT 1
        """, (user_id, new_expertise))
        existing_request = cursor.fetchone()

        if existing_request:
            flash("You already have a pending request for this expertise.", "warning")
            return redirect(url_for("editor_manage_profile"))

        cursor.execute("""
            INSERT INTO EditorExpertiseRequest
            (userID, currentExpertise, requestedExpertise, status, requested_at)
            VALUES (%s, %s, %s, 'pending', NOW())
        """, (user_id, current_expertise, new_expertise))

        conn.commit()
        flash("Expertise change request submitted successfully for admin approval.", "success")

    except Exception as e:
        conn.rollback()
        print("REQUEST EXPERTISE ERROR:", e)
        flash("Failed to submit expertise request.", "error")

    finally:
        cursor.close()
        conn.close()

    return redirect(url_for("editor_manage_profile"))

@app.route("/editor/profile_background")
def editor_profile_background():
    if "userID" not in session:
        return redirect(url_for("login.login"))

    user_id = session.get("userID")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM UserAccount
        WHERE userID = %s
    """, (user_id,))

    profile = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template(
        "editor_profile_background.html",
        profile=profile,
        active_page="profile"
    )

@app.route("/editor/article/<int:article_id>")
def editor_article_detail(article_id):
    if "userID" not in session:
        return redirect(url_for("login.login"))

    user_type = (session.get("userType") or "").strip().lower()
    editor_status = (session.get("editorApprovalStatus") or "").strip().lower()

    if user_type != "editor" or editor_status != "approved":
        return redirect(url_for("login.login"))

    article = article_controller.get_article(article_id)
    comments = article_controller.get_comments_for_article(article_id)

    if not article:
        flash("Article not found.", "error")
        return redirect(url_for("editor_my_articles"))

    return render_template(
        "editor_article_detail.html",
        article=article,
        comments=comments,
        active_page="my_articles"
    )


@app.route("/logout")
def logout():
    user_id = session.get("userID")

    if user_id:
        SystemLogCTL.logAction(
            accountID=user_id,
            action="Logged Out",
            targetID=user_id,
            targetType="UserAccount"
        )

    session.clear()
    return redirect(url_for("login.login"))


if __name__ == "__main__":
    app.run(debug=True)
