from entity.Comment import CommentEntity 

comment_entity = CommentEntity()

def add_comment(articleID, userID, commentText):
    """
    Adds a comment to the database
    """
    comment_entity.add_comment(articleID, userID, commentText)
    print("Comment Added")