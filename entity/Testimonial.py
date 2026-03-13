from entity.db_connection import get_db_connection

class TestimonialEntity:

    @staticmethod
    def getAllTestimonials():
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
        SELECT ua.username, t.rating, t.comment
        FROM Testimonial t
        JOIN UserAccount ua ON t.userID = ua.userID
        ORDER BY t.created_at DESC
        """

        cursor.execute(query)
        testimonials = cursor.fetchall()

        cursor.close()
        conn.close()

        return testimonials