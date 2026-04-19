import tensorflow as tf
import numpy as np
import cv2
import os

print("Loading model...")
try:
    model = tf.keras.models.load_model('new_models/resnet50_fold_4.keras', compile=False, safe_mode=False)
except TypeError:
    model = tf.keras.models.load_model('new_models/resnet50_fold_4.keras', compile=False)

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

def test_all_methods(path):
    img_bgr = cv2.imread(path)
    if img_bgr is None: return
    
    try:
        img_cropped = crop_simple(img_bgr)
    except:
        img_cropped = img_bgr
    
    img_resized = cv2.resize(img_cropped, (224, 224))
    
    # Method 1: RGB [-1,1] (Current fix)
    img_rgb = cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB)
    rgb_input = (img_rgb.astype('float32') / 127.5) - 1.0
    rgb_batch = np.expand_dims(rgb_input, axis=0)
    rgb_preds = model.predict(rgb_batch, verbose=0)[0]
    
    # Method 2: BGR [-1,1] (Previous)
    bgr_input = (img_resized.astype('float32') / 127.5) - 1.0
    bgr_batch = np.expand_dims(bgr_input, axis=0)
    bgr_preds = model.predict(bgr_batch, verbose=0)[0]
    
    # Method 3: RGB [0,1]
    rgb_01 = img_rgb.astype('float32') / 255.0
    rgb_01_batch = np.expand_dims(rgb_01, axis=0)
    rgb_01_preds = model.predict(rgb_01_batch, verbose=0)[0]
    
    # Method 4: ImageNet preprocess (caffe mode - subtracts mean, no scaling to [-1,1])
    from tensorflow.keras.applications.resnet50 import preprocess_input
    imagenet_input = img_resized.astype('float32').copy()
    imagenet_batch = np.expand_dims(imagenet_input, axis=0)
    imagenet_batch = preprocess_input(imagenet_batch)
    imagenet_preds = model.predict(imagenet_batch, verbose=0)[0]
    
    print(f'FILE: {os.path.basename(path)}')
    print(f'  RGB [-1,1]:  {CLASSES[np.argmax(rgb_preds)]:15s} ({np.max(rgb_preds):.4f})')
    print(f'  BGR [-1,1]:  {CLASSES[np.argmax(bgr_preds)]:15s} ({np.max(bgr_preds):.4f})')
    print(f'  RGB [0,1]:   {CLASSES[np.argmax(rgb_01_preds)]:15s} ({np.max(rgb_01_preds):.4f})')
    print(f'  ImageNet:    {CLASSES[np.argmax(imagenet_preds)]:15s} ({np.max(imagenet_preds):.4f})')
    print()

print("\n=== FULL COMPARISON (Last 15 uploads) ===\n")
for f in files[:15]:
    test_all_methods(f)
