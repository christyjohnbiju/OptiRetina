import tensorflow as tf
import numpy as np
import cv2
import os

print("Loading model...")
model = tf.keras.models.load_model('new_models/resnet50_fold_4.keras', compile=False, safe_mode=False)

uploads_dir = 'uploads'
files = [os.path.join(uploads_dir, f) for f in os.listdir(uploads_dir) if os.path.isfile(os.path.join(uploads_dir, f))]
files.sort(key=os.path.getmtime, reverse=True)

CLASSES = ['No_DR', 'Mild', 'Moderate', 'Severe', 'Proliferative']

def crop_simple(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray, 7, 255, cv2.THRESH_BINARY)
    coords = cv2.findNonZero(mask)
    if coords is not None:
        x, y, w, h = cv2.boundingRect(coords)
        return img[y:y+h, x:x+w]
    return img

def test_permutations(path):
    img_bgr_raw = cv2.imread(path)
    if img_bgr_raw is None: return
    
    print(f'FILE: {os.path.basename(path)}')
    
    for crop in [True, False]:
        if crop:
            try:
                img_bgr = crop_simple(img_bgr_raw)
            except:
                img_bgr = img_bgr_raw
        else:
            img_bgr = img_bgr_raw
            
        img_resized = cv2.resize(img_bgr, (224, 224))
        
        # Method 1: RGB [-1, 1]
        img_rgb = cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB)
        rgb_input = (img_rgb.astype('float32') / 127.5) - 1.0
        preds = model.predict(np.expand_dims(rgb_input, axis=0), verbose=0)[0]
        p_idx = np.argmax(preds)
        print(f'  [Crop={str(crop):5s}] RGB [-1,1]: {CLASSES[p_idx]:15s} ({preds[p_idx]:.4f})')
        
        # Method 2: RGB [0, 1]
        rgb_01 = img_rgb.astype('float32') / 255.0
        preds = model.predict(np.expand_dims(rgb_01, axis=0), verbose=0)[0]
        p_idx = np.argmax(preds)
        print(f'  [Crop={str(crop):5s}] RGB [0,1]:  {CLASSES[p_idx]:15s} ({preds[p_idx]:.4f})')
        
        # Method 3: BGR [-1, 1]
        bgr_input = (img_resized.astype('float32') / 127.5) - 1.0
        preds = model.predict(np.expand_dims(bgr_input, axis=0), verbose=0)[0]
        p_idx = np.argmax(preds)
        print(f'  [Crop={str(crop):5s}] BGR [-1,1]: {CLASSES[p_idx]:15s} ({preds[p_idx]:.4f})')

    print()

# Test last 3 uploads
for f in files[:3]:
    test_permutations(f)
