# control/ArticleController.py
from entity.Article import Article
from entity.db_connection import get_db_connection
from pymysql.cursors import DictCursor

class ArticleController:

    def __init__(self):
        self.article_entity = Article()

    def get_articles(self):
        return self.article_entity.get_all_articles()
    
    def search(self, keyword):
        return self.article_entity.search_articles(keyword)

    def get_categories(self):
        return self.article_entity.get_categories()
    
    def get_my_articles(self, user_id):
        return self.article_entity.get_my_articles(user_id)
    
    def create_article(self, user_id, title, category_id, content, status, featured_image=None):
        article_id = self.article_entity.insert_article(user_id, title, category_id, content, status)
        if article_id and featured_image:
            self.article_entity.insert_article_image(article_id, featured_image)
        return article_id

    def get_headline(self):
        return self.article_entity.get_headline_article()

    def get_latest_articles_by_category(self, limit=6):
        return self.article_entity.get_latest_articles_by_category(limit)

    def get_home_headline(self):
        return self.article_entity.get_home_headline_article()

    def get_home_latest_articles(self, limit=5, offset=0, exclude_id=None):
        return self.article_entity.get_home_latest_articles(limit, offset, exclude_id)

    def delete_article(self, article_id):
        return self.article_entity.delete_article(article_id)

    def search_my_articles(self, user_id, keyword="", category_id=""):
        return self.article_entity.search_my_articles(user_id, keyword, category_id)
    
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
                CONCAT(u.first_name, ' ', u.last_name) AS full_name,
                c.categoryName,
                a.created_by,
                ai.imageURL AS featured_image
            FROM Article a
            JOIN UserAccount u ON a.created_by = u.userID
            JOIN ArticleCategory c ON a.categoryID = c.categoryID
            LEFT JOIN ArticleImage ai ON a.articleID = ai.articleID
            WHERE a.articleID = %s
            ORDER BY ai.uploaded_at ASC
            LIMIT 1
        """
        cursor.execute(query, (article_id,))
        article = cursor.fetchone()
        cursor.close()
        conn.close()
        return article

    def update_article(self, article_id, title, category_id, content, status, featured_image=None):
        conn = get_db_connection()
        cursor = conn.cursor()
        # Update article basic info
        sql = """
            UPDATE Article
            SET articleTitle=%s,
                categoryID=%s,
                content=%s,
                articleStatus=%s,
                updated_at=NOW()
            WHERE articleID=%s
        """
        cursor.execute(sql, (title, category_id, content, status, article_id))
        
        # If there's a new featured image, update it or insert
        if featured_image:
            # Check if an image already exists for this article
            check_sql = "SELECT articleID FROM ArticleImage WHERE articleID=%s LIMIT 1"
            cursor.execute(check_sql, (article_id,))
            exists = cursor.fetchone()
            if exists:
                # Update existing image
                update_sql = "UPDATE ArticleImage SET imageURL=%s, uploaded_at=NOW() WHERE articleID=%s"
                cursor.execute(update_sql, (featured_image, article_id))
            else:
                # Insert new image
                insert_sql = "INSERT INTO ArticleImage (articleID, imageURL, uploaded_at) VALUES (%s, %s, NOW())"
                cursor.execute(insert_sql, (article_id, featured_image))

        conn.commit()
        cursor.close()
        conn.close()

        
    def get_article_images(self, article_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = "SELECT imageURL FROM ArticleImage WHERE articleID=%s ORDER BY uploaded_at ASC"
        cursor.execute(sql, (article_id,))
        images = cursor.fetchall()
        cursor.close()
        conn.close()
        return [img['imageURL'] for img in images]
    

    def get_article_insight(self, article_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
            SELECT 
                a.articleID,
                a.articleTitle,
                a.content,
                a.credibilityScore,
                a.reviewPriority,
                a.updated_at,
                IFNULL(an.views,0) as views,
                IFNULL(an.likes,0) as likes,
                IFNULL(an.shares,0) as shares
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

    def save_ai_review(self, article_id, review_text):
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = "UPDATE Article SET aiReview = %s WHERE articleID = %s"
        cursor.execute(sql, (review_text, article_id))
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
        """
        Check if a given article is already saved by the user.
        Returns True if saved, False otherwise.
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            sql = "SELECT 1 FROM Favourite WHERE userID=%s AND articleID=%s LIMIT 1"
            cursor.execute(sql, (user_id, article_id))
            result = cursor.fetchone()  # fetch just one row
            return bool(result)
        finally:
            cursor.close()
            conn.close()
    
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
        try:
            if self.is_article_saved(user_id, article_id):
                # Already saved → remove
                sql = "DELETE FROM Favourite WHERE userID=%s AND articleID=%s"
                cursor.execute(sql, (user_id, article_id))
                conn.commit()
                return False  # now unsaved
            else:
                # Not saved → add
                sql = "INSERT INTO Favourite (userID, articleID, saved_at) VALUES (%s, %s, NOW())"
                cursor.execute(sql, (user_id, article_id))
                conn.commit()
                return True  # now saved
        finally:
            cursor.close()
            conn.close()
    
    
    def get_article_by_id(self, article_id):
        conn = get_db_connection()
        cursor = conn.cursor(DictCursor)  # <--- important
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
                IFNULL(ai.imageURL, NULL) AS featured_image, IFNULL(an.views,0) AS views
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
                IFNULL(ai.imageURL, NULL) AS featured_image, IFNULL(an.views,0) AS views
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
    
    def get_user_saved_articles(self, user_id, limit=5):
        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
            SELECT a.articleID, a.articleTitle, a.content, c.categoryID, c.categoryName, u.username,
                IFNULL(ai.imageURL, NULL) AS featured_image
            FROM Favourite f
            JOIN Article a ON f.articleID = a.articleID
            JOIN UserAccount u ON a.created_by = u.userID
            JOIN ArticleCategory c ON a.categoryID = c.categoryID
            LEFT JOIN ArticleImage ai ON a.articleID = ai.articleID
            WHERE f.userID = %s AND a.articleStatus = 'published'
            ORDER BY f.saved_at DESC
            LIMIT %s
        """
        cursor.execute(query, (user_id, limit))
        articles = cursor.fetchall()
        cursor.close()
        conn.close()
        return articles
    
    def increment_view_count(self, article_id):
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if record exists
        cursor.execute("""
            SELECT analyticsID FROM ArticleAnalytics WHERE articleID = %s
        """, (article_id,))
        result = cursor.fetchone()

        if result:
            cursor.execute("""
                UPDATE ArticleAnalytics
                SET views = views + 1,
                    lastUpdated = NOW()
                WHERE articleID = %s
            """, (article_id,))
        else:
            cursor.execute("""
                INSERT INTO ArticleAnalytics (articleID, views, likes, shares, lastUpdated)
                VALUES (%s, 1, 0, 0, NOW())
            """, (article_id,))

        conn.commit()
        cursor.close()
        conn.close()