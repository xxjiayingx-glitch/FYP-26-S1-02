from werkzeug.security import generate_password_hash
from entity.db_connection import get_db_connection

# def hash_password(password):
#     password_bytes = password.encode('utf-8')
#     hashed_bytes = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
#     return hashed_bytes.decode('utf-8')


# def update_user_password(username, hashed_password):
#     try:
#         conn = get_db_connection()
#         cursor = conn.cursor()

#         sql = "UPDATE UserAccount SET pwd = %s WHERE username = %s"
#         # sql = "Insert into UserAccount(username, email, pwd,first_name,last_name, phone, userType, gender, dateOfBirth) Values (%s, 'alex@gmail.com', %s, %s, %s, 12345678, 'Premium', 'Male', '1993-02-01')"
#         val = (hashed_password, username)

#         cursor.execute(sql, val)
#         conn.commit()

#         print("Password updated successfully")

#     except Exception as err:
#         print(f"Error: {err}")

#     finally:
#         cursor.close()
#         conn.close()


# # Example
# # firstName = "Alex"
# # lastName = "Smith"
# # username = firstName + lastName
# # user_password = "alex@123"
# # hashed_password = hash_password(user_password)

# # print("Hashed Password:", hashed_password)

# # update_user_password(username, firstName, lastName, hashed_password)

# def get_pwd(username):
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     sql = "SELECT pwd FROM UserAccount WHERE username = %s"
#     cursor.execute(sql, (username,))
#     result = cursor.fetchone()
#     cursor.close()
#     conn.close()

#     if result:
#         return result["pwd"]
    
#     return None

# username = "max"
# pwd = get_pwd(username)
# if pwd:
#     hashed_password = hash_password(pwd)
#     update_user_password(username, hashed_password)

new_hash = generate_password_hash("12345678", method="pbkdf2:sha256")

conn = get_db_connection()
cursor = conn.cursor()
cursor.execute(
    "UPDATE UserAccount SET pwd = %s WHERE email = %s",
    (new_hash, "admin12@gmail.com")
)
conn.commit()
cursor.close()
conn.close()