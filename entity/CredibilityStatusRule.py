from entity.db_connection import get_db_connection

class CredibilityStatusRule:
    @staticmethod
    def get_active_rule():
        connection = get_db_connection()
        cursor = connection.cursor()

        query = """
            SELECT 
                rule_ID,
                verifiedMinScore,
                highlyCredibleMinScore,
                generallyReliableMinScore,
                mixedMinScore,
                lowConfidenceMinScore,
                misleadingCutoffScore,
                ruleStatus,
                updated_by,
                updated_at
            FROM CredibilityStatusRule
            WHERE ruleStatus = 'active'
            ORDER BY updated_at DESC
            LIMIT 1
        """
        cursor.execute(query)
        rule = cursor.fetchone()

        cursor.close()
        connection.close()

        return rule
    
    @staticmethod
    def update_active_rule(verified, highly_credible, generally_reliable,
                           mixed, low_confidence, misleading_cutoff, updated_by):
        connection = get_db_connection()
        cursor = connection.cursor()

        query = """
            UPDATE CredibilityStatusRule
            SET verifiedMinScore = %s,
                highlyCredibleMinScore = %s,
                generallyReliableMinScore = %s,
                mixedMinScore = %s,
                lowConfidenceMinScore = %s,
                misleadingCutoffScore = %s,
                updated_by = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE ruleStatus = 'active'
        """

        cursor.execute(query, (
            verified,
            highly_credible,
            generally_reliable,
            mixed,
            low_confidence,
            misleading_cutoff,
            updated_by
        ))

        connection.commit()
        success = cursor.rowcount > 0

        cursor.close()
        connection.close()

        return success