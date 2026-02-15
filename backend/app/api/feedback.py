import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import bleach
from fastapi import APIRouter

from ..schemas import FeedbackCreate

router = APIRouter()


@router.post("", status_code=201)
def create_feedback(feedback: FeedbackCreate):
    """Submit feedback or contact message via Gmail SMTP"""
    smtp_user = os.environ.get("SMTP_USER")
    smtp_password = os.environ.get("SMTP_PASSWORD")

    if not smtp_user or not smtp_password:
        print("Error: SMTP_USER or SMTP_PASSWORD not configured")
        return {"status": "received", "note": "Email not configured"}

    # Sanitize inputs
    safe_message = bleach.clean(feedback.message, tags=[], strip=True)
    safe_name = bleach.clean(feedback.name or "Anonymous", tags=[], strip=True)
    safe_email = bleach.clean(
        feedback.email or "No Email Provided", tags=[], strip=True
    )

    # Email Content
    subject = f"Boba Seeker Feedback: {feedback.type.title()}"
    body = f"""
    New Feedback Received:
    
    Type: {feedback.type.title()}
    Name: {safe_name}
    Email: {safe_email}
    
    Message:
    {safe_message}
    """

    msg = MIMEMultipart()
    msg["From"] = smtp_user
    msg["To"] = smtp_user  # Send to self
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        # Connect to Gmail SMTP
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(msg)
        server.quit()
        print(f"Email sent successfully to {smtp_user}")
    except Exception as e:
        print(f"Failed to send email: {e}")
        # Still return success to frontend

    return {"status": "sent"}
