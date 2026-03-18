from entity.db_connection import get_db_connection
from datetime import datetime

class AutoPublishRule:
    @staticmethod
    def getCurrentRule():
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT rule_ID, minCredibilityScore, updated_at, ruleStatus, updated_by
            FROM AutoPublishRule
            ORDER BY rule_ID DESC
            LIMIT 1
        """)
        rule = cursor.fetchone()

        conn.close()
        return rule

    @staticmethod
    def updateAutoPublishRules(minCredibilityScore, updated_by):
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT rule_ID
            FROM AutoPublishRule
            ORDER BY rule_ID DESC
            LIMIT 1
        """)
        existing_rule = cursor.fetchone()

        if existing_rule:
            cursor.execute("""
                UPDATE AutoPublishRule
                SET minCredibilityScore = %s,
                    updated_at = %s,
                    ruleStatus = %s,
                    updated_by = %s
                WHERE rule_ID = %s
            """, (
                minCredibilityScore,
                datetime.now(),
                "Active",
                updated_by,
                existing_rule["rule_ID"]
            ))
        else:
            cursor.execute("""
                INSERT INTO AutoPublishRule (
                    minCredibilityScore,
                    updated_at,
                    ruleStatus,
                    updated_by
                )
                VALUES (%s, %s, %s, %s)
            """, (
                minCredibilityScore,
                datetime.now(),
                "Active",
                updated_by
            ))

        conn.commit()
        updated = cursor.rowcount > 0
        conn.close()
        return updated