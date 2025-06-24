from supabase import create_client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get credentials from .env
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

# Create Supabase client
supabase = create_client(url, key)

# Test insert into table "progress"
data = {"user_id": "254700123456", "days_completed": 1}
response = supabase.table("progress").insert(data).execute()

print(response)