from entity.Subscription import Subscription 

def view_subscription(userID):
    return Subscription.get_subscription(userID)  