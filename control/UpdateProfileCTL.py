import hashlib, binascii, os

from entity.UserAccount import UserAccount
from entity.Article import Article
from werkzeug.security import check_password_hash, generate_password_hash

class UpdateProfileCTL:

    @staticmethod
    def update_profile(userID, form):
        first_name = form.get("firstName")
        last_name = form.get("lastName")
        email = form.get("email")
        username = form.get("username")
        phone = form.get("phone")
        gender = form.get("gender")
        dateOfBirth = form.get("dateOfBirth")

        interests_list = form.getlist("interests[]")

        cleaned_interests = list(dict.fromkeys(
            item.strip().lower()
            for item in interests_list
            if item.strip()
        ))

        if len(cleaned_interests) > 5:
            raise ValueError("You can select a maximum of 5 interests only.")

        interests = ",".join(cleaned_interests) if cleaned_interests else None

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

        try:
            prefix, salt_b64, hash_hex = stored_pw.split('$')
            _, N, r, p = prefix.split(':')
            N, r, p = int(N), int(r), int(p)
            salt = binascii.a2b_base64(salt_b64)
            hash_bytes = bytes.fromhex(hash_hex)
        except Exception as e:
            raise ValueError(f"Stored password format is invalid: {e}")

        # Verify current password by hashing and comparing
        test_hash = hashlib.scrypt(
            current_password.encode(),
            salt=salt,
            n=N, r=r, p=p,
            dklen=len(hash_bytes)
        )
        if test_hash != hash_bytes:
            raise ValueError("Current password is incorrect.")

        if len(new_password) < 6:
            raise ValueError("Password must be at least 6 characters long.")

        # Generate new hash for new password with new salt
        new_salt = os.urandom(16)
        new_hash_bytes = hashlib.scrypt(
            new_password.encode(),
            salt=new_salt,
            n=N, r=r, p=p,
            dklen=64
        )
        new_salt_b64 = binascii.b2a_base64(new_salt).decode().strip()
        new_hash_hex = new_hash_bytes.hex()

        stored_new = f"scrypt:{N}:{r}:{p}${new_salt_b64}${new_hash_hex}"
        UserAccount.update_password(userID, stored_new)

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

        eligible_article_count = UserAccount.count_eligible_verified_articles(userID)

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