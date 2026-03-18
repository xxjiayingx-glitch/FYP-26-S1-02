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
        SELECT * FROM Article
        WHERE articleTitle LIKE %s
        ORDER BY created_at DESC
        """
        cursor.execute(sql, ("%" + keyword + "%",))
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

        sql = "SELECT * FROM Article WHERE articleID = %s"
        cursor.execute(sql, (articleID,))
        article = cursor.fetchone()

        conn.close()
        return article

    def get_headline_article(self):
        conn = get_db_connection()
        cursor = conn.cursor()

        sql = """
        SELECT a.*, c.categoryName, ai.imageURL, u.username
        FROM Article a
        LEFT JOIN ArticleCategory c ON a.categoryID = c.categoryID
        LEFT JOIN ArticleImage ai ON a.articleID = ai.articleID
        LEFT JOIN UserAccount u ON a.created_by = u.userID
        WHERE a.articleStatus = 'published'
        ORDER BY a.created_at DESC
        LIMIT 1
        """

        cursor.execute(sql)
        article = cursor.fetchone()

        conn.close()
        return article

    def get_latest_articles(self, limit=4):
        conn = get_db_connection()
        cursor = conn.cursor()

        sql = """
            SELECT a.*, c.categoryName, ai.imageURL, u.username
            FROM Article a
            LEFT JOIN ArticleCategory c ON a.categoryID = c.categoryID
            LEFT JOIN ArticleImage ai ON a.articleID = ai.articleID
            LEFT JOIN UserAccount u ON a.created_by = u.userID
            WHERE a.articleStatus = 'published'
            ORDER BY a.created_at DESC
            LIMIT 1, %s
        """        
        cursor.execute(sql, (limit,))
        articles = cursor.fetchall()

        conn.close()
        return articles

    def get_categories(self):
        conn = get_db_connection()
        cursor = conn.cursor()

        sql = """
        SELECT categoryID, categoryName
        FROM ArticleCategory
        ORDER BY categoryName ASC
        """
        cursor.execute(sql)
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
        SELECT a.*, c.categoryName
        FROM Article a
        LEFT JOIN ArticleCategory c ON a.categoryID = c.categoryID
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
        SELECT a.*, ai.imageURL
        FROM Article a
        LEFT JOIN ArticleImage ai ON a.articleID = ai.articleID
        WHERE a.articleStatus = 'Active'
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
        SELECT a.articleID, a.articleTitle, a.content, ai.imageURL
        FROM Article a
        LEFT JOIN ArticleImage ai ON a.articleID = ai.articleID
        WHERE a.articleStatus = 'Active'
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