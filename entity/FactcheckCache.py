from entity.db_connection import get_db_connection
import json

class FactcheckCache:

    def get_cached_result(self, query):
        conn = get_db_connection()
        cursor = conn.cursor()

        sql = """
        SELECT * FROM Factcheck_Cache
        WHERE query = %s
        AND created_at >= NOW() - INTERVAL 24 HOUR
        ORDER BY created_at DESC
        LIMIT 1
        """
        cursor.execute(sql, (query,))
        result = cursor.fetchone()

        cursor.close()
        conn.close()

        if result:
            return json.loads(result["response_json"])

        return None

    def save(self, query, data):
        conn = get_db_connection()
        cursor = conn.cursor()

        sql = """
        INSERT INTO Factcheck_Cache (query, response_json)
        VALUES (%s, %s)
        """
        cursor.execute(sql, (query, json.dumps(data)))
        conn.commit()

        cursor.close()
        conn.close()