from flask import Blueprint, render_template

subscription_bp = Blueprint('subscription', __name__)

@subscription_bp.route("/subscription")
def subscription():

    return render_template("subscription.html")