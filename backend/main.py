from fastapi import FastAPI, File, UploadFile, HTTPException
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
print("Initializing AI Model...")
# Initialize Model (Ensemble load)
print("Initializing AI Ensemble...")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models")
dr_model = DRModel(MODEL_DIR)

HEALTH_TIPS = {
    "No_DR": ["Maintain healthy diet.", "Yearly eye exams.", "Regular exercise."],
    "Mild": ["Control blood sugar strictly.", "Monitor blood pressure.", "Follow up in 6-12 months."],
    "Moderate": ["Consult retina specialist.", "Consider laser therapy if needed.", "More frequent checkups (3-6 months)."],
    "Severe": ["Urgent ophthalmology referral.", "Glycemic control is critical.", "Possible surgical intervention."],
    "Proliferate_DR": ["Immediate treatment required.", "High risk of vision loss.", "Anti-VEGF or Pan-retinal photocoagulation."],
    "Uncertain": ["Low confidence – requires ophthalmologist review.", "Please retake the image to ensure quality.", "Consult a doctor for manual diagnosis."]
}

@app.get("/health")
def health_check():
    return {
        "status": "ok", 
        "model_loaded": dr_model.model is not None,
        "supabase_connected": supabase is not None
    }

@app.get("/history")
def get_history():
    if not supabase:
        # Fallback to empty or local logic if needed, but for now returned empty
        return []
    
    try:
        # Fetch from 'analysis_history' table
        response = supabase.table("analysis_history").select("*").order("created_at", desc=True).execute()
        return response.data
    except Exception as e:
        print(f"Fetch history failed: {e}")
        return []

@app.post("/analyze")
async def analyze_retina(file: UploadFile = File(...), patient_id: str = "Anonymous"):
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
        batch_img, processed_img_cv2, is_noisy = preprocess_image(content)
        print(f"Preprocessing done. Batch shape: {batch_img.shape}, Original shape: {processed_img_cv2.shape}")
        
        # 3. Predict & Explain
        print("Starting prediction...")
        label, confidence, gradcam_img = dr_model.predict(batch_img, processed_img_cv2)
        print(f"Prediction done. Label: {label}, Conf: {confidence}")
        
        # 4. Generate Report
        tips = HEALTH_TIPS.get(label, ["Consult a doctor."])
        pdf_filename = f"report_{file_id}.pdf"
        pdf_path = os.path.join(REPORT_DIR, pdf_filename)
        
        
        generate_pdf(patient_id, label, confidence, processed_img_cv2, gradcam_img, tips, pdf_path)
        
        # Save to History
        import json
        timestamp = datetime.datetime.now().isoformat()
        record = {
            "id": file_id,
            "filename": file.filename,
            "prediction": label,
            "confidence": confidence,
            "tips": tips,
            "report_url": f"/reports/{pdf_filename}",
            "image_url": f"/uploads/{filename}",
            "date": timestamp,
            "is_noisy": bool(is_noisy)
        }
        
        
        # 5. Upload to Supabase Storage
        image_public_url = None
        pdf_public_url = None
        
        if supabase:
            # Upload Original Image
            # Determine content type
            mime_type, _ = mimetypes.guess_type(file.filename)
            if not mime_type: mime_type = "image/png"
            
            # Using the saved temp file for upload is easiest
            original_url = upload_to_supabase(file_path, "uploads", filename, mime_type)
            image_public_url = original_url if original_url else f"/uploads/{filename}" # Fallback? No, just broken link if fails

            # Upload Report PDF
            pdf_url = upload_to_supabase(pdf_path, "reports", pdf_filename, "application/pdf")
            pdf_public_url = pdf_url if pdf_url else f"/reports/{pdf_filename}"
        
        else:
            # Fallback (should not happen if key provided)
            print("Supabase not active, skipping upload.")
            image_public_url = "error_no_db"
            pdf_public_url = "error_no_db"

        # 6. Save to Supabase Database
        if supabase:
            record = {
                "user_email": patient_id, # Using patient_id as email/user identifier per user request logic
                "filename": file.filename,
                "prediction": label,
                "confidence": float(confidence),
                "is_noisy": bool(is_noisy),
                "tips": tips, # Supabase array(text)
                "report_url": pdf_public_url,
                "image_url": image_public_url
                # created_at is auto
            }
            try:
                supabase.table("analysis_history").insert(record).execute()
                print("Record saved to Supabase DB.")
            except Exception as e:
                print(f"DB Insert failed: {e}")

        # Cleanup Temp Files? optional, but good for serverless. We keep for now for debug.

        return JSONResponse({
            "success": True,
            "prediction": label,
            "confidence": confidence,
            "is_noisy": bool(is_noisy),
            "report_url": pdf_public_url, # Frontend uses this link
            "image_url": image_public_url,
            "tips": tips
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
