from entity.Testimonial import TestimonialEntity

class TestimonialController:
    
    @staticmethod
    def getTestimonials():
        testimonials = TestimonialEntity.getAllTestimonials()
        for t in testimonials:
            rating = t["rating"]
            t["stars"] = "★" * rating + "☆" * (5 - rating)
        return testimonials
    
    @staticmethod
    def addTestimonial(user_id, rating, comment):
        TestimonialEntity.insertTestimonial(user_id, rating, comment)