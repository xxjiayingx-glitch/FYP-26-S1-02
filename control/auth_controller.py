from entity.user_entity import get_user

def login_user(username,password):

    user = get_user(username,password)

    if user:
        return user
    else:
        return None