# entity/LLMCache.py
import json
import hashlib
from entity.db_connection import get_db_connection

class LLMCache:
    @staticmethod
    def build_cache_key(sentence, version="v1"):
        raw = f"{version}|{sentence.strip().lower()}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def get_cached_result(self, sentence, version="v1"):
        cache_key = self.build_cache_key(sentence, version)

        conn = get_db_connection()
        cursor = conn.cursor()

        sql = """
            SELECT response_json
            FROM LLM_Cache
            WHERE cache_key = %s
            LIMIT 1
        """
        cursor.execute(sql, (cache_key,))
        row = cursor.fetchone()

        cursor.close()
        conn.close()

        if not row:
            return None

        return json.loads(row["response_json"])

    def save(self, sentence, result, version="v1"):
        cache_key = self.build_cache_key(sentence, version)

        conn = get_db_connection()
        cursor = conn.cursor()

        sql = """
            INSERT INTO LLM_Cache (cache_key, sentence_text, response_json)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE
                sentence_text = VALUES(sentence_text),
                response_json = VALUES(response_json),
                updated_at = CURRENT_TIMESTAMP
        """
        cursor.execute(sql, (
            cache_key,
            sentence,
            json.dumps(result)
        ))

        conn.commit()
        cursor.close()
        conn.close()