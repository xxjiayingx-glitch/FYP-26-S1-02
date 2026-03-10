from db import get_db_connection

db = get_db_connection()
cursor = db.cursor()

cursor.execute("SELECT * FROM users")

for row in cursor.fetchall():
    print(row)