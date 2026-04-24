from entity.UserAccount import UserAccount

class SearchUsersCTL:
    def searchFilterUsers(self, q, userType, accountStatus):
        return UserAccount.findUsersByCriteria(q, userType, accountStatus)
    
    def get_all_user_roles():
        return UserAccount.get_all_user_roles()