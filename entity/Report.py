from entity.db_connection import get_db_connection

def report_article(articleID, userID, reason):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        query = """
        INSERT INTO ReportedArticle(articleID, userID, optionalComment, reported_at)
        VALUES(%s,%s,%s,NOW())
        """
        cursor.execute(query, (articleID, userID, reason))
        conn.commit()
    finally:
        conn.close()   