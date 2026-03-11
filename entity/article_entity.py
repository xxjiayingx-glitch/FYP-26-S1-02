from entity.database import connect_db

def get_articles():

    conn = connect_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT articleID, articleTitle FROM Article")

    return cursor.fetchall()


def search_articles(keyword):

    conn = connect_db()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT articleTitle FROM Article WHERE articleTitle LIKE %s"

    cursor.execute(query,("%"+keyword+"%",))

    return cursor.fetchall()