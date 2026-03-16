from flask import Blueprint, render_template
from control.UnregisteredUser.SubscriptionCTL import SubscriptionCTL

unregSub_bp = Blueprint("unregsub", __name__)
subscriptionCTL = SubscriptionCTL()

@unregSub_bp.route("/guestsubscription")
def unreg_sub():
    result = subscriptionCTL.getSubscriptionPlans()

    if not result["success"]:
        return render_template("Unregistered/UnregSubscription.html", plans=[])

    return render_template("Unregistered/UnregSubscription.html", plans=result["plans"])
