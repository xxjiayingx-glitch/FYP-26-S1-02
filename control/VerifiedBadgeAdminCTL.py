from entity.UserAccount import UserAccount

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