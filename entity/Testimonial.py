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
            SELECT u.username, t.rating, t.comment, t.created_at
            FROM UserAccount u
            JOIN Testimonial t ON u.userID = t.userID
            WHERE t.created_at >= DATE_SUB(NOW(), INTERVAL 14 DAY)
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
                "created_at": row[3],
                "stars": "★" * row[1] + "☆" * (5 - row[1])
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

    def getHomeTestimonial(self, offset=0, limit=3):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT t.testimonial_ID, u.username, t.rating, t.comment, t.created_at
            FROM UserAccount u
            JOIN Testimonial t ON u.userID = t.userID
            WHERE t.created_at >= DATE_SUB(NOW(), INTERVAL 14 DAY)
            ORDER BY t.created_at DESC
            LIMIT %s OFFSET %s
        """, (limit, offset))

        rows = cursor.fetchall()

        cursor.close()
        conn.close()

        results = []

        for row in rows:
            results.append({
                "testimonial_ID": row[0],
                "username": row[1],
                "rating": row[2],
                "comment": row[3],
                "created_at": row[4],
                "stars": "★" * row[2] + "☆" * (5 - row[2])
            })

        return results