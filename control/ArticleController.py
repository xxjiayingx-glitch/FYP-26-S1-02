# control/ArticleController.py
from entity.Article import Article
from db_connection import get_db_connection  

class ArticleController:

    def __init__(self):
        self.article_entity = Article()
        self.db = get_db_connection()  

    def get_articles(self):
        return self.article_entity.get_all_articles()
    
    def search(self, keyword):
        return self.article_entity.search_articles(keyword)

    def get_article(self, id):
        return self.article_entity.get_article(id)

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

    def get_latest(self, limit=5):
        return self.article_entity.get_latest_articles(limit)
    
    def get_home_headline(self):
        return self.article_entity.get_home_headline_article()

    def get_home_latest_articles(self, limit=5, offset=0, exclude_id=None):
        return self.article_entity.get_home_latest_articles(limit, offset, exclude_id)

    def delete_article(self, article_id):
        return self.article_entity.delete_article(article_id)

    def search_my_articles(self, user_id, keyword):
        return self.article_entity.search_my_articles(user_id, keyword)
    
    def get_article(self, article_id):
        cursor = self.db.cursor(dictionary=True)
        query = """
            SELECT 
                a.articleID,
                a.articleTitle,
                a.content,
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
        return article

    def update_article(self, article_id, title, category_id, content, status, featured_image=None):
        cursor = self.db.cursor()
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

        self.db.commit()
        cursor.close()

        
    def get_article_images(self, article_id):
        cursor = self.db.cursor(dictionary=True)
        sql = "SELECT imageURL FROM ArticleImage WHERE articleID=%s ORDER BY uploaded_at ASC"
        cursor.execute(sql, (article_id,))
        images = cursor.fetchall()
        cursor.close()
        return [img['imageURL'] for img in images]
    

    def get_article_insight(self, article_id):
        cursor = self.db.cursor(dictionary=True)
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
        return article

    def save_ai_review(self, article_id, review_text):
        cursor = self.db.cursor()
        sql = "UPDATE Article SET aiReview = %s WHERE articleID = %s"
        cursor.execute(sql, (review_text, article_id))
        self.db.commit()
        cursor.close()

    def get_recommended_articles(self, user_id):
        """
        Fetch recommended articles for the given user.
        For now, we just return the latest 5 articles as a placeholder.
        """
        cursor = self.db.cursor(dictionary=True)
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

        # Add featured_image key if missing
        for article in articles:
            if 'featured_image' not in article:
                article['featured_image'] = None

        return articles
    
    # Fetch approved comments for an article
    def get_comments_for_article(self, article_id):
        cursor = self.db.cursor(dictionary=True)
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
        return comments

    # Add a new comment
    def add_comment(self, user_id, article_id, comment_text):
        cursor = self.db.cursor()
        sql = """
            INSERT INTO Comment (articleID, userID, commentText, created_at, commentStatus)
            VALUES (%s, %s, %s, NOW(), 'approved')
        """
        cursor.execute(sql, (article_id, user_id, comment_text))
        self.db.commit()
        cursor.close()

    def is_article_saved(self, user_id, article_id):
        cursor = self.db.cursor(dictionary=True)  # use dictionary cursor
        sql = "SELECT 1 FROM Favourite WHERE userID=%s AND articleID=%s LIMIT 1"
        cursor.execute(sql, (user_id, article_id))
        result = cursor.fetchone()  # fetch just one row
        cursor.close()
        return bool(result)
    
    def save_article(self, user_id, article_id):
        cursor = self.db.cursor()
        sql = "INSERT INTO Favourite (userID, articleID, saved_at) VALUES (%s, %s, NOW())"
        cursor.execute(sql, (user_id, article_id))
        self.db.commit()
        cursor.close()

    def toggle_save_article(self, user_id, article_id):
        if self.is_article_saved(user_id, article_id):
            # Already saved → remove
            cursor = self.db.cursor()
            sql = "DELETE FROM Favourite WHERE userID=%s AND articleID=%s"
            cursor.execute(sql, (user_id, article_id))
            self.db.commit()
            cursor.close()
            return False  # now it’s unsaved
        else:
            # Not saved → add
            cursor = self.db.cursor()
            sql = "INSERT INTO Favourite (userID, articleID, saved_at) VALUES (%s, %s, NOW())"
            cursor.execute(sql, (user_id, article_id))
            self.db.commit()
            cursor.close()
            return True  # now it’s saved
    
    def report_article(self, user_id, article_id, author_id, optional_comment=""):
        cursor = self.db.cursor()
        sql = """
            INSERT INTO ReportedArticle (articleID, author, userID, optionalComment, reported_at, reportStatus)
            VALUES (%s, %s, %s, %s, NOW(), 'pending')
        """
        cursor.execute(sql, (article_id, author_id, user_id, optional_comment))
        self.db.commit()
        cursor.close()

    def get_testimonials(self, limit=2):
        return self.article_entity.get_latest_testimonials(limit)

    