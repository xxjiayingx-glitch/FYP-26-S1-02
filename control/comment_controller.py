from entity.comment_entity import add_comment

def comment_article(articleID,userID,comment):

    add_comment(articleID,userID,comment)

    print("Comment Added")