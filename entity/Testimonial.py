from entity.db_connection import get_db_connection

class TestimonialEntity:
    @staticmethod
    def getAllTestimonials():
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT u.username, t.rating, t.comment, t.created_at
            FROM UserAccount u
            JOIN Testimonial t ON u.userID = t.userID
            WHERE t.created_at >= DATE_SUB(NOW(), INTERVAL 180 DAY)
            ORDER BY t.created_at DESC
        """)

        rows = cursor.fetchall()

        cursor.close()
        conn.close()

        testimonials = []

        for row in rows:
            testimonials.append({
                "username": row["username"],
                "rating": row["rating"],
                "comment": row["comment"],
                "created_at": row["created_at"],
                "stars": "★" * row["rating"] + "☆" * (5 - row["rating"])
            })

        return testimonials
    
    @staticmethod
    def insertTestimonial(user_id, rating, comment, semantic_score, combined_score):
        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
            INSERT INTO Testimonial (userID, rating, comment, semanticScore, combinedScore, created_at)
            VALUES (%s, %s, %s, %s, %s, NOW())
        """
        cursor.execute(query, (user_id, rating, comment, semantic_score, combined_score))
        conn.commit()
        cursor.close()
        conn.close()


    @staticmethod
    def getHomeTestimonial(offset=0, limit=3):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.username, t.rating, t.comment, t.created_at
            FROM UserAccount u
            JOIN Testimonial t ON u.userID = t.userID
            WHERE t.created_at >= DATE_SUB(NOW(), INTERVAL 180 DAY)
            ORDER BY t.created_at DESC
            LIMIT %s OFFSET %s
        """, (limit, offset))

        rows = cursor.fetchall()

        cursor.close()
        conn.close()

        results = []

        for row in rows:
            results.append({
                "username": row["username"],
                "rating": row["rating"],
                "comment": row["comment"],
                "created_at": row["created_at"],
                "stars": "★" * row["rating"] + "☆" * (5 - row["rating"])
            })
            

        return results
        