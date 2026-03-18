from entity.Article import Article

class ActionOnArticle:
    def updateArticleStatus(self, articleID, action):
        return Article.updateStatus(articleID, action)
