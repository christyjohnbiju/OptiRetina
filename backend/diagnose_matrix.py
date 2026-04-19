import tensorflow as tf
import numpy as np
import cv2
import os

uploads_dir = 'uploads'
files = [os.path.join(uploads_dir, f) for f in os.listdir(uploads_dir) if os.path.isfile(os.path.join(uploads_dir, f))]
files.sort(key=os.path.getmtime, reverse=True)

CLASSES = ['No_DR', 'Mild', 'Moderate', 'Severe', 'Proliferative']

def test_everything(path):
    img_bgr = cv2.imread(path)
    if img_bgr is None: return
    
    img_resized = cv2.resize(img_bgr, (224, 224))
    img_rgb = cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB)
    
    rgb_input = (img_rgb.astype('float32') / 127.5) - 1.0
    bgr_input = (img_resized.astype('float32') / 127.5) - 1.0
    
    rgb_batch = np.expand_dims(rgb_input, axis=0)
    bgr_batch = np.expand_dims(bgr_input, axis=0)
    
    output = []
    output.append(f"FILE: {os.path.basename(path)}")
    
    for fold in [1, 2, 3, 4]:
        model_name = f"resnet50_fold_{fold}.keras"
        try:
            model = tf.keras.models.load_model(f"new_models/{model_name}", compile=False, safe_mode=False)
            # Test RGB
            p_rgb = model.predict(rgb_batch, verbose=0)[0]
            idx_rgb = np.argmax(p_rgb)
            # Test BGR
            p_bgr = model.predict(bgr_batch, verbose=0)[0]
            idx_bgr = np.argmax(p_bgr)
            output.append(f"  Fold {fold}:")
            output.append(f"    RGB: {CLASSES[idx_rgb]:15s} ({p_rgb[idx_rgb]:.4f}) | {[f'{p:.2f}' for p in p_rgb]}")
            output.append(f"    BGR: {CLASSES[idx_bgr]:15s} ({p_bgr[idx_bgr]:.4f}) | {[f'{p:.2f}' for p in p_bgr]}")
        except Exception as e:
            output.append(f"  Fold {fold}: Error {e}")
    
    return "\n".join(output) + "\n\n"

results = ""
for f in files[:4]:
    results += test_everything(f)

with open("diagnose_matrix.txt", "w") as f:
    f.write(results)
print("Done writing to diagnose_matrix.txt")
