# from flask import jsonify, request
# from flask_cors import cross_origin
# from app.entities.UserAccount import UserAccount
# from app.routes.UnregisteredUser_routes import UnregisteredUser


# class RegisterAccountCTL:
#     def __init__(self):
#         self.userAccount = UserAccount()

#     def regAcc(self, username, email, password, firstName, lastName, phone):
#         isRegistered = self.userAccount.regAcc(
#             username, email, password, firstName, lastName, phone
#         )

#         if isRegistered is True:
#             return True
#         else:
#             return False


# @UnregisteredUser.route("/api/register", methods=["POST"])
# @cross_origin()
# def regAcc():
#     registrationData = request.json

#     username = registrationData["username"]
#     email = registrationData["email"]
#     password = registrationData["password"]
#     firstName = registrationData["firstName"]
#     lastName = registrationData["lastName"]
#     phone = registrationData["phone"]

#     registerAccountCTL = RegisterAccountCTL()

#     try:
#         isRegistered = registerAccountCTL.regAcc(
#             username, email, password, firstName, lastName, phone
#         )

#         if isRegistered:
#             return (
#                 jsonify(
#                     {
#                         "status": "success",
#                         "message": "Account has been registered successfully.",
#                         "isRegistered": isRegistered,
#                     }
#                 ),
#                 201,
#             )
#         else:
#             return (
#                 jsonify(
#                     {
#                         "status": "error",
#                         "message": "Duplicate email / Incomplete details.",
#                         "isRegistered": isRegistered,
#                     }
#                 ),
#                 400,
#             )

#     except Exception as e:
#         return (
#             jsonify({
#                 "status": "error",
#                 "message": str(e),
#             }),
#             500,
#         )

# working code
# from entity.db_connection import get_db_connection

# class RegisterController:

#     def register(self, username, email, password, retypePassword):

#         conn = get_db_connection()
#         cursor = conn.cursor()

#         # Check if email already exists
#         check_query = "SELECT * FROM UserAccount WHERE email = %s"
#         cursor.execute(check_query, (email,))
#         existing_user = cursor.fetchone()

#         if existing_user:
#             cursor.close()
#             conn.close()
#             return {"success": False, "message": "Email already registered"}

#         # Insert new user
#         insert_query = """
#         INSERT INTO UserAccount (username, email, pwd, userType, accountStatus)
#         VALUES (%s, %s, %s, 'free', 'active')
#         """

#         cursor.execute(insert_query, (username, email, password))
#         conn.commit()

#         cursor.close()
#         conn.close()

#         return {"success": True}
    

# test password validation
from entity.db_connection import get_db_connection

class RegisterController:

    def register(self, username, email, password, retypePassword):

        # Check password length
        if len(password) < 10:
            return {"success": False, "message": "Password must be at least 10 characters"}

        # Check password match
        if password != retypePassword:
            return {"success": False, "message": "Passwords do not match"}

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if email already exists
        check_query = "SELECT * FROM UserAccount WHERE email = %s"
        cursor.execute(check_query, (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            cursor.close()
            conn.close()
            return {"success": False, "message": "Email already registered"}

        # Insert new user
        insert_query = """
        INSERT INTO UserAccount (username, email, pwd, userType, accountStatus)
        VALUES (%s, %s, %s, 'free', 'active')
        """

        cursor.execute(insert_query, (username, email, password))
        conn.commit()

        cursor.close()
        conn.close()

        return {"success": True}
