from entity.UserAccount import UserAccount

class UpdateProfileCTL:

    @staticmethod
    def update_profile(userID, form):

        firstName = form.get("firstName")
        lastName = form.get("lastName")
        email = form.get("email")
        phone = form.get("phone")
        age = form.get("age")
        gender = form.get("gender")

        UserAccount.update_profile(
            userID,
            firstName,
            lastName,
            email,
            phone,
            age,
            gender
        )

    @staticmethod
    def update_profile_photo(userID, filename):
        UserAccount.update_photo(userID, filename)