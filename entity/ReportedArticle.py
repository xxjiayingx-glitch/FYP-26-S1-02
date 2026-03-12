from entity.db_connection import get_db_connection

class ReportedArticle:
    @staticmethod
    def get_total_reported_articles():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) AS reported_articles FROM ReportedArticle")
        result = cursor.fetchone()
        conn.close()
        return result["reported_articles"]

    @staticmethod
    def get_reported_articles_needing_review():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                ra.reportID,
                a.articleTitle,
                DATE(ra.reported_at) AS report_date,
                COUNT(*) AS report_count
            FROM ReportedArticle ra
            JOIN Article a ON ra.articleID = a.articleID
            WHERE ra.reportStatus IS NULL OR ra.reportStatus = 'Pending'
            GROUP BY ra.reportID, a.articleTitle, DATE(ra.reported_at), ra.articleID
            ORDER BY ra.reported_at DESC
            LIMIT 5
        """)
        result = cursor.fetchall()
        conn.close()
        return result

    def report_article(articleID,userID,reason):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
    INSERT INTO ReportedArticle(articleID,userID,optionalComment,reported_at)
    VALUES(%s,%s,%s,NOW())
    """
    cursor.execute(query,(articleID,userID,reason))
    conn.commit()
