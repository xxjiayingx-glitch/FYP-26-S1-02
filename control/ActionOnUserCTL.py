from entity.UserAccount import UserAccount

class ActionOnUserCTL:
    def updateUserStatus(self, userId, action):
        return UserAccount.updateStatus(userId, action)