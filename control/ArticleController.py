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

    def get_headline(self):
        return self.article_entity.get_headline_article()

    def get_latest(self, limit=3):
        return self.article_entity.get_latest_articles(limit)