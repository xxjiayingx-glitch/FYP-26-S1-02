from flask import jsonify, request
from flask_cors import cross_origin
from app.entities.UserAccount import UserAccount
from app.routes.UnregisteredUser_routes import UnregisteredUser


class RegisterAccountCTL:
    def __init__(self):
        self.userAccount = UserAccount()

    def regAcc(self, username, email, password, firstName, lastName, phone):
        isRegistered = self.userAccount.regAcc(
            username, email, password, firstName, lastName, phone
        )

        if isRegistered is True:
            return True
        else:
            return False


@UnregisteredUser.route("/api/register", methods=["POST"])
@cross_origin()
def regAcc():
    registrationData = request.json

    username = registrationData["username"]
    email = registrationData["email"]
    password = registrationData["password"]
    firstName = registrationData["firstName"]
    lastName = registrationData["lastName"]
    phone = registrationData["phone"]

    registerAccountCTL = RegisterAccountCTL()

    try:
        isRegistered = registerAccountCTL.regAcc(
            username, email, password, firstName, lastName, phone
        )

        if isRegistered:
            return (
                jsonify(
                    {
                        "status": "success",
                        "message": "Account has been registered successfully.",
                        "isRegistered": isRegistered,
                    }
                ),
                201,
            )
        else:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "Duplicate email / Incomplete details.",
                        "isRegistered": isRegistered,
                    }
                ),
                400,
            )

    except Exception as e:
        return (
            jsonify({
                "status": "error",
                "message": str(e),
            }),
            500,
        )