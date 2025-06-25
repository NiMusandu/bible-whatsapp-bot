print("✅ DEBUG: SUPABASE_URL =", os.getenv("SUPABASE_URL"))
print("✅ DEBUG: SUPABASE_KEY =", os.getenv("SUPABASE_KEY")[:6], "...")  # mask key


from fastapi import FastAPI, Request
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client
import json, os

# 🔒 Optional: only load .env locally
if os.getenv("RUN_LOCAL", "0") == "1":
    load_dotenv()

# 📦 Check if Supabase credentials exist
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# 👀 Sanity check print — will show in Render logs
print("🔍 SUPABASE_URL seen by Render:", SUPABASE_URL)

if not SUPABASE_URL or not SUPABASE_KEY:
    raise Exception("❌ Missing Supabase credentials")

# ✅ Connect Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# 📖 Load Bible reading plan
try:
    with open("reading_plan.json", "r", encoding="utf-8") as f:
        reading_plan = json.load(f)
    print("✅ Reading plan loaded")
except Exception as e:
    print(f"❌ Error loading reading plan: {e}")
    reading_plan = []

# 🚀 App instance
app = FastAPI()

# 🕕 Scheduled Job (send daily reading)
def send_whatsapp_message():
    # Import here to avoid early crash if misconfigured
    from twilio.rest import Client

    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_TOKEN")
    sender = os.getenv("TWILIO_NUMBER")
    recipients = os.getenv("RECIPIENT_NUMBER", "").split(";")

    today = datetime.now().date().strftime("%Y-%m-%d")
    reading = next((r for r in reading_plan if r["date"] == today), None)

    if not reading:
        print("⚠️ No reading found for today.")
        return

    msg = (
        f"📖 Day {reading['day']} Bible Reading Plan\n\n"
        f"📜 OT: {reading['old_testament']}\n"
        f"📘 NT: {reading['new_testament']}\n"
        f"🎵 Psalm/Gospel: {reading['psalm_or_gospel']}"
    )

    client = Client(account_sid, auth_token)
    for number in recipients:
        if number.strip():
            client.messages.create(
                from_=sender,
                to=number.strip(),
                body=msg
            )
            print(f"✅ Sent to {number.strip()}")

# ⏰ APScheduler config
scheduler = BackgroundScheduler(timezone="Africa/Nairobi")
scheduler.add_job(send_whatsapp_message, 'cron', hour=6, minute=0)
scheduler.start()

# 🌐 Endpoints

@app.get("/")
def home():
    return {"message": "📖 Bible Bot is running"}

@app.get("/reading/today")
def get_today_reading():
    today = datetime.now().date().strftime("%Y-%m-%d")
    for entry in reading_plan:
        if entry["date"] == today:
            return {
                "day": entry["day"],
                "old_testament": entry["old_testament"],
                "new_testament": entry["new_testament"],
                "psalm_or_gospel": entry["psalm_or_gospel"]
            }
    return {"message": "📅 No reading found for today."}

@app.get("/send_message")
def manual_send():
    send_whatsapp_message()
    return {"message": "✅ Message sent manually"}

# 🔄 Supabase progress tracking

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

# 📩 WhatsApp Webhook
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
            "message": "🤖 Bible Bot\nCommands:\nREAD – Mark today's reading\nSTATS – See progress\nREMIND – Get reminder at 8 PM"
        }

# 🏁 Local debug
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=10000)



