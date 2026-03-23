import base64
import os
import json
from email.message import EmailMessage
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from dotenv import load_dotenv
load_dotenv()

CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
FROM_EMAIL = os.getenv("FROM_EMAIL")
BASE_URL = os.getenv("BASE_URL")

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# TOKEN_PATH = os.path.join(BASE_DIR, "token.json")

def send_verification_email(email, token):
    token_info = json.loads(os.getenv("GMAIL_TOKEN"))

    # with open(TOKEN_PATH, "r") as f:
    #     token_data = json.load(f)
    # Send account verification email with token link.
    # creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    creds = Credentials(
        token=token_info.get("token"),
        refresh_token=token_info.get("refresh_token"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        scopes=SCOPES
    )

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())

    # Save the updated token back to file
    # with open(TOKEN_PATH, "w") as token_file:
    #     token_file.write(creds.to_json())
    
    service = build("gmail", "v1", credentials=creds)

    # Change 127.0.0.1:5000 to hosted site
    verification_link = f"{BASE_URL}/verify?token={token}"

    message = EmailMessage()
    message.set_content(
        f"Hi!\n\nPlease verify your account by clicking the link below:\n{verification_link}\n\nThank you!"
    )

    message["To"] = email
    message["From"] = FROM_EMAIL
    message["Subject"] = "Account Verification"

    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    try:
        service.users().messages().send(
            userId="me",
            body={"raw": encoded_message}
        ).execute()
        print("Email sent successfully")
    except Exception as e:
        print("Email failed", str(e))



# Generating token file
# from google_auth_oauthlib.flow import InstalledAppFlow

# SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

# import os
# from dotenv import load_dotenv
# load_dotenv()

# flow = InstalledAppFlow.from_client_config(
#     {
#         "installed": {
#             "client_id": os.getenv("GOOGLE_CLIENT_ID"),
#             "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
#             "auth_uri": "https://accounts.google.com/o/oauth2/auth",
#             "token_uri": "https://oauth2.googleapis.com/token"
#         }
#     },
#     SCOPES
# )

# creds = flow.run_local_server(port=8080)

# with open("token.json", "w") as token:
#     token.write(creds.to_json())

# print("✅ token.json generated")