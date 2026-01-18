import cv2
import numpy as np
import os
import tensorflow as tf
from preprocessing import preprocess_image
from ml_model import DRModel

def test_inference():
    # Create a dummy image (224, 224, 3) random noise
    print("Generating dummy image...")
    dummy_img = np.random.randint(0, 255, (300, 300, 3), dtype=np.uint8)
    _, buf = cv2.imencode(".jpg", dummy_img)
    content = buf.tobytes()

    print("Testing Preprocessing...")
    batch_img, processed_bgr, is_noisy = preprocess_image(content)
    print(f"Batch Shape: {batch_img.shape}")
    print(f"Batch Min: {batch_img.min():.4f}, Batch Max: {batch_img.max():.4f}")
    print(f"Processed BGR Shape: {processed_bgr.shape}")
    
    # Expected min/max for MobileNetV3 preprocess_input is usually -1 to 1 (if it uses inception style)
    # or 0 to 1 depending on the specific implementation version, but usually tf.keras.applications.mobilenet_v3 uses 0-255 -> 0-1 or -1 to 1.
    # Actually, tf.keras.applications.mobilenet_v3.preprocess_input expects inputs in range [0, 255] and converts them.
    # Wait, documentation says: "The inputs are expected to be 0-255." and it scales them.
    # Let's verify what values we get to ensure it's doing something reasonable.

    print("\nTesting Model Loading & Prediction...")
    try:
        dr_model = DRModel("models")
        # Ensure models exist or handle gracefully
        if not dr_model.models:
            print("No models found in 'models' directory. Cannot test prediction.")
            return

        print("Predicting...")
        # predict takes (img_array, original_image_bgr)
        # We pass the preprocessed batch and the resized BGR image (which predict uses for gradcam overlay)
        label, conf, overlay = dr_model.predict(batch_img, processed_bgr)
        print(f"Prediction Result: Label={label}, Confidence={conf}")
        print(f"Overlay shape: {overlay.shape}")
        
    except Exception as e:
        print(f"Model prediction failed or skipped: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_inference()
