# import os
# import time
# from werkzeug.utils import secure_filename
from entity.UserAccount import UserAccount
# from entity.Subscription import Subscription
from entity.ReportedArticle import ReportedArticle
from entity.Article import Article
from entity.SystemLog import SystemLog

class AdminDashboardControl:
    def calculate_change_data(self, current, previous, label="items"):
        if previous is None or previous == 0:
            return {
                "percentage": None,
                "difference": None,
                "direction": None,
                "text": "N/A"
            }

        change = ((current - previous) / previous) * 100
        difference = current - previous

        if difference > 0:
            direction = "up"
            text = f"+{round(change, 1)}% (↑ +{difference} {label})"
        elif difference < 0:
            direction = "down"
            text = f"{round(change, 1)}% (↓ {difference} {label})"
        else:
            direction = "same"
            text = f"0.0% (→ 0 {label})"

        return {
            "percentage": round(change, 1),
            "difference": difference,
            "direction": direction,
            "text": text
        }
     
    def get_dashboard_data(self):
        admin = UserAccount.get_system_admin()
        total_users = UserAccount.get_total_users()
        active_subscriptions = UserAccount.count_premium()
        reported_articles = ReportedArticle.get_total_reported_articles()
        total_articles = Article.get_total_articles()

        prev_total_users = UserAccount.get_total_users_before_days(7)
        previous_active_subscriptions = UserAccount.count_premium_before_days(7)
        prev_reported_articles = ReportedArticle.get_total_reports_before_days(7)
        current_articles_7_days = Article.get_articles_last_7_days()
        previous_articles_7_days = Article.get_articles_previous_7_days()

        application_list = UserAccount.get_applications_needing_review()
        recent_logs = SystemLog.get_recent_logs()

        return {
            "admin": admin,
            "stats": {
                "total_users": total_users,
                "users_change": self.calculate_change_data(total_users, prev_total_users),

                "active_subscriptions": active_subscriptions,
                "subscriptions_change": self.calculate_change_data(
                    active_subscriptions, previous_active_subscriptions
                ),

                "reported_articles": reported_articles,
                "reported_change": self.calculate_change_data(
                    reported_articles, prev_reported_articles
                ),

                "total_articles": total_articles,
                "articles_change": self.calculate_change_data(
                    current_articles_7_days, previous_articles_7_days
                )
            },
            "application_list": application_list,
            "recent_logs": recent_logs
        }
    