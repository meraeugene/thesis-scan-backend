# app/utils/emailer.py
import os
from dotenv import load_dotenv
from sib_api_v3_sdk import ApiClient, Configuration
from sib_api_v3_sdk.api.transactional_emails_api import TransactionalEmailsApi
from sib_api_v3_sdk.models.send_smtp_email import SendSmtpEmail
from sib_api_v3_sdk.models.send_smtp_email_to1 import SendSmtpEmailTo1
from sib_api_v3_sdk.rest import ApiException

load_dotenv()

API_KEY = os.getenv("BREVO_API_KEY")
FROM_NAME = os.getenv("EMAIL_FROM_NAME", "ThesiScan")
FROM_EMAIL = os.getenv("EMAIL_FROM_EMAIL", "no-reply@thesiscan.com")

if not API_KEY:
    raise RuntimeError("BREVO_API_KEY not set in environment variables.")

# Initialize ApiClient once
configuration = Configuration()
configuration.api_key['api-key'] = API_KEY
api_client = ApiClient(configuration)
smtp_api = TransactionalEmailsApi(api_client)

def send_reset_email(to_email: str, reset_link: str, recipient_name: str | None = None):
    recipient_name = recipient_name or "User"
    subject = "ThesiScan — Password Reset"
    html_content = f"""
    <p>Hi {recipient_name},</p>
    <p>You recently requested a password reset for your ThesiScan account. Click the link below to reset your password:</p>
    <p><a href="{reset_link}">Reset Password</a></p>
    <p>If you did not request this, you can safely ignore this email.</p>
    <p>— ThesiScan Team</p>
    """

    email = SendSmtpEmail(
        to=[SendSmtpEmailTo1(email=to_email, name=recipient_name)],
        sender={"name": FROM_NAME, "email": FROM_EMAIL},
        subject=subject,
        html_content=html_content
    )

    try:
        response = smtp_api.send_transac_email(email)
        return response
    except ApiException as e:
        raise RuntimeError(f"Failed to send email via Brevo API: {e}")
