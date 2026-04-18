from entity.Article import Article

class ActionOnArticle:
    def update_article_and_report_status(self, articleID, action, reviewed_by):
        return Article.update_status_and_complete_reports(articleID, action, reviewed_by)
