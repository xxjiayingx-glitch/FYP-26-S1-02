from entity.UserAccount import UserAccount

class UserDetailsCTL:
    def getUserDetails(self, user_id):
        user = UserAccount.getUserByID(user_id)
        subscription_status = UserAccount.getUserSubscriptionStatus(user_id)
        interests = UserAccount.getUserInterests(user_id)

        return {
            "user": user,
            "subscription_status": subscription_status,
            "interests": interests
        }