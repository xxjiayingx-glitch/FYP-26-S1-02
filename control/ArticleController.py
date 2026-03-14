from entity.Article import Article

class ArticleController:

    def __init__(self):
        self.article_entity = Article()

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

    def delete_article(self, article_id):
        return self.article_entity.delete_article(article_id)

    def search_my_articles(self, user_id, keyword):
        return self.article_entity.search_my_articles(user_id, keyword)