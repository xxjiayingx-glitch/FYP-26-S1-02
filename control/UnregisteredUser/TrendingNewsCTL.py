from flask import jsonify, request
from flask_cors import cross_origin
from app.entities.Article import Article
from app.db import get_database
from app.routes.UnregisteredUser_routes import UnregisteredUser


class TrendingNewsCTL:
    def __init__(self):
        self.article_entity = Article()

    def getTrendingNews(self, articleID):
        articleList = self.article_entity.getTrendingNews(articleID)
        return articleList


@UnregisteredUser.route("/api/trending-news", methods=["GET"])
@cross_origin()
def getTrendingNews():
    articleID = int(request.args.get("articleID"))
    trendingNewsCTL = TrendingNewsCTL()

    try:
        articleList = trendingNewsCTL.getTrendingNews(articleID)

        if articleList:
            return jsonify(articleList), 200
        else:
            return (
                jsonify({
                    "status": "error",
                    "message": "No trending news found"
                }),
                404,
            )

    except Exception as e:
        return (
            jsonify({
                "status": "error",
                "message": str(e),
            }),
            500,
        )