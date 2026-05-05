from entity.db_connection import get_db_connection

class SystemLog:
    @staticmethod
    def get_recent_logs():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ua.username, sl.action, sl.created_at
            FROM SystemLog sl
            JOIN UserAccount ua ON sl.accountID = ua.userID
            ORDER BY created_at DESC
            LIMIT 6
        """)
        result = cursor.fetchall()
        conn.close()
        return result
    
    @staticmethod
    def getAllLogs(limit=20, offset=0):
        conn = get_db_connection()
        cursor = conn.cursor()

        sql = """
            SELECT sl.logID, sl.accountID, ua.username, sl.action, sl.targetID, sl.targetType, sl.created_at
            FROM SystemLog sl
            JOIN UserAccount ua ON sl.accountID = ua.userID
            WHERE sl.created_at >= NOW() - INTERVAL 30 DAY
            ORDER BY sl.created_at DESC
            LIMIT %s OFFSET %s;
        """
        cursor.execute(sql, (limit, offset))
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

    # @staticmethod
    # def get_logs(q="", search_by="", log_date=""):
    #     conn = get_db_connection()
    #     cursor = conn.cursor()

    #     sql = """
    #         SELECT logID, accountID, action, targetID, targetType, created_at
    #         FROM SystemLog
    #         WHERE 1=1
    #     """
    #     params = []

    #     if q:
    #         if search_by == "logID":
    #             sql += " AND logID = %s"
    #             params.append(int(q))

    #         elif search_by == "accountID":
    #             sql += " AND accountID = %s"
    #             params.append(int(q))

    #         elif search_by == "targetID":
    #             sql += " AND targetID = %s"
    #             params.append(int(q))

    #         elif search_by == "action":
    #             sql += " AND action LIKE %s"
    #             params.append(f"%{q}%")

    #         elif search_by == "targetType":
    #             sql += " AND targetType LIKE %s"
    #             params.append(f"%{q}%")

    #         else:
    #             sql += """
    #                 AND (
    #                     CAST(logID AS CHAR) LIKE %s
    #                     OR CAST(accountID AS CHAR) LIKE %s
    #                     OR CAST(targetID AS CHAR) LIKE %s
    #                     OR action LIKE %s
    #                     OR targetType LIKE %s
    #                 )
    #             """
    #             keyword = f"%{q}%"
    #             params.extend([keyword, keyword, keyword, keyword, keyword])

    #     if log_date:
    #         sql += " AND DATE(created_at) = %s"
    #         params.append(log_date)

    #     sql += " ORDER BY created_at DESC"

    #     cursor.execute(sql, tuple(params))
    #     logs = cursor.fetchall()

    #     cursor.close()
    #     conn.close()
    #     return logs

    @staticmethod
    def get_logs(q="", search_by="", start_date="", end_date=""):

        numeric_fields = ["logID", "accountID", "targetID"]

        if q and search_by in numeric_fields and not q.isdigit():
            return []

        conn = get_db_connection()
        cursor = conn.cursor()

        sql = """
            SELECT sl.logID, sl.accountID, ua.username, sl.action, sl.targetID, sl.targetType, sl.created_at
            FROM SystemLog sl
            JOIN UserAccount ua ON sl.accountID = ua.userID
            WHERE 1=1
        """
        params = []

        if q:
            if search_by == "logID":
                sql += " AND sl.logID = %s"
                params.append(int(q))

            elif search_by == "accountID":
                sql += " AND sl.accountID = %s"
                params.append(int(q))

            elif search_by == "username":
                sql += " AND ua.username LIKE %s"
                params.append(f"%{q}%")

            elif search_by == "targetID":
                sql += " AND sl.targetID = %s"
                params.append(int(q))

            elif search_by == "action":
                sql += " AND sl.action LIKE %s"
                params.append(f"%{q}%")

            elif search_by == "targetType":
                sql += " AND sl.targetType LIKE %s"
                params.append(f"%{q}%")

            else:
                sql += """
                    AND (
                        CAST(sl.logID AS CHAR) LIKE %s
                        OR CAST(sl.accountID AS CHAR) LIKE %s
                        OR ua.username LIKE %s
                        OR CAST(sl.targetID AS CHAR) LIKE %s
                        OR sl.action LIKE %s
                        OR sl.targetType LIKE %s
                    )
                """
                keyword = f"%{q}%"
                params.extend([keyword, keyword, keyword, keyword, keyword, keyword])

        if start_date and end_date:
            sql += " AND DATE(sl.created_at) BETWEEN %s AND %s"
            params.extend([start_date, end_date])

        elif start_date:
            sql += " AND DATE(sl.created_at) >= %s"
            params.append(start_date)

        elif end_date:
            sql += " AND DATE(sl.created_at) <= %s"
            params.append(end_date)

        sql += " ORDER BY sl.created_at DESC"

        cursor.execute(sql, tuple(params))
        logs = cursor.fetchall()

        cursor.close()
        conn.close()

        return logs
    
    # @staticmethod
    # def count_logs(q="", search_by="", start_date="", end_date=""):
    #     conn = get_db_connection()
    #     cursor = conn.cursor()

    #     sql = """
    #         SELECT COUNT(*) AS total
    #         FROM SystemLog
    #         WHERE 1=1
    #     """
    #     params = []

    #     numeric_fields = ["logID", "accountID", "targetID"]

    #     if q and search_by in numeric_fields and not q.isdigit():
    #         return 0

    #     has_filter = bool(q or start_date or end_date)

    #     if q:
    #         if search_by == "logID":
    #             sql += " AND logID = %s"
    #             params.append(int(q))

    #         elif search_by == "accountID":
    #             sql += " AND accountID = %s"
    #             params.append(int(q))

    #         elif search_by == "targetID":
    #             sql += " AND targetID = %s"
    #             params.append(int(q))

    #         elif search_by == "action":
    #             sql += " AND action LIKE %s"
    #             params.append(f"%{q}%")

    #         elif search_by == "targetType":
    #             sql += " AND targetType LIKE %s"
    #             params.append(f"%{q}%")

    #         else:
    #             sql += """
    #                 AND (
    #                     CAST(logID AS CHAR) LIKE %s
    #                     OR CAST(accountID AS CHAR) LIKE %s
    #                     OR CAST(targetID AS CHAR) LIKE %s
    #                     OR action LIKE %s
    #                     OR targetType LIKE %s
    #                 )
    #             """
    #             keyword = f"%{q}%"
    #             params.extend([keyword, keyword, keyword, keyword, keyword])

    #     # 🔥 Date range logic
    #     if start_date and end_date:
    #         sql += " AND DATE(created_at) BETWEEN %s AND %s"
    #         params.extend([start_date, end_date])

    #     elif start_date:
    #         sql += " AND DATE(created_at) >= %s"
    #         params.append(start_date)

    #     elif end_date:
    #         sql += " AND DATE(created_at) <= %s"
    #         params.append(end_date)

    #     # 🔥 Default 30 days ONLY when no filter
    #     if not has_filter:
    #         sql += " AND created_at >= NOW() - INTERVAL 30 DAY"

    #     cursor.execute(sql, tuple(params))
    #     result = cursor.fetchone()
    #     total = result["total"]

    #     cursor.close()
    #     conn.close()
    #     return total

    @staticmethod
    def count_logs(q="", search_by="", start_date="", end_date=""):

        numeric_fields = ["logID", "accountID", "targetID"]

        if q and search_by in numeric_fields and not q.isdigit():
            return 0

        conn = get_db_connection()
        cursor = conn.cursor()

        sql = """
            SELECT COUNT(*) AS total
            FROM SystemLog sl
            JOIN UserAccount ua ON sl.accountID = ua.userID
            WHERE 1=1
        """
        params = []

        if q:
            if search_by == "logID":
                sql += " AND sl.logID = %s"
                params.append(int(q))

            elif search_by == "accountID":
                sql += " AND sl.accountID = %s"
                params.append(int(q))

            elif search_by == "username":
                sql += " AND ua.username LIKE %s"
                params.append(f"%{q}%")

            elif search_by == "targetID":
                sql += " AND sl.targetID = %s"
                params.append(int(q))

            elif search_by == "action":
                sql += " AND sl.action LIKE %s"
                params.append(f"%{q}%")

            elif search_by == "targetType":
                sql += " AND sl.targetType LIKE %s"
                params.append(f"%{q}%")

            else:
                sql += """
                    AND (
                        CAST(sl.logID AS CHAR) LIKE %s
                        OR CAST(sl.accountID AS CHAR) LIKE %s
                        OR ua.username LIKE %s
                        OR CAST(sl.targetID AS CHAR) LIKE %s
                        OR sl.action LIKE %s
                        OR sl.targetType LIKE %s
                    )
                """
                keyword = f"%{q}%"
                params.extend([keyword, keyword, keyword, keyword, keyword, keyword])

        if start_date and end_date:
            sql += " AND DATE(sl.created_at) BETWEEN %s AND %s"
            params.extend([start_date, end_date])

        elif start_date:
            sql += " AND DATE(sl.created_at) >= %s"
            params.append(start_date)

        elif end_date:
            sql += " AND DATE(sl.created_at) <= %s"
            params.append(end_date)

        cursor.execute(sql, tuple(params))
        result = cursor.fetchone()

        cursor.close()
        conn.close()

        return result["total"] if result else 0