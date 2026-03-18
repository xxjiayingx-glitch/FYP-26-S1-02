from flask import Blueprint, render_template

unregSub_bp = Blueprint('unregsub', __name__)

@unregSub_bp.route("/guestsubscription")
def unreg_sub():
    return render_template("Unregistered/UnregSubscription.html")