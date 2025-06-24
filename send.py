# send.py

import os
import json
from datetime import datetime
from twilio.rest import Client

# Load reading plan
try:
    with open("reading_plan.json", "r", encoding="utf-8") as f:
        reading_plan = json.load(f)
except Exception as e:
    print(f"❌ Error loading reading plan: {e}")
    reading_plan = []

# Send WhatsApp message via Twilio
def send_whatsapp_message():
    if not reading_plan:
        print("❌ No reading plan loaded. Message not sent.")
        return

    today = datetime.now().strftime("%Y-%m-%d")
    entry = next((item for item in reading_plan if item["date"] == today), None)

    if not entry:
        print(f"📅 No entry found for today's date: {today}")
        return

    # Prepare message
    message = (
        f"📖 *Day {entry['day']} Bible Reading*\n"
        f"📜 Old Testament: {entry['old_testament']}\n"
        f"📜 New Testament: {entry['new_testament']}\n"
        f"🎵 Psalms or Gospels: {entry['psalm_or_gospel']}\n\n"
        f"_Reply with:_ READ | REMIND | STATS"
    )

    # Twilio credentials from environment variables
    account_sid = os.getenv("TWILIO_SID")
    auth_token = os.getenv("TWILIO_TOKEN")
    from_whatsapp_number = os.getenv("TWILIO_FROM")
    to_whatsapp_number = os.getenv("TWILIO_TO")  # or a test group/contact

    if not all([account_sid, auth_token, from_whatsapp_number, to_whatsapp_number]):
        print("❌ Missing Twilio environment variables.")
        return

    try:
        client = Client(account_sid, auth_token)
        message = client.messages.create(
            from_=f"whatsapp:{from_whatsapp_number}",
            body=message,
            to=f"whatsapp:{to_whatsapp_number}"
        )
        print(f"✅ Message sent: SID {message.sid}")
    except Exception as e:
        print(f"❌ Failed to send message: {e}")
