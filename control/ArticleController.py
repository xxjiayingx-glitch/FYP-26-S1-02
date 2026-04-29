# control/ArticleController.py
from entity.Article import Article
from entity.db_connection import get_db_connection
from pymysql.cursors import DictCursor
from datetime import datetime

class ArticleController:

    def __init__(self):
        self.article_entity = Article()

    def get_articles(self):
        return self.article_entity.get_all_articles()
    
    def search(self, keyword):
        return self.article_entity.search_articles(keyword)
    
    def search_article_in_category(self, keyword, category_id=None, limit=12):
        return self.article_entity.search_article_in_category(keyword, category_id, limit)

    def get_categories(self):
        return self.article_entity.get_categories()
    
    def get_my_articles(self, user_id):
        return self.search_my_articles(user_id)    
    
    def create_article(self, user_id, title, category_id, content, status, featured_image=None,
                   ai_fact_check_score=0, ai_fact_check_status=None):
        article_id = self.article_entity.insert_article(
            user_id, title, category_id, content, status,
            ai_fact_check_score, ai_fact_check_status
        )
        if article_id and featured_image:
            self.article_entity.insert_article_image(article_id, featured_image)
        return article_id

    def get_headline(self):
        return self.article_entity.get_headline_article()

    def get_latest_articles_by_category(self, limit=12, exclude_id=None):
        return self.article_entity.get_latest_articles_by_category(limit)

    def get_home_headline(self):
        return self.article_entity.get_home_headline_article()
    
    def get_featured_article_by_category(self, category_id, exclude_id=None):
        return self.article_entity.get_featured_article_by_category(category_id, exclude_id)

    def get_home_latest_articles(self, exclude_id=None):
        return self.article_entity.get_home_latest_articles(exclude_id)
    
    def home_article_by_category(self, category_id, exclude_id=None):
        return self.article_entity.home_article_by_category(
            category_id=category_id,
            exclude_id=exclude_id
        )

    def delete_article(self, article_id):
        return self.article_entity.delete_article(article_id)

    def search_my_articles(self, user_id, keyword="", category_id="", status=""):
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            SELECT 
                a.articleID,
                a.articleTitle,
                a.content,
                a.articleStatus,
                a.categoryID,
                a.created_at,
                a.first_edited_at,
                a.last_edited_at,
                c.categoryName,
                ai.imageURL
            FROM Article a
            LEFT JOIN ArticleCategory c ON a.categoryID = c.categoryID
            LEFT JOIN ArticleImage ai ON a.articleID = ai.articleID
            WHERE a.created_by = %s
        """
        params = [user_id]

        if keyword:
            query += " AND a.articleTitle LIKE %s"
            params.append(f"%{keyword}%")

        if category_id:
            query += " AND a.categoryID = %s"
            params.append(category_id)

        if status:
            query += " AND LOWER(a.articleStatus) = LOWER(%s)"
            params.append(status)

        query += " ORDER BY a.created_at DESC"

        cursor.execute(query, params)
        articles = cursor.fetchall()

        cursor.close()
        conn.close()
        return articles
    
    def get_article(self, article_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT 
                a.articleID,
                a.articleTitle,
                a.content,
                a.categoryID,
                a.articleStatus,
                a.created_at,
                a.first_edited_at,
                a.last_edited_at,
                a.updated_at,
                a.aiFactCheckScore,
                a.aiFactCheckStatus,
                CONCAT(u.first_name, ' ', u.last_name) AS full_name,
                c.categoryName,
                a.created_by,
                ai.imageURL AS featured_image,
                IFNULL(an.likes, 0) AS likes,
                IFNULL(an.views, 0) AS views
            FROM Article a
            JOIN UserAccount u ON a.created_by = u.userID
            JOIN ArticleCategory c ON a.categoryID = c.categoryID
            LEFT JOIN ArticleImage ai ON a.articleID = ai.articleID
            LEFT JOIN ArticleAnalytics an ON a.articleID = an.articleID
            WHERE a.articleID = %s
            ORDER BY ai.uploaded_at ASC
            LIMIT 1
        """

        cursor.execute(query, (article_id,))
        article = cursor.fetchone()
        cursor.close()
        conn.close()
        return article
    
    #-------------------#
    #old update article #
    #-------------------#
    # def update_article(self, article_id, title, category_id, content, status, featured_image=None):
    #     conn = get_db_connection()
    #     cursor = conn.cursor()
    #     # Update article basic info
    #     sql = """
    #         UPDATE Article
    #         SET articleTitle=%s,
    #             categoryID=%s,
    #             content=%s,
    #             articleStatus=%s,
    #             updated_at=NOW()
    #         WHERE articleID=%s
    #     """
    #     cursor.execute(sql, (title, category_id, content, status, article_id))
        
    #     # If there's a new featured image, update it or insert
    #     if featured_image:
    #         # Check if an image already exists for this article
    #         check_sql = "SELECT articleID FROM ArticleImage WHERE articleID=%s LIMIT 1"
    #         cursor.execute(check_sql, (article_id,))
    #         exists = cursor.fetchone()
    #         if exists:
    #             # Update existing image
    #             update_sql = "UPDATE ArticleImage SET imageURL=%s, uploaded_at=NOW() WHERE articleID=%s"
    #             cursor.execute(update_sql, (featured_image, article_id))
    #         else:
    #             # Insert new image
    #             insert_sql = "INSERT INTO ArticleImage (articleID, imageURL, uploaded_at) VALUES (%s, %s, NOW())"
    #             cursor.execute(insert_sql, (article_id, featured_image))

    #     conn.commit()
    #     cursor.close()
    #     conn.close()

    #----------------#
    # Update Article #
    #----------------#
    def update_article(self, article_id, title, category_id, content, status,
                   ai_fact_check_score=0, ai_fact_check_status=None):
        return self.article_entity.update_article(
            article_id, title, category_id, content, status,
            ai_fact_check_score, ai_fact_check_status
        )

    def update_article_image(self, article_id, image_filename):
        return self.article_entity.update_article_image(article_id, image_filename)

    #-------------------#
    # Get Article Image #
    #-------------------#
    def get_article_images(self, article_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = "SELECT imageURL FROM ArticleImage WHERE articleID=%s ORDER BY uploaded_at ASC"
        cursor.execute(sql, (article_id,))
        images = cursor.fetchall()
        cursor.close()
        conn.close()
        return [img['imageURL'] for img in images]
    
    # Get Article Insight #
    def get_article_insight(self, article_id):
        conn = get_db_connection()
        cursor = conn.cursor(DictCursor)
        query = """
            SELECT 
                a.articleID,
                a.articleTitle,
                a.content,
                a.updated_at,
                a.aiFactCheckScore,
                a.aiFactCheckStatus,
                a.aiReview,
                IFNULL(an.views, 0) AS views,
                IFNULL(an.likes, 0) AS likes
            FROM Article a
            LEFT JOIN ArticleAnalytics an
                ON a.articleID = an.articleID
            WHERE a.articleID = %s
        """
        cursor.execute(query, (article_id,))
        article = cursor.fetchone()
        cursor.close()
        conn.close()

        return article

    def get_max_views(self):
        # Fetch max views dynamically from the database
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT MAX(views) FROM ArticleAnalytics")
            result = cursor.fetchone()

            # Check if result is None or empty, and handle it gracefully
            if result is None or result[0] is None:
                max_views = 10000  # Default value if no data is found
            else:
                max_views = result[0]  # Get the max views value if data exists
        except Exception as e:
            # In case of any database error, log and use a fallback value
            print(f"Error fetching max views: {e}")
            max_views = 10000  # Default value in case of an error

        cursor.close()
        conn.close()
        return max_views

    def get_max_likes(self):
        # Fetch max likes dynamically from the database
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT MAX(likes) FROM ArticleAnalytics")
            result = cursor.fetchone()

            # Check if result is None or empty, and handle it gracefully
            if result is None or result[0] is None:
                max_likes = 5000  # Default value if no data is found
            else:
                max_likes = result[0]  # Get the max likes value if data exists
        except Exception as e:
            # In case of any database error, log and use a fallback value
            print(f"Error fetching max likes: {e}")
            max_likes = 5000  # Default value in case of an error

        cursor.close()
        conn.close()
        return max_likes

    def save_ai_review(self, article_id, review_text):
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = "UPDATE Article SET aiReview = %s WHERE articleID = %s"
        cursor.execute(sql, (review_text, article_id))
        conn.commit()
        cursor.close()
        conn.close()

    # ---- Article Fetching ----
    def get_article_by_id(self, article_id):
        conn = get_db_connection()
        cursor = conn.cursor(DictCursor)
        query = """
            SELECT 
                a.articleID,
                a.articleTitle,
                a.content,
                c.categoryID,
                c.categoryName,
                CONCAT(u.first_name, ' ', u.last_name) AS full_name,
                ai.imageURL AS featured_image
            FROM Article a
            JOIN ArticleCategory c ON a.categoryID = c.categoryID
            JOIN UserAccount u ON a.created_by = u.userID
            LEFT JOIN ArticleImage ai 
                ON a.articleID = ai.articleID
            WHERE a.articleID = %s
            ORDER BY ai.uploaded_at ASC
            LIMIT 1
        """
        cursor.execute(query, (article_id,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        if not row:
            return None
        return {
            'articleID': row['articleID'],
            'articleTitle': row['articleTitle'],
            'content': row['content'],
            'categoryID': row['categoryID'],
            'categoryName': row['categoryName'],
            'full_name': row['full_name'],
            'featured_image': row['featured_image']
        }

    # ---- Article Analytics ----
    def get_article_analytics(self, article_id):
        conn = get_db_connection()
        cursor = conn.cursor(DictCursor)

        cursor.execute("""
            SELECT views, likes
            FROM ArticleAnalytics
            WHERE articleID = %s
        """, (article_id,))

        result = cursor.fetchone()
        cursor.close()
        conn.close()

        return result if result else {"views": 0, "likes": 0}

    def increment_view_count(self, article_id):
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO ArticleAnalytics (articleID, views, likes, shares)
            VALUES (%s, 0, 0, 0)
            ON DUPLICATE KEY UPDATE articleID = articleID
        """, (article_id,))

        cursor.execute("""
            UPDATE ArticleAnalytics
            SET views = views + 1
            WHERE articleID = %s
        """, (article_id,))

        conn.commit()
        cursor.close()
        conn.close()


    def increment_like_count(self, article_id):
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO ArticleAnalytics (articleID, views, likes, shares)
            VALUES (%s, 0, 0, 0)
            ON DUPLICATE KEY UPDATE articleID = articleID
        """, (article_id,))

        cursor.execute("""
            UPDATE ArticleAnalytics
            SET likes = likes + 1
            WHERE articleID = %s
        """, (article_id,))

        conn.commit()
        cursor.close()
        conn.close()

    def decrement_like_count(self, article_id):
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO ArticleAnalytics (articleID, views, likes, shares)
            VALUES (%s, 0, 0, 0)
            ON DUPLICATE KEY UPDATE articleID = articleID
        """, (article_id,))

        cursor.execute("""
            UPDATE ArticleAnalytics
            SET likes = GREATEST(likes - 1, 0)
            WHERE articleID = %s
        """, (article_id,))

        conn.commit()
        cursor.close()
        conn.close()

    def get_recommended_articles(self, user_id):
        """
        Fetch recommended articles for the given user.
        For now, we just return the latest 5 articles as a placeholder.
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
            SELECT a.articleID, a.articleTitle, a.content AS summary, c.categoryName,
                a.created_at, u.username
            FROM Article a
            JOIN UserAccount u ON a.created_by = u.userID
            JOIN ArticleCategory c ON a.categoryID = c.categoryID
            WHERE a.articleStatus = 'published'
            ORDER BY a.created_at DESC
            LIMIT 5
        """
        cursor.execute(query)
        articles = cursor.fetchall()
        cursor.close()
        conn.close()

        # Add featured_image key if missing
        for article in articles:
            if 'featured_image' not in article:
                article['featured_image'] = None

        return articles
    
    # Fetch approved comments for an article
    def get_comments_for_article(self, article_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = """
            SELECT c.commentID, c.commentText, c.created_at, u.username
            FROM Comment c
            JOIN UserAccount u ON c.userID = u.userID
            WHERE c.articleID = %s AND c.commentStatus = 'approved'
            ORDER BY c.created_at ASC
        """
        cursor.execute(sql, (article_id,))
        comments = cursor.fetchall()
        cursor.close()
        conn.close()
        return comments

    # Add a new comment
    def add_comment(self, user_id, article_id, comment_text):
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = """
            INSERT INTO Comment (articleID, userID, commentText, created_at, commentStatus)
            VALUES (%s, %s, %s, NOW(), 'approved')
        """
        cursor.execute(sql, (article_id, user_id, comment_text))
        conn.commit()
        cursor.close()
        conn.close()

    def is_article_saved(self, user_id, article_id):
        if not user_id:
            return False

        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            SELECT 1 
            FROM Favourite 
            WHERE userID = %s AND articleID = %s
            LIMIT 1
        """
        cursor.execute(query, (user_id, article_id))
        result = cursor.fetchone()

        cursor.close()
        conn.close()

        return result is not None
    
    def save_article(self, user_id, article_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            sql = "INSERT INTO Favourite (userID, articleID, saved_at) VALUES (%s, %s, NOW())"
            cursor.execute(sql, (user_id, article_id))
            conn.commit() 
        finally:
            cursor.close()
            conn.close()

    def toggle_save_article(self, user_id, article_id):
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT 1 FROM Favourite WHERE userID=%s AND articleID=%s",
            (user_id, article_id)
        )

        if cursor.fetchone():
            cursor.execute(
                "DELETE FROM Favourite WHERE userID=%s AND articleID=%s",
                (user_id, article_id)
            )
            saved = False
        else:
            cursor.execute(
                "INSERT INTO Favourite (userID, articleID, saved_at) VALUES (%s, %s, NOW())",
                (user_id, article_id)
            )
            saved = True

        conn.commit()
        cursor.close()
        conn.close()

        if saved:
            self.increment_like_count(article_id)
        else:
            self.decrement_like_count(article_id)

        return saved
    
    
    def is_valid_report_category(self, report_category_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
            SELECT 1 
            FROM ReportCategory 
            WHERE reportCategoryID = %s AND categoryStatus = 'active'
        """
        cursor.execute(query, (report_category_id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result is not None  # If a result is found, the category is valid
 
    def report_article(self, article_id, user_id, optional_comment, report_category_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        # Check if the reportCategoryID exists and is active in the ReportCategory table
        if not self.is_valid_report_category(report_category_id):
            raise ValueError(f"Category ID {report_category_id} does not exist or is inactive in the ReportCategory table.")
        # If category is valid, proceed to insert the report
        try:
            query = """
                INSERT INTO ReportedArticle (articleID, userID, reportCategoryID, optionalComment, reported_at)
                VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)
            """
            cursor.execute(query, (article_id, user_id, report_category_id, optional_comment))
            conn.commit()  # Commit the transaction to make the changes permanent
        except Exception as e:
            print(f"Error reporting article: {e}")
            raise  # Reraise the error so it's logged and handled
        finally:
            cursor.close()
            conn.close()

    def get_testimonials(self, limit=2):
        return self.article_entity.get_latest_testimonials(limit)

    def get_top_viewed_articles(self, limit=5):
        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
            SELECT a.articleID, a.articleTitle, a.content, c.categoryName, u.username,
                IFNULL(ai.imageURL, NULL) AS featured_image,
                IFNULL(an.views, 0) AS views,
                IFNULL(an.likes, 0) AS likes
            FROM Article a
            JOIN UserAccount u ON a.created_by = u.userID
            JOIN ArticleCategory c ON a.categoryID = c.categoryID
            LEFT JOIN ArticleImage ai ON a.articleID = ai.articleID
            LEFT JOIN ArticleAnalytics an ON a.articleID = an.articleID
            WHERE a.articleStatus = 'published'
            ORDER BY views DESC
            LIMIT %s
        """
        cursor.execute(query, (limit,))
        articles = cursor.fetchall()
        cursor.close()
        conn.close()
        return articles
    
    def get_top_articles_by_category(self, category_id, limit=5):
        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
            SELECT a.articleID, a.articleTitle, a.content, u.username,
                IFNULL(ai.imageURL, NULL) AS featured_image,
                IFNULL(an.views, 0) AS views,
                IFNULL(an.likes, 0) AS likes
            FROM Article a
            JOIN UserAccount u ON a.created_by = u.userID
            LEFT JOIN ArticleImage ai ON a.articleID = ai.articleID
            LEFT JOIN ArticleAnalytics an ON a.articleID = an.articleID
            WHERE a.articleStatus = 'published' AND a.categoryID = %s
            ORDER BY views DESC
            LIMIT %s
        """
        cursor.execute(query, (category_id, limit))
        articles = cursor.fetchall()
        cursor.close()
        conn.close()
        return articles
    
    def get_user_saved_articles(self, user_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
            SELECT a.articleID, a.articleTitle, a.content, c.categoryID, c.categoryName, u.username,
                IFNULL(ai.imageURL, NULL) AS featured_image,
                IFNULL(an.views, 0) AS views,
                IFNULL(an.likes, 0) AS likes,
                IFNULL(a.aiFactCheckScore, 0) AS aiFactCheckScore,
                COALESCE(NULLIF(a.aiFactCheckStatus, ''), 'Not Checked') AS aiFactCheckStatus
            FROM Favourite f
            JOIN Article a ON f.articleID = a.articleID
            JOIN UserAccount u ON a.created_by = u.userID
            JOIN ArticleCategory c ON a.categoryID = c.categoryID
            LEFT JOIN ArticleImage ai ON a.articleID = ai.articleID
            LEFT JOIN ArticleAnalytics an ON a.articleID = an.articleID
            WHERE f.userID = %s AND a.articleStatus = 'published'
            ORDER BY f.saved_at DESC
        """
        cursor.execute(query, (user_id,))
        articles = cursor.fetchall()
        cursor.close()
        conn.close()
        return articles
    
    def calculate_credibility(self, ai_score, views, likes):
         ai_score = float(ai_score or 0)
         views = int(views or 0)
         likes = int(likes or 0)

         if views < 10:
            engagement_score = 0.0
         else:
            engagement_rate = likes / views
            engagement_score = min(engagement_rate * 100, 100)

         return round((ai_score * 0.5) + (engagement_score * 0.5), 2)
    
    def get_credibility_label(score):
        if score >= 80:
            return "Highly Credible"
        elif score >= 50:
            return "Moderately Credible"
        else:
            return "Low Credibility"
        
    
    # In control/ArticleController.py
    def get_article_analytics_over_time(self, article_id):
        article = self.get_article(article_id)
        if not article:
            return []
        today = datetime.now().date()
        return [(article["views"], article["likes"], today)]
    
    
    # For User Interests 
    def get_user_interests(self, user_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT interests FROM UserAccount WHERE userID = %s", (user_id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        if result and result.get("interests"):
            return [x.strip() for x in result["interests"].split(",")]
        return []
        
    def get_category_ids_from_names(self, category_names):
        if not category_names:
            return []
        conn = get_db_connection()
        cursor = conn.cursor()
        placeholders = ",".join(["%s"] * len(category_names))
        query = f"""
            SELECT categoryID
            FROM ArticleCategory
            WHERE categoryName IN ({placeholders})
        """
        cursor.execute(query, category_names)
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return [row["categoryID"] for row in results]
    
    def get_articles_by_multiple_categories(self, category_ids, limit=12, exclude_id=None):
        if not category_ids:
            return []
        conn = get_db_connection()
        cursor = conn.cursor()
        placeholders = ",".join(["%s"] * len(category_ids))
        query = f"""
            SELECT a.articleID, a.articleTitle, a.content, c.categoryName,
                IFNULL(ai.imageURL, NULL) AS featured_image,
                IFNULL(an.views, 0) AS views,
                IFNULL(an.likes, 0) AS likes,
                IFNULL(a.aiFactCheckScore, 0) AS aiFactCheckScore,
                COALESCE(NULLIF(a.aiFactCheckStatus, ''), 'Not Checked') AS aiFactCheckStatus
            FROM Article a
            LEFT JOIN ArticleImage ai ON a.articleID = ai.articleID
            LEFT JOIN ArticleAnalytics an ON a.articleID = an.articleID
            LEFT JOIN ArticleCategory c ON a.categoryID = c.categoryID
            WHERE a.articleStatus = 'published'
            AND a.categoryID IN ({placeholders})
        """

        params = list(category_ids)

        if exclude_id:
            query += " AND a.articleID != %s"
            params.append(exclude_id)

        query += """
            ORDER BY a.created_at DESC, IFNULL(an.views, 0) DESC
            LIMIT %s
        """

        params.append(limit)

        cursor.execute(query, tuple(params))
        # cursor.execute(query, (*category_ids, limit))
        articles = cursor.fetchall()
        cursor.close()
        conn.close()
        return articles
