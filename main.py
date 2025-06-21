import json
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from dotenv import load_dotenv
import os
import requests

load_dotenv()

app = FastAPI()

# Load reading plan
with open("reading_plan.json", "r") as f:
    reading_plan = json.load(f)

# In-memory progress tracker
user_progress = {}

# Twilio credentials from .env
TOKEN = os.getenv("TWILIO_TOKEN")
FROM = os.getenv("TWILIO_NUMBER")
TO = os.getenv("RECIPIENT_NUMBER")

def send_to_whatsapp(message: str):
    url = "https://api.ultramsg.com/instanceXXXXX/messages/chat"  # Use Ultramsg or Twilio API
    payload = {
        "token": TOKEN,
        "to": TO,
        "body": message
    }
    try:
        r = requests.post(url, data=payload)
        print("Message sent:", r.status_code)
    except Exception as e:
        print("Error sending:", e)

def send_daily_reading():
    today = datetime.now().strftime("%Y-%m-%d")
    for entry in reading_plan:
        if entry["date"] == today:
            message = (
                f"📖 Day {entry['day']} Bible Reading\n"
                f"Old Testament: {entry['old_testament']}\n"
                f"New Testament: {entry['new_testament']}\n"
                "Reply READ | REMIND | STATS"
            )
            send_to_whatsapp(message)
            break

# Schedule job daily at 6:00 AM
scheduler = BackgroundScheduler()
scheduler.add_job(send_daily_reading, 'cron', hour=6, minute=0)
scheduler.start()

@app.post("/webhook")
async def receive_command(request: Request):
    data = await request.json()
    user_id = data.get("from", "unknown_user")
    message = data.get("body", "").strip().upper()

    if message == "READ":
        user_progress[user_id] = user_progress.get(user_id, 0) + 1
        return JSONResponse({"reply": "✅ Reading marked complete."})

    elif message == "REMIND":
        return JSONResponse({"reply": "⏰ You’ll be reminded at 8:00 PM."})

    elif message == "STATS":
        read = user_progress.get(user_id, 0)
        return JSONResponse({"reply": f"📊 You’ve completed {read} day(s)."})

    return JSONResponse({"reply": "❓ Unknown command. Use READ, REMIND, STATS."})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
