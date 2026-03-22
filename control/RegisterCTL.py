import re
import secrets
from entity.UserAccount import UserAccount
from server.email_service import send_verification_email
from werkzeug.security import generate_password_hash

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

        hashed_pw = generate_password_hash(password)

        # Save user WITH token + unverified status
        new_user_id = self.user_entity.register_user(
            username, email, hashed_pw, firstName, lastName, phone, token
        )

        # --- Save category interests if provided ---
        if interests:
            category_ids = self.user_entity.get_category_ids_by_names(interests)  # convert names → IDs
            if category_ids:
                self.user_entity.save_category_interests(new_user_id, category_ids)

        try:
            send_verification_email(email, token)
        except Exception as e:
            print("Failed to send verification email:", e)
        
        return {"success": True, "message": "Registration successful", "userID": new_user_id}
