from entity.UserAccount import UserAccount
from entity.Article import Article
from werkzeug.security import check_password_hash, generate_password_hash

import re
import secrets
from datetime import date
from server.email_service import send_email_change_verification_email

class UpdateProfileCTL:

    @staticmethod
    def update_profile(userID, form):
        user_entity = UserAccount()
        user = user_entity.get_profile(userID)

        if not user:
            raise ValueError("User not found.")

        first_name = form.get("firstName", "").strip()
        last_name = form.get("lastName", "").strip()
        username = form.get("username", "").strip()
        phone = form.get("phone", "").strip()
        gender = form.get("gender")
        dateOfBirth = form.get("dateOfBirth", "").strip()
        new_email = form.get("newEmail", "").strip()

        # ========= REQUIRED FIELDS =========
        if not first_name:
            raise ValueError("First name is required.")
        if not last_name:
            raise ValueError("Last name is required.")
        if not phone:
            raise ValueError("Phone number is required.")
        if not gender or gender not in ["Male", "Female"]:
            raise ValueError("Please select a gender.")
        if not dateOfBirth:
            raise ValueError("Date of birth is required.")

        # ========= DOB VALIDATION =========
        try:
            dob_obj = date.fromisoformat(dateOfBirth)
        except ValueError:
            raise ValueError("Invalid date of birth format.")

        if dob_obj > date.today():
            raise ValueError("Date of birth cannot be a future date.")

        # ========= INTERESTS =========
        interests_list = form.getlist("interests[]")

        cleaned_interests = list(dict.fromkeys(
            item.strip().lower()
            for item in interests_list
            if item.strip()
        ))

        if len(cleaned_interests) < 1:
            raise ValueError("Please select at least 1 interest.")

        if len(cleaned_interests) > 5:
            raise ValueError("You can select a maximum of 5 interests only.")

        interests = ",".join(cleaned_interests)

        # ========= USERNAME LOGIC =========
        current_username = (user.get("username") or "").strip()
        username_changed = username != current_username

        if username_changed:
            if not user.get("can_edit_username"):
                raise ValueError("You already changed username 3 times in 30 days.")

            if not username:
                raise ValueError("Username is required.")

            existing = user_entity.find_by_username_excluding_user(username, userID)
            if existing:
                raise ValueError("Username already taken.")
        else:
            username = current_username

        # ========= SAVE PROFILE =========
        UserAccount.update_profile(
            userID,
            first_name,
            last_name,
            username,
            phone,
            gender,
            dateOfBirth,
            interests,
            username_changed=username_changed
        )

        message = "Profile updated successfully."

        # ========= EMAIL CHANGE FLOW =========
        current_email = (user.get("email") or "").lower()
        new_email_lower = new_email.lower()

        if new_email_lower and new_email_lower != current_email:
            email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
            if not re.match(email_pattern, new_email_lower):
                raise ValueError("Invalid new email format.")

            existing_email = user_entity.find_by_email_excluding_user(new_email_lower, userID)
            if existing_email:
                raise ValueError("Email already in use.")

            token = secrets.token_urlsafe(32)

            UserAccount.start_email_change_request(userID, new_email_lower, token)

            try:
                send_email_change_verification_email(new_email_lower, token)
                message += " Verification email sent."
            except Exception as e:
                print("Email send failed:", e)
                raise ValueError("Profile updated, but email verification failed.")

        return {"message": message}

    @staticmethod
    def update_profile_photo(userID, filename):
        UserAccount.update_profile_image(userID, filename)

    @staticmethod
    def change_password(userID, current_password, new_password):
        user = UserAccount().get_profile(userID)

        if not user:
            raise ValueError("User not found.")

        stored_pw = user.get("pwd")

        if not stored_pw:
            raise ValueError("Password data is corrupted.")

        # VERIFY CURRENT PASSWORD
        if not check_password_hash(stored_pw, current_password):
            raise ValueError("Current password is incorrect.")

        # PASSWORD POLICY
        if len(new_password) < 8:
            raise ValueError("Password must be at least 8 characters long.")

        # HASH PASSWORD
        new_hash = generate_password_hash(new_password, method='pbkdf2:sha256')

        UserAccount.update_password(userID, new_hash)

    @staticmethod
    def apply_verified_badge(userID):
        user = UserAccount().get_profile(userID)

        if not user:
            raise ValueError("User not found.")

        user_type = (user.get("userType") or "").lower()

        if "premium" not in user_type:
            raise ValueError("Only premium users can apply for verification.")

        if user.get("isVerifiedPublisher") == 1:
            raise ValueError("You are already a verified publisher.")

        if user.get("verifiedBadgeStatus") == "Pending":
            raise ValueError("Your verification application is already pending.")

        # FIXED (correct source)
        eligible_article_count = Article.count_eligible_verified_articles(userID)

        if eligible_article_count < 5:
            raise ValueError(
                "You need at least 5 published articles with AI fact-check scores of 90 or above to apply."
            )

        success = UserAccount.apply_verified_badge(userID)

        if not success:
            raise ValueError("Unable to submit verification request.")

    @staticmethod
    def verify_count(userID):
        return Article.count_eligible_verified_articles(userID)
    
    @staticmethod
    def update_required_fields(userID, gender, dob, interests):
        return UserAccount.update_required_fields(userID, gender, dob, interests)