from entity.db_connection import get_db_connection

class SystemLog:
    @staticmethod
    def get_recent_logs():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT action, created_at
            FROM SystemLog
            ORDER BY created_at DESC
            LIMIT 6
        """)
        result = cursor.fetchall()
        conn.close()
        return result
    
    @staticmethod
    def getAllLogs():
        conn = get_db_connection()
        cursor = conn.cursor()

        sql = """
            SELECT logID, accountID, action, targetID, targetType, created_at
            FROM SystemLog
            ORDER BY created_at DESC
        """
        cursor.execute(sql)
        logs = cursor.fetchall()

        cursor.close()
        conn.close()

        return logs