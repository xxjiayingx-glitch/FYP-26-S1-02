from entity.db_connection import get_db_connection
from werkzeug.security import check_password_hash
from datetime import datetime, timedelta

class UserAccount:
    """Handles user account login, profile, admin, and registration related database actions."""

    # ==============================
    # AUTHENTICATION / LOGIN
    # ==============================
    def login(self, email, pwd):
        conn = get_db_connection()
        cursor = conn.cursor()

        sql = "SELECT * FROM UserAccount WHERE email = %s"
        cursor.execute(sql, (email,))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if not user:
            print("No user with that email")
            return None

        print("Stored hash:", user["pwd"])
        print("Entered password:", pwd)

        if check_password_hash(user["pwd"], pwd):
            print("Password matched")
            if user.get("accountStatus") == "pending":
                print("Account not verified")
                return "pending_verification"

            return user

        print("Password did not match")
        return None

    # ==============================
    # PROFILE
    # ==============================
    def get_profile(self, userID):
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM UserAccount WHERE userID = %s", (userID,))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if not user:
            return None

        now = datetime.now()

        change_count = user.get("usernameChangeCount") or 0
        window_start = user.get("usernameChangeWindowStart")

        can_edit_username = True
        remaining_changes = 3
        wait_until = None

        if window_start:
            if now - window_start < timedelta(days=30):
                remaining_changes = max(0, 3 - change_count)
                can_edit_username = change_count < 3

                if not can_edit_username:
                    wait_until = window_start + timedelta(days=30)
            else:
                remaining_changes = 3
                can_edit_username = True

        user["can_edit_username"] = can_edit_username
        user["remaining_username_changes"] = remaining_changes
        user["username_wait_until"] = wait_until

        user["can_edit_email"] = False

        return user

    @staticmethod
    def update_profile(userID, first_name, last_name, username, phone, gender, dateOfBirth, interests, username_changed=False):
        conn = get_db_connection()
        cursor = conn.cursor()

        if username_changed:
            query = """
                UPDATE UserAccount
                SET first_name = %s,
                    last_name = %s,
                    username = %s,
                    phone = %s,
                    gender = %s,
                    dateOfBirth = %s,
                    interests = %s,
                    usernameChangeWindowStart = CASE
                        WHEN usernameChangeWindowStart IS NULL
                            OR usernameChangeWindowStart < DATE_SUB(NOW(), INTERVAL 30 DAY)
                        THEN NOW()
                        ELSE usernameChangeWindowStart
                    END,
                    usernameChangeCount = CASE
                        WHEN usernameChangeWindowStart IS NULL
                            OR usernameChangeWindowStart < DATE_SUB(NOW(), INTERVAL 30 DAY)
                        THEN 1
                        ELSE usernameChangeCount + 1
                    END,
                    lastUsernameChangedAt = NOW(),
                    updated_at = NOW()
                WHERE userID = %s
            """
            cursor.execute(query, (
                first_name,
                last_name,
                username,
                phone,
                gender,
                dateOfBirth,
                interests,
                userID
            ))
        else:
            query = """
                UPDATE UserAccount
                SET first_name = %s,
                    last_name = %s,
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
                phone,
                gender,
                dateOfBirth,
                interests,
                userID
            ))

        conn.commit()
        cursor.close()
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

    @staticmethod
    def update_password(userID, new_password):
        """Update user's password."""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE UserAccount
            SET pwd = %s,
                updated_at = NOW()
            WHERE userID = %s
        """, (new_password, userID))

        conn.commit()
        conn.close()
    
    def find_by_email_excluding_user(self, email, userID):
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM UserAccount WHERE email = %s AND userID != %s",
            (email, userID)
        )
        result = cursor.fetchone()

        cursor.close()
        conn.close()
        return result


    def find_by_username_excluding_user(self, username, userID):
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM UserAccount WHERE username = %s AND userID != %s",
            (username, userID)
        )
        result = cursor.fetchone()

        cursor.close()
        conn.close()
        return result


    @staticmethod
    def start_email_change_request(userID, pending_email, token):
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE UserAccount
            SET pendingEmail = %s,
                verificationToken = %s,
                emailChangeRequestedAt = NOW(),
                updated_at = NOW()
            WHERE userID = %s
        """, (pending_email, token, userID))

    @staticmethod
    def verify_pending_email_change(token):
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                UPDATE UserAccount
                SET email = pendingEmail,
                    pendingEmail = NULL,
                    verificationToken = NULL,
                    emailChangeRequestedAt = NULL,
                    isVerified = 1,
                    updated_at = NOW()
                WHERE verificationToken = %s
                AND pendingEmail IS NOT NULL
            """, (token,))

            success = cursor.rowcount > 0
            conn.commit()
            return success
        except:
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()

    #------------------------#
    # Force complete profile #
    #------------------------#
    @staticmethod
    def update_required_fields(userID, gender, dob, interests):
        conn = get_db_connection()
        cursor = conn.cursor()

        interests_str = ",".join(interests)

        cursor.execute("""
            UPDATE UserAccount
            SET gender = %s,
                dateOfBirth = %s,
                interests = %s,
                profileCompleted = 1
            WHERE userID = %s
        """, (gender, dob, interests_str, userID))

        conn.commit()
        cursor.close()
        conn.close()



    #----------------------------#
    # Verified Badge For Premium #
    #----------------------------#
    @staticmethod
    def apply_verified_badge(userID):
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE UserAccount
            SET verifiedBadgeStatus = 'Pending',
                updated_at = NOW()
            WHERE userID = %s
            AND LOWER(userType) LIKE %s
            AND (verifiedBadgeStatus IS NULL OR verifiedBadgeStatus = 'Rejected')
        """, (userID, "%premium%"))

        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success    
    
    @staticmethod
    def approve_verified_badge(userID):
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE UserAccount
            SET isVerifiedPublisher = 1,
                verifiedBadgeStatus = 'Approved',
                updated_at = NOW()
            WHERE userID = %s
        """, (userID,))

        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success

    @staticmethod
    def reject_verified_badge(userID):
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE UserAccount
            SET isVerifiedPublisher = 0,
                verifiedBadgeStatus = 'Rejected',
                updated_at = NOW()
            WHERE userID = %s
        """, (userID,))

        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success

    @staticmethod
    def get_pending_verified_badge_requests():
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT 
                u.userID,
                u.username,
                u.email,
                COUNT(CASE 
                    WHEN a.articleStatus = 'Published' THEN 1 
                END) AS total_published_articles,
                COUNT(CASE 
                    WHEN a.articleStatus = 'Published' AND a.credibilityScore >= 90 THEN 1 
                END) AS qualifying_articles
            FROM UserAccount u
            LEFT JOIN Article a ON u.userID = a.created_by
            WHERE u.verifiedBadgeStatus = 'Pending'
            GROUP BY u.userID, u.username, u.email
            ORDER BY u.userID ASC
        """)

        requests = cursor.fetchall()
        conn.close()
        return requests
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
    
    @staticmethod
    def update_verified_status(user_id, is_verified):
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE UserAccount
            SET isVerified = %s
            WHERE userID = %s
        """, (is_verified, user_id))

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

    def register_user(self, username, email, password, firstName, lastName, phone, token, profileCompleted = 0):
        """Register a new user with pending account status and verification token."""
        conn = get_db_connection()
        cursor = conn.cursor()

        insert_query = """
            INSERT INTO UserAccount
            (username, email, pwd, first_name, last_name, phone, userType, accountStatus, verificationToken, created_at, profileCompleted)
            VALUES (%s, %s, %s, %s, %s, %s, 'free', 'pending', %s, NOW())
        """
        cursor.execute(insert_query, (username, email, password, firstName, lastName, phone, token, profileCompleted))
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

        success = cursor.rowcount > 0  # True if a matching token was found and updated

        conn.commit()
        cursor.close()
        conn.close()

        return success