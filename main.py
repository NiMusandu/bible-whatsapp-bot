import os
import json
from datetime import datetime
from fastapi import FastAPI, Request
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
from supabase import create_client

# Load .env
load_dotenv()

# ✅ Sanity check
print("✅ DEBUG: SUPABASE_URL =", os.getenv("SUPABASE_URL"))

# Get credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
if not SUPABASE_URL or not SUPABASE_KEY:
    raise Exception("❌ Missing Supabase credentials")

# Connect to Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Load reading plan
try:
    with open("reading_plan.json", "r", encoding="utf-8") as f:
        reading_plan = json.load(f)
    print("✅ reading_plan.json loaded successfully.")
except Exception as e:
    print(f"❌ Error loading reading plan: {e}")
    reading_plan = []

# Twilio credentials
TWILIO_NUMBER = os.getenv("TWILIO_NUMBER")
RECIPIENTS = os.getenv("RECIPIENT_NUMBER", "").split(";")
TWILIO_TOKEN = os.getenv("TWILIO_TOKEN")

# WhatsApp sender function (dummy placeholder)
def send_whatsapp_message():
    today = datetime.now().strftime("%Y-%m-%d")
    reading = next((r for r in reading_plan if r["date"] == today), None)
    if not reading:
        print("⚠️ No reading found for today.")
        return
    message = (
        f"📖 Day {reading['day']} Bible Reading Plan:\n"
        f"📘 OT: {reading['old_testament']}\n"
        f"📕 NT: {reading['new_testament']}\n"
        f"🎵 Psalms/Gospel: {reading['psalm_or_gospel']}"
    )
    for recipient in RECIPIENTS:
        print(f"📤 Sending to {recipient.strip()}: {message}")
        # Add Twilio API call here

# FastAPI + Scheduler setup
app = FastAPI()

scheduler = BackgroundScheduler(timezone="Africa/Nairobi")
scheduler.add_job(send_whatsapp_message, "cron", hour=6, minute=0)
scheduler.start()

@app.get("/")
def home():
    return {"message": "📖 Bible Bot is running"}

@app.get("/send_message")
def manual_send():
    send_whatsapp_message()
    return {"message": "✅ Message sent manually"}

@app.get("/reading/today")
def get_today_reading():
    today = datetime.now().date()
    for entry in reading_plan:
        if entry["date"] == today.strftime("%Y-%m-%d"):
            return {
                "day": entry["day"],
                "old_testament": entry["old_testament"],
                "new_testament": entry["new_testament"],
                "psalm_or_gospel": entry["psalm_or_gospel"]
            }
    return {"message": "📅 No reading found for today."}

# Supabase progress tracking
def mark_as_read(user_id):
    result = supabase.table("progress").select("*").eq("user_id", user_id).execute()
    if result.data:
        current = result.data[0]["days_completed"]
        supabase.table("progress").update({"days_completed": current + 1}).eq("user_id", user_id).execute()
    else:
        supabase.table("progress").insert({"user_id": user_id, "days_completed": 1}).execute()

def get_user_stats(user_id):
    result = supabase.table("progress").select("*").eq("user_id", user_id).execute()
    if result.data:
        return result.data[0]["days_completed"]
    return 0

@app.post("/webhook")
async def handle_webhook(request: Request):
    data = await request.json()
    incoming_msg = data.get("Body", "").strip().upper()
    sender = data.get("From", "").replace("whatsapp:", "")
    print(f"📩 Message from {sender}: {incoming_msg}")

    if incoming_msg == "READ":
        mark_as_read(sender)
        return {"message": "✅ Progress saved for today!"}
    elif incoming_msg == "STATS":
        count = get_user_stats(sender)
        return {"message": f"📊 You’ve completed {count} days of Bible reading!"}
    elif incoming_msg == "REMIND":
        return {"message": "⏰ A reminder has been scheduled for 8 PM!"}
    else:
        return {
            "message": (
                "🤖 Bible Bot Commands:\n"
                "READ – Mark today's reading\n"
                "STATS – See progress\n"
                "REMIND – Get reminder at 8 PM"
            )
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=10000)
