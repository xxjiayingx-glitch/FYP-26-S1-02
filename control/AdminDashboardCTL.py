from entity.UserAccount import UserAccount
from entity.Subscription import Subscription
from entity.ReportedArticle import ReportedArticle
from entity.Article import Article
from entity.SystemLog import SystemLog

class AdminDashboardControl:
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
    