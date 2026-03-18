from entity.ReportedArticle import ReportedArticle

class ArticleReported:
    def list_article_reported(self):
        return ReportedArticle.get_article_reported()
