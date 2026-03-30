from entity.SystemLog import SystemLog

class SystemLogCTL:
    @staticmethod
    def logAction(accountID, action, targetID=None, targetType=None):
        SystemLog.createLog(accountID, action, targetID, targetType)

    # @staticmethod
    # def viewLogs():
    #     return SystemLog.getAllLogs()
    
    # @staticmethod
    # def get_logs(q="", search_by="", log_date=""):
    #     return SystemLog.get_logs(q=q, search_by=search_by, log_date=log_date)

    @staticmethod
    def viewLogs(page=1):
        limit = 20
        offset = (page - 1) * limit

        return SystemLog.getAllLogs(limit, offset)
    
    @staticmethod
    def get_logs(q="", search_by="", start_date="", end_date=""):
        return SystemLog.get_logs(
            q=q,
            search_by=search_by,
            start_date=start_date,
            end_date=end_date
        )
    
    @staticmethod
    def count_logs(q="", search_by="", start_date="", end_date=""):
        return SystemLog.count_logs(
            q=q,
            search_by=search_by,
            start_date=start_date,
            end_date=end_date
        )