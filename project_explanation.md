# OptiRetina - Project Repository Analysis & Review Guide

## 1. Executive Summary
**OptiRetina** is a comprehensive medical AI system designed for the automated detection and grading of **Diabetic Retinopathy (DR)** from retinal fundus images. The system provides a seamless end-to-end workflow: from secure image upload to AI-powered analysis (grading DR severity), explainable AI visualization (Grad-CAM), PDF report generation, and an interactive AI Assistant for patient education.

## 2. Technical Architecture

### 2.1 Frontend (Client-Side)
- **Framework**: [Next.js 16](https://nextjs.org/) (React Framework) with TypeScript.
- **Styling**: [Tailwind CSS](https://tailwindcss.com/) for responsive design.
- **UI Components**: [Shadcn UI](https://ui.shadcn.com/) (Cards, Tabs, Buttons, Sheets) based on Radix UI primitives.
- **Authentication**: [Clerk](https://clerk.com/) (`@clerk/nextjs`) for secure user management (Login/Signup).
- **HTTP Client**: `axios` for communicating with the Python backend.
- **Icons**: `lucide-react`.

### 2.2 Backend (Server-Side)
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python) for high-performance API endpoints.
- **ML Framework**: `TensorFlow` / `Keras` for model inference.
- **Database/Storage**: [Supabase](https://supabase.com/) (PostgreSQL) for saving analysis history and Cloud Storage for report PDFs.
- **PDF Generation**: `ReportLab` for programmatically creating medical certificates.
- **AI Chatbot**: Integration with **Groq** (Llama-3.3-70b) or **OpenAI** (GPT-3.5) for LLM-based assistants.

---

## 3. Deep Dive: Backend Analysis Logic

### 3.1 Preprocessing Pipeline (`backend/preprocessing.py`)
Before any AI analysis, the raw image undergoes a rigorous preprocessing pipeline to standardize input and enhance critical features.
1.  **Circle Crop**:
    -   **Technique**: Detects the circular fundus region and crops out the black borders.
    -   **Why?**: Removes irrelevant black pixels that can bias the model or waste computational resources.
2.  **Ben Graham's Method (Gaussian Filtering)**:
    -   **Concept**: An image enhancement technique widely used in DR detection (e.g., Kaggle competitions).
    -   **Formula**: `Image = 4 * Image - 4 * GaussianBlur(Image) + 128`
    -   **Result**: Normalizes lighting conditions and enhances the contrast of blood vessels and lesions (exudates, hemorrhages), giving the image a distinctive "orange/brown" high-contrast look.
3.  **Resizing**: Standardized to `224 x 224` pixels.
4.  **Normalization**: Pixel values are scaled to the range `[-1, 1]` for MobileNetV3 input.

### 3.2 Machine Learning Model (`backend/ml_model.py`)
-   **Architecture**: **MobileNetV3 Large**.
    -   **Why?**: Chosen for its efficiency and speed (low latency) while maintaining high accuracy, making it suitable for deployment.
-   **Ensembling Technique**: **Soft Voting**.
    -   **Implementation**: Five separate models (5-Fold Cross-Validation splits) are loaded (`mobilenetv3_fold_1.keras` to `...fold_5.keras`).
    -   **Inference**: The input image is passed through *all 5 models*.
    -   **Aggregation**: We take the **average of the probability vectors** output by all 5 models.
    -   **Decision**: The class with the highest average probability is selected as the final prediction.
    -   **Benefit**: Reduces variance and improves robustness compared to a single model.
-   **Classes**: `No_DR`, `Mild`, `Moderate`, `Severe`, `Proliferative`.

### 3.3 Explainable AI (Grad-CAM)
-   **Technique**: Gradient-weighted Class Activation Mapping (Grad-CAM).
-   **Logic**:
    1.  Hooks into the last convolutional layer of the model (e.g., `Conv_1`).
    2.  Computes gradients of the predicted class score with respect to the feature maps.
    3.  Generates a heatmap highlighting region of the image that contributed most to the decision (e.g., clustering of microaneurysms).
    4.  Overlays this heatmap on the original image for the final report.

---

## 4. Key Features & Workflows

### 4.1 Image Upload & Analysis Flow
1.  **Frontend**: User uploads image via drag-and-drop (`dashboard/upload/page.tsx`).
2.  **API Call**: `POST /analyze` sends `FormData` to backend.
3.  **Processing**:
    -   Backend preprocesses image.
    -   Runs Ensemble Inference.
    -   Generates Grad-CAM overlay.
4.  **Report Generation**:
    -   `backend/report_utils.py` uses **ReportLab** to draw a PDF canvas.
    -   Embeds specific fonts, patient ID, diagnosis, health tips, and both Original/Grad-CAM images.
    -   Saves PDF to Supabase Storage.
5.  **Result**: Returns JSON with Prediction, Confidence, Health Tips, and the PDF URL.

### 4.2 Medical Chatbot Assistant
-   **Tech**: Powered by **Llama-3.3-70b-versatile** via the Groq API (extremely fast & free tier).
-   **Context-Aware**: The chatbot does *not* just answer generic questions. It receives the **specific diagnosis** (e.g., "Mild DR") and **health tips** as a "System Prompt".
-   **Safety Rails**: Explicitly instructed *never* to provide dosage/prescriptions or confident prognoses, acting only as a supportive assistant.
-   **UI**: A chat interface (`Chatbot.tsx`) with predefined quick questions and a responsive design.

### 4.3 Patient History
-   **Database**: Supabase PostgreSQL.
-   **Table**: `analysis_results` stores `patient_id`, `prediction`, `confidence`, and file paths.
-   **Privacy**: Using Row Level Security (RLS) standards (conceptually) where users only access their own records via Clerk integration.

---

## 5. Review Checklist (Q&A Prep)

| Area | Question | Answer |
| :--- | :--- | :--- |
| **Model** | Which model architecture? | MobileNetV3 Large (Pretrained on ImageNet, fine-tuned on TF/Kaggle DR datasets). |
| **Ensemble** | How is the consensus reached? | **Soft Voting**: Averaging the softmax probability outputs of 5 models. |
| **Preprocessing** | Why does the image look orange/brown? | That is **Ben Graham's method** (Gaussian filtering) to enhance lesion contrast and normalize lighting. |
| **Explanation** | How do we know the AI isn't guessing? | We use **Grad-CAM** to visualize the exact regions (lesions/vessels) the model focused on. |
| **Report** | How is the PDF made? | Typically Python `ReportLab` library, generated dynamically on the server. |
| **Chatbot** | Is it a fixed script? | No, it's a Generative LLM (Llama-3.3) running with a custom prompt injected with the patient's specific report context. |

---

## 6. Directory Structure
```
/
├── backend/
│   ├── models/                # 5x .keras model files
│   ├── chatbot_service.py     # Groq/OpenAI integration
│   ├── ml_model.py            # Ensemble & Grad-CAM logic
│   ├── preprocessing.py       # Ben Graham & Crop logic
│   ├── report_utils.py        # PDF Generation
│   ├── main.py                # FastAPI Routes
│   └── requirements.txt       # Dependencies
├── frontend/
│   ├── src/app/dashboard/     # Dashboard Pages (Next.js)
│   ├── src/components/        # UI Components (Chatbot, Sidebar)
│   ├── package.json           # Frontend Deps
│   └── ...
└── ...
```
