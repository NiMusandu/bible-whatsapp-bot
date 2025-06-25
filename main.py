import os
import json
from fastapi import FastAPI, Request
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client

# ✅ Sanity print
print("🚀 Starting Bible Bot...")

# ✅ Load .env values
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
TWILIO_TOKEN = os.getenv("TWILIO_TOKEN")
TWILIO_NUMBER = os.getenv("TWILIO_NUMBER")
RECIPIENTS = os.getenv("RECIPIENT_NUMBER", "").split(";")

# ✅ Supabase sanity check
if not SUPABASE_URL or not SUPABASE_KEY:
    raise Exception("❌ Missing Supabase credentials")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ✅ Load Bible Reading Plan
try:
    with open("reading_plan.json", "r", encoding="utf-8") as f:
        reading_plan = json.load(f)
    print("✅ Reading plan loaded successfully.")
except Exception as e:
    print(f"❌ Error loading reading plan: {e}")
    reading_plan = []

# ✅ WhatsApp Message Function (Twilio example)
def send_whatsapp_message():
    from twilio.rest import Client
    client = Client("AC" + TWILIO_TOKEN, TWILIO_TOKEN)  # Adjust if needed
    today = datetime.now().strftime("%Y-%m-%d")

    reading = next((entry for entry in reading_plan if entry["date"] == today), None)
    if not reading:
        print("❌ No reading found for today.")
        return

    text = (
        f"📖 *Day {reading['day']} – {today}*\n"
        f"📘 OT: {reading['old_testament']}\n"
        f"📙 NT: {reading['new_testament']}\n"
        f"📗 Psalm/Gospel: {reading['psalm_or_gospel']}\n\n"
        f"Reply with:\nREAD ✅ to mark done\nSTATS 📊 to check progress\nREMIND ⏰ to set reminder"
    )

    for recipient in RECIPIENTS:
        recipient = recipient.strip()
        if recipient:
            client.messages.create(
                from_=TWILIO_NUMBER,
                body=text,
                to=recipient
            )
    print("✅ Daily WhatsApp messages sent.")

# ✅ BackgroundScheduler task
def send_daily_reading():
    print(f"⏰ Triggered at {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    send_whatsapp_message()

# ✅ FastAPI app
app = FastAPI()

# ✅ APScheduler runs as app imports
scheduler = BackgroundScheduler(timezone="Africa/Nairobi")
scheduler.add_job(send_daily_reading, 'cron', hour=6, minute=0)
scheduler.start()
print("✅ APScheduler is running and scheduled for 6AM Nairobi time.")

# ✅ Web Endpoints
@app.get("/")
def home():
    return {"message": "📖 Bible Bot is running"}

@app.get("/send_message")
def manual_send():
    send_whatsapp_message()
    return {"message": "✅ Message sent manually"}

@app.get("/reading/today")
def get_today_reading():
    today = datetime.now().strftime("%Y-%m-%d")
    for entry in reading_plan:
        if entry["date"] == today:
            return entry
    return {"message": "📅 No reading found for today."}

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    msg = data.get("Body", "").strip().upper()
    sender = data.get("From", "").replace("whatsapp:", "")

    print(f"📩 WhatsApp from {sender}: {msg}")

    if msg == "READ":
        result = supabase.table("progress").select("*").eq("user_id", sender).execute()
        if result.data:
            days = result.data[0]["days_completed"]
            supabase.table("progress").update({"days_completed": days + 1}).eq("user_id", sender).execute()
        else:
            supabase.table("progress").insert({"user_id": sender, "days_completed": 1}).execute()
        return {"message": "✅ Progress marked for today!"}

    elif msg == "STATS":
        result = supabase.table("progress").select("*").eq("user_id", sender).execute()
        count = result.data[0]["days_completed"] if result.data else 0
        return {"message": f"📊 You have completed {count} days."}

    elif msg == "REMIND":
        return {"message": "⏰ You will be reminded at 8PM!"}

    return {
        "message": "🤖 Bible Bot Commands:\nREAD ✅\nSTATS 📊\nREMIND ⏰"
    }

# ✅ Run Uvicorn if local
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=10000)
