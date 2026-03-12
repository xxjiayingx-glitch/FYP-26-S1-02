from flask import Flask, render_template, request, redirect, session, url_for
import mysql.connector

from boundary.LoginPage import login_bp
from boundary.UpdateProfilePage import profile_bp
from boundary.SearchPage import article_bp
from boundary.ArticlePage import comment_bp
from boundary.ViewandManagePage import subscription_bp

app = Flask(__name__)
app.secret_key = "secretkey"

# Register Blueprints
app.register_blueprint(login_bp)
app.register_blueprint(profile_bp)
app.register_blueprint(article_bp)
app.register_blueprint(comment_bp)
app.register_blueprint(subscription_bp)

# MySQL connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="news_system"
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


@app.route("/dashboard")
def dashboard():
    if "userID" not in session:
        return redirect(url_for("login"))

    if session.get("userType", "").lower() == "premium":
        return render_template("premium_dashboard.html")
    return render_template("free_dashboard.html")


@app.route("/article")
def article_detail():
    if "userID" not in session:
        return redirect(url_for("login"))
    return render_template("article_detail.html")


@app.route("/my-articles")
def my_articles():
    if "userID" not in session:
        return redirect(url_for("login"))
    return render_template("my_articles.html")


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


@app.route("/testimonial")
def testimonial():
    if "userID" not in session:
        return redirect(url_for("login"))
    return render_template("testimonial.html")


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