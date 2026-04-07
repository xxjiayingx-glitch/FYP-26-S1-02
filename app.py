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
from boundary.EditKeyProductFeatures import web_management_bp

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
app.register_blueprint(web_management_bp)

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
        from statistics import mean
        from sumy.parsers.plaintext import PlaintextParser
        from sumy.nlp.tokenizers import Tokenizer
        from sumy.summarizers.lsa import LsaSummarizer
        import textstat
        from rake_nltk import Rake

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
        parser = PlaintextParser.from_string(content, Tokenizer("english"))
        summarizer = LsaSummarizer()
        summary_sentences = summarizer(parser.document, 2)
        summary = " ".join(str(s) for s in summary_sentences).strip()

        if not summary:
            summary = " ".join(sentences[:2])

        # -----------------------------
        # Readability
        # -----------------------------
        readability = round(textstat.flesch_reading_ease(clean_content), 1)
        grade_level = round(textstat.flesch_kincaid_grade(clean_content), 1)

        # -----------------------------
        # Keyword extraction
        # -----------------------------
        rake = Rake()
        rake.extract_keywords_from_text(clean_content)
        keywords = rake.get_ranked_phrases()[:5]
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
        print("LOCAL AI REVIEW ERROR:", str(e))
        return jsonify({"success": False, "message": str(e)})
    
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