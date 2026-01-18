import numpy as np
import tensorflow as tf
from tensorflow.keras.applications.mobilenet_v3 import preprocess_input

def check_preprocessing():
    with open("debug_vals.txt", "w") as f:
        f.write("--- TEST 1: FLOAT32 ---\n")
        img_float = np.array([[[0, 127.5, 255]]], dtype=np.float32)
        processed_float = preprocess_input(img_float.copy())
        f.write(f"In (float): {img_float}\n")
        f.write(f"Out: {processed_float}\n")
        
        f.write("\n--- TEST 2: UINT8 ---\n")
        img_uint = np.array([[[0, 127, 255]]], dtype=np.uint8)
        processed_uint = preprocess_input(img_uint.copy())
        f.write(f"In (uint8): {img_uint}\n")
        f.write(f"Out: {processed_uint}\n")

        if processed_uint.max() <= 1.0:
             f.write("CONCLUSION: uint8 input triggers rescaling.\n")
        else:
             f.write("CONCLUSION: uint8 input does NOT trigger rescaling.\n")

if __name__ == "__main__":
    check_preprocessing()
