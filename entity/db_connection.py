import pymysql

def get_db_connection():

    connection = pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="news_system",
        cursorclass=pymysql.cursors.DictCursor,
        charset="utf8mb4",
        autocommit=True
    )

    return connection