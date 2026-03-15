# control/ArticleController.py
from entity.Article import Article
from db_connection import connect_db  # this should work now

class ArticleController:

    def __init__(self):
        self.article_entity = Article()
        self.db = connect_db()  

    def get_articles(self):
        return self.article_entity.get_all_articles()
    
    def search(self, keyword):
        return self.article_entity.search_articles(keyword)

    def get_article(self, id):
        return self.article_entity.get_article(id)

    def get_categories(self):
        return self.article_entity.get_categories()
    
    def get_my_articles(self, user_id):
        return self.article_entity.get_my_articles(user_id)
    
    def create_article(self, user_id, title, category_id, content, status, featured_image=None):
        article_id = self.article_entity.insert_article(user_id, title, category_id, content, status)
        if article_id and featured_image:
            self.article_entity.insert_article_image(article_id, featured_image)
        return article_id

    def get_headline(self):
        return self.article_entity.get_headline_article()

    def get_latest(self, limit=3):
        return self.article_entity.get_latest_articles(limit)

    def get_home_latest_articles(self, limit=3, offset=0, exclude_id=None):
        return self.article_entity.get_home_latest_articles(limit, offset, exclude_id)

    def delete_article(self, article_id):
        return self.article_entity.delete_article(article_id)

    def search_my_articles(self, user_id, keyword):
        return self.article_entity.search_my_articles(user_id, keyword)
    
    def get_article(self, article_id):
        return self.article_entity.get_article(article_id)

    def get_article_insight(self, article_id):
        cursor = self.db.cursor(dictionary=True)
        query = """
            SELECT 
                a.articleID,
                a.articleTitle,
                a.content,
                a.credibilityScore,
                a.reviewPriority,
                a.updated_at,
                a.aiReview,
                IFNULL(an.views,0) as views,
                IFNULL(an.likes,0) as likes,
                IFNULL(an.shares,0) as shares
            FROM Article a
            LEFT JOIN ArticleAnalytics an
            ON a.articleID = an.articleID
            WHERE a.articleID = %s
        """
        cursor.execute(query, (article_id,))
        article = cursor.fetchone()
        cursor.close()
        return article

    def save_ai_review(self, article_id, review_text):
        cursor = self.db.cursor()
        sql = "UPDATE Article SET aiReview = %s WHERE articleID = %s"
        cursor.execute(sql, (review_text, article_id))
        self.db.commit()
        cursor.close()