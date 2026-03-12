from entity.db_connection import get_db_connection

class UserAccount:
    @staticmethod
    def get_system_admin():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT userID, username, userType
            FROM UserAccount
            WHERE userType = 'System Admin'
            LIMIT 1
        """)
        admin = cursor.fetchone()
        conn.close()
        return admin
    
    @staticmethod
    def get_total_users():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) AS total_users FROM UserAccount")
        result = cursor.fetchone()
        conn.close()
        return result["total_users"]