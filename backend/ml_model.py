import tensorflow as tf
import numpy as np
import cv2
import os

# ⚠️ MUST MATCH train_gen.class_indices EXACTLY
CLASSES = [
    "No_DR",           # index 0
    "Mild",            # index 1
    "Moderate",        # index 2
    "Severe",          # index 3
    "Proliferative"    # index 4 (Mapped from Proliferate_DR)
]

class DRModel:
    def __init__(self, model_dir="new_models"):
        self.model = None  # Single model (no ensemble)
        self.model_dir = model_dir
        self.load_model()
        
        self.last_conv_layer_name = None
        if self.model:
            self.last_conv_layer_name = self.find_last_conv_layer(self.model)
            print("Last Conv Layer for Grad-CAM:", self.last_conv_layer_name)

    # -------------------------------
    # Load single model (Fold 4)
    # -------------------------------
    def load_model(self):
        model_file = "resnet50_fold_4.keras"
        path = os.path.join(self.model_dir, model_file)
        print(f"Loading ResNet50 model ({model_file})...")
        
        if os.path.exists(path):
            try:
                self.model = tf.keras.models.load_model(path, compile=False, safe_mode=False)
                print(f"Successfully loaded {model_file}.")
            except TypeError:
                try:
                    self.model = tf.keras.models.load_model(path, compile=False)
                    print(f"Successfully loaded {model_file} (fallback).")
                except Exception as e:
                    print(f"Failed to load {model_file}: {e}")
            except Exception as e:
                print(f"Failed to load {model_file}: {e}")
        else:
            print(f"WARNING: Model file {model_file} not found at {path}.")

    # -------------------------------
    # Find last Conv2D layer (Grad-CAM)
    # -------------------------------
    def find_last_conv_layer(self, model):
        target_layers = ["conv5_block3_3_conv", "conv5_block3_out", "conv5_block3_2_conv"]
        for name in target_layers:
            try:
                layer = model.get_layer(name)
                if "Conv2D" in str(type(layer)) or "Conv" in layer.name.lower():
                    return name
            except:
                continue
        
        last_conv = None
        for layer in model.layers:
            if "Conv" in str(type(layer)) or "conv" in layer.name.lower():
                last_conv = layer.name
        return last_conv

    # -------------------------------
    # Grad-CAM Heatmap Generation
    # -------------------------------
    def make_gradcam_heatmap(self, img_array, pred_index):
        if not self.model or not self.last_conv_layer_name:
             return None

        grad_model = tf.keras.models.Model(
            inputs=self.model.inputs,
            outputs=[
                self.model.get_layer(self.last_conv_layer_name).output,
                self.model.output
            ]
        )

        with tf.GradientTape() as tape:
            conv_outputs, predictions = grad_model(img_array)
            if isinstance(predictions, list):
                predictions = predictions[0]
            loss = predictions[:, pred_index]

        grads = tape.gradient(loss, conv_outputs)
        pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))

        conv_outputs = conv_outputs[0]
        heatmap = conv_outputs @ pooled_grads[..., tf.newaxis]
        heatmap = tf.squeeze(heatmap)

        heatmap = tf.maximum(heatmap, 0)
        max_val = tf.math.reduce_max(heatmap)
        if max_val > 0:
            heatmap /= max_val
        
        return heatmap.numpy()

    # -------------------------------
    # Prediction pipeline (Single Model)
    # -------------------------------
    def predict(self, img_array, original_image_bgr):
        """
        Expects:
            img_array: Preprocessed (1, 224, 224, 3) batch (BGR, [-1, 1])
            original_image_bgr: Original image in BGR format for overlay
        Returns:
            label (str)
            confidence (float)
            gradcam_overlay (np.ndarray) - BGR
        """
        if not self.model:
            raise Exception("No model loaded for inference.")

        # 1. Single Model Inference
        print("\n--- SINGLE MODEL INFERENCE ---")
        preds = self.model.predict(img_array, verbose=0)[0]
        print(f"Raw Predictions: {[f'{v:.4f}' for v in preds]}")
        
        pred_index = int(np.argmax(preds))
        confidence = float(preds[pred_index])
        
        print(f"Predicted Class Index: {pred_index}")
        print(f"Confidence Score: {confidence:.4f}")
        print("------------------------------\n")

        label = CLASSES[pred_index]

        # 2. Grad-CAM Overlay (Standard BGR path)
        heatmap = None
        try:
            heatmap = self.make_gradcam_heatmap(img_array, pred_index)
            if heatmap is not None:
                heatmap = np.power(heatmap, 0.6) 
                heatmap = cv2.resize(
                    heatmap,
                    (original_image_bgr.shape[1], original_image_bgr.shape[0])
                )
        except Exception as e:
            print(f"Grad-CAM failed: {e}")
            heatmap = None

        if heatmap is not None:
            heatmap_255 = np.uint8(255 * heatmap)
            heatmap_bgr = cv2.applyColorMap(heatmap_255, cv2.COLORMAP_JET)

            overlay = cv2.addWeighted(
                original_image_bgr, 0.6,
                heatmap_bgr, 0.4,
                0
            )
            return label, confidence, overlay
        else:
            return label, confidence, original_image_bgr
