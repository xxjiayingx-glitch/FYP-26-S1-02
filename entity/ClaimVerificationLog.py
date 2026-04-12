from entity.db_connection import get_db_connection

class ClaimVerificationLog:

    def save_log(self, claim_text, route, factcheck_provider, stats_source, llm_provider, score, status):
        conn = get_db_connection()
        cursor = conn.cursor()

        sql = """
        INSERT INTO Claim_Verification_Log
        (claim_text, route_used, llm_provider, factcheck_provider, stats_source, final_score, final_status)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        cursor.execute(sql, (
            claim_text,
            route,
            llm_provider,
            factcheck_provider,
            stats_source,
            score,
            status
        ))

        conn.commit()
        cursor.close()
        conn.close()