from entity.db_connection import get_db_connection
from datetime import datetime, timedelta

class ReportedArticle:
    #-------#
    # Admin #
    #-------#
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
    def get_article_reported(expertise_category=None):
        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
            SELECT
                MIN(ra.reportID) AS reportID,
                a.articleID,
                a.articleTitle,
                ac.categoryName as category,
                COUNT(ra.articleID) AS totalReports,
                MAX(ra.reported_at) AS latestReportDate,
                a.articleStatus,
                MIN(ra.reportStatus) AS reportStatus
            FROM ReportedArticle ra
            JOIN Article a ON ra.articleID = a.articleID
            LEFT JOIN ArticleCategory ac ON a.categoryID = ac.categoryID
            WHERE 1=1
        """

        params = []

        if expertise_category:
            query += " AND ac.categoryName = %s"
            params.append(expertise_category)

        query += """
            GROUP BY a.articleID, a.articleTitle, ac.categoryName, a.articleStatus
            ORDER BY totalReports DESC
        """

        print("expertise_category =", expertise_category)
        print("query =", query)
        print("params =", params)
        
        cursor.execute(query, params)
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
                GROUP_CONCAT(DISTINCT ua.username SEPARATOR ', ') AS reportedBy,
                GROUP_CONCAT(DISTINCT rc.categoryName SEPARATOR ', ') AS reasons,
                totals.totalReports,
                a.articleTitle,
                author.username AS createdBy,
                a.credibilityScore,
                a.articleStatus,
                ra.reportStatus,
                ai.imageURL,
                a.content
            FROM ReportedArticle ra
            JOIN Article a ON ra.articleID = a.articleID
            JOIN ArticleImage ai on a.articleID = ai.articleID
            LEFT JOIN ReportCategory rc on ra.reportCategoryID = rc.reportCategoryID
            LEFT JOIN UserAccount ua on ra.userID = ua.userID
            LEFT JOIN UserAccount author on a.created_by = author.userID
            JOIN (
                SELECT articleID, COUNT(*) AS totalReports
                FROM ReportedArticle
                GROUP BY articleID
            ) totals ON totals.articleID = a.articleID
            WHERE a.articleID = (
                SELECT articleID
                FROM ReportedArticle
                WHERE reportID = %s)
        """, (report_id,))

        reportDetails = cursor.fetchone()
        conn.close()

        return reportDetails

    @staticmethod
    def get_total_reports_before_days(days):
        conn = get_db_connection()
        cursor = conn.cursor()

        cutoff = datetime.now() - timedelta(days=days)

        query = """
            SELECT COUNT(*) AS total
            FROM ReportedArticle
            WHERE reported_at < %s
        """
        cursor.execute(query, (cutoff,))
        result = cursor.fetchone()

        cursor.close()
        conn.close()

        return result["total"] if result else 0
        
    #--------#
    #  User  #
    #--------#
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
