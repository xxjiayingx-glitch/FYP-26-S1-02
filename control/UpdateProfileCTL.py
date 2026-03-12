from entity.User import UserEntity

user_entity = UserEntity()

def update_user_profile(userID, first, last, phone):

    user_entity.update_profile(userID, first, last, phone)

    print("Profile Updated")