from flask import Blueprint, render_template

subscription_bp = Blueprint('subscription', __name__)

@subscription_bp.route("/")
def subscription_page():
    return render_template("subscription.html")