import boto3
import os

def send_verification_email(email, token):
    ses = boto3.client(
        'ses',
        region_name=os.getenv("AWS_REGION"),
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
    )
    print(ses)

    verification_link = f"http://localhost:5000/verify/{token}"

    ses.send_email(
        Source=os.getenv("SES_SENDER_EMAIL"),
        Destination={'ToAddresses': [email]},
        Message={
            'Subject': {'Data': 'Verify your account'},
            'Body': {
                'Html': {
                    'Data': f"""
                    <h2>Verify your account</h2>
                    <a href="{verification_link}">Verify Account</a>
                    """
                }
            }
        }
    )
    print(ses.get_send_quota())