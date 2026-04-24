from entity.UserAccount import UserAccount
from entity.VerifiedBadgeRule import VerifiedBadgeRule

class VerifiedBadgeAdminCTL:

    @staticmethod
    def get_pending_requests():
        return UserAccount.get_pending_verified_badge_requests()

    @staticmethod
    def approve(userID):
        success = UserAccount.approve_verified_badge(userID)
        if not success:
            raise ValueError("Failed to approve verification.")

    @staticmethod
    def reject(userID):
        success = UserAccount.reject_verified_badge(userID)
        if not success:
            raise ValueError("Failed to reject verification.")
        
    @staticmethod
    def update_verified_badge_rule(required_article_count, minimum_factcheck_score, admin_id):
        return VerifiedBadgeRule.save_verified_badge_rule(required_article_count, minimum_factcheck_score, admin_id)