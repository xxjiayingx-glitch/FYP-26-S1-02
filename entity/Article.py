from entity.db_connection import get_db_connection

class Article:

    def get_all_articles(self):
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM Article")
        articles = cursor.fetchall()

        conn.close()
        return articles


    def search_articles(self, keyword):
        conn = get_db_connection()
        cursor = conn.cursor()

        sql = "SELECT * FROM Article WHERE articleTitle LIKE %s"
        cursor.execute(sql, ('%' + keyword + '%',))
        articles = cursor.fetchall()

        conn.close()
        return articles


    def get_article(self, articleID):
        conn = get_db_connection()
        cursor = conn.cursor()

        sql = "SELECT * FROM Article WHERE articleID=%s"
        cursor.execute(sql, (articleID,))
        article = cursor.fetchone()

        conn.close()
        return article


    def get_headline_article(self):
        conn = get_db_connection()
        cursor = conn.cursor()

        sql = """
        SELECT * FROM Article
        WHERE articleStatus = 'published'
        ORDER BY created_at DESC
        LIMIT 1
        """
        cursor.execute(sql)
        article = cursor.fetchone()

        conn.close()
        return article


    def get_latest_articles(self, limit=3):
        conn = get_db_connection()
        cursor = conn.cursor()

        sql = """
        SELECT * FROM Article
        WHERE articleStatus = 'published'
        ORDER BY created_at DESC
        LIMIT 1, %s
        """
        cursor.execute(sql, (limit,))
        articles = cursor.fetchall()

        conn.close()
        return articles


    @staticmethod
    def get_total_articles():
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM Article")
        result = cursor.fetchone()

        conn.close()
        return result[0]