from entity.db_connection import get_db_connection

class CompanyProfileController:

    def getCompanyProfile(self):

        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
        SELECT companyName, description, mission, vision, contactEmail, contactPhone
        FROM CompanyProfile
        ORDER BY updated_at DESC
        LIMIT 1
        """

        cursor.execute(query)
        profile = cursor.fetchone()

        cursor.close()
        conn.close()

        return profile