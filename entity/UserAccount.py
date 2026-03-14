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


    @staticmethod
    def update_profile(userID, firstName, lastName, email, phone, age, gender):
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
        UPDATE user
        SET firstName=%s,
            lastName=%s,
            email=%s,
            phone=%s,
            age=%s,
            gender=%s
        WHERE userID=%s
        """
        cursor.execute(query, (firstName, lastName, email, phone, age, gender, userID))
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

    @staticmethod
    def update_profile_image(user_id, filename):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE UserAccount
            SET profileImage = %s
            WHERE userID = %s
        """, (filename, user_id))
        conn.commit()
        conn.close()

    def update_photo(userID, filename):
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE UserAccount SET profile_pic=%s WHERE userID=%s",
            (filename, userID)
        )

        conn.commit()
        conn.close()