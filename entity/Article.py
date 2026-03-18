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
    
    @staticmethod
    def updateStatus(articleID, action):
        conn = get_db_connection()
        cursor = conn.cursor()

        if action == "suspend":
            new_status = "Suspended"
        elif action == "unsuspend":
            new_status = "Active"
        else:
            conn.close()
            return False
        
        cursor.execute("""
            UPDATE Article SET articleStatus = %s WHERE articleID = %s 
        """, (new_status, articleID))

        conn.commit()
        updated = cursor.rowcount > 0
        conn.close()

        return updated
    
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

    def get_my_articles(self, user_id):
        conn = get_db_connection()
        cursor = conn.cursor()

        sql = """
        SELECT a.*, c.categoryName, ai.imageURL
        FROM Article a
        LEFT JOIN ArticleCategory c ON a.categoryID = c.categoryID
        LEFT JOIN ArticleImage ai ON a.articleID = ai.articleID
        WHERE a.created_by = %s
        ORDER BY a.created_at DESC
        """
        cursor.execute(sql, (user_id,))
        articles = cursor.fetchall()

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

    def get_latest_articles_by_category(self, limit=6):
        conn = get_db_connection()
        cursor = conn.cursor()

        sql = """
        SELECT a.articleID, a.articleTitle, a.content, a.created_at,
            a.articleStatus, a.categoryID,
            c.categoryName, ai.imageURL, u.username
        FROM Article a
        LEFT JOIN ArticleCategory c ON a.categoryID = c.categoryID
        LEFT JOIN ArticleImage ai ON a.articleID = ai.articleID
        LEFT JOIN UserAccount u ON a.created_by = u.userID
        INNER JOIN (
            SELECT categoryID, MAX(created_at) AS latest_created
            FROM Article
            WHERE articleStatus = 'published'
            GROUP BY categoryID
        ) latest_per_category
        ON a.categoryID = latest_per_category.categoryID
        AND a.created_at = latest_per_category.latest_created
        WHERE a.articleStatus = 'published'
        ORDER BY a.created_at DESC
        LIMIT %s
        """

        cursor.execute(sql, (limit,))
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

    def insert_article(self, user_id, title, category_id, content, status):
        conn = get_db_connection()
        cursor = conn.cursor()

        sql = """
        INSERT INTO Article
        (articleTitle, content, created_at, articleStatus, created_by, updated_at, categoryID)
        VALUES (%s, %s, NOW(), %s, %s, NOW(), %s)
        """
        cursor.execute(sql, (title, content, status, user_id, category_id))
        article_id = cursor.lastrowid

        conn.commit()
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

    def delete_article(self, article_id):
        conn = get_db_connection()
        cursor = conn.cursor()

        # delete image records first if they exist
        cursor.execute("DELETE FROM ArticleImage WHERE articleID = %s", (article_id,))

        # delete the article
        cursor.execute("DELETE FROM Article WHERE articleID = %s", (article_id,))

        conn.commit()
        conn.close()

    def search_my_articles(self, user_id, keyword):
        conn = get_db_connection()
        cursor = conn.cursor()

        sql = """
        SELECT a.*, c.categoryName, ai.imageURL
        FROM Article a
        LEFT JOIN ArticleCategory c ON a.categoryID = c.categoryID
        LEFT JOIN ArticleImage ai ON a.articleID = ai.articleID
        WHERE a.created_by = %s
        AND a.articleTitle LIKE %s
        ORDER BY a.created_at DESC
        """
        cursor.execute(sql, (user_id, "%" + keyword + "%"))
        articles = cursor.fetchall()

        conn.close()
        return articles

    def get_home_headline_article(self):
        conn = get_db_connection()
        cursor = conn.cursor()

        sql = """
        SELECT a.*, ai.imageURL, c.categoryName, u.username
        FROM Article a
        LEFT JOIN ArticleImage ai ON a.articleID = ai.articleID
        LEFT JOIN ArticleCategory c ON a.categoryID = c.categoryID
        LEFT JOIN UserAccount u ON a.created_by = u.userID
        WHERE a.articleStatus = 'published'
        ORDER BY a.created_at DESC
        LIMIT 1
        """

        cursor.execute(sql)
        article = cursor.fetchone()

        conn.close()
        return article

    def get_home_latest_articles(self, limit=4, offset=0, exclude_id=None):
        conn = get_db_connection()
        cursor = conn.cursor()

        sql = """
        SELECT a.articleID, a.articleTitle, a.content, ai.imageURL, c.categoryName, u.username
        FROM Article a
        LEFT JOIN ArticleImage ai ON a.articleID = ai.articleID
        LEFT JOIN ArticleCategory c ON a.categoryID = c.categoryID
        LEFT JOIN UserAccount u ON a.created_by = u.userID
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
