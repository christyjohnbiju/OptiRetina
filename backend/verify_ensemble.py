import tensorflow as tf
import numpy as np
import cv2
import os
import sys

# Add backend to path to import official classes
sys.path.append(os.getcwd())

print("Loading Ensemble Folds 1-4...")
folds = []
for fold in [1, 2, 3, 4]:
    folds.append(tf.keras.models.load_model(f'new_models/resnet50_fold_{fold}.keras', compile=False, safe_mode=False))

CLASSES = ['No_DR', 'Mild', 'Moderate', 'Severe', 'Proliferative']

uploads_dir = 'uploads'
files = [os.path.join(uploads_dir, f) for f in os.listdir(uploads_dir) if os.path.isfile(os.path.join(uploads_dir, f))]
files.sort(key=os.path.getmtime, reverse=True)

def test_ensemble(path):
    img_bgr = cv2.imread(path)
    if img_bgr is None: return
    
    # Standard Preprocessing (BGR [-1, 1])
    img_resized = cv2.resize(img_bgr, (224, 224))
    img_float = img_resized.astype('float32')
    batch_input = (img_float / 127.5) - 1.0
    batch = np.expand_dims(batch_input, axis=0)
    
    all_preds = []
    for model in folds:
        all_preds.append(model.predict(batch, verbose=0)[0])
    
    avg_preds = np.mean(all_preds, axis=0)
    pred_idx = np.argmax(avg_preds)
    
    print(f'FILE: {os.path.basename(path)}')
    print(f'  Ensemble Prediction: {CLASSES[pred_idx]:15s} ({avg_preds[pred_idx]:.4f})')
    print(f'  Probabilities:       {[f"{v:.2f}" for v in avg_preds]}')
    print()

print("\n=== FINAL ENSEMBLE VERIFICATION ===\n")

# Test 1: The user's severe image (should be Moderate/Severe)
target = None
for f in files:
    if 'bb7e0a2544cd' in f:
        target = f
        break
if target:
    test_ensemble(target)

# Test 2: The healthy image that was previously showing as Severe (should be No_DR)
target2 = None
for f in files:
    if 'a9e984b57556' in f:
        target2 = f
        break
if target2:
    test_ensemble(target2)

# Test 3: Other recent uploads
print("--- Other recent samples ---")
for f in files[:5]:
    if f not in [target, target2]:
        test_ensemble(f)
