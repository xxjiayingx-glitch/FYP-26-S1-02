import base64
import os
from email.message import EmailMessage
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
FROM_EMAIL = "dailyscoopnewssys@gmail.com"  

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_PATH = os.path.join(BASE_DIR, "token.json")

def send_verification_email(email, token):
    """Send account verification email with token link."""
    creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    service = build("gmail", "v1", credentials=creds)

    # Change to hosted link
    verification_link = f"http://127.0.0.1:5000/verify?token={token}"

    message = EmailMessage()
    message.set_content(
        f"Hi!\n\nPlease verify your account by clicking the link below:\n{verification_link}\n\nThank you!"
    )

    message["To"] = email
    message["From"] = FROM_EMAIL
    message["Subject"] = "Account Verification"

    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    service.users().messages().send(
        userId="me",
        body={"raw": encoded_message}
    ).execute()