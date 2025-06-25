from twilio.rest import Client
import os
import json
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

account_sid = os.getenv("TWILIO_SID")
auth_token = os.getenv("TWILIO_TOKEN")
from_whatsapp = os.getenv("FROM_WHATSAPP_NUMBER")
to_whatsapp = os.getenv("TO_WHATSAPP_NUMBER")

client = Client(account_sid, auth_token)

def send_whatsapp_message():
    today = datetime.now().strftime("%Y-%m-%d")

    with open("reading_plan.json", "r", encoding="utf-8") as f:
        plan = json.load(f)

    entry = next((day for day in plan if day["date"] == today), None)

    if not entry:
        print("❌ No reading for today")
        return

    message = f"📖 *Day {entry['day']} - {today}*\n\n"
    message += f"📜 OT: {entry['old_testament']}\n"
    message += f"📜 NT: {entry['new_testament']}\n"
    message += f"📜 Psalm/Gospel: {entry['psalm_or_gospel']}"

    client.messages.create(
        body=message,
        from_=f"whatsapp:{from_whatsapp}",
        to=f"whatsapp:{to_whatsapp}"
    )

    print("✅ WhatsApp message sent")
