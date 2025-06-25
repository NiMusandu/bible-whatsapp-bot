import os
import json
from datetime import datetime
from fastapi import FastAPI, Request
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
from supabase import create_client

# Load .env file
load_dotenv()

# ✅ Debug sanity check
print("✅ DEBUG: SUPABASE_URL =", os.getenv("SUPABASE_URL"))

# 📦 Check if Supabase credentials exist
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
if not SUPABASE_URL or not SUPABASE_KEY:
    raise Exception("❌ Missing Supabase credentials")

# 🔌 Connect to Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# 📚 Load Bible reading plan
try:
    with open("reading_plan.json", "r", encoding="utf-8") as f:
        reading_plan = json.load(f)
    print("✅ reading_plan.json loaded successfully.")
except Exception as e:
    print(f"❌ Error loading reading_plan.json: {e}")
    reading_plan = []

# 📲 Twilio setup (values come from .env)
TWILIO_NUMBER = os.getenv("TWILIO_NUMBER")
RECIPIENTS = os.getenv("RECIPIENT_NUMBER", "").split(";")
TWILIO_TOKEN = os.getenv("TWILIO_TOKEN")

# ✉️ Send WhatsApp message (dummy placeholder function)
def send_whatsapp_message():
    today = datetime.now().strftime("%Y-%m-%d")
    reading = next((r for r in reading_plan if r["date"] == today), None)
    if not reading:
        print("⚠️ No reading found for today.")
        return
    message = f"📖 Day {reading['day']} Bible Reading Plan:\n📘 OT: {reading['old_testament']}\n📕 NT: {reading['new_testament']}\n🎵 Psalms/Gospel: {reading['psalm_or_gospel']}"
    for recipient in RECIPIENTS:
        print(f"📤 Sending to {recipient.strip()}: {message}")
        # Integrate Twilio API here to actually send

# 🕕 Schedule daily reading
scheduler = BackgroundScheduler(timezone="Africa/Nairobi")
scheduler.add_job(send_whatsapp_message, "cron", hour=6, minute=0)
scheduler.start()

# 🚀 FastAPI setup
app = FastAPI()

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
                "new
