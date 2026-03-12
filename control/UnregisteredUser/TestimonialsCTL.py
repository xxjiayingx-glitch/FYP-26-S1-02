from flask import jsonify, request
from flask_cors import cross_origin
from app.entities.Testimonials import Testimonials
from app.db import get_database
from app.routes.UnregisteredUser_routes import UnregisteredUser


class TestimonialsCTL:
    def __init__(self):
        self.testimonials = Testimonials()

    def fetchAllTestimonials(self, testimonial_ID):
        testimonialListing = self.testimonials.fetchAllTestimonials(testimonial_ID)
        return testimonialListing


@UnregisteredUser.route("/api/testimonials", methods=["GET"])
def fetchAllTestimonials():
    testimonial_ID = int(request.args.get("testimonial_ID"))
    testimonialsCTL = TestimonialsCTL()
    try:
        testimonialListing = testimonialsCTL.fetchAllTestimonials(testimonial_ID)

        if testimonialListing:
            return jsonify(testimonialListing), 200
        else:
            return (
                jsonify({
                    "status": "error",
                    "message": "No testimonials found"
                }),
                404,
            )

    except Exception as e:
        return (
            jsonify({
                "status": "error",
                "message": str(e),
            }),
            500,
        )