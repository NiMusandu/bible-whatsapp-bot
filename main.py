from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from send import send_whatsapp_message
from routes import setup_routes

app = FastAPI()

# Load routes from another file
setup_routes(app)

# Scheduled job for daily reading
def send_daily_reading():
    print(f"⏰ Sending daily reading at {datetime.now()}")
    send_whatsapp_message()

scheduler = BackgroundScheduler(timezone="Africa/Nairobi")
scheduler.add_job(send_daily_reading, "cron", hour=6, minute=0)
scheduler.start()

@app.get("/")
def root():
    return {"message": "✅ Bible Bot is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=10000)
s