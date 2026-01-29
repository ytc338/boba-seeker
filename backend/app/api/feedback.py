import os
import requests
import bleach
from fastapi import APIRouter
from ..schemas import FeedbackCreate

router = APIRouter()

@router.post("", status_code=201)
def create_feedback(feedback: FeedbackCreate):
    """Submit feedback or contact message via Discord Webhook"""
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        print("Error: DISCORD_WEBHOOK_URL not configured")
        # Return success to frontend to avoid user error, but log it
        return {"status": "received", "note": "Webhook not configured"}

    # Format message for Discord
    content = f"**New {feedback.type.title()}**\n"
    if feedback.name:
        content += f"**Name:** {feedback.name}\n"
    if feedback.email:
        content += f"**Email:** {feedback.email}\n"
    
    # Sanitize message 
    safe_message = bleach.clean(feedback.message, tags=[], strip=True)
    content += f"\n{safe_message}"

    try:
        response = requests.post(webhook_url, json={"content": content})
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"Failed to send to Discord: {e}")
        if response.status_code == 429:
            print(f"Rate Limit Headers: {response.headers}")
            print(f"Response Body: {response.text}")
    except Exception as e:
        print(f"Failed to send to Discord: {e}")
        # Still return success to frontend so user isn't confused
    
    return {"status": "sent"}
