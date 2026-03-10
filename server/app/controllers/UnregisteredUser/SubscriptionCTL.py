from flask import jsonify
from flask_cors import cross_origin
from app.entities.SubscriptionPlan import SubscriptionPlan
from app.db import get_database
from app.routes.UnregisteredUser_routes import UnregisteredUser


class SubscriptionCTL:
    def __init__(self):
        self.subscription_plan_entity = SubscriptionPlan()

    def fetchAllSubscription(self):
        subscriptionListing = self.subscription_plan_entity.fetchAllSubscription()
        return subscriptionListing


@UnregisteredUser.route("/api/subscription", methods=["GET"])
def fetchAllSubscription():
    subscriptionCTL = SubscriptionCTL()
    try:
        subscriptionListing = subscriptionCTL.fetchAllSubscription()

        if subscriptionListing:
            return jsonify(subscriptionListing), 200
        else:
            return (
                jsonify({
                    "status": "error",
                    "message": "No subscription plans found"
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