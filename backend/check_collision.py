import os
from dotenv import load_dotenv
from supabase import create_client, Client
import datetime
import uuid

# Load environment variables
load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def test_collision():
    # User 1
    uid1 = "user_" + str(uuid.uuid4())
    # User 2
    uid2 = "user_" + str(uuid.uuid4())
    
    email = "anonymous_test@example.com" # Simulating "Anonymous"

    print(f"Testing collision with Email: {email}")

    # Upsert User 1
    try:
        r1 = supabase.table("users").upsert({
            "id": uid1,
            "email": email,
            "updated_at": datetime.datetime.now().isoformat()
        }).execute()
        print("User 1 Upsert Success")
    except Exception as e:
        print(f"User 1 Upsert Failed: {e}")

    # Upsert User 2 (Should fail if email is unique)
    try:
        r2 = supabase.table("users").upsert({
            "id": uid2,
            "email": email,
            "updated_at": datetime.datetime.now().isoformat()
        }).execute()
        print("User 2 Upsert Success")
    except Exception as e:
        print(f"User 2 Upsert Failed (EXPECTED): {e}")

    # Cleanup
    try:
        supabase.table("users").delete().eq("id", uid1).execute()
        supabase.table("users").delete().eq("id", uid2).execute() 
        # (user 2 might not exist if failed)
    except:
        pass

if __name__ == "__main__":
    test_collision()
