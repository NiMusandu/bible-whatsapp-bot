from supabase import create_client
import os
from dotenv import load_dotenv

# Load .env file if you're using one
load_dotenv()

# Supabase credentials
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

# Test insert
try:
    data = {"user_id": "254700123456", "days_completed": 1}
    result = supabase.table("progress").insert(data).execute()
    print("✅ Insert successful:", result)
except Exception as e:
    print("❌ Insert failed:", e)