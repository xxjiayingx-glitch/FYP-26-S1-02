from entity.db_connection import get_db_connection

class ProductFeature:

    def get_features(self, offset=0, limit=4):

        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
        SELECT featureID, featureName, featureDescription, featureImage
        FROM ProductFeature
        WHERE featureStatus = 'Active'
        ORDER BY created_at DESC
        LIMIT %s OFFSET %s
        """

        cursor.execute(query, (limit, offset))
        features = cursor.fetchall()

        conn.close()

        return features