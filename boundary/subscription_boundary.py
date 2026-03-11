from control.subscription_controller import view_subscription

def view_subscription_info(userID):

    sub = view_subscription(userID)

    if sub:
        print("Subscription Active")
    else:
        print("Free User")