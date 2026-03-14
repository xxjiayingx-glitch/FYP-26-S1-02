from flask import Flask, render_template, request, redirect, session, url_for
import mysql.connector

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

from control.ArticleController import ArticleController
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

# Image File Size
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024

# MySQL connection
db = mysql.connector.connect(
    host="localhost", user="root", password="", database="news_system"
)


@app.route("/", methods=["GET", "POST"])
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

    user_type = str(session.get("userType","")).lower()

    if user_type == "premium":
        return render_template("premium_homepage.html")

    headline = article_controller.get_headline()
    latest_news = article_controller.get_latest(3)

    # ADD THESE TWO LINES HERE
    print("HEADLINE =", headline)
    print("LATEST =", latest_news)

    return render_template(
        "free_homepage.html",
        headline=headline,
        latest_news=latest_news
    )


@app.route("/article")
def article_detail():
    if "userID" not in session:
        return redirect(url_for("login"))
    return render_template("article_detail.html")


# My Articles page
@app.route("/my_articles")
def my_articles():
    user_id = session.get('userID')  # <-- use the same key as login
    if not user_id:
        return redirect(url_for("login"))
    articles = article_controller.get_my_articles(user_id)
    return render_template("my_articles.html", articles=articles)


# Create Article page
@app.route("/create_article", methods=["GET", "POST"])
def create_article():
    if "userID" not in session:
        return redirect(url_for("login"))

    user_id = session.get("userID")
    categories = article_controller.get_categories()

    if request.method == "POST":
        title = request.form.get("title")
        category = request.form.get("category")
        content = request.form.get("content")
        status = request.form.get("status")
        featured_image = request.files.get("featured_image")

        # Debugging prints
        print("Form submission:")
        print("user_id:", user_id)
        print("title:", title)
        print("category:", category)
        print("content length:", len(content) if content else 0)
        print("status:", status)
        print("featured_image:", featured_image.filename if featured_image else None)

        article_id = article_controller.create_article(user_id, title, category, content, status, featured_image)

        if article_id:
            print("Article created successfully with ID:", article_id)
            return redirect(url_for("my_articles"))
        else:
            print("Failed to create article.")
            return render_template("create_article.html", categories=categories, error="Failed to create article.")

    return render_template("create_article.html", categories=categories)


@app.route("/profile")
def profile():
    if "userID" not in session:
        return redirect(url_for("login"))
    return render_template("profile.html")


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

    return render_template("insight.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
