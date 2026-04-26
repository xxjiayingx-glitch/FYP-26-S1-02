import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

FROM_EMAIL = os.getenv("FROM_EMAIL")
BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:5000/")
EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))

def send_verification_email(email, token):
    verification_link = f"{BASE_URL.rstrip('/')}/verify?token={token}"
    message = MIMEMultipart()
    message["To"] = email
    message["From"] = FROM_EMAIL
    message["Subject"] = "Account Verification"
    body = f"Hi!\n\nPlease verify your account by clicking the link below:\n{verification_link}\n\nThank you!"
    message.attach(MIMEText(body, "plain"))
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.login(FROM_EMAIL, EMAIL_APP_PASSWORD)
        smtp.sendmail(FROM_EMAIL, email, message.as_string())

def send_email_change_verification_email(email, token):
    verification_link = f"{BASE_URL.rstrip('/')}/profile/verify-email-change?token={token}"
    message = MIMEMultipart()
    message["To"] = email
    message["From"] = FROM_EMAIL
    message["Subject"] = "Verify Your New Email"
    body = (
        f"Hi!\n\n"
        f"You requested to change your email for Daily Scoop News System.\n\n"
        f"Please verify your new email by clicking the link below:\n"
        f"{verification_link}\n\n"
        f"If you did not request this change, please ignore this email."
    )
    message.attach(MIMEText(body, "plain"))
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.login(FROM_EMAIL, EMAIL_APP_PASSWORD)
        smtp.sendmail(FROM_EMAIL, email, message.as_string())

def send_forgot_password_email(email, token):
    reset_link = f"{BASE_URL.rstrip('/')}/reset-password?token={token}"
    message = MIMEMultipart()
    message["To"] = email
    message["From"] = FROM_EMAIL
    message["Subject"] = "Reset Your Password"
    body = (
        f"Hi!\n\n"
        f"You requested to reset your password for Daily Scoop News System.\n\n"
        f"Click the link below to reset your password:\n"
        f"{reset_link}\n\n"
        f"If you did not request this, please ignore this email."
    )
    message.attach(MIMEText(body, "plain"))
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.login(FROM_EMAIL, EMAIL_APP_PASSWORD)
        smtp.sendmail(FROM_EMAIL, email, message.as_string())


# import base64
# import os
# import json
# from email.message import EmailMessage
# from google.oauth2.credentials import Credentials
# from googleapiclient.discovery import build
# from google.auth.transport.requests import Request
# from dotenv import load_dotenv
# load_dotenv()

# CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
# CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
# FROM_EMAIL = os.getenv("FROM_EMAIL")
# BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:5000/")

# SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# TOKEN_PATH = os.path.join(BASE_DIR, "token.json")

# def send_verification_email(email, token):
#     gmail_token_env = os.getenv("GMAIL_TOKEN")

#     if gmail_token_env:
#         token_info = json.loads(gmail_token_env)
#     else:
#         with open(TOKEN_PATH, "r") as f:
#             token_info = json.load(f)

#     # with open(TOKEN_PATH, "r") as f:
#     #     token_data = json.load(f)
#     # Send account verification email with token link.
#     # creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
#     creds = Credentials(
#         token=token_info.get("token"),
#         refresh_token=token_info.get("refresh_token"),
#         token_uri="https://oauth2.googleapis.com/token",
#         client_id=CLIENT_ID,
#         client_secret=CLIENT_SECRET,
#         scopes=SCOPES
#     )

#     if creds.expired and creds.refresh_token:
#         creds.refresh(Request())

#     # Save the updated token back to file
#     # with open(TOKEN_PATH, "w") as token_file:
#     #     token_file.write(creds.to_json())
    
#     service = build("gmail", "v1", credentials=creds)

#     # Change 127.0.0.1:5000 to hosted site
#     verification_link = f"{BASE_URL.rstrip('/')}/verify?token={token}"

#     message = EmailMessage()
#     message.set_content(
#         f"Hi!\n\nPlease verify your account by clicking the link below:\n{verification_link}\n\nThank you!"
#     )

#     message["To"] = email
#     message["From"] = FROM_EMAIL
#     message["Subject"] = "Account Verification"

#     encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
#     try:
#         service.users().messages().send(
#             userId="me",
#             body={"raw": encoded_message}
#         ).execute()
#         print("Email sent successfully")
#     except Exception as e:
#         print("Email failed", str(e))


# def send_email_change_verification_email(email, token):
#     verification_link = f"{BASE_URL.rstrip('/')}/profile/verify-email-change?token={token}"

#     body = (
#         f"Hi!\n\n"
#         f"You requested to change your email for Daily Scoop News System.\n\n"
#         f"Please verify your new email by clicking the link below:\n"
#         f"{verification_link}\n\n"
#         f"If you did not request this change, please ignore this email."
#     )

#     service = build("gmail", "v1", credentials=_build_credentials())

#     message = EmailMessage()
#     message.set_content(body)
#     message["To"] = email
#     message["From"] = FROM_EMAIL
#     message["Subject"] = "Verify Your New Email"

#     encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

#     service.users().messages().send(
#         userId="me",
#         body={"raw": encoded_message}
#     ).execute()

# def _build_credentials():
#     gmail_token_env = os.getenv("GMAIL_TOKEN")

#     if gmail_token_env:
#         token_info = json.loads(gmail_token_env)
#     else:
#         with open(TOKEN_PATH, "r") as f:
#             token_info = json.load(f)

#     creds = Credentials(
#         token=token_info.get("token"),
#         refresh_token=token_info.get("refresh_token"),
#         token_uri="https://oauth2.googleapis.com/token",
#         client_id=CLIENT_ID,
#         client_secret=CLIENT_SECRET,
#         scopes=SCOPES
#     )

#     if creds.expired and creds.refresh_token:
#         creds.refresh(Request())
#         with open(TOKEN_PATH, "w") as token_file:
#             token_file.write(creds.to_json())

#     return creds

# def send_forgot_password_email(email, token):
#     reset_link = f"{BASE_URL}/reset-password?token={token}"

#     body = (
#         f"Hi!\n\n"
#         f"You requested to reset your password for Daily Scoop News System.\n\n"
#         f"Click the link below to reset your password:\n"
#         f"{reset_link}\n\n"
#         f"If you did not request this, please ignore this email."
#     )

#     service = build("gmail", "v1", credentials=_build_credentials())

#     message = EmailMessage()
#     message.set_content(body)
#     message["To"] = email
#     message["From"] = FROM_EMAIL
#     message["Subject"] = "Reset Your Password"

#     encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
#     service.users().messages().send(
#         userId="me",
#         body={"raw": encoded_message}
#     ).execute()

# # Generating token file
# # from google_auth_oauthlib.flow import InstalledAppFlow

# # SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

# # import os
# # from dotenv import load_dotenv
# # load_dotenv()

# # flow = InstalledAppFlow.from_client_config(
# #     {
# #         "installed": {
# #             "client_id": os.getenv("GOOGLE_CLIENT_ID"),
# #             "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
# #             "auth_uri": "https://accounts.google.com/o/oauth2/auth",
# #             "token_uri": "https://oauth2.googleapis.com/token"
# #         }
# #     },
# #     SCOPES
# # )

# # creds = flow.run_local_server(port=8080,access_type="offline", prompt="consent")

# # with open("server/token.json", "w") as token:
# #     token.write(creds.to_json())

# # print("✅ token.json generated")