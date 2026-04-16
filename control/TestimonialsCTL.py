from entity.Testimonial import TestimonialEntity
from textblob import TextBlob
import re

class TestimonialController:

    @staticmethod
    def classify_sentiment(comment):
        polarity = TextBlob(comment).sentiment.polarity

        if polarity > 0.15:
            label = "positive"
        elif polarity < -0.15:
            label = "negative"
        else:
            label = "neutral"

        return polarity, label
    
    @staticmethod
    def check_consistency(rating, polarity):
        if rating >= 4 and polarity < -0.15:
            return "inconsistent"
        elif rating == 3 and (polarity > 0.4 or polarity < -0.4):
            return "inconsistent"
        elif rating <= 2 and polarity > 0.15:
            return "inconsistent"
        return "consistent"
    
    @staticmethod
    def is_meaningful_comment(comment):
        if not comment:
            return False

        cleaned = comment.strip().lower()

        # too short
        if len(cleaned) < 15:
            return False

        # too few words
        words = cleaned.split()
        if len(words) < 3:
            return False

        # repeated same word / spam-like
        unique_words = set(words)
        if len(unique_words) == 1:
            return False

        # vague low-value comments
        vague_comments = {
            "bad", "good", "okay", "ok", "nice", "not recommended",
            "recommended", "great", "poor", "free"
        }
        if cleaned in vague_comments:
            return False

        return True
    
    @staticmethod
    def is_abusive_or_spam(comment):
        if not comment:
            return True

        cleaned = comment.strip().lower()

        banned_terms = {
            "idiot", "stupid", "scam", "trash", "useless"
        }

        for word in banned_terms:
            if word in cleaned:
                return True

        # simple spam pattern
        if "http://" in cleaned or "https://" in cleaned or "www." in cleaned:
            return True

        return False
    
    @staticmethod
    def getTestimonials():
        # Fetch all testimonials
        testimonials = TestimonialEntity.getAllTestimonials()
        filtered_testimonials = []
        for t in testimonials:
            rating = t["rating"]
            comment = t["comment"]
            # Compute semantic score (TextBlob polarity)
            semantic_score, sentiment_label = TestimonialController.classify_sentiment(comment)
            consistency_status = TestimonialController.check_consistency(rating, semantic_score)
            # Compute combined score (optional, simple average)
            combined_score = (rating / 5 + semantic_score) / 2  # normalize rating to 0-1
            # Store scores in dict (optional, for backend tracking)
            t["semanticScore"] = semantic_score
            t["combinedScore"] = combined_score
            t["sentimentLabel"] = sentiment_label
            t["consistencyStatus"] = consistency_status
            t["stars"] = "★" * rating + "☆" * (5 - rating)

            # only exclude conflicting testimonials
            if consistency_status == "consistent" and TestimonialController.is_meaningful_comment(comment) and not TestimonialController.is_abusive_or_spam(comment):
                filtered_testimonials.append(t)
                
        return filtered_testimonials
            # Only keep testimonials with high rating AND positive sentiment
        #     if rating >= 4 and semantic_score >= 0:
        #         # Also compute stars as before
        #         t["stars"] = "★" * rating + "☆" * (5 - rating)
        #         filtered_testimonials.append(t)
        # return filtered_testimonials
    
    @staticmethod
    def addTestimonial(user_id, rating, comment):
        semantic_score, sentiment_label = TestimonialController.classify_sentiment(comment)
        # Compute semantic and combined score before storing
        # semantic_score = TextBlob(comment).sentiment.polarity
        combined_score = (rating / 5 + semantic_score) / 2
        TestimonialEntity.insertTestimonial(user_id, rating, comment, semantic_score, combined_score)

    @staticmethod
    def getHomeTestimonials():
        testimonials = TestimonialEntity.getHomeTestimonial()

        positive = []
        neutral = []
        negative = []

        for t in testimonials:
            rating = t["rating"]
            comment = t["comment"]
            # semantic_score = TextBlob(comment).sentiment.polarity
            semantic_score, sentiment_label = TestimonialController.classify_sentiment(comment)
            consistency_status = TestimonialController.check_consistency(rating, semantic_score)
    
            t["semanticScore"] = semantic_score
            t["sentimentLabel"] = sentiment_label
            t["consistencyStatus"] = consistency_status
            t["stars"] = "★" * rating + "☆" * (5 - rating)
            # Optional filter for positive/strong ratings
            # if rating >= 4 and semantic_score >= 0:
            #     t["stars"] = "★" * rating + "☆" * (5 - rating)
            #     filtered_testimonials.append(t)

            # only keep valid testimonials
            if consistency_status != "consistent":
                continue
            if not TestimonialController.is_meaningful_comment(comment):
                continue
            if TestimonialController.is_abusive_or_spam(comment):
                continue

            # split by sentiment group
            if sentiment_label == "positive":
                positive.append(t)
            elif sentiment_label == "neutral":
                neutral.append(t)
            else:
                negative.append(t)

        featured = []

        # target mix: 3 positive, 1 neutral, 1 constructive negative
        featured.extend(positive[:3])
        featured.extend(neutral[:1])
        featured.extend(negative[:1])

        # fallback: fill remaining slots up to 5
        used_keys = {(x["username"], x["comment"], x["created_at"]) for x in featured}

        for group in [positive[3:], neutral[1:], negative[1:]]:
            for item in group:
                key = (item["username"], item["comment"], item["created_at"])
                if key not in used_keys:
                    featured.append(item)
                    used_keys.add(key)
                if len(featured) >= 5:
                    break
            if len(featured) >= 5:
                break

        return featured
    
