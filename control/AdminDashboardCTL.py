import os
import time
from werkzeug.utils import secure_filename
from entity.UserAccount import UserAccount
from entity.Subscription import Subscription
from entity.ReportedArticle import ReportedArticle
from entity.Article import Article
from entity.SystemLog import SystemLog

class AdminDashboardControl:
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
    UPLOAD_FOLDER = os.path.join("static", "images", "profile")
    
    def get_dashboard_data(self):
        admin = UserAccount.get_system_admin()
        total_users = UserAccount.get_total_users()
        active_subscriptions = Subscription.get_active_subscriptions()
        reported_articles = ReportedArticle.get_total_reported_articles()
        total_articles = Article.get_total_articles()
        reported_list = ReportedArticle.get_reported_articles_needing_review()
        recent_logs = SystemLog.get_recent_logs()

        return {
            "admin": admin,
            "stats": {
                "total_users": total_users,
                "active_subscriptions": active_subscriptions,
                "reported_articles": reported_articles,
                "total_articles": total_articles
            },
            "reported_list": reported_list,
            "recent_logs": recent_logs
        }
    
    def allowed_file(self, filename):
        return "." in filename and filename.rsplit(".", 1)[1].lower() in self.ALLOWED_EXTENSIONS

    def upload_profile_picture(self, file):
        admin = UserAccount.get_system_admin()

        if not admin:
            return {"success": False, "message": "System Admin not found."}

        if not file or file.filename == "":
            return {"success": False, "message": "No file selected."}

        if not self.allowed_file(file.filename):
            return {"success": False, "message": "Invalid file type."}

        filename = secure_filename(file.filename)
        unique_filename = f"{int(time.time())}_{filename}"

        os.makedirs(self.UPLOAD_FOLDER, exist_ok=True)
        file_path = os.path.join(self.UPLOAD_FOLDER, unique_filename)
        file.save(file_path)

        UserAccount.update_profile_image(admin["userID"], unique_filename)

        return {"success": True, "message": "Profile picture updated successfully."}
    