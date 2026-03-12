from entity.db_connection import connect_db

def report_article(articleID, userID, reason):
    conn = connect_db()
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