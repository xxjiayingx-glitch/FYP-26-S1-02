# entity/Article.py
from entity.db_connection import get_db_connection

class Article:

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

    def get_headline_article(self):
        conn, cursor = None, None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            sql = """
            SELECT * FROM Article
            WHERE articleStatus = 'published'
            ORDER BY created_at DESC
            LIMIT 1
            """
            cursor.execute(sql)
            row = cursor.fetchone()
            if row:
                columns = [col[0] for col in cursor.description]
                return dict(zip(columns, row))
            return None
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def get_latest_articles(self, limit=3):
        conn, cursor = None, None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            sql = """
            SELECT * FROM Article
            WHERE articleStatus = 'published'
            ORDER BY created_at DESC
            LIMIT %s
            """
            cursor.execute(sql, (limit,))
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    @staticmethod
    def get_total_articles():
        conn, cursor = None, None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM Article")
            result = cursor.fetchone()
            return result[0] if result else 0
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    # My Article Section
    def get_my_articles(self, user_id):
        conn, cursor = None, None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            sql = "SELECT * FROM Article WHERE created_by=%s ORDER BY created_at DESC"
            cursor.execute(sql, (user_id,))
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception as e:
            print("Error in get_my_articles:", e)
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
            print("Article inserted with ID:", cursor.lastrowid)
            return cursor.lastrowid
        except Exception as e:
            print("Error inserting article:", e)
            return None
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    # Insert featured image
    def insert_article_image(self, article_id, featured_image):
        conn, cursor = None, None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            filename = featured_image.filename
            upload_path = os.path.join("static", "uploads", filename)
            os.makedirs(os.path.dirname(upload_path), exist_ok=True)
            featured_image.save(upload_path)

            sql = """
            INSERT INTO ArticleImage (articleID, imageURL, uploaded_at)
            VALUES (%s, %s, NOW())
            """
            cursor.execute(sql, (article_id, upload_path))
            conn.commit()
            print("Featured image saved:", upload_path)
        except Exception as e:
            print("Error inserting article image:", e)
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
            categories = [dict(zip(columns, row)) for row in cursor.fetchall()]
            print("Fetched categories:", categories)
            return categories
        except Exception as e:
            print("Error fetching categories:", e)
            return []
        finally:
            if cursor: cursor.close()
            if conn: conn.close()