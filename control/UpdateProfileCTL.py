from entity.UserAccount import UserAccount

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

        interests_list = form.getlist("interests")
        interests = ",".join(interests_list)

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