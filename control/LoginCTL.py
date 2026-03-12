from entity.User import UserEntity

class AuthController:

    def __init__(self):
        self.user_entity = UserEntity()

    def login(self,email,pwd):

        user = self.user_entity.login(email,pwd)

        if user:
            return user
        return None