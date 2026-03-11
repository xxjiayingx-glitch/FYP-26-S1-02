from control.comment_controller import comment_article

def comment(userID):

    articleID = input("Article ID: ")
    text = input("Comment: ")

    comment_article(articleID,userID,text)