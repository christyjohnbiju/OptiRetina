from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import shutil
import os
import uuid
import datetime
import mimetypes
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

from preprocessing import preprocess_image
from ml_model import DRModel
from report_utils import generate_pdf
from chatbot_service import ChatbotService
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="OptiRetina Backend")

# Initialize Supabase
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

if not url or not key:
    print("Warning: Supabase credentials not found in env!")
    supabase: Client = None
else:
    try:
        supabase: Client = create_client(url, key)
        print("Supabase client initialized.")
    except Exception as e:
        print(f"Failed to init Supabase: {e}")
        supabase = None

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Security: Restrict in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup directories (Still needed for temporary processing)
UPLOAD_DIR = "uploads"
REPORT_DIR = "reports"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)

# Helper: Upload to Supabase Storage
def upload_to_supabase(file_path: str, bucket: str, destination_name: str, content_type: str = "image/png"):
    if not supabase:
        return None
    try:
        with open(file_path, 'rb') as f:
            supabase.storage.from_(bucket).upload(
                file=f,
                path=destination_name,
                file_options={"content-type": content_type}
            )
        # Get Public URL
        return supabase.storage.from_(bucket).get_public_url(destination_name)
    except Exception as e:
        print(f"Upload to Supabase failed: {e}")
        return None

# Initialize Model (Global load)
print("Initializing AI Model (ResNet50 Fold 4)...")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "new_models")
dr_model = DRModel(MODEL_DIR)
chatbot_service = ChatbotService()

HEALTH_TIPS = {
    "No_DR": ["Maintain healthy diet.", "Yearly eye exams.", "Regular exercise."],
    "Mild": ["Control blood sugar strictly.", "Monitor blood pressure.", "Follow up in 6-12 months."],
    "Moderate": ["Consult retina specialist.", "Consider laser therapy if needed.", "More frequent checkups (3-6 months)."],
    "Severe": ["Urgent ophthalmology referral.", "Glycemic control is critical.", "Possible surgical intervention."],
    "Proliferate_DR": ["Immediate treatment required.", "High risk of vision loss.", "Anti-VEGF or Pan-retinal photocoagulation."],
    "Uncertain": ["Low confidence – requires ophthalmologist review.", "Please retake the image to ensure quality.", "Consult a doctor for manual diagnosis."],
    "Invalid_Image": ["The uploaded image does not appear to be a valid retina/fundus image.", "Please upload a clear picture of the retina for analysis."]
}

@app.get("/")
def read_root():
    return {"message": "OptiRetina Backend is running. Visit /docs for API documentation."}

@app.get("/health")
def health_check():
    return {
        "status": "ok", 
        "model_loaded": dr_model.model is not None,
        "supabase_connected": supabase is not None
    }

from auth_dependency import get_current_user_id

@app.get("/history")
def get_history(user_id: str = Depends(get_current_user_id)):
    if not supabase:
        return []
    
    try:
        # Fetch from 'analysis_history' table, filtered by user_id
        response = supabase.table("analysis_history").select("*").eq("clerk_user_id", user_id).order("created_at", desc=True).execute()
        return response.data
    except Exception as e:
        print(f"Fetch history failed: {e}")
        return []

def get_clerk_email(user_id: str):
    """Fetch user logic from Clerk Backend API"""
    clerk_key = os.environ.get("CLERK_SECRET_KEY")
    if not clerk_key:
        return "Unknown"
    
    try:
        import requests
        headers = {"Authorization": f"Bearer {clerk_key}"}
        resp = requests.get(f"https://api.clerk.com/v1/users/{user_id}", headers=headers)
        if resp.status_code == 200:
            data = resp.json()
            # Return primary email
            for email in data.get("email_addresses", []):
                if email.get("id") == data.get("primary_email_address_id"):
                    return email.get("email_address")
                # Fallback to first
            if data.get("email_addresses"):
                return data["email_addresses"][0]["email_address"]
    except Exception as e:
        print(f"Clerk API Error: {e}")
    return "Unknown"

@app.post("/analyze")
async def analyze_retina(
    file: UploadFile = File(...), 
    patient_id: str = "Anonymous", # Legacy: Frontend might send this, but we prefer Clerk Email
    user_id: str = Depends(get_current_user_id)
):
    try:
        # 1. Save upload temporarily
        content = await file.read()
        file_id = str(uuid.uuid4())
        filename = f"{file_id}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        
        with open(file_path, "wb") as f:
            f.write(content)
        
        # 2. Preprocess
        print("Starting preprocessing...")
        batch_img, processed_img_cv2, is_noisy, is_valid = preprocess_image(content)
        
        if not is_valid:
            print("Validation failed. Not a valid fundus image.")
            label = "Invalid_Image"
            confidence = 1.0
            
            import cv2
            import numpy as np
            nparr = np.frombuffer(content, np.uint8)
            img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            # Keep as BGR, but resize to standard for consistency
            processed_img_cv2 = cv2.resize(img_bgr, (224, 224)) if img_bgr is not None else np.zeros((224,224,3), np.uint8)
            gradcam_img = processed_img_cv2.copy()
            tips = HEALTH_TIPS["Invalid_Image"]
        else:
            print(f"Preprocessing done. Batch shape: {batch_img.shape}, Original shape: {processed_img_cv2.shape}")
            
            # 3. Predict & Explain
            print("Starting prediction...")
            label, confidence, gradcam_img = dr_model.predict(batch_img, processed_img_cv2)
            print(f"Prediction done. Label: {label}, Conf: {confidence}")
            tips = HEALTH_TIPS.get(label, ["Consult a doctor."])
        pdf_filename = f"report_{file_id}.pdf"
        pdf_path = os.path.join(REPORT_DIR, pdf_filename)
        
        # Determine User Email for Report/DB
        user_email = patient_id
        if user_email == "Anonymous" or user_email == "undefined":
            # Try to fetch from Clerk
            fetched_email = get_clerk_email(user_id)
            if fetched_email != "Unknown":
                user_email = fetched_email

        # Final DB Email (Ensure Uniqueness)
        db_email = user_email
        if db_email in ["Anonymous", "undefined", "Unknown"]:
            # Generate unique placeholder to satisfy DB Unique constraint
            db_email = f"anonymous_{user_id}@optiretina.local"

        generate_pdf(user_email, label, confidence, processed_img_cv2, gradcam_img, tips, pdf_path)
        
        # Save to History (In-Memory/Local)
        import json
        timestamp = datetime.datetime.now().isoformat()
        
        # 5. Upload to Supabase Storage
        image_public_url = None
        pdf_public_url = None
        
        if supabase:
            # Upload Original Image
            mime_type, _ = mimetypes.guess_type(file.filename)
            if not mime_type: mime_type = "image/png"
            
            original_url = upload_to_supabase(file_path, "uploads", filename, mime_type)
            image_public_url = original_url if original_url else f"/uploads/{filename}"

            # Upload Report PDF
            pdf_url = upload_to_supabase(pdf_path, "reports", pdf_filename, "application/pdf")
            pdf_public_url = pdf_url if pdf_url else f"/reports/{pdf_filename}"
        
        else:
            print("Supabase not active, skipping upload.")
            image_public_url = "error_no_db"
            pdf_public_url = "error_no_db"

        # 6. Save to Supabase Database
        if supabase:
            # Sync User to 'users' table
            try:
                # Upsert user to ensure they exist in our DB
                user_record = {
                    "id": user_id,
                    "email": db_email,
                    "updated_at": datetime.datetime.now().isoformat()
                }
                supabase.table("users").upsert(user_record).execute()
            except Exception as e:
                print(f"User sync to 'users' table failed (Table might fail or strict schema): {e}")

            # Save Analysis Record
            record = {
                "user_email": db_email, 
                "clerk_user_id": user_id, 
                "filename": file.filename,
                "prediction": label,
                "confidence": float(confidence),
                "is_noisy": bool(is_noisy),
                "tips": tips, 
                "report_url": pdf_public_url,
                "image_url": image_public_url
            }
            try:
                supabase.table("analysis_history").insert(record).execute()
                print("Record saved to Supabase DB.")
            except Exception as e:
                print(f"DB Insert failed: {e}")

        return JSONResponse({
            "success": True,
            "prediction": label,
            "confidence": confidence,
            "is_noisy": bool(is_noisy),
            "report_url": pdf_public_url, 
            "image_url": image_public_url,
            "tips": tips
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

        raise HTTPException(status_code=500, detail=str(e))

# Chatbot Endpoint
class ChatRequest(BaseModel):
    query: str
    context: dict

@app.post("/chatbot/query")
async def chat_query(request: ChatRequest, user_id: str = Depends(get_current_user_id)):
    try:
        response = chatbot_service.get_response(request.query, request.context)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
