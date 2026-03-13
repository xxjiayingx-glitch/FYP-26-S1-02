from flask import Blueprint, render_template, request, redirect, url_for, session
from control.TestimonialsCTL import TestimonialController

testimonial_bp = Blueprint("testimonial", __name__, url_prefix="/testimonial")
testimonialCTL = TestimonialController()

# Display all testimonials
@testimonial_bp.route("/testimonials")
def testimonial_page():
    testimonials = testimonialCTL.getTestimonials()
    user_logged_in = "userID" in session
    return render_template(
        "testimonial_page.html",
        testimonials=testimonials,
        user_logged_in=user_logged_in
    )

# Create testimonial (separate form page)
@testimonial_bp.route("/create", methods=["GET", "POST"])
def create_testimonial():
    if "userID" not in session:
        # redirect unregistered users to login
        return redirect(url_for("login"))
    if request.method == "POST":
        rating = int(request.form.get("rating"))
        comment = request.form.get("comment")
        user_id = session["userID"]
        # Insert new testimonial
        testimonialCTL.addTestimonial(user_id, rating, comment)
        # Redirect back to testimonial listing
        return redirect(url_for("testimonial.testimonial_page"))
    # Show form to create testimonial
    return render_template("create_testimonial.html")
