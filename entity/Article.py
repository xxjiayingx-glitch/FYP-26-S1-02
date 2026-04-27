# entity/Article.py
from entity.db_connection import get_db_connection
from datetime import datetime, timedelta

class Article:
    #-------#
    # Admin #
    #-------#
    @staticmethod
    def get_total_articles():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) AS total_articles FROM Article")
        result = cursor.fetchone()
        conn.close()
        return result["total_articles"]

    # @staticmethod
    # def updateStatus(articleID, action):
    #     conn = get_db_connection()
    #     cursor = conn.cursor()

    #     if action == "suspend":
    #         new_status = "suspended"
    #     elif action == "unsuspend":
    #         new_status = "published"
    #     else:
    #         conn.close()
    #         return False

    #     cursor.execute(
    #         """
    #         UPDATE Article SET articleStatus = %s WHERE articleID = %s 
    #     """,
    #         (new_status, articleID),
    #     )

    #     conn.commit()
    #     updated = cursor.rowcount > 0
    #     conn.close()

    #     return updated

    @staticmethod
    def update_status_and_complete_reports(articleID, action, reviewed_by):
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            new_status = None
            report_status = "completed"

            if action == "suspend":
                new_status = "suspended"
            elif action == "unsuspend":
                new_status = "published"
            elif action == "complete":
                pass
            else:
                conn.close()
                return False
            
            # 1. Update the article status
            if new_status is not None:
                cursor.execute("""
                    UPDATE Article
                    SET articleStatus = %s
                    WHERE articleID = %s
                """, (new_status, articleID))

            # 2. Complete all related reports for this article
            cursor.execute("""
                UPDATE ReportedArticle
                SET reportStatus = %s,
                    reviewed_by = %s,
                    reviewed_at = NOW()
                WHERE articleID = %s
                AND reportStatus = %s
            """, (report_status, reviewed_by, articleID, "pending review"))

            conn.commit()
            return True

        except Exception as e:
            conn.rollback()
            print("update_status_and_complete_reports error:", e)
            return False

        finally:
            conn.close()

    @staticmethod
    def get_articles_last_7_days():
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            SELECT COUNT(*) AS total
            FROM Article
            WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
        """
        cursor.execute(query)
        result = cursor.fetchone()

        cursor.close()
        conn.close()

        return result["total"] if result else 0


    @staticmethod
    def get_articles_previous_7_days():
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            SELECT COUNT(*) AS total
            FROM Article
            WHERE created_at >= DATE_SUB(NOW(), INTERVAL 14 DAY)
            AND created_at < DATE_SUB(NOW(), INTERVAL 7 DAY)
        """
        cursor.execute(query)
        result = cursor.fetchone()

        cursor.close()
        conn.close()

        return result["total"] if result else 0
    #--------#
    #  User  # 
    #--------#
    def get_all_articles(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Article ORDER BY created_at DESC")
        articles = cursor.fetchall()
        conn.close()
        return articles

    def search_articles(self, keyword):
        conn = get_db_connection()
        cursor = conn.cursor()

        sql = """
        SELECT a.*, c.categoryName, ai.imageURL, u.username
        FROM Article a
        LEFT JOIN ArticleCategory c ON a.categoryID = c.categoryID
        LEFT JOIN ArticleImage ai ON a.articleID = ai.articleID
        LEFT JOIN UserAccount u ON a.created_by = u.userID
        WHERE a.articleTitle LIKE %s OR a.content LIKE %s
        AND a.articleStatus = 'published'
        ORDER BY a.created_at DESC
        """
        keyword_param = f"%{keyword}%"
        cursor.execute(sql, (keyword_param, keyword_param))
        articles = cursor.fetchall()
        conn.close()
        return articles
    
    def search_article_in_category(self, keyword, category_id=None, limit=12):
        conn = get_db_connection()
        cursor = conn.cursor()

        search_term = f"%{keyword}%"

        if category_id:
            query = """
                SELECT 
                    a.articleID,
                    a.articleTitle,
                    a.content,
                    c.categoryName,
                    u.username,
                    IFNULL(ai.imageURL, NULL) AS imageURL,
                    IFNULL(an.views, 0) AS views,
                    IFNULL(an.likes, 0) AS likes
                FROM Article a
                JOIN UserAccount u ON a.created_by = u.userID
                JOIN ArticleCategory c ON a.categoryID = c.categoryID
                LEFT JOIN ArticleImage ai ON a.articleID = ai.articleID
                LEFT JOIN ArticleAnalytics an ON a.articleID = an.articleID
                WHERE a.articleStatus = 'published'
                AND a.categoryID = %s
                AND (
                        a.articleTitle LIKE %s
                        OR a.content LIKE %s
                        OR c.categoryName LIKE %s
                    )
                GROUP BY 
                    a.articleID,
                    a.articleTitle,
                    a.content,
                    c.categoryName,
                    u.username,
                    ai.imageURL,
                    an.views,
                    an.likes
                ORDER BY a.created_at DESC
                LIMIT %s
            """
            cursor.execute(query, (category_id, search_term, search_term, search_term, limit))

        else:
            query = """
                SELECT 
                    a.articleID,
                    a.articleTitle,
                    a.content,
                    c.categoryName,
                    u.username,
                    IFNULL(ai.imageURL, NULL) AS imageURL,
                    IFNULL(an.views, 0) AS views,
                    IFNULL(an.likes, 0) AS likes
                FROM Article a
                JOIN UserAccount u ON a.created_by = u.userID
                JOIN ArticleCategory c ON a.categoryID = c.categoryID
                LEFT JOIN ArticleImage ai ON a.articleID = ai.articleID
                LEFT JOIN ArticleAnalytics an ON a.articleID = an.articleID
                WHERE a.articleStatus = 'published'
                AND (
                        a.articleTitle LIKE %s
                        OR a.content LIKE %s
                        OR c.categoryName LIKE %s
                    )
                GROUP BY 
                    a.articleID,
                    a.articleTitle,
                    a.content,
                    c.categoryName,
                    u.username,
                    ai.imageURL,
                    an.views,
                    an.likes
                ORDER BY a.created_at DESC
                LIMIT %s
            """
            cursor.execute(query, (search_term, search_term, search_term, limit))

        articles = cursor.fetchall()

        cursor.close()
        conn.close()

        return articles

    def get_my_articles(self, user_id):
        conn = get_db_connection()
        cursor = conn.cursor()

        sql = """
        SELECT 
            a.articleID,
            a.articleTitle,
            a.content,
            a.articleStatus,
            a.categoryID,
            a.created_at,
            a.first_edited_at,
            a.last_edited_at,
            c.categoryName,
            ai.imageURL
        FROM Article a
        LEFT JOIN ArticleCategory c ON a.categoryID = c.categoryID
        LEFT JOIN ArticleImage ai ON a.articleID = ai.articleID
        WHERE a.created_by = %s
        ORDER BY a.created_at DESC
        """

        cursor.execute(sql, (user_id,))
        articles = cursor.fetchall()
        
        cursor.close()
        conn.close()
        return articles

    def get_article(self, articleID):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT 
                a.articleID,
                a.articleTitle,
                a.content,
                a.categoryID,
                a.articleStatus,
                a.created_at,
                a.first_edited_at,
                a.last_edited_at,
                a.updated_at,
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

        cursor.execute(query, (articleID,))
        article = cursor.fetchone()
        
        cursor.close()
        conn.close()
        return article

    def get_headline_article(self):
        conn = get_db_connection()
        cursor = conn.cursor()

        sql = """
        SELECT a.*, c.categoryName, ai.imageURL, u.username,
            IFNULL(an.views, 0) AS views
        FROM Article a
        LEFT JOIN ArticleCategory c ON a.categoryID = c.categoryID
        LEFT JOIN ArticleImage ai ON a.articleID = ai.articleID
        LEFT JOIN UserAccount u ON a.created_by = u.userID
        LEFT JOIN ArticleAnalytics an ON a.articleID = an.articleID
        WHERE a.articleStatus = 'published'
        ORDER BY IFNULL(an.views, 0) DESC, a.created_at DESC
        LIMIT 1
        """

        cursor.execute(sql)
        article = cursor.fetchone()

        conn.close()
        return article

    def get_latest_articles_by_category(self, limit=6, exclude_id=None):
        conn = get_db_connection()
        cursor = conn.cursor()

        sql = """
        SELECT a.articleID, a.articleTitle, a.content, a.created_at,
            a.articleStatus, a.categoryID,
            c.categoryName, ai.imageURL, u.username,
            COALESCE(aa.views, 0) AS views,
            COALESCE(aa.likes, 0) AS likes
        FROM Article a
        LEFT JOIN ArticleCategory c ON a.categoryID = c.categoryID
        LEFT JOIN ArticleImage ai ON a.articleID = ai.articleID
        LEFT JOIN UserAccount u ON a.created_by = u.userID
        LEFT JOIN ArticleAnalytics aa ON a.articleID = aa.articleID
        INNER JOIN (
            SELECT categoryID, MAX(created_at) AS latest_created
            FROM Article
            WHERE articleStatus = 'published'
            GROUP BY categoryID
        ) latest_per_category
        ON a.categoryID = latest_per_category.categoryID
        AND a.created_at = latest_per_category.latest_created
        WHERE a.articleStatus = 'published'
        """
        params = []

        if exclude_id:
            sql += " AND a.articleID != %s"
            params.append(exclude_id)

        sql += """
        ORDER BY a.created_at DESC
        LIMIT %s
        """

        params.extend([limit])

        cursor.execute(sql, params)
        articles = cursor.fetchall()
        conn.close()
        return articles

    def get_categories(self):
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM ArticleCategory WHERE categoryStatus='active'")
        categories = cursor.fetchall()

        conn.close()
        return categories
    
    @staticmethod
    def home_article_by_category(category_id, limit=6, exclude_id=None):
        conn = get_db_connection()
        cursor = conn.cursor()

        sql = """
            SELECT 
                a.articleID,
                a.articleTitle,
                a.content,
                a.created_at,
                a.articleStatus,
                a.categoryID,
                ac.categoryName,
                ai.imageURL,
                IFNULL(aa.views, 0) AS views,
                IFNULL(aa.likes, 0) AS likes
            FROM Article a
            LEFT JOIN ArticleCategory ac ON a.categoryID = ac.categoryID
            LEFT JOIN ArticleImage ai ON a.articleID = ai.articleID
            LEFT JOIN ArticleAnalytics aa ON a.articleID = aa.articleID
            WHERE a.articleStatus = 'published'
            AND a.categoryID = %s
        """

        params = [category_id]

        if exclude_id is not None:
            sql += " AND a.articleID != %s"
            params.append(exclude_id)

        sql += """
            ORDER BY a.created_at DESC
            LIMIT %s
        """
        params.append(limit)

        cursor.execute(sql, params)
        result = cursor.fetchall()
        conn.close()
        return result

    def insert_article(self, user_id, title, category_id, content, status,
                   ai_fact_check_score=0, ai_fact_check_status=None):
        conn = get_db_connection()
        cursor = conn.cursor()

        sql = """
        INSERT INTO Article
        (
            articleTitle,
            content,
            created_at,
            first_edited_at,
            last_edited_at,
            articleStatus,
            created_by,
            updated_at,
            categoryID,
            aiFactCheckScore,
            aiFactCheckStatus
        )
        VALUES (%s, %s, NOW(), NULL, NULL, %s, %s, NOW(), %s, %s, %s)
        """
        cursor.execute(
            sql,
            (
                title,
                content,
                status,
                user_id,
                category_id,
                float(ai_fact_check_score or 0),
                ai_fact_check_status
            )
        )
        article_id = cursor.lastrowid

        conn.commit()
        cursor.close()
        conn.close()
        return article_id



    def insert_article_image(self, article_id, image_url):
        conn = get_db_connection()
        cursor = conn.cursor()

        sql = """
        INSERT INTO ArticleImage (articleID, imageURL, uploaded_at)
        VALUES (%s, %s, NOW())
        """
        cursor.execute(sql, (article_id, image_url))

        conn.commit()
        conn.close()

    #----------------#
    # Update Article #
    #----------------#
    
    def update_article(self, article_id, title, category_id, content, status,
                   ai_fact_check_score=0, ai_fact_check_status=None):
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            check_sql = "SELECT first_edited_at FROM Article WHERE articleID = %s"
            cursor.execute(check_sql, (article_id,))
            article = cursor.fetchone()

            if article and article["first_edited_at"] is None:
                sql = """
                    UPDATE Article
                    SET articleTitle = %s,
                        categoryID = %s,
                        content = %s,
                        articleStatus = %s,
                        aiFactCheckScore = %s,
                        aiFactCheckStatus = %s,
                        first_edited_at = NOW(),
                        last_edited_at = NOW()
                    WHERE articleID = %s
                """
                cursor.execute(
                    sql,
                    (
                        title,
                        category_id,
                        content,
                        status,
                        float(ai_fact_check_score or 0),
                        ai_fact_check_status,
                        article_id
                    )
                )
            else:
                sql = """
                    UPDATE Article
                    SET articleTitle = %s,
                        categoryID = %s,
                        content = %s,
                        articleStatus = %s,
                        aiFactCheckScore = %s,
                        aiFactCheckStatus = %s,
                        last_edited_at = NOW()
                    WHERE articleID = %s
                """
                cursor.execute(
                    sql,
                    (
                        title,
                        category_id,
                        content,
                        status,
                        float(ai_fact_check_score or 0),
                        ai_fact_check_status,
                        article_id
                    )
                )

            conn.commit()
            return True

        except Exception as e:
            conn.rollback()
            print("update_article error:", e)
            return False

        finally:
            cursor.close()
            conn.close()

    def update_article_image(self, article_id, image_filename):
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            sql_check = "SELECT * FROM ArticleImage WHERE articleID = %s"
            cursor.execute(sql_check, (article_id,))
            existing = cursor.fetchone()

            if existing:
                sql = """
                    UPDATE ArticleImage
                    SET imageURL = %s
                    WHERE articleID = %s
                """
                cursor.execute(sql, (image_filename, article_id))
            else:
                sql = """
                    INSERT INTO ArticleImage (articleID, imageURL)
                    VALUES (%s, %s)
                """
                cursor.execute(sql, (article_id, image_filename))

            conn.commit()
            return True

        except Exception as e:
            conn.rollback()
            print("update_article_image error:", e)
            return False

        finally:
            cursor.close()
            conn.close()

    #----------------#
    # Delete Article #
    #----------------#
    def delete_article(self, article_id):
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # delete child records first
            cursor.execute("DELETE FROM ArticleImage WHERE articleID = %s", (article_id,))
            cursor.execute("DELETE FROM ArticleAnalytics WHERE articleID = %s", (article_id,))

            # then delete parent record
            cursor.execute("DELETE FROM Article WHERE articleID = %s", (article_id,))

            conn.commit()
            return True

        except Exception as e:
            conn.rollback()
            print("delete_article error:", e)
            return False

        finally:
            cursor.close()
            conn.close()

    def search_my_articles(self, user_id, keyword="", category_id="", status=""):
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            SELECT 
                a.articleID,
                a.articleTitle,
                a.content,
                a.articleStatus,
                a.categoryID,
                a.created_at,
                a.first_edited_at,
                a.last_edited_at,
                c.categoryName,
                ai.imageURL
            FROM Article a
            LEFT JOIN ArticleCategory c ON a.categoryID = c.categoryID
            LEFT JOIN ArticleImage ai ON a.articleID = ai.articleID
            WHERE a.created_by = %s
        """
        params = [user_id]

        if keyword:
            query += " AND a.articleTitle LIKE %s"
            params.append(f"%{keyword}%")

        if category_id:
            query += " AND a.categoryID = %s"
            params.append(category_id)

        if status:
            query += " AND LOWER(a.articleStatus) = LOWER(%s)"
            params.append(status)

        query += " ORDER BY a.created_at DESC"

        cursor.execute(query, params)
        articles = cursor.fetchall()

        cursor.close()
        conn.close()
        return articles

    # def get_home_headline_article(self):
    #     conn = get_db_connection()
    #     cursor = conn.cursor()

    #     sql = """
    #     SELECT a.*, c.categoryName, ai.imageURL, u.username,
    #         IFNULL(an.views, 0) AS views, 
    #         IFNULL(an.likes, 0) AS likes,
    #         IFNULL(a.credibilityScore, 0) AS credibilityScore
    #     FROM Article a
    #     LEFT JOIN ArticleCategory c ON a.categoryID = c.categoryID
    #     LEFT JOIN ArticleImage ai ON a.articleID = ai.articleID
    #     LEFT JOIN UserAccount u ON a.created_by = u.userID
    #     LEFT JOIN ArticleAnalytics an ON a.articleID = an.articleID
    #     WHERE a.articleStatus = 'published'
    #     ORDER BY IFNULL(an.views, 0) DESC, a.created_at DESC
    #     LIMIT 1
    #     """

    #     cursor.execute(sql)
    #     article = cursor.fetchone()

    #     conn.close()
    #     return article

    def get_home_headline_article(self):
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            base_select = """
                SELECT a.*, c.categoryName, ai.imageURL, u.username,
                    IFNULL(an.views, 0) AS views,
                    IFNULL(an.likes, 0) AS likes,
                    IFNULL(a.credibilityScore, 0) AS credibilityScore
                FROM Article a
                LEFT JOIN ArticleCategory c ON a.categoryID = c.categoryID
                LEFT JOIN ArticleImage ai ON a.articleID = ai.articleID
                LEFT JOIN UserAccount u ON a.created_by = u.userID
                LEFT JOIN ArticleAnalytics an ON a.articleID = an.articleID
                WHERE a.articleStatus = 'published'
            """

            # 1) Most viewed in the last 1 day
            sql_1_day = base_select + """
                AND a.created_at >= DATE_SUB(NOW(), INTERVAL 1 DAY)
                ORDER BY IFNULL(an.views, 0) DESC, a.created_at DESC
                LIMIT 1
            """
            cursor.execute(sql_1_day)
            article = cursor.fetchone()

            # 2) Fallback: most viewed in the last 3 days
            if not article:
                sql_3_day = base_select + """
                    AND a.created_at >= DATE_SUB(NOW(), INTERVAL 3 DAY)
                    ORDER BY IFNULL(an.views, 0) DESC, a.created_at DESC
                    LIMIT 1
                """
                cursor.execute(sql_3_day)
                article = cursor.fetchone()

            # 3) Final fallback: latest published article
            if not article:
                sql_latest = base_select + """
                    ORDER BY a.created_at DESC
                    LIMIT 1
                """
                cursor.execute(sql_latest)
                article = cursor.fetchone()

            return article

        finally:
            conn.close()

    def get_featured_article_by_category(self, category_id, exclude_id=None):
        conn = get_db_connection()
        cursor = conn.cursor()

        params = [category_id]
        sql = """
        SELECT a.articleID, a.articleTitle, a.content, a.created_at,
            a.categoryID, a.articleStatus,
            c.categoryName, ai.imageURL As featured_image, u.username,
            IFNULL(an.views, 0) AS views,
            IFNULL(an.likes, 0) AS likes,
            IFNULL(a.credibilityScore, 0) AS credibilityScore
        FROM Article a
        LEFT JOIN ArticleCategory c ON a.categoryID = c.categoryID
        LEFT JOIN ArticleImage ai ON a.articleID = ai.articleID
        LEFT JOIN UserAccount u ON a.created_by = u.userID
        LEFT JOIN ArticleAnalytics an ON a.articleID = an.articleID
        WHERE a.articleStatus = 'published'
        AND a.categoryID = %s
        AND a.created_at >= DATE_SUB(NOW(), INTERVAL 3 DAY)
        """

        if exclude_id:
            sql += " AND a.articleID != %s"
            params.append(exclude_id)

        sql += """
        ORDER BY IFNULL(an.views, 0) DESC, a.created_at DESC
        LIMIT 1
        """

        cursor.execute(sql, params)
        article = cursor.fetchone()

        # fallback: if no recent result, use latest article in that category
        if not article:
            params = [category_id]
            fallback_sql = """
            SELECT a.articleID, a.articleTitle, a.content, a.created_at,
                a.categoryID, a.articleStatus,
                c.categoryName, ai.imageURL, u.username,
                IFNULL(an.views, 0) AS views,
                IFNULL(an.likes, 0) AS likes,
                IFNULL(a.credibilityScore, 0) AS credibilityScore
            FROM Article a
            LEFT JOIN ArticleCategory c ON a.categoryID = c.categoryID
            LEFT JOIN ArticleImage ai ON a.articleID = ai.articleID
            LEFT JOIN UserAccount u ON a.created_by = u.userID
            LEFT JOIN ArticleAnalytics an ON a.articleID = an.articleID
            WHERE a.articleStatus = 'published'
            AND a.categoryID = %s
            """

            if exclude_id:
                fallback_sql += " AND a.articleID != %s"
                params.append(exclude_id)

            fallback_sql += """
            ORDER BY a.created_at DESC
            LIMIT 1
            """

            cursor.execute(fallback_sql, params)
            article = cursor.fetchone()

        conn.close()
        return article

    def get_home_latest_articles(self, limit=4, offset=0, exclude_id=None):
        conn = get_db_connection()
        cursor = conn.cursor()

        sql = """
        SELECT a.articleID, a.articleTitle, a.content, ai.imageURL, 
            c.categoryName, u.username,
            IFNULL(an.views, 0) AS views,
            IFNULL(an.likes, 0) AS likes,
            IFNULL(a.credibilityScore, 0) AS credibilityScore
        FROM Article a
        LEFT JOIN ArticleImage ai ON a.articleID = ai.articleID
        LEFT JOIN ArticleCategory c ON a.categoryID = c.categoryID
        LEFT JOIN UserAccount u ON a.created_by = u.userID
        LEFT JOIN ArticleAnalytics an ON a.articleID = an.articleID
        WHERE a.articleStatus = 'published'
        """

        params = []

        if exclude_id:
            sql += " AND a.articleID != %s"
            params.append(exclude_id)

        sql += """
        ORDER BY a.created_at DESC
        LIMIT %s OFFSET %s
        """

        params.extend([limit, offset])

        cursor.execute(sql, params)
        articles = cursor.fetchall()
        conn.close()
        return articles

    def get_latest_testimonials(self, limit=2):
        conn = get_db_connection()
        cursor = conn.cursor()

        sql = """
        SELECT t.*, u.username
        FROM Testimonial t
        LEFT JOIN UserAccount u ON t.userID = u.userID
        ORDER BY t.created_at DESC
        LIMIT %s
        """
        cursor.execute(sql, (limit,))
        testimonials = cursor.fetchall()

        conn.close()
        return testimonials

    @staticmethod
    def get_total_articles():
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) AS total_articles FROM Article")
        result = cursor.fetchone()

        conn.close()
        return result["total_articles"]

    @staticmethod
    def count_eligible_verified_articles(userID):
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM Article
            WHERE created_by = %s
            AND articleStatus = 'Published'
            AND credibilityScore >= 90
        """,
            (userID,),
        )

        result = cursor.fetchone()
        conn.close()
        return result["total"] if result else 0
