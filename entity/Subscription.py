from entity.db_connection import get_db_connection
from datetime import datetime, timedelta

class Subscription:
    @staticmethod
    def get_subscription(userID):
        """
        Get subscription info for a specific user
        """
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            query = "SELECT * FROM Subscription WHERE userID=%s"
            cursor.execute(query, (userID,))
            return cursor.fetchone()
        finally:
            conn.close()

    @staticmethod
    def get_active_subscriptions():
        """
        Count all active subscriptions
        """
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) AS active_subscriptions FROM Subscription WHERE status = 'Active'"
            )
            result = cursor.fetchone()
            return result["active_subscriptions"]
        finally:
            conn.close()

    @staticmethod
    def get_new_subscriptions_last_7_days():
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            SELECT COUNT(*) AS total
            FROM Subscription
            WHERE startDate >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
        """
        cursor.execute(query)
        result = cursor.fetchone()

        cursor.close()
        conn.close()

        return result["total"] if result else 0
    
    @staticmethod
    def get_new_subscriptions_previous_7_days():
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            SELECT COUNT(*) AS total
            FROM Subscription
            WHERE startDate >= DATE_SUB(CURDATE(), INTERVAL 14 DAY)
            AND startDate < DATE_SUB(CURDATE(), INTERVAL 7 DAY)
        """
        cursor.execute(query)
        result = cursor.fetchone()

        cursor.close()
        conn.close()

        return result["total"] if result else 0
    
    @staticmethod
    def get_all_plans(self):

        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
        SELECT planID, planName, planDescription, price, billingCycle
        FROM SubscriptionPlan
        WHERE planStatus = 'Active'
        """

        cursor.execute(query)
        plans = cursor.fetchall()

        cursor.close()
        conn.close()

        return plans

    