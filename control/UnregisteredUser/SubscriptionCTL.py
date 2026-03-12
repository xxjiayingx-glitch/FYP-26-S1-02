from entity.subscription_entity import get_subscription

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