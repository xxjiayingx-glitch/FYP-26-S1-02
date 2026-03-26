from entity.UserAccount import UserAccount

class AuthController:

    def __init__(self):
        self.user_entity = UserAccount()

    def login(self, email, pwd):
        result = self.user_entity.login(email, pwd)

        if result == "pending_verification":
            return "pending_verification"

        return result