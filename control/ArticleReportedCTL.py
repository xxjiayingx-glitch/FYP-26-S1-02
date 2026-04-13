from entity.ReportedArticle import ReportedArticle

class ArticleReported:
    def list_article_reported(self, expertise_category=None):
        return ReportedArticle.get_article_reported(expertise_category)
