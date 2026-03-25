from entity.SystemLog import SystemLog

class SystemLogCTL:
    @staticmethod
    def logAction(accountID, action, targetID=None, targetType=None):
        SystemLog.createLog(accountID, action, targetID, targetType)

    @staticmethod
    def viewLogs():
        return SystemLog.getAllLogs()
    
    @staticmethod
    def get_logs(q="", search_by="", log_date=""):
        return SystemLog.get_logs(q=q, search_by=search_by, log_date=log_date)