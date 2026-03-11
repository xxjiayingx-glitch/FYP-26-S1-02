from entity.database import connect_db

def get_user(username, password):

    conn = connect_db()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM UserAccount WHERE username=%s AND pwd=%s"
    cursor.execute(query,(username,password))

    return cursor.fetchone()


def update_profile(userID, phone, email):

    conn = connect_db()
    cursor = conn.cursor()

    query = """
    UPDATE UserAccount
    SET phone=%s,email=%s
    WHERE userID=%s
    """

    cursor.execute(query,(phone,email,userID))
    conn.commit()