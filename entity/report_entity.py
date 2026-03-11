from entity.database import connect_db

def report_article(articleID,userID,reason):

    conn = connect_db()
    cursor = conn.cursor()

    query = """
    INSERT INTO ReportedArticle(articleID,userID,optionalComment,reported_at)
    VALUES(%s,%s,%s,NOW())
    """

    cursor.execute(query,(articleID,userID,reason))
    conn.commit()