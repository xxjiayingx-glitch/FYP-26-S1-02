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
from dotenv import load_dotenv
load_dotenv()
from werkzeug.utils import secure_filename
from entity.db_connection import get_db_connection

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

# Controllers
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
@app.route("/", methods=["GET", "POST"])
def login():
    if "userID" in session:
        # redirect based on user type
        if session.get("userType", "").lower() == "premium":
            return redirect(url_for("premium_homepage"))
        else:
            return redirect(url_for("free_homepage"))

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
            SELECT * FROM UserAccount
            WHERE email = %s AND pwd = %s AND accountStatus = 'active'
        """
        cursor.execute(query, (email, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            # set session
            session["userID"] = user["userID"]
            session["username"] = user["username"]
            session["userType"] = user["userType"].lower().strip()

            # redirect based on user type
            if "premium" in session.get("userType", "").lower():
                return redirect(url_for("premium_homepage"))
            else:
                return redirect(url_for("free_homepage"))

        return render_template("login.html", error="Invalid email or password")

    return render_template("login.html")

# Free Registered User Homepage 
@app.route("/free_homepage", methods=["GET", "POST"])
def free_homepage():
    user_id = session.get("userID")
    search_query = request.args.get("q")  # get query from URL
    
    if search_query:
        latest_news = article_controller.search(search_query)  # use your search function
    else:
        latest_news = article_controller.get_latest_articles_by_category(6)
    testimonials = article_controller.get_testimonials()
    
    return render_template(
        "free_homepage.html",
        latest_news=latest_news,
        testimonials=testimonials,
        search_query=search_query
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
        latest_articles = article_controller.search(search_query)  # ✅ use search
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
    if "userID" not in session:
        return redirect(url_for("login"))

    user_id = session["userID"]
    article = article_controller.get_article(article_id)
    comments = article_controller.get_comments_for_article(article_id)
    is_saved = article_controller.is_article_saved(user_id, article_id)

    # Robust premium check
    user_type = session.get("userType", "").strip().lower()
    is_premium = "premium" in user_type  # <- key fix

    # Debugging
    print(f"[DEBUG] userID={user_id}, userType={user_type}, is_premium={is_premium}, is_saved={is_saved}")

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


# Save article route (for premium users)
@app.route("/toggle_save_article", methods=["POST"])
def toggle_save_article():
    if "userID" not in session:
        return redirect(url_for("login"))

    if "premium" not in session.get("userType", "").lower():
        return redirect(url_for("dashboard"))

    article_id = request.form.get("articleID")
    user_id = session["userID"]

    # This handles save/unsave automatically
    now_saved = article_controller.toggle_save_article(user_id, article_id)

    if now_saved:
        flash("Article saved successfully!", "success")
    else:
        flash("Article removed from saved list.", "info")

    return redirect(request.referrer)


# Report article route
@app.route("/report_article", methods=["POST"])
def report_article():
    if "userID" not in session:
        return redirect(url_for("login"))

    article_id = request.form.get("articleID")
    author_id = request.form.get("authorID")
    user_id = session["userID"]
    optional_comment = request.form.get("optionalComment", "")

    article_controller.report_article(user_id, article_id, author_id, optional_comment)

    flash("Article reported successfully!", "success")
    return redirect(request.referrer)


# My Articles Route
@app.route("/my_articles", methods=["GET"])
def my_articles():
    user_id = session.get("userID")
    if not user_id:
        return redirect(url_for("login"))

    keyword = request.args.get("keyword", "").strip()

    if keyword:
        articles = article_controller.search_my_articles(user_id, keyword)
    else:
        articles = article_controller.get_my_articles(user_id)

    return render_template("my_articles.html", articles=articles, keyword=keyword)


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
        
        # Use the button pressed to determine status
        status = request.form.get("submit_action")  # 'draft' or 'published'
        if not status:
            status = "draft"  # fallback default

        featured_image = request.files.get("featured_image")
        image_filename = None

        if featured_image and featured_image.filename:
            image_filename = secure_filename(featured_image.filename)
            save_path = os.path.join(app.config["UPLOAD_FOLDER"], image_filename)
            featured_image.save(save_path)

        # Insert article
        article_controller.create_article(
            user_id, title, category_id, content, status, image_filename
        )

        flash("Article created successfully!", "success")
        return redirect(url_for("my_articles"))

    # GET → fetch categories
    categories = article_controller.get_categories()
    return render_template("create_article.html", categories=categories)


# Edit Article Route
@app.route("/edit_article/<int:article_id>", methods=["GET", "POST"])
def edit_article(article_id):
    user_id = session.get("userID")
    if not user_id:
        return redirect(url_for("login"))

    article = article_controller.get_article(article_id)

    # Ensure the article belongs to the logged-in user
    if not article or article["created_by"] != user_id:
        flash("You do not have permission to edit this article.", "error")
        return redirect(url_for("my_articles"))

    categories = article_controller.get_categories()

    if request.method == "POST":
        title = request.form.get("title")
        category_id = request.form.get("category")
        content = request.form.get("content")
        status = request.form.get("status")

        featured_image = request.files.get("featured_image")
        image_filename = None

        if featured_image and featured_image.filename:
            image_filename = secure_filename(featured_image.filename)
            save_path = os.path.join(app.config["UPLOAD_FOLDER"], image_filename)
            featured_image.save(save_path)

        article_controller.update_article(
            article_id, title, category_id, content, status, image_filename
        )
        flash("Article updated successfully!", "success")
        return redirect(url_for("my_articles"))

    return render_template("edit_article.html", article=article, categories=categories)


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

    article_controller.delete_article(article_id)
    flash("Article deleted successfully!", "success")
    return redirect(url_for("my_articles"))





@app.route("/subscription")
def subscription():
    if "userID" not in session:
        return redirect(url_for("login"))
    return render_template("subscription.html")

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


@app.route("/insight")
def insight():
    if "userID" not in session:
        return redirect(url_for("login"))
    if "premium" not in session.get("userType", "").lower():
        return redirect(url_for("dashboard"))
    
    user_id = session.get("userID")
    article_id = request.args.get("article_id")
    articles = article_controller.get_my_articles(user_id)
    selected_article = None

    if article_id:
        try:
            article_id = int(article_id)
            selected_article = article_controller.get_article_insight(article_id)
        except ValueError:
            selected_article = None

    # Auto-show first article if none selected
    if not selected_article and articles:
        selected_article = article_controller.get_article_insight(
            articles[0]["articleID"]
        )

    return render_template(
        "insight.html", articles=articles, selected_article=selected_article
    )


@app.route("/generate_ai_review_ajax/<int:article_id>")
def generate_ai_review_ajax(article_id):
    # Use your ArticleController method
    article = article_controller.get_article_insight(article_id)

    if not article:
        return jsonify({"success": False, "message": "Article not found"})

    # If AI review already exists, return it
    if article.get("aiReview"):
        review = article["aiReview"]
    else:
        try:
            # Replace with your real AI logic
            review = f"This is an AI summary for '{article['articleTitle']}'"

            # Save AI review in DB
            article_controller.save_ai_review(article_id, review)

        except Exception as e:
            return jsonify({"success": False, "message": str(e)})

    return jsonify({"success": True, "review": review})


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)