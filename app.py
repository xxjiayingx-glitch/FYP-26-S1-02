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
from werkzeug.utils import secure_filename
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
from boundary.CompanyProfilePage import companyprof_bp
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

# Controllers
from control.ArticleController import ArticleController
from control.SystemLogCTL import SystemLogCTL
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
app.register_blueprint(companyprof_bp, url_prefix="/company")
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

# Image File Size
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024

# Upload image
app.config["UPLOAD_FOLDER"] = os.path.join("static", "uploads")
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
    search_query = request.args.get("q")

    # Top viewed (HEADER)
    top_viewed = article_controller.get_top_viewed_articles(limit=5)

    # User interest category top articles
    categories = article_controller.get_categories()
    category_top_articles = []

    if categories:
        # Just pick first category OR trending category
        category_id = categories[0]["categoryID"]
        category_top_articles = article_controller.get_top_articles_by_category(category_id, limit=5)

    # Latest articles
    if search_query:
        latest_articles = article_controller.search(search_query) 
    else:
        latest_articles = article_controller.get_latest_articles_by_category(limit=6)

    for article in latest_articles:
            article["featured_image"] = article.get("imageURL")

    return render_template(
        "free_homepage.html",
        search_query=search_query,
        top_viewed=top_viewed,
        category_top_articles=category_top_articles,
        latest_articles=latest_articles
    )


@app.route("/premium_homepage", methods=["GET", "POST"])
def premium_homepage():
    user_id = session.get("userID")
    search_query = request.args.get("q")
    
    # Top viewed articles
    top_viewed = article_controller.get_top_viewed_articles(limit=5)
    
    # User interest category top articles
    saved_articles = article_controller.get_user_saved_articles(user_id, limit=5)
    user_top_category_id = saved_articles[0]["categoryID"] if saved_articles else None
    category_top_articles = article_controller.get_top_articles_by_category(user_top_category_id, limit=5) if user_top_category_id else []

    # Latest articles
    if search_query:
        latest_articles = article_controller.search(search_query) 
    else:
        latest_articles = article_controller.get_latest_articles_by_category(limit=6)

    # Map imageURL → featured_image
    for article in latest_articles:
        article["featured_image"] = article.get("imageURL")
    
    return render_template(
        "premium_homepage.html",
        search_query=search_query,
        top_viewed=top_viewed,
        category_top_articles=category_top_articles,
        saved_articles=saved_articles,
        latest_articles=latest_articles
    )


@app.route("/dashboard")
def dashboard():
    if "userID" not in session:
        return redirect(url_for("login"))

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
        return redirect(url_for("login"))

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
        return redirect(url_for("login"))  # Redirect to login page if not logged in
    
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
    
# Create Article Route
@app.route("/create_article", methods=["GET", "POST"])
def create_article():
    user_id = session.get("userID")
    if not user_id:
        return redirect(url_for("login"))

    if request.method == "POST":
        title = request.form.get("title")
        category_id = request.form.get("category")
        content = request.form.get("content")
        ai_fact_check_score = request.form.get("ai_fact_check_score", 0)
        ai_fact_check_status = request.form.get("ai_fact_check_status")

        status = request.form.get("submit_action")
        if not status:
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
            flash("Article created successfully!", "success")
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
        return redirect(url_for("login"))

    article = article_controller.get_article(article_id)

    if not article or article["created_by"] != user_id:
        flash("You do not have permission to edit this article.", "error")
        return redirect(url_for("my_articles"))

    categories = article_controller.get_categories()

    if request.method == "POST":
        title = request.form.get("title")
        category_id = request.form.get("category")
        content = request.form.get("content")
        status = request.form.get("status")
        ai_fact_check_score = request.form.get("ai_fact_check_score", 0)
        ai_fact_check_status = request.form.get("ai_fact_check_status")

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
            flash("Article updated successfully!", "success")
            SystemLogCTL.logAction(
                accountID=session["userID"],
                action="Updated Article",
                targetID=article_id,
                targetType="Article"
            )
            return redirect(url_for("my_articles"))
        else:
            flash("Failed to update article.", "error")

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
        return redirect(url_for("login"))

    article = article_controller.get_article(article_id)

    if not article or article["created_by"] != user_id:
        flash("You do not have permission to delete this article.", "error")
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
        
    return redirect(url_for("my_articles"))


# @app.route("/testimonial")
# def testimonial():
#     if "userID" not in session:
#         return redirect(url_for("login"))
#     return render_template("testimonial.html")

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
    if "userID" not in session:
        return redirect(url_for("login.login"))
    
    if "premium" not in session.get("userType", "").lower():
        return redirect(url_for("dashboard"))

    user_id = session.get("userID")
    article_id = request.args.get("article_id")

    # Fetch all articles for this user
    articles = article_controller.get_my_articles(user_id)
    selected_article = None
    analytics = {"views": 0, "likes": 0}

    # Try to fetch selected article if provided
    if article_id:
        try:
            article_id = int(article_id)
            selected_article = article_controller.get_article_insight(article_id)

            if selected_article:
                analytics = article_controller.get_article_analytics(article_id)
            else:
                flash("Selected article not found.", "warning")
        except ValueError:
            flash("Invalid article ID.", "error")

    # Auto-select first article if none chosen or invalid
    if not selected_article and articles:
        first_id = articles[0]["articleID"]
        selected_article = article_controller.get_article_insight(first_id)
        analytics = article_controller.get_article_analytics(first_id)

    return render_template(
        "insight.html",
        articles=articles,
        selected_article=selected_article,
        analytics=analytics
    )


# Credibility Trend for Chart.js
@app.route('/credibility_trend/<int:article_id>')
def credibility_trend(article_id):
    data = article_controller.get_article_analytics_over_time(article_id)
    trend = []
    for row in data:
        views, likes, date = row
        score = min((likes / views * 70 + 30), 100) if views else 0
        trend.append({"date": str(date), "score": round(score, 2)})
    return jsonify({"success": True, "data": trend})


# Generate AI Review (AJAX)
@app.route("/generate_ai_review_ajax/<int:article_id>")
def generate_ai_review_ajax(article_id):
    article = article_controller.get_article_insight(article_id)

    if not article:
        return jsonify({"success": False, "message": "Article not found"})

    # If AI review already exists, return it
    if article.get("aiReview"):
        review = article["aiReview"]
    else:
        try:
            # Generate AI summary (replace this with real AI logic)
            review = f"This is an AI summary for '{article['articleTitle']}'"

            # Save AI review to DB
            article_controller.save_ai_review(article_id, review)

        except Exception as e:
            return jsonify({"success": False, "message": str(e)})

    return jsonify({"success": True, "review": review})

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