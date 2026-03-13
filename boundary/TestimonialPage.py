from flask import Blueprint, render_template
from control.TestimonialsCTL import TestimonialController

testimonial_bp = Blueprint("testimonial", __name__)

testimonialCTL = TestimonialController()


@testimonial_bp.route("/testimonials")
def testimonial_page():

    testimonials = testimonialCTL.getTestimonials()

    return render_template(
        "Unregistered/UnregTestimonial.html", testimonials=testimonials
    )
