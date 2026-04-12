import json
import hashlib
from entity.db_connection import get_db_connection
from datetime import datetime, timedelta, timezone



class AIFeedbackCache:
    @staticmethod
    def build_cache_key(cache_input, version="v1"):
        raw = f"{version}|{cache_input}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def get_cached_result(self, cache_input, cache_type, version="v1", ttl_days=None):
        cache_key = self.build_cache_key(cache_input, version)

        conn = get_db_connection()
        cursor = conn.cursor()

        sql = """
            SELECT response_json, created_at
            FROM AI_Feedback_Cache
            WHERE cache_key = %s AND cache_type = %s
            LIMIT 1
        """
        cursor.execute(sql, (cache_key, cache_type))
        row = cursor.fetchone()

        cursor.close()
        conn.close()

        if not row:
            return None

        created_at = row["created_at"]

        if ttl_days is not None and created_at:
            created_at = created_at.replace(tzinfo=timezone.utc)
            age = datetime.now(timezone.utc) - created_at

            if age > timedelta(days=ttl_days):
                print(f"[AI_CACHE] Cache expired | cache_type={cache_type} | age_days={age.days}", flush=True)
                return None

        return json.loads(row["response_json"])

    def save(self, cache_input, result, cache_type, version="v1"):
        cache_key = self.build_cache_key(cache_input, version)

        conn = get_db_connection()
        cursor = conn.cursor()

        sql = """
            INSERT INTO AI_Feedback_Cache (cache_key, cache_type, cache_input, response_json)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                response_json = VALUES(response_json),
                updated_at = CURRENT_TIMESTAMP
        """

        cursor.execute(sql, (
            cache_key,
            cache_type,
            cache_input,
            json.dumps(result)
        ))

        conn.commit()
        cursor.close()
        conn.close()