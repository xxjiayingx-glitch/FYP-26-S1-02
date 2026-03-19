from entity.db_connection import get_db_connection


class UserAccount:
    """Handles user account login, profile, admin, and registration related database actions."""

    # ==============================
    # AUTHENTICATION / LOGIN
    # ==============================
    def login(self, email, pwd):
        """Check if user exists with the given email and password."""
        conn = get_db_connection()
        cursor = conn.cursor()

        sql = "SELECT * FROM UserAccount WHERE email = %s AND pwd = %s"
        cursor.execute(sql, (email, pwd))

        user = cursor.fetchone()
        conn.close()

        return user

    # ==============================
    # PROFILE
    # ==============================
    def get_profile(self, userID):
        """Get full profile details for a specific user."""
        conn = get_db_connection()
        cursor = conn.cursor()

        sql = "SELECT * FROM UserAccount WHERE userID = %s"
        cursor.execute(sql, (userID,))

        user = cursor.fetchone()
        conn.close()

        return user

    @staticmethod
    def update_profile(userID, first_name, last_name, email, username, phone, gender, dateOfBirth, interests):
        """Update user's profile information."""
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
    def update_profile_image(userID, filename):
        """Update user's profile image filename."""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE UserAccount
            SET profileImage = %s,
                updated_at = NOW()
            WHERE userID = %s
        """, (filename, userID))

        conn.commit()
        conn.close()

    # ==============================
    # ADMIN / USER MANAGEMENT
    # ==============================
    @staticmethod
    def get_system_admin():
        """Get one system admin account."""
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
        """Get total number of users."""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) AS total_users FROM UserAccount")
        result = cursor.fetchone()
        conn.close()

        return result["total_users"]

    @staticmethod
    def getAllUsers():
        """Get all users for admin listing."""
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
        """Search/filter users by keyword, user type, and account status."""
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
        """Get selected user details by ID."""
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
    def updateStatus(userId, action):
        """Suspend or unsuspend a user account, except for system admin."""
        conn = get_db_connection()
        cursor = conn.cursor()

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
            return False

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

    # ==============================
    # SUBSCRIPTION / INTERESTS
    # ==============================
    @staticmethod
    def getUserSubscriptionStatus(user_id):
        """Get active subscription plan name for a user."""
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
        """Get category interests for a user."""
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

    def get_category_ids_by_names(self, category_names):
        """Convert category names into category IDs."""
        conn = get_db_connection()
        cursor = conn.cursor()

        format_strings = ",".join(["%s"] * len(category_names))
        cursor.execute(
            f"SELECT categoryID FROM ArticleCategory WHERE categoryName IN ({format_strings})",
            tuple(category_names)
        )
        ids = [row["categoryID"] for row in cursor.fetchall()]
        cursor.close()
        conn.close()

        return ids

    def save_category_interests(self, user_id, category_ids):
        """Save selected category interests for a user."""
        conn = get_db_connection()
        cursor = conn.cursor()

        values = [(user_id, cat_id) for cat_id in category_ids]
        cursor.executemany(
            "INSERT INTO UserCategoryInterest (userID, categoryID) VALUES (%s, %s)",
            values
        )

        conn.commit()
        cursor.close()
        conn.close()

    # ==============================
    # REGISTRATION / VERIFICATION
    # ==============================
    def find_by_email(self, email):
        """Find a user by email."""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM UserAccount WHERE email = %s", (email,))
        result = cursor.fetchone()

        cursor.close()
        conn.close()
        return result

    def find_by_username(self, username):
        """Find a user by username."""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM UserAccount WHERE username = %s", (username,))
        result = cursor.fetchone()

        cursor.close()
        conn.close()
        return result

    def register_user(self, username, email, password, firstName, lastName, phone, token):
        """Register a new user with pending account status and verification token."""
        conn = get_db_connection()
        cursor = conn.cursor()

        insert_query = """
            INSERT INTO UserAccount
            (username, email, pwd, first_name, last_name, phone, userType, accountStatus, verificationToken, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, 'free user', 'pending', %s, NOW())
        """
        cursor.execute(insert_query, (username, email, password, firstName, lastName, phone, token))
        conn.commit()

        new_user_id = cursor.lastrowid

        cursor.close()
        conn.close()
        return new_user_id

    def find_by_token(self, token):
        """Find a user using verification token."""
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM UserAccount WHERE verificationToken = %s", (token,))
        user = cursor.fetchone()

        cursor.close()
        conn.close()
        return user

    def verify_user(self, token):
        """Verify user account and clear verification token."""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE UserAccount
            SET accountStatus = 'active',
                verificationToken = NULL
            WHERE verificationToken = %s
        """, (token,))

        conn.commit()
        cursor.close()
        conn.close()