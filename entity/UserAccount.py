from entity.db_connection import get_db_connection
# import bcrypt

class UserAccount:
    # def login(self, email, pwd):
    #     conn = get_db_connection()
    #     cursor = conn.cursor()

    #     sql = "SELECT * FROM UserAccount WHERE email = %s"
    #     cursor.execute(sql, (email,))
    #     user = cursor.fetchone()

    #     cursor.close()
    #     conn.close()

    #     if not user:
    #         return None

    #     stored_hash = user["pwd"]

    #     if bcrypt.checkpw(pwd.encode("utf-8"), stored_hash.encode("utf-8")):
    #         return user

    #     return None
    def login(self,email,pwd):
        conn = get_db_connection()
        cursor = conn.cursor()

        sql = "SELECT * FROM UserAccount WHERE email=%s AND pwd=%s"
        cursor.execute(sql,(email,pwd))

        user = cursor.fetchone()
        conn.close()

        return user

    @staticmethod
    def get_system_admin():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT userID, username, userType, profileImage
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

    @staticmethod
    def getAllUsers():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT userID, username, userType, created_at, accountStatus
            FROM UserAccount
            ORDER BY userID ASC
        """)
        users = cursor.fetchall()
        conn.close()
        return users
    
    @staticmethod
    def findUsersByCriteria(q, userType, accountStatus):
        conn = get_db_connection()
        cursor = conn.cursor()

        sql = """
            SELECT userID, username, userType, created_at, accountStatus
            FROM UserAccount
            WHERE 1=1
        """
        params = []

        if q:
            sql += " AND (username LIKE %s OR CAST(userID AS CHAR) LIKE %s)"
            keyword = f"%{q}%"
            params.extend([keyword, keyword])

        if userType:
            sql += " AND userType = %s"
            params.append(userType)

        if accountStatus:
            sql += " AND accountStatus = %s"
            params.append(accountStatus)

        sql += " ORDER BY userID ASC"

        cursor.execute(sql, params)
        users = cursor.fetchall()
        conn.close()
        return users
    
    @staticmethod
    def getUserByID(user_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT userID, first_name, last_name, email, gender, dateOfBirth, phone,
                   accountStatus, created_at
            FROM UserAccount
            WHERE userID = %s
        """, (user_id,))
        user = cursor.fetchone()
        conn.close()
        return user

    @staticmethod
    def getUserSubscriptionStatus(user_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT sp.planName
            FROM Subscription s
            JOIN SubscriptionPlan sp ON s.planID = sp.planID
            WHERE s.userID = %s
            AND s.status = 'Active'
            LIMIT 1
        """, (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result["planName"] if result else None

    @staticmethod
    def getUserInterests(user_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ac.categoryName
            FROM UserCategoryInterest uci
            JOIN ArticleCategory ac ON uci.categoryID = ac.categoryID
            WHERE uci.userID = %s
        """, (user_id,))
        rows = cursor.fetchall()
        conn.close()
        return [row["categoryName"] for row in rows]

    @staticmethod
    def updateStatus(userId, action):

        conn = get_db_connection()
        cursor = conn.cursor()

        # check user type
        cursor.execute("""
            SELECT userType
            FROM UserAccount
            WHERE userID = %s
        """, (userId,))

        user = cursor.fetchone()

        if not user:
            conn.close()
            return False

        if user["userType"] == "System Admin":
            conn.close()
            return False   # cannot suspend admin

        if action == "suspend":
            new_status = "Suspended"
        elif action == "unsuspend":
            new_status = "Active"
        else:
            conn.close()
            return False

        cursor.execute("""
            UPDATE UserAccount
            SET accountStatus = %s
            WHERE userID = %s
        """, (new_status, userId))

        conn.commit()

        updated = cursor.rowcount > 0
        conn.close()

        return updated
    
    #####################################

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

    def update_photo(userID, filename):
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE UserAccount SET profile_pic=%s WHERE userID=%s",
            (filename, userID)
        )

        conn.commit()
        conn.close()