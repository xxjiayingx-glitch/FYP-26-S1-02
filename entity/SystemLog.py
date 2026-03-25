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
    
    @staticmethod
    def createLog(accountID, action, targetID=None, targetType=None):
        conn = get_db_connection()
        cursor = conn.cursor()

        sql = """
            INSERT INTO SystemLog (accountID, action, targetID, targetType, created_at)
            VALUES (%s, %s, %s, %s, NOW())
        """
        cursor.execute(sql, (accountID, action, targetID, targetType))
        conn.commit()

        cursor.close()
        conn.close()

    @staticmethod
    def get_logs(q="", search_by="", log_date=""):
        conn = get_db_connection()
        cursor = conn.cursor()

        sql = """
            SELECT logID, accountID, action, targetID, targetType, created_at
            FROM SystemLog
            WHERE 1=1
        """
        params = []

        if q:
            if search_by == "logID":
                sql += " AND logID = %s"
                params.append(int(q))

            elif search_by == "accountID":
                sql += " AND accountID = %s"
                params.append(int(q))

            elif search_by == "targetID":
                sql += " AND targetID = %s"
                params.append(int(q))

            elif search_by == "action":
                sql += " AND action LIKE %s"
                params.append(f"%{q}%")

            elif search_by == "targetType":
                sql += " AND targetType LIKE %s"
                params.append(f"%{q}%")

            else:
                sql += """
                    AND (
                        CAST(logID AS CHAR) LIKE %s
                        OR CAST(accountID AS CHAR) LIKE %s
                        OR CAST(targetID AS CHAR) LIKE %s
                        OR action LIKE %s
                        OR targetType LIKE %s
                    )
                """
                keyword = f"%{q}%"
                params.extend([keyword, keyword, keyword, keyword, keyword])

        if log_date:
            sql += " AND DATE(created_at) = %s"
            params.append(log_date)

        sql += " ORDER BY created_at DESC"

        cursor.execute(sql, tuple(params))
        logs = cursor.fetchall()

        cursor.close()
        conn.close()
        return logs