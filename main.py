from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import os
from send import send_whatsapp_message  # your WhatsApp function

app = FastAPI()

# Define job
def send_daily_reading():
    print(f"⏰ Triggered at {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    send_whatsapp_message()

# Start scheduler
scheduler = BackgroundScheduler(timezone="Africa/Nairobi")
scheduler.add_job(send_daily_reading, 'cron', hour=6, minute=0)
scheduler.start()

@app.get("/")
def home():
    return {"message": "✅ Bible Bot is running"}

@app.get("/send_message")
def manual_send():
    send_whatsapp_message()
    return {"message": "✅ Message sent manually"}


import json

# Load reading plan
try:
    with open("reading_plan.json", "r", encoding="utf-8") as f:
        reading_plan = json.load(f)
except Exception as e:
    print(f"❌ Error loading reading plan: {e}")
    reading_plan = []

from fastapi import FastAPI
from datetime import datetime

app = FastAPI()

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


from fastapi import FastAPI, Request
from supabase import create_client
from dotenv import load_dotenv
import os
import json

app = FastAPI()

# Load .env
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Load the Bible reading plan
try:
    with open("reading_plan.json", "r", encoding="utf-8") as f:
        reading_plan = json.load(f)
    print("✅ Reading plan loaded")
except Exception as e:
    print(f"❌ Error loading reading plan: {e}")
    reading_plan = []

# ----------- Supabase Interaction Logic ------------

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

# ---------- WhatsApp Webhook --------------

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
        # Placeholder — add APScheduler job if needed
        return {"message": "⏰ A reminder has been scheduled for 8 PM!"}

    else:
        return {
            "message": "🤖 Bible Bot\nCommands:\nREAD – Mark today's reading\nSTATS – See progress\nREMIND – Get reminder at 8 PM"
        }

@app.get("/")
def home():
    return {"message": "📖 Bible Bot is running"}


