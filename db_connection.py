# db_connection.py

import pymysql

def get_db_connection():
    return pymysql.connect(
        host="news-system.clcguooacqgr.ap-southeast-1.rds.amazonaws.com",
        user="admin",
        password="DailyscoopNews",
        database="news_system",
        cursorclass=pymysql.cursors.DictCursor
    )