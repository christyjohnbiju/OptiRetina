import cv2
import numpy as np

def is_fundus_image(img_rgb):
    """
    Validates if an image is a fundus photograph based on a minimal, universal structural check.
    Fundus images (even heavily preprocessed ones) should be mostly a circular disk of pixels inside a squarish bounding box.
    """
    try:

        gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
        
        # Identify background padding color from corners (could be black padding or gray padding)
        bg_val = np.median([gray[0,0], gray[0,-1], gray[-1,0], gray[-1,-1]])
        
        if bg_val < 40:
            # 1. Standard black padding -> Otsu is best
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        else:
            # 2. Gray/Preprocessed padding -> MUST use absdiff to catch dark features
            # Lowered thresh to 8 to catch grayish retinas on gray backgrounds
            diff = cv2.absdiff(gray, int(bg_val))
            _, thresh = cv2.threshold(diff, 8, 255, cv2.THRESH_BINARY)
        
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            print("DEBUG: No contours found during initial segmentation.")
            return False

        largest_contour = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(largest_contour)
        img_area = gray.shape[0] * gray.shape[1]
        area_ratio = area / float(img_area + 1e-5)
        
        x, y, w, h = cv2.boundingRect(largest_contour)
        aspect_ratio = float(w) / h if h > 0 else 0
        extent = area / float(w * h + 1) if w*h > 0 else 0
        
        # Color Analysis (using BGR source)
        img_rgb_real = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2RGB)
        
        # Create mask based on the SAME segmentation logic (thresh 8 for gray)
        if bg_val < 40:
            _, mask_thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            mask = mask_thresh > 0
        else:
            mask = cv2.absdiff(gray, int(bg_val)) > 8
            
        if not np.any(mask):
            return False
            
        mean_r = np.mean(img_rgb_real[:,:,0][mask])
        mean_g = np.mean(img_rgb_real[:,:,1][mask])
        mean_b = np.mean(img_rgb_real[:,:,2][mask])
        
        # Internal variance to reject flat logos/text
        pixel_variance = np.std(gray[mask]) if np.any(mask) else 0
        
        # --- THE HIGH-SECURITY MEDICAL SHIELD ---
        
        # 1. THE EXTENT SHIELD (Digital/Square Block)
        # Blocks clear digital artifacts (Logos, Confusion Matrices, Square Screenshots).
        # Genuine circular/cropped retinas naturally have an extent < 0.92.
        if extent > 0.95:
            print(f"DEBUG: REJECTED - Perfect square content detected (Extent={extent:.3f})")
            return False

        # 2. COLOR ANALYSIS
        color_std = np.std([mean_r, mean_g, mean_b])
        is_machine_gray = color_std < 3.0
        is_nearly_gray = color_std < 25.0
        
        # 3. RED-DOMINANCE SHIELD (Blocks Landscapes/Buildings)
        # Human fundus images are ALWAYS Red-dominant if they have any color.
        # Landscapes have sky (Blue) or grass (Green).
        if not is_machine_gray:
            if mean_g > (mean_r + 5) or mean_b > (mean_r + 5):
                print(f"DEBUG: REJECTED - Non-medical color (Green/Blue dominant). G={mean_g:.1f}, B={mean_b:.1f}, R={mean_r:.1f}")
                return False

        # 4. MEDICAL ACCEPTANCE (Whitelist)
        if is_machine_gray:
            # Machine-clean grayscale scans pass if they have texture detail
            if pixel_variance >= 11.0:
                print("DEBUG: Machine-Gray Medical Scan ACCEPTED.")
                return True
        elif is_nearly_gray:
            # --- THE GREY-ZONE (For grayish/scanned fundus images) ---
            # We trust a grayish image if its shape is non-square and it has texture.
            if extent < 0.92 and pixel_variance > 11.0:
                print(f"DEBUG: Grey-Zone Medical Scan ACCEPTED (Extent={extent:.3f}, Var={pixel_variance:.1f})")
                return True
        else:
            # 5. VIBRANT RETINA SIGNATURE (Standard Color Scans)
            if mean_r > mean_g and mean_r > (mean_b * 1.7):
                print("DEBUG: Color Fundus Scan (Red-Dominant Signature) ACCEPTED.")
                return True
            
            # Special case for dim/preprocessed scans
            if mean_r > mean_g and mean_r > 30 and (mean_r / (mean_b + 1e-5)) > 1.6:
                 print("DEBUG: Dim Color Fundus ACCEPTED.")
                 return True

        # IF EXTENT IS VERY LOW (Circle-like), be more lenient with color
        if extent < 0.85 and pixel_variance > 15 and mean_r > mean_g:
             print(f"DEBUG: Flexible Circular Medical ACCEPTED (Extent={extent:.3f})")
             return True

        # If it reached here, it's likely a face or landscape posing as gray
        print(f"DEBUG: REJECTED - Non-medical profile (R={mean_r:.1f}, G={mean_g:.1f}, B={mean_b:.1f}, Ext={extent:.3f})")
        return False

    except Exception as e:
        print(f"Validation error: {e}")
        return False

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
        
        bg_val = np.median([gray_img[0,0], gray_img[0,-1], gray[-1,0], gray[-1,-1]])
        # Same hybrid logic for cropping
        if bg_val < 40:
            _, mask_thresh = cv2.threshold(gray_img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            mask = mask_thresh > 0
        else:
            mask = cv2.absdiff(gray_img, int(bg_val)) > tol

        
        check_shape = img[:,:,0][np.ix_(mask.any(1),mask.any(0))].shape[0]
        if (check_shape == 0): # image is too dark so that we crop out everything
            return img 
        else:
            img1=img[:,:,0][np.ix_(mask.any(1),mask.any(0))]
            img2=img[:,:,1][np.ix_(mask.any(1),mask.any(0))]
            img3=img[:,:,2][np.ix_(mask.any(1),mask.any(0))]
            img = np.stack([img1,img2,img3],axis=-1)
        return img

def preprocess_image(image_bytes: bytes):
    """
    Unified BGR preprocessing for ResNet50:
    1. Read BGR image
    2. Structural Validation (uses grayscale)
    3. Circle Crop (BGR)
    4. Resize to 224x224
    5. Universal scaling to [-1, 1] (BGR order)
    """
    # 1. Read image (OpenCV reads as BGR)
    nparr = np.frombuffer(image_bytes, np.uint8)
    img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if img_bgr is None:
        return None, None, False, False

    # 2. Structural Validate (uses grayscale internal)
    is_valid = is_fundus_image(img_bgr) 
    if not is_valid:
        return None, None, False, False

    # 3. Circle Crop
    try:
        img_bgr = crop_image_from_gray(img_bgr)
    except:
        pass

    # 4. Resize
    img_resized = cv2.resize(img_bgr, (224, 224))

    # 5. Final Inference Input (BGR, [-1, 1])
    img_float = img_resized.astype("float32")
    batch_input = (img_float / 127.5) - 1.0
    batch_img = np.expand_dims(batch_input, axis=0)

    is_noisy = False
    # Return: batch for model (BGR), resized image for Grad-CAM overlay (BGR)
    return batch_img, img_resized, is_noisy, is_valid
