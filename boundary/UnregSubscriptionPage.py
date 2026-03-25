from flask import Blueprint, render_template, session, redirect, url_for
from control.UnregisteredUser.SubscriptionCTL import SubscriptionCTL

unregSub_bp = Blueprint("unregsub", __name__)
subscriptionCTL = SubscriptionCTL()

@unregSub_bp.route("/guestsubscription")
def unreg_sub():
    user_type = session.get('userType', '').lower()
    if "free" in user_type:
        return render_template("free_homepage.html")

    if "premium" in user_type:
        return render_template("premium_homepage.html")
    
    result = subscriptionCTL.getSubscriptionPlans()

    if not result["success"]:
        return render_template("Unregistered/UnregSubscription.html", plans=[])

    return render_template("Unregistered/UnregSubscription.html", plans=result["plans"])
