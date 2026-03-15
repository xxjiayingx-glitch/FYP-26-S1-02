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
import mysql.connector
import os
from werkzeug.utils import secure_filename
from transformers import pipeline

# Blueprints
from boundary.LoginPage import login_bp
from boundary.UpdateProfilePage import profile_bp
from boundary.SearchPage import article_bp
from boundary.ArticlePage import comment_bp
from boundary.ViewandManagePage import subscription_bp
from boundary.TestimonialPage import testimonial_bp
from boundary.HomePage import home_bp
from boundary.CompanyProfilePage import companyprof_bp
from boundary.UnregSubscriptionPage import unregSub_bp
from boundary.RegisterPage import register_bp
from boundary.AdminDashboardPage import admin_dashboard_bp
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
app.register_blueprint(login_bp)
app.register_blueprint(profile_bp, url_prefix="/profile")
app.register_blueprint(article_bp, url_prefix="/articles")
app.register_blueprint(comment_bp, url_prefix="/comments")
app.register_blueprint(subscription_bp, url_prefix="/subscription")
app.register_blueprint(testimonial_bp, url_prefix="/testimonial")
app.register_blueprint(home_bp)
app.register_blueprint(companyprof_bp, url_prefix="/company")
app.register_blueprint(unregSub_bp, url_prefix="/subscribe")
app.register_blueprint(register_bp)
app.register_blueprint(admin_dashboard_bp, url_prefix="/admin")
app.register_blueprint(category_management_bp)
app.register_blueprint(article_category_page_bp)
app.register_blueprint(category_bp)
app.register_blueprint(webpage_management_bp)
app.register_blueprint(edit_company_profile_bp)
app.register_blueprint(edit_subscription_plans_bp)
app.register_blueprint(web_admin_api_bp)

# Image File Size
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024
# Upload image
app.config["UPLOAD_FOLDER"] = os.path.join("static", "uploads")
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# MySQL connection
db = mysql.connector.connect(
    host="localhost", user="root", password="", database="news_system"
)

@app.route("/")
def unreghome():
    return render_template("Unregistered/UnregHome.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        cursor = db.cursor(dictionary=True)
        query = """
            SELECT * FROM UserAccount
            WHERE email = %s AND pwd = %s AND accountStatus = 'active'
        """
        cursor.execute(query, (email, password))
        user = cursor.fetchone()
        cursor.close()

        if user:
            session["userID"] = user["userID"]
            session["username"] = user["username"]
            session["userType"] = user["userType"]
            return redirect(url_for("dashboard"))

        return render_template("login.html", error="Invalid email or password")

    return render_template("login.html")


article_controller = ArticleController()

@app.route("/dashboard")
def dashboard():
    if "userID" not in session:
        return redirect(url_for("login"))

    user_type = str(session.get("userType", "")).lower()

    if user_type == "premium":
        return render_template("premium_homepage.html")

    headline = article_controller.get_headline()
    latest_news = article_controller.get_latest(3)

    # ADD THESE TWO LINES HERE
    print("HEADLINE =", headline)
    print("LATEST =", latest_news)

    return render_template(
        "free_homepage.html", headline=headline, latest_news=latest_news
    )


@app.route("/article")
def article_detail():
    if "userID" not in session:
        return redirect(url_for("login"))
    return render_template("article_detail.html")


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
    user_id = session.get("userID")  # match your login session key
    if not user_id:
        return redirect(url_for("login"))

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

        # create article
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

        article_controller.update_article(
            article_id, title, category_id, content, status, featured_image
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


@app.route("/profile")
def profile():
    if "userID" not in session:
        return redirect(url_for("login"))

    user = {
        "userID": session.get("userID"),
        "username": session.get("username"),
        "userType": session.get("userType"),
    }

    return render_template("profile.html", user=user)


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

    if session.get("userType", "").lower() != "premium":
        return redirect(url_for("dashboard"))

    return render_template("saved_articles.html")


@app.route("/insight")
def insight():
    if "userID" not in session:
        return redirect(url_for("login"))

    if session.get("userType", "").lower() != "premium":
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
