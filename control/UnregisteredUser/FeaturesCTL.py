from flask import jsonify
from flask_cors import cross_origin
from app.entities.ProductFeatures import ProductFeatures
from app.db import get_database
from app.routes.UnregisteredUser_routes import UnregisteredUser


class FeaturesCTL:
    def __init__(self):
        self.productFeatures_entity = ProductFeatures()

    def requestKeyFeatures(self):
        featuresList = self.productFeatures_entity.requestKeyFeatures()
        return featuresList


@UnregisteredUser.route("/api/features", methods=["GET"])
def requestKeyFeatures():
    featuresCTL = FeaturesCTL()
    try:
        featuresList = featuresCTL.requestKeyFeatures()

        if featuresList:
            return jsonify(featuresList), 200
        else:
            return (
                jsonify({
                    "status": "error",
                    "message": "No features found"
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