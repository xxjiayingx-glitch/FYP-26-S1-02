from entity.UserAccount import UserAccount

class AuthController:

    def __init__(self):
        self.user_entity = UserAccount()

    def login(self,email,pwd):
        return self.user_entity.login(email,pwd)

   
