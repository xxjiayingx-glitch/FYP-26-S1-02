# control/ArticleController.py
from entity.Article import Article

class ArticleController:

    def __init__(self):
        self.article_entity = Article()

    # Fetch all articles
    def get_articles(self):
        return self.article_entity.get_all_articles()

    # Search articles by keyword
    def search(self, keyword):
        return self.article_entity.search_articles(keyword)

    # Fetch a single article by ID
    def get_article(self, article_id):
        return self.article_entity.get_article(article_id)

    # Get the headline article
    def get_headline(self):
        return self.article_entity.get_headline_article()

    # Get latest articles with optional limit
    def get_latest(self, limit=3):
        return self.article_entity.get_latest_articles(limit)
    
    # Fetch all articles created by a specific user
    def get_my_articles(self, user_id):
        return self.article_entity.get_my_articles(user_id)
    
    # Fetch all categories
    def get_categories(self):
        return self.article_entity.get_categories()
    
    # Create a new article, optionally with a featured image
    def create_article(self, user_id, title, category_id, content, status, featured_image=None):
        print("Creating article:", title, category_id, user_id, status)
        article_id = self.article_entity.insert_article(user_id, title, category_id, content, status)
        if featured_image and article_id:
            self.article_entity.insert_article_image(article_id, featured_image)
        return article_id