from entity.db_connection import get_db_connection


class Article:
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

        # sql = """
        # SELECT * FROM Article
        # WHERE articleStatus = 'Active'
        # ORDER BY created_at DESC
        # LIMIT 1
        # """

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

    def get_latest_articles(self, limit=3):
        conn = get_db_connection()
        cursor = conn.cursor()

        sql = """
        SELECT * FROM Article
        WHERE articleStatus = 'Active'
        ORDER BY created_at DESC
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

    def get_home_latest_articles(self, limit=3, offset=0, exclude_id=None):
        conn = get_db_connection()
        cursor = conn.cursor()

        sql = """
        SELECT a.*, ai.imageURL
        FROM Article a
        LEFT JOIN ArticleImage ai ON a.articleID = ai.articleID
        WHERE a.articleStatus = 'Active'
        """
        params = []

        if exclude_id:
            sql += " AND a.articleID != %s"
            params.append(exclude_id)

        sql += " ORDER BY a.created_at DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])

        cursor.execute(sql, tuple(params))
        articles = cursor.fetchall()
        conn.close()
        return articles

    @staticmethod
    def get_total_articles():
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) AS total_articles FROM Article")
        result = cursor.fetchone()

        conn.close()
        return result["total_articles"]
