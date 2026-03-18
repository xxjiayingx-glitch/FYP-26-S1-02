from entity.UserAccount import UserAccount

class ViewUsersCTL:
    def listUsers(self):
        return UserAccount.getAllUsers()