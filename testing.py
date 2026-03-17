from db_connection import get_db_connection

conn = get_db_connection()
cursor = conn.cursor()

cursor.execute("SELECT * FROM UserAccount")
users = cursor.fetchall()

print(users)