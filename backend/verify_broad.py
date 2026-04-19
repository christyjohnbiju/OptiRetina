import tensorflow as tf
import numpy as np
import cv2
import os

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
    
    img_resized = cv2.resize(img_bgr, (224, 224))
    img_float = img_resized.astype('float32')
    batch_input = (img_float / 127.5) - 1.0
    batch = np.expand_dims(batch_input, axis=0)
    
    all_preds = []
    for model in folds:
        all_preds.append(model.predict(batch, verbose=0)[0])
    
    avg_preds = np.mean(all_preds, axis=0)
    pred_idx = np.argmax(avg_preds)
    
    return f"{CLASSES[pred_idx]:15s} ({avg_preds[pred_idx]:.4f}) | {[f'{v:.2f}' for v in avg_preds]}"

results = []
print("\n=== BROAD ENSEMBLE TEST ===\n")
for f in files[:20]:
    res = test_ensemble(f)
    print(f"{os.path.basename(f):40s} : {res}")
