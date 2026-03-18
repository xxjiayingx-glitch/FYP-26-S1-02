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
    def update_profile(userID, first_name, last_name, email, username, phone, gender, dateOfBirth, interests):
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            UPDATE UserAccount
            SET first_name = %s,
                last_name = %s,
                email = %s,
                username = %s,
                phone = %s,
                gender = %s,
                dateOfBirth = %s,
                interests = %s,
                updated_at = NOW()
            WHERE userID = %s
        """
        cursor.execute(query, (
            first_name,
            last_name,
            email,
            username,
            phone,
            gender,
            dateOfBirth,
            interests,
            userID
        ))

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
    def update_photo(userID, filename):
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE UserAccount SET profileImage = %s, updated_at = NOW() WHERE userID = %s",
            (filename, userID)
        )

        conn.commit()
        conn.close()