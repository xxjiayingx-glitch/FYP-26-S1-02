import mysql.connector
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="news_system"
    )
class TestimonialEntity:
    @staticmethod
    def getAllTestimonials():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.username, t.rating, t.comment
            FROM UserAccount u
            JOIN Testimonial t ON u.userID = t.userID
            ORDER BY t.created_at DESC
        """)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        testimonials = []
        for row in rows:
            testimonials.append({
                "username": row[0],
                "rating": row[1],
                "comment": row[2],
                "stars": "★" * row[1] + "☆" * (5 - row[1])  # Add star display
            })
        return testimonials
    
    @staticmethod
    def insertTestimonial(user_id, rating, comment, semantic_score, combined_score):
        conn = get_connection()
        cursor = conn.cursor()
        query = """
            INSERT INTO Testimonial (userID, rating, comment, semanticScore, combinedScore, created_at)
            VALUES (%s, %s, %s, %s, %s, NOW())
        """
        cursor.execute(query, (user_id, rating, comment, semantic_score, combined_score))
        conn.commit()
        cursor.close()
        conn.close()
