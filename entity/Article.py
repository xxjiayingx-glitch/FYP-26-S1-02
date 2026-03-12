from entity.db_connection import get_db_connection

class Article:
    @staticmethod
    def get_total_articles():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) AS total_articles FROM Article")
        result = cursor.fetchone()
        conn.close()
        return result["total_articles"]