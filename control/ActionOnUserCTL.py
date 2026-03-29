from entity.UserAccount import UserAccount
from entity.SystemLog import SystemLog

class ActionOnUserCTL:
    def updateUserStatus(self, userId, action, admin_id):
        if not userId:
            return {"success": False, "message": "Invalid user ID."}
        
        user = UserAccount.getUserByID(userId)

        if not user:
            return {"success": False, "message": "User not found."}

        if user.get("userType") == "system admin":
            return {"success": False, "message": "Cannot delete system admin."}

        success = UserAccount.updateStatus(userId, action)

        if success and action == 'suspend':
            SystemLog.createLog(
                accountID=admin_id,
                action="Suspended User",
                targetID=userId,
                targetType="UserAccount"
            )
        elif success and action == 'unsuspend':
            SystemLog.createLog(
                accountID=admin_id,
                action="Unsuspended User",
                targetID=userId,
                targetType="UserAccount"
            )
        else:
            return {"success": False, "message": "Failed to delete user."}

        return {"success": True}


    def delete_user(self, user_id, admin_id):
        if not user_id:
            return {"success": False, "message": "Invalid user ID."}

        user = UserAccount.getUserByID(user_id)
        if not user:
            return {"success": False, "message": "User not found."}

        if user.get("userType") == "system admin":
            return {"success": False, "message": "Cannot delete system admin."}

        success = UserAccount.delete_user(user_id)

        if success:
            SystemLog.createLog(
                accountID=admin_id,
                action="Deleted User",
                targetID=user_id,
                targetType="UserAccount"
            )
        else:
            return {"success": False, "message": "Failed to delete user."}

        return {"success": True}