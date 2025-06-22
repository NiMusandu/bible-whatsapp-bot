import json

# Load reading plan
try:
    with open("reading_plan.json", "r", encoding="utf-8") as f:
        reading_plan = json.load(f)
except Exception as e:
    print(f"❌ Error loading reading plan: {e}")
    reading_plan = []
