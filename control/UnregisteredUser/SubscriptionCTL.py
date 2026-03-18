from entity.Subscription import Subscription

class SubscriptionCTL:
    def __init__(self):
        self.subscription_plan_entity = Subscription()

    def getSubscriptionPlans(self):

        plans = self.subscription_plan_entity.get_all_plans(self)

        if not plans:
            return {
                "success": False,
                "plans": []
            }

        return {
            "success": True,
            "plans": plans
        }
