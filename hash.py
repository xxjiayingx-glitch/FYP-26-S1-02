from werkzeug.security import generate_password_hash

print("12345678 =>", generate_password_hash("12345678"))
print("abcd1234 =>", generate_password_hash("abcd1234"))
print("test123456 =>", generate_password_hash("test123456"))
print("1234567890 =>", generate_password_hash("1234567890"))
print(generate_password_hash("1234567899"))