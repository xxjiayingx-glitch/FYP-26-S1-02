# Controller class to control the flow of traffic to
# send to UserAccount entity to fetch data

from flask import jsonify, request
from app.routes.login_routes import login
from flask_cors import CORS, cross_origin
from app.entities import UserAccount
from app.db import get_database


class LoginUserCTL:
    def __init__(self):
        self.user_entity = UserAccount()

    def validateUser(self, email, pwd):
        """
        Process login logic: Call User Entity to fetch user from DB and verify the password.
        """

        user = self.user_entity.validateUser(email, pwd)

        if user is None:
            return None
        else:
            return user


# Initialize Entity and Controller


@login.route("/api/login", methods=["POST"])
def login():
    """
    Handle login request by passing data to the login controller.
    """
    loginController = LoginUserCTL()
    # if request.method == "OPTIONS":
    #     # This is the preflight request
    #     return jsonify({"status": "CORS preflight successful"}), 200
    data = request.json
    email = data.get("email")
    password = data.get("password")

    # Delegate the login logic to the login controller
    try:
        user = loginController.validateUser(email, password)

        if user is None:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "Email/password is wrong!",
                        "user_data": None,
                    }
                ),
                404,
            )
        else:
            # user_data = {"email": user["email"], "role": user["role"].lower()}
            return (
                jsonify(
                    {
                        "status": "success",
                        "message": "Login successful!",
                        "user_data": user,
                    }
                ),
                200,
            )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
