import os
from dotenv import load_dotenv
from supabase import create_client, Client
import datetime
import uuid

# Load environment variables
load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

if not url or not key:
    print("Error: Supabase credentials not found in env!")
    exit(1)

try:
    supabase: Client = create_client(url, key)
    print("Supabase client initialized.")
except Exception as e:
    print(f"Failed to init Supabase: {e}")
    exit(1)

def test_db_operations():
    test_user_id = "test_user_" + str(uuid.uuid4())
    print(f"Testing with User ID: {test_user_id}")

    # 1. Upsert User (REQUIRED for Foreign Key)
    user_record = {
        "id": test_user_id,
        "email": f"test_{test_user_id}@example.com", # Unique email to avoid collision
        "updated_at": datetime.datetime.now().isoformat()
    }
    
    try:
        response = supabase.table("users").upsert(user_record).execute()
        print("User Upsert successful:", response)
    except Exception as e:
        print(f"User Upsert failed: {e}")
        return

    # 2. Insert analysis history
    record = {
        "user_email": user_record["email"], 
        "clerk_user_id": test_user_id, 
        "filename": "test_image.png",
        "prediction": "No_DR",
        "confidence": 0.99,
        "is_noisy": False,
        "tips": ["Test tip"], 
        "report_url": "http://example.com/report.pdf",
        "image_url": "http://example.com/image.png",
        "created_at": datetime.datetime.now().isoformat()
    }
    
    try:
        response = supabase.table("analysis_history").insert(record).execute()
        print("History Insert successful:", response)
    except Exception as e:
        print(f"History Insert failed: {e}")
        # Clean up user if history failed
        supabase.table("users").delete().eq("id", test_user_id).execute()
        return

    # 3. Fetch the record
    try:
        response = supabase.table("analysis_history").select("*").eq("clerk_user_id", test_user_id).execute()
        data = response.data
        if data and len(data) > 0:
            print("Fetch successful. Record found.")
            print(f"Count: {len(data)}")
        else:
            print("Fetch returned no data!")
    except Exception as e:
        print(f"Fetch failed: {e}")

    # 4. Clean up (Delete)
    try:
        # Delete history first
        supabase.table("analysis_history").delete().eq("clerk_user_id", test_user_id).execute()
        # Delete user
        supabase.table("users").delete().eq("id", test_user_id).execute()
        print("Cleanup successful.")
    except Exception as e:
        print(f"Cleanup failed: {e}")

if __name__ == "__main__":
    test_db_operations()
