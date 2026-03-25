from entity.UserAccount import UserAccount
from entity.Article import Article
from werkzeug.security import check_password_hash, generate_password_hash

class UpdateProfileCTL:

    @staticmethod
    def update_profile(userID, form):
        user = UserAccount().get_profile(userID)

        if not user:
            raise ValueError("User not found.")

        first_name = form.get("firstName")
        last_name = form.get("lastName")
        email = form.get("email")
        username = form.get("username")
        phone = form.get("phone")
        gender = form.get("gender")
        dateOfBirth = form.get("dateOfBirth")

        # REQUIRED FIELD VALIDATION
        if not first_name or not first_name.strip():
            raise ValueError("First name is required.")
        if not last_name or not last_name.strip():
            raise ValueError("Last name is required.")
        if not phone or not phone.strip():
            raise ValueError("Phone number is required.")
        if not gender or gender not in ["Male", "Female"]:
            raise ValueError("Please select a gender.")
        if not dateOfBirth or not dateOfBirth.strip():
            raise ValueError("Date of birth is required.")

        # ENFORCE BACKEND RESTRICTIONS (IMPORTANT)
        if not user.get("can_edit_email"):
            email = user.get("email")

        if not user.get("can_edit_username"):
            username = user.get("username")

        # VALIDATE GENDER
        if gender not in ["Male", "Female"]:
            gender = None

        # INTERESTS HANDLING
        interests_list = form.getlist("interests[]")

        cleaned_interests = list(dict.fromkeys(
            item.strip().lower()
            for item in interests_list
            if item.strip()
        ))

        # MIN + MAX VALIDATION
        if len(cleaned_interests) < 1:
            raise ValueError("Please select at least 1 interest.")

        if len(cleaned_interests) > 5:
            raise ValueError("You can select a maximum of 5 interests only.")

        interests = ",".join(cleaned_interests)

        UserAccount.update_profile(
            userID,
            first_name,
            last_name,
            email,
            username,
            phone,
            gender,
            dateOfBirth,
            interests
        )

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