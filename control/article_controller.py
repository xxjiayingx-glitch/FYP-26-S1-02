from entity.article_entity import ArticleEntity

class ArticleController:

    def __init__(self):
        self.article_entity = ArticleEntity()

    def get_articles(self):
        return self.article_entity.get_all_articles()

    def search(self,keyword):
        return self.article_entity.search_articles(keyword)

    def get_article(self,id):
        return self.article_entity.get_article(id)