from fastapi import Request
from supabase import create_client
import os
from dotenv import load_dotenv
import json

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

try:
    with open("reading_plan.json", "r", encoding="utf-8") as f:
        reading_plan = json.load(f)
except Exception as e:
    print(f"❌ Error loading plan: {e}")
    reading_plan = []

def setup_routes(app):
    @app.get("/reading/today")
    def today_reading():
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        for entry in reading_plan:
            if entry["date"] == today:
                return entry
        return {"message": "📅 No reading for today."}

    @app.post("/webhook")
    async def webhook(request: Request):
        data = await request.json()
        body = data.get("Body", "").strip().upper()
        sender = data.get("From", "").replace("whatsapp:", "")

        print(f"📩 {sender} said: {body}")

        if body == "READ":
            mark_as_read(sender)
            return {"message": "✅ Marked today's reading as complete."}
        elif body == "STATS":
            days = get_user_stats(sender)
            return {"message": f"📊 You’ve completed {days} days!"}
        elif body == "REMIND":
            return {"message": "⏰ Reminder set for 8 PM!"}
        else:
            return {
                "message": "🤖 Commands:\nREAD – Mark today's reading\nSTATS – Check progress\nREMIND – Set reminder"
            }

def mark_as_read(user_id):
    res = supabase.table("progress").select("*").eq("user_id", user_id).execute()
    if res.data:
        current = res.data[0]["days_completed"]
        supabase.table("progress").update({"days_completed": current + 1}).eq("user_id", user_id).execute()
    else:
        supabase.table("progress").insert({"user_id": user_id, "days_completed": 1}).execute()

def get_user_stats(user_id):
    res = supabase.table("progress").select("*").eq("user_id", user_id).execute()
    if res.data:
        return res.data[0]["days_completed"]
    return 0
