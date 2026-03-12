from entity.db_connection import get_db_connection

class UserAccount:
    def login(self,email,pwd):

        conn = get_db_connection()
        cursor = conn.cursor()

        sql = "SELECT * FROM UserAccount WHERE email=%s AND pwd=%s"
        cursor.execute(sql,(email,pwd))

        user = cursor.fetchone()
        conn.close()

        return user


    def get_profile(self,userID):

        conn = get_db_connection()
        cursor = conn.cursor()

        sql = "SELECT * FROM UserAccount WHERE userID=%s"
        cursor.execute(sql,(userID,))

        user = cursor.fetchone()
        conn.close()

        return user


    def update_profile(self,userID,first,last,phone):

        conn = get_db_connection()
        cursor = conn.cursor()

        sql = """
        UPDATE UserAccount
        SET first_name=%s,last_name=%s,phone=%s
        WHERE userID=%s
        """

        cursor.execute(sql,(first,last,phone,userID))
        conn.commit()
        conn.close()
        
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
