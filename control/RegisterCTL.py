import re
import secrets
from entity.UserAccount import UserAccount
from server.email_service import send_verification_email

class RegisterController:

    def __init__(self):
        self.user_entity = UserAccount()

    def register(self, firstName, lastName, phone, username, email, password, retypePassword, interests=None):

        # --- Validation ---
        if len(password) < 10:
            return {"success": False, "message": "Password must be at least 10 characters"}

        if password != retypePassword:
            return {"success": False, "message": "Passwords do not match"}

        email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not re.match(email_pattern, email):
            return {"success": False, "message": "Invalid email format"}

        phone_pattern = r"^\d{8}$"
        if not re.match(phone_pattern, phone):
            return {"success": False, "message": "Phone number must be 8 digits"}

        # --- Duplicate checks (calls entity) ---
        if self.user_entity.find_by_email(email):
            return {"success": False, "message": "Email already registered"}

        if self.user_entity.find_by_username(username):
            return {"success": False, "message": "Username already taken"}

        # Generate verification token
        token = secrets.token_urlsafe(32)

        # Save user WITH token + unverified status
        new_user_id = self.user_entity.register_user(
            username, email, password, firstName, lastName, phone, token
        )

        # --- Save category interests if provided ---
        if interests:
            category_ids = self.user_entity.get_category_ids_by_names(interests)  # convert names → IDs
            if category_ids:
                self.user_entity.save_category_interests(new_user_id, category_ids)

        send_verification_email(email, token)
        
        return {"success": True, "message": "Registration successful", "userID": new_user_id}

# class RegisterController:

#     def register(
#         self, firstName, lastName, phone, username, email, password, retypePassword
#     ):

#         # Check password length
#         if len(password) < 10:
#             return {
#                 "success": False,
#                 "message": "Password must be at least 10 characters",
#             }

#         # Check password match
#         if password != retypePassword:
#             return {"success": False, "message": "Passwords do not match"}

#         # Email format validation
#         email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
#         if not re.match(email_pattern, email):
#             return {"success": False, "message": "Invalid email format"}

#         # Phone validation (Singapore 8 digits)
#         phone_pattern = r"^\d{8}$"
#         if not re.match(phone_pattern, phone):
#             return {"success": False, "message": "Phone number must be 8 digits"}

#         conn = get_db_connection()
#         cursor = conn.cursor()

#         # Check duplicate email
#         cursor.execute("SELECT * FROM UserAccount WHERE email = %s", (email,))
#         if cursor.fetchone():
#             cursor.close()
#             conn.close()
#             return {"success": False, "message": "Email already registered"}

#         # Check duplicate username
#         cursor.execute("SELECT * FROM UserAccount WHERE username = %s", (username,))
#         if cursor.fetchone():
#             cursor.close()
#             conn.close()
#             return {"success": False, "message": "Username already taken"}

#         # Insert new user
#         insert_query = """
#         INSERT INTO UserAccount (username, email, pwd, first_name, last_name, phone, userType, accountStatus, created_at)
#         VALUES (%s, %s, %s, %s, %s, %s, 'free', 'active', NOW())
#         """

#         cursor.execute(
#             insert_query, (username, email, password, firstName, lastName, phone)
#         )
#         conn.commit()

#         cursor.close()
#         conn.close()

#         return {"success": True, "message": "Registration successful"}
