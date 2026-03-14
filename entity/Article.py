from entity.db_connection import get_db_connection
import os

class Article:

    # Fetch all articles
    def get_all_articles(self):
        conn, cursor = None, None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Article")
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    # Search articles
    def search_articles(self, keyword):
        conn, cursor = None, None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            sql = "SELECT * FROM Article WHERE articleTitle LIKE %s"
            cursor.execute(sql, ('%' + keyword + '%',))
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    # Get article by ID
    def get_article(self, articleID):
        conn, cursor = None, None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            sql = "SELECT * FROM Article WHERE articleID=%s"
            cursor.execute(sql, (articleID,))
            row = cursor.fetchone()
            if row:
                columns = [col[0] for col in cursor.description]
                return dict(zip(columns, row))
            return None
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    # Get categories for dropdown
    def get_categories(self):
        conn, cursor = None, None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT categoryID, categoryName FROM ArticleCategory")
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception as e:
            print("Error fetching categories:", e)
            return []
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    # Insert a new article
    def insert_article(self, user_id, title, category_id, content, status):
        conn, cursor = None, None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            sql = """
                INSERT INTO Article (articleTitle, content, articleStatus, created_by, categoryID, created_at)
                VALUES (%s, %s, %s, %s, %s, NOW())
            """
            cursor.execute(sql, (title, content, status, user_id, category_id))
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print("Error inserting article:", e)
            return None
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    # Insert featured image
    def insert_article_image(self, article_id, featured_image):
        if not featured_image:
            return
        conn, cursor = None, None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            filename = featured_image.filename
            filepath = os.path.join("static/uploads", filename)
            featured_image.save(filepath)
            sql = "INSERT INTO ArticleImage (articleID, imageURL, uploaded_at) VALUES (%s, %s, NOW())"
            cursor.execute(sql, (article_id, filepath))
            conn.commit()
        except Exception as e:
            print("Error inserting article image:", e)
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    # Get articles for a specific user, with category name    
    def get_my_articles(self, user_id):
        conn, cursor = None, None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            sql = """
            SELECT 
                a.articleID, 
                a.articleTitle, 
                a.articleStatus, 
                a.created_at, 
                c.categoryName,
                img.imageURL AS featuredImage
            FROM Article a
            LEFT JOIN ArticleCategory c ON a.categoryID = c.categoryID
            LEFT JOIN (
                SELECT articleID, imageURL 
                FROM ArticleImage 
                GROUP BY articleID
            ) img ON a.articleID = img.articleID
            WHERE a.created_by = %s
            ORDER BY a.created_at DESC
            """
            cursor.execute(sql, (user_id,))
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            articles = [dict(zip(columns, row)) for row in rows]
            print("Fetched articles:", articles)  # debug
            return articles
        except Exception as e:
            print("Error in get_my_articles:", e)
            return []
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    # Update Article
    def update_article(self, article_id, title, category_id, content, status, featured_image=None):
        conn, cursor = None, None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            sql = """
            UPDATE Article
            SET articleTitle=%s, content=%s, categoryID=%s, articleStatus=%s, updated_at=NOW()
            WHERE articleID=%s
            """
            cursor.execute(sql, (title, content, category_id, status, article_id))
            conn.commit()

            # Update featured image if provided
            if featured_image:
                self.insert_article_image(article_id, featured_image)
        except Exception as e:
            print("Error updating article:", e)
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    # Delete Article
    def delete_article(self, article_id):
        conn, cursor = None, None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            # Delete associated images first
            cursor.execute("DELETE FROM ArticleImage WHERE articleID=%s", (article_id,))
            # Delete the article itself
            cursor.execute("DELETE FROM Article WHERE articleID=%s", (article_id,))
            conn.commit()
        except Exception as e:
            print("Error deleting article:", e)
        finally:
            if cursor: cursor.close()
            if conn: conn.close()