
from entity.Testimonial import TestimonialEntity
from textblob import TextBlob
class TestimonialController:
    
    @staticmethod
    def getTestimonials():
        # Fetch all testimonials
        testimonials = TestimonialEntity.getAllTestimonials()
        filtered_testimonials = []
        for t in testimonials:
            rating = t["rating"]
            comment = t["comment"]
            # Compute semantic score (TextBlob polarity)
            semantic_score = TextBlob(comment).sentiment.polarity  # range -1 to 1
            # Compute combined score (optional, simple average)
            combined_score = (rating / 5 + semantic_score) / 2  # normalize rating to 0-1
            # Store scores in dict (optional, for backend tracking)
            t["semanticScore"] = semantic_score
            t["combinedScore"] = combined_score
            # Only keep testimonials with high rating AND positive sentiment
            if rating >= 4 and semantic_score >= 0:
                # Also compute stars as before
                t["stars"] = "★" * rating + "☆" * (5 - rating)
                filtered_testimonials.append(t)
        return filtered_testimonials
    
    @staticmethod
    def addTestimonial(user_id, rating, comment):
        # Compute semantic and combined score before storing
        semantic_score = TextBlob(comment).sentiment.polarity
        combined_score = (rating / 5 + semantic_score) / 2
        TestimonialEntity.insertTestimonial(user_id, rating, comment, semantic_score, combined_score)

    @staticmethod
    def getHomeTestimonials(offset, limit):
        testimonials = TestimonialEntity.getHomeTestimonial(offset, limit*3)

        filtered_testimonials = []
        for t in testimonials:
            rating = t["rating"]
            comment = t["comment"]
            semantic_score = TextBlob(comment).sentiment.polarity
            combined_score = (rating / 5 + semantic_score) / 2
            t["semanticScore"] = semantic_score
            t["combinedScore"] = combined_score
            # Optional filter for positive/strong ratings
            if rating >= 4 and semantic_score >= 0:
                t["stars"] = "★" * rating + "☆" * (5 - rating)
                filtered_testimonials.append(t)

            # Stop once we have enough
            if len(filtered_testimonials) == limit:
                break

        return filtered_testimonials
