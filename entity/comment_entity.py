from entity.database import connect_db

def add_comment(articleID,userID,comment):

    conn = connect_db()
    cursor = conn.cursor()

    query = """
    INSERT INTO Comment(articleID,userID,commentText,created_at)
    VALUES(%s,%s,%s,NOW())
    """

    cursor.execute(query,(articleID,userID,comment))
    conn.commit()