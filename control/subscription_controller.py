from entity.subscription_entity import get_subscription

def view_subscription(userID):

    sub = get_subscription(userID)

    return sub