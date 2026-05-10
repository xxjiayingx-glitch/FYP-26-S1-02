# from entity.ReportedArticle import ReportedArticle

# class ArticleReported:
#     def list_article_reported(self, expertise_category=None):
#         return ReportedArticle.get_article_reported(expertise_category)

from entity.ReportedArticle import ReportedArticle

class ArticleReported:
    def list_article_reported(self, expertise_category=None, admin_fallback_only=False):
        return ReportedArticle.get_article_reported(
            expertise_category,
            admin_fallback_only
        )