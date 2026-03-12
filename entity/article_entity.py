from entity.db_connection import get_db_connection

class ArticleEntity:

    def get_all_articles(self):

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM Article")
        articles = cursor.fetchall()

        conn.close()
        return articles


    def search_articles(self,keyword):

        conn = get_db_connection()
        cursor = conn.cursor()

        sql = "SELECT * FROM Article WHERE articleTitle LIKE %s"
        cursor.execute(sql,('%'+keyword+'%',))

        articles = cursor.fetchall()
        conn.close()

        return articles


    def get_article(self,articleID):

        conn = get_db_connection()
        cursor = conn.cursor()

        sql="SELECT * FROM Article WHERE articleID=%s"
        cursor.execute(sql,(articleID,))

        article = cursor.fetchone()
        conn.close()

        return article