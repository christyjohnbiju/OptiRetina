import tensorflow as tf
import numpy as np
import cv2
import os

uploads_dir = 'uploads'
files = [os.path.join(uploads_dir, f) for f in os.listdir(uploads_dir) if os.path.isfile(os.path.join(uploads_dir, f))]
files.sort(key=os.path.getmtime, reverse=True)

CLASSES = ['No_DR', 'Mild', 'Moderate', 'Severe', 'Proliferative']

def test_folds(path):
    img_bgr = cv2.imread(path)
    if img_bgr is None: return
    
    img_resized = cv2.resize(img_bgr, (224, 224))
    img_rgb = cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB)
    rgb_input = (img_rgb.astype('float32') / 127.5) - 1.0
    batch = np.expand_dims(rgb_input, axis=0)
    
    print(f'FILE: {os.path.basename(path)}')
    
    for fold in [1, 2, 3, 4]:
        model_name = f'resnet50_fold_{fold}.keras'
        try:
            model = tf.keras.models.load_model(f'new_models/{model_name}', compile=False, safe_mode=False)
            preds = model.predict(batch, verbose=0)[0]
            p_idx = np.argmax(preds)
            print(f'  Fold {fold}: {CLASSES[p_idx]:15s} ({preds[p_idx]:.4f}) | {[f"{p:.2f}" for p in preds]}')
        except Exception as e:
            print(f'  Fold {fold}: Error {e}')
    print()

for f in files[:8]:
    test_folds(f)
