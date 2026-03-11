from entity.database import connect_db

def get_subscription(userID):

    conn = connect_db()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM Subscription WHERE userID=%s"

    cursor.execute(query,(userID,))
    return cursor.fetchone()