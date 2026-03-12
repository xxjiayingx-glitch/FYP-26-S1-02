from entity.db_connection import get_db_connection

class Subscription:
    def get_subscription(userID):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM Subscription WHERE userID=%s"
    cursor.execute(query,(userID,))
    return cursor.fetchone()
    
    @staticmethod
    def get_active_subscriptions():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) AS active_subscriptions FROM Subscription WHERE status = 'Active'")
        result = cursor.fetchone()
        conn.close()
        return result["active_subscriptions"]
