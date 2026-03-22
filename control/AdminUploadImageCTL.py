import os
import time
from werkzeug.utils import secure_filename
from entity.UserAccount import UserAccount

class AdminUploadImageCTL:
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
    UPLOAD_FOLDER = os.path.join("static", "images", "profile")

    def allowed_file(self, filename):
        return "." in filename and filename.rsplit(".", 1)[1].lower() in self.ALLOWED_EXTENSIONS

    def upload_profile_picture(self, file, user_id):
        if not file or file.filename == "":
            return {"success": False, "message": "No file selected."}

        if not self.allowed_file(file.filename):
            return {"success": False, "message": "Invalid file type."}

        filename = secure_filename(file.filename)
        unique_filename = f"{int(time.time())}_{filename}"

        os.makedirs(self.UPLOAD_FOLDER, exist_ok=True)
        file_path = os.path.join(self.UPLOAD_FOLDER, unique_filename)
        file.save(file_path)

        UserAccount.update_profile_image(user_id, unique_filename)

        return {
            "success": True,
            "message": "Profile picture updated successfully.",
            "filename": unique_filename
        }