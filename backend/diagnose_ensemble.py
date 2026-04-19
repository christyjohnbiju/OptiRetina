import tensorflow as tf
import numpy as np
import cv2
import os

print("Loading folds...")
folds = {}
for fold in [1, 2, 3, 4]:
    folds[fold] = tf.keras.models.load_model(f'new_models/resnet50_fold_{fold}.keras', compile=False, safe_mode=False)

CLASSES = ['No_DR', 'Mild', 'Moderate', 'Severe', 'Proliferative']

# Find the specific image bb7e0a2544cd.png
uploads_dir = 'uploads'
target_file = None
for f in os.listdir(uploads_dir):
    if 'bb7e0a2544cd' in f:
        target_file = os.path.join(uploads_dir, f)
        break

if not target_file:
    print("Could not find bb7e0a2544cd.png in uploads/")
    sys.exit(1)

def test_image(path):
    img_bgr = cv2.imread(path)
    if img_bgr is None: return
    
    img_resized = cv2.resize(img_bgr, (224, 224))
    img_rgb = cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB)
    
    inputs = {
        'RGB': (img_rgb.astype('float32') / 127.5) - 1.0,
        'BGR': (img_resized.astype('float32') / 127.5) - 1.0
    }
    
    print(f'FILE: {os.path.basename(path)}')
    
    for label, inp in inputs.items():
        batch = np.expand_dims(inp, axis=0)
        all_preds = []
        print(f'  {label}:')
        for fold, model in folds.items():
            preds = model.predict(batch, verbose=0)[0]
            all_preds.append(preds)
            p_idx = np.argmax(preds)
            print(f'    Fold {fold}: {CLASSES[p_idx]:15s} ({preds[p_idx]:.4f})')
        
        # Ensemble result
        avg_preds = np.mean(all_preds, axis=0)
        ens_idx = np.argmax(avg_preds)
        print(f'    ENSEMBLE: {CLASSES[ens_idx]:15s} ({avg_preds[ens_idx]:.4f}) | {[f"{p:.2f}" for p in avg_preds]}')
    print()

test_image(target_file)
