from control.auth_controller import login_user

def login():

    username = input("Username: ")
    password = input("Password: ")

    user = login_user(username,password)

    if user:
        print("Login Successful")
        return user
    else:
        print("Login Failed")
        return None