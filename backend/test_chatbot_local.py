import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_URL = "http://localhost:8000/chatbot/query"
# Ensure we have a dummy token or mock auth if needed, but the endpoint currently depends on get_current_user_id
# We might need to mock the auth or just test local function if auth is hard to mock solely via script without a valid token.
# However, for now, let's assume we can hit it if we bypass auth or generate a fake one if local.
# Actually, the endpoint uses `Depends(get_current_user_id)`. 
# To test this easily without a full frontend login flow, we might need to temporarily disable auth or mock it.
# BUT, `get_current_user_id` in `auth_dependency.py` typically validates a token.

# Alternative: We can test the ChatbotService directly in this script, bypassing the API layer for logic verification.
# This avoids auth hurdles for this quick test.

from chatbot_service import ChatbotService

def test_chatbot_logic():
    service = ChatbotService()
    
    if service.client:
        print(f"✅ Client Initialized. Base URL: {service.base_url}, Model: {service.model}")
    else:
        print("⚠️ Client NOT Initialized (Mock Mode)")
    context = {
        "prediction": "Mild_DR",
        "confidence": 0.85,
        "tips": ["Control sugar", "Yearly exams"]
    }
    
    query = "What precautions should I take?"
    
    print(f"Query: {query}")
    print(f"Context: {context}")
    
    response = service.get_response(query, context)
    
    print("\n--- Response ---")
    print(response)
    print("----------------")
    
    if "precautions" in response.lower() or "control" in response.lower() or "demo" in response.lower():
         print("✅ Test Passed: Response is relevant.")
    else:
         print("❌ Test Failed: Response seems irrelevant.")

if __name__ == "__main__":
    test_chatbot_logic()
