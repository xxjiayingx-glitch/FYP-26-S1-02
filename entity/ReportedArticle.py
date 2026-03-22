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
                MAX(ra.reported_at) AS latestReportDate,
                COUNT(ra.articleID) AS totalReports
            FROM ReportedArticle ra
            JOIN Article a ON ra.articleID = a.articleID
            GROUP BY a.articleID
            ORDER BY totalReports DESC
            LIMIT 5
        """)
        result = cursor.fetchall()
        conn.close()
        return result
    
    @staticmethod
    def report_occurence_count():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                articleID,
                COUNT(*) AS total_occurences
            FROM ReportedArticle
            GROUP BY articleID
        """)
        result = cursor.fetchall()
        conn.close()
        return result

    
    @staticmethod
    def get_article_reported():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                ra.reportID,
                a.articleID,
                a.articleTitle,
                COUNT(ra.articleID) AS totalReports,
                MAX(ra.reported_at) AS latestReportDate,
                a.articleStatus,
                ra.reportStatus
            FROM ReportedArticle ra
            JOIN Article a ON ra.articleID = a.articleID
            GROUP BY a.articleID
            ORDER BY totalReports DESC
        """)
        result = cursor.fetchall()
        conn.close()
        return result
     
    @staticmethod
    def get_report_details(report_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(""" 
            SELECT 
                a.articleID,
                rc.categoryName AS reason,
                COUNT(ra.articleID) AS totalReports,
                a.articleTitle,
                a.credibilityScore,
                a.articleStatus,
                ra.reportStatus,
                ai.imageURL,
                a.content
            FROM ReportedArticle ra
            JOIN Article a ON ra.articleID = a.articleID
            JOIN ArticleImage ai on a.articleID = ai.articleID
            LEFT JOIN ReportCategory rc on ra.reason = rc.reportCategoryID
            WHERE ra.reportID = %s
        """, (report_id,))

        reportDetails = cursor.fetchone()
        conn.close()

        return reportDetails
    
    def report_article(articleID, userID, reason, reportCategoryID):
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = """
            INSERT INTO ReportedArticle
            (articleID, userID, reportReason, reportCategoryID, reportDate)
            VALUES (%s, %s, %s, %s, NOW())
        """
        cursor.execute(sql, (articleID, userID, reason, reportCategoryID))
        conn.commit()
        cursor.close()
        conn.close()
