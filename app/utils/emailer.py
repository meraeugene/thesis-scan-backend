# app/utils/emailer.py
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()  # loads .env into environment

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))  # 465 for SSL
SMTP_USER = os.getenv("EMAIL_USER")
SMTP_PASS = os.getenv("EMAIL_PASS")  # app-specific password or real SMTP password
FROM_NAME = os.getenv("EMAIL_FROM_NAME", "ThesiScan")
FROM_EMAIL = SMTP_USER

if not SMTP_USER or not SMTP_PASS:
    # we don't raise here because dev/test environments may not have SMTP configured.
    pass

def send_reset_email(to_email: str, reset_link: str, recipient_name: str | None = None):
    """
    Sends a password reset email. Raises Exception/HTTPException on failure.
    """
    subject = "ThesiScan — Password Reset"
    display_name = FROM_NAME
    from_addr = FROM_EMAIL

    html_body = f"""
    <p>Hi {recipient_name or ''},</p>
    <p>You recently requested a password reset for your ThesiScan account. Click the link below to reset your password. This link will expire in a short time.</p>
    <p><a href="{reset_link}">Reset your password</a></p>
    <p>If you did not request this, you can safely ignore this email.</p>
    <p>— ThesiScan Team</p>
    """

    # plain text fallback
    text_body = f"Reset your password: {reset_link}"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{display_name} <{from_addr}>"
    msg["To"] = to_email

    part1 = MIMEText(text_body, "plain")
    part2 = MIMEText(html_body, "html")
    msg.attach(part1)
    msg.attach(part2)

    # Send via SMTP SSL
    try:
        server = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=10)
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(from_addr, [to_email], msg.as_string())
        server.quit()
    except Exception as e:
        # bubble up so calling endpoint returns 500
        raise Exception(f"Failed to send email: {e}")
