from control.user_controller import update_user_profile

def update_profile(userID):

    phone = input("New Phone: ")
    email = input("New Email: ")

    update_user_profile(userID,phone,email)