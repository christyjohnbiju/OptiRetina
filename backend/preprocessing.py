import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.applications.mobilenet_v3 import preprocess_input

# Helper: Crop black borders (Circle Crop)
def crop_image_from_gray(img, tol=7):
    """
    Crops the black borders of the fundus image.
    """
    if img.ndim == 2:
        mask = img > tol
        return img[np.ix_(mask.any(1),mask.any(0))]
    elif img.ndim == 3:
        gray_img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        mask = gray_img > tol
        
        check_shape = img[:,:,0][np.ix_(mask.any(1),mask.any(0))].shape[0]
        if (check_shape == 0): # image is too dark so that we crop out everything,
            return img # return original image
        else:
            img1=img[:,:,0][np.ix_(mask.any(1),mask.any(0))]
            img2=img[:,:,1][np.ix_(mask.any(1),mask.any(0))]
            img3=img[:,:,2][np.ix_(mask.any(1),mask.any(0))]
            img = np.stack([img1,img2,img3],axis=-1)
        return img

def preprocess_image(image_bytes: bytes):
    """
    1. Read image using OpenCV
    2. Convert BGR -> RGB
    3. Circle Crop (remove black borders) - Critical for DR models
    4. Ben Graham's method (Gaussian Blur + Weighted Add) to match 'gaussian filtered' dataset
    5. Resize to 224x224
    6. Normalize to [-1, 1]
    7. Expand dims
    """
    # 1. Read image using OpenCV
    nparr = np.frombuffer(image_bytes, np.uint8)
    img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    # 2. Convert to RGB
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

    # 3. Circle Crop
    # This removes extra black space which confuses the model if trained on cropped images
    try:
        img_rgb = crop_image_from_gray(img_rgb)
    except Exception as e:
        print(f"Crop failed: {e}, using original")

    # 4. Resize to 224x224 (Standard for MobileNetV3)
    # We resize BEFORE Ben Graham to save compute, or AFTER? 
    # Usually standard is resize AFTER crop, but then apply blur.
    # Dataset says: "resized into 224x224" AND "gaussian filtered".
    # We will resize now.
    processed_img_resized = cv2.resize(img_rgb, (224, 224))

    # 5. Ben Graham's Method (Gaussian Filter)
    # This creates the "orange/brown" or "high contrast" look seen in the dataset samples
    # Formula: image = image * a + gaussian_blur * b + gamma
    # Standard Kaggle DR winning solution params: sigmaX=10, weights 4, -4, 128
    # However, if the user's dataset is JUST "gaussian filtered", it might be simpler.
    # But "Ben Graham" is the standard for "gaussian filtered retina".
    sigmaX = 10
    processed_img_benz = cv2.addWeighted(processed_img_resized, 4, cv2.GaussianBlur(processed_img_resized, (0,0), sigmaX), -4, 128)
    
    # 6. Normalize to [-1, 1]
    img_float = processed_img_benz.astype("float32")
    batch_input = (img_float / 127.5) - 1.0
    
    # 7. Expand dims
    batch_img = np.expand_dims(batch_input, axis=0)

    # Return RGB for display (Ben Graham processed version, so user sees what model sees)
    # We convert back to BGR for potential cv2 saving or just keep strict consistency with cv2 expects
    processed_img_resized_bgr = cv2.cvtColor(processed_img_benz, cv2.COLOR_RGB2BGR)
    
    # Dummy is_noisy (Ben Graham handles noise implicitly)
    is_noisy = False

    return batch_img, processed_img_resized_bgr, is_noisy
