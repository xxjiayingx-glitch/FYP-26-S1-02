from entity.UserAccount import UserAccount
from entity.Article import Article

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

        cleaned_interests = []
        for item in interests_list:
            item = item.strip()
            if item and item not in cleaned_interests:
                cleaned_interests.append(item)

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

        if user["pwd"] != current_password:
            raise ValueError("Current password is incorrect.")

        UserAccount.update_password(userID, new_password)

    @staticmethod
    def apply_verified_badge(userID):
        user = UserAccount().get_profile(userID)

        if not user:
            raise ValueError("User not found.")

        if "premium" not in user["userType"].lower():
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