from entity.db_connection import get_db_connection

class VerifiedBadgeRule:

    @staticmethod
    def get_verified_badge_rule():
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            SELECT ruleID, required_article_count, minimum_factcheck_score
            FROM VerifiedBadgeRule
            WHERE ruleStatus = 'active'
            ORDER BY ruleID DESC
            LIMIT 1
        """
        cursor.execute(query)
        result = cursor.fetchone()

        cursor.close()
        conn.close()

        return result
    
    # @staticmethod
    # def update_verified_badge_rule(required_article_count, minimum_factcheck_score, updated_by):
    #     conn = get_db_connection()
    #     cursor = conn.cursor()

    #     query = """
    #         UPDATE VerifiedBadgeRule
    #         SET required_article_count = %s,
    #             minimum_factcheck_score = %s,
    #             updated_by = %s,
    #             updated_at = NOW()
    #         WHERE ruleStatus = 'active'
    #     """
    #     cursor.execute(query, (required_article_count, minimum_factcheck_score, updated_by))
    #     conn.commit()

    #     cursor.close()
    #     conn.close()

    #     return True

    @staticmethod
    def save_verified_badge_rule(required_article_count, minimum_factcheck_score, updated_by):
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if active rule already exists
        check_query = """
            SELECT ruleID
            FROM VerifiedBadgeRule
            WHERE ruleStatus = 'active'
            LIMIT 1
        """
        cursor.execute(check_query)
        existing_rule = cursor.fetchone()

        if existing_rule:
            query = """
                UPDATE VerifiedBadgeRule
                SET required_article_count = %s,
                    minimum_factcheck_score = %s,
                    updated_by = %s,
                    updated_at = NOW()
                WHERE ruleID = %s
            """
            cursor.execute(
                query,
                (
                    required_article_count,
                    minimum_factcheck_score,
                    updated_by,
                    existing_rule["ruleID"]
                )
            )
        else:
            query = """
                INSERT INTO VerifiedBadgeRule
                (required_article_count, minimum_factcheck_score, ruleStatus, updated_by, updated_at)
                VALUES (%s, %s, 'active', %s, NOW())
            """
            cursor.execute(
                query,
                (required_article_count, minimum_factcheck_score, updated_by)
            )

        conn.commit()
        affected = cursor.rowcount > 0

        cursor.close()
        conn.close()

        return affected