from entity.db_connection import get_db_connection

class RegisterController:

    def register(self, username, email, password, retypePassword):

        # Check password length
        if len(password) < 10:
            return {"success": False, "message": "Password must be at least 10 characters"}

        # Check password match
        if password != retypePassword:
            return {"success": False, "message": "Passwords do not match"}

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if email already exists
        check_query = "SELECT * FROM UserAccount WHERE email = %s"
        cursor.execute(check_query, (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            cursor.close()
            conn.close()
            return {"success": False, "message": "Email already registered"}

        # Insert new user
        insert_query = """
        INSERT INTO UserAccount (username, email, pwd, userType, accountStatus)
        VALUES (%s, %s, %s, 'free', 'active')
        """

        cursor.execute(insert_query, (username, email, password))
        conn.commit()

        cursor.close()
        conn.close()

        return {"success": True}
