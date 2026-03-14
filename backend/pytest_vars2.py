import cv2
import numpy as np
import os
import glob

def test_heuristic(path):
    img = cv2.imread(path)
    if img is None: return False, 'not found'
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
    _, thresh = cv2.threshold(gray, 15, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours: return False, 'no contours'
    
    largest_contour = max(contours, key=cv2.contourArea)
    area = cv2.contourArea(largest_contour)
    ih, iw = gray.shape
    img_area = ih * iw
    
    mask = np.zeros_like(gray)
    cv2.drawContours(mask, [largest_contour], -1, 255, -1)
    
    mean_color = cv2.mean(img_rgb, mask=mask)
    r_mean, g_mean, b_mean = mean_color[0], mean_color[1], mean_color[2]
    
    masked_gray = gray[mask == 255]
    if len(masked_gray) == 0: return False, 'empty'
    p95 = np.percentile(masked_gray, 95)
    p05 = np.percentile(masked_gray, 5)
    contrast = p95 - p05

    perimeter = cv2.arcLength(largest_contour, True)
    circularity = 4 * np.pi * (area / (perimeter * perimeter)) if perimeter > 0 else 0
    std_dev = np.std(masked_gray)
    
    # Check black border percentage
    black_pixels = np.sum(gray < 15)
    black_ratio = black_pixels / float(img_area)
    
    return True, f"R:{r_mean:.0f} G:{g_mean:.0f} B:{b_mean:.0f} c:{contrast:.0f} circ:{circularity:.2f} blk:{black_ratio:.2f} std:{std_dev:.0f}"

imgs_to_test = [
    'uploads/bf5063ea-2d33-4232-b709-6d2febc503db_pikachu.png',
    'uploads/f0183f2b-507a-4292-ae96-818e5e833bfe_yellow rose.jpg',
    'uploads/9945388b-216b-4764-83a9-720d9406d7e4_white rose.jpg',
    'uploads/718fe72b-d664-4acf-a0fd-3257cf5a1930_red rose.avif',
    'uploads/031e1e73-9eea-4687-a921-bac6b89b1226_0e94cd271c00.png',
    'uploads/0b0fc698-4dce-4db4-a113-fb56fc40662b_c0261071-800px-wm.jpg'
]

results = []
for f in imgs_to_test:
   res, msg = test_heuristic(f)
   results.append(f"{f.split('_')[-1]}: {msg}")

for r in results:
   print(r)
