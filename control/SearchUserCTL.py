from entity.UserAccount import UserAccount

class SearchUsersCTL:
    def searchFilterUsers(self, q, userType, accountStatus):
        return UserAccount.findUsersByCriteria(q, userType, accountStatus)