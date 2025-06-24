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
