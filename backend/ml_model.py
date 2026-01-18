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
    def __init__(self, model_dir="models"):
        self.models = []
        self.model_dir = model_dir
        self.load_ensemble()
        
        # Use the first model for Grad-CAM visualization
        self.viz_model = self.models[0] if self.models else None
        self.last_conv_layer_name = None

        if self.viz_model:
            self.last_conv_layer_name = self.find_last_conv_layer(self.viz_model)
            print("Last Conv Layer for Grad-CAM (Model 1):", self.last_conv_layer_name)

    # -------------------------------
    # Load 5 Models
    # -------------------------------
    def load_ensemble(self):
        print("Loading ensemble models...")
        model_files = [
            "mobilenetv3_fold_1.keras",
            "mobilenetv3_fold_2.keras",
            "mobilenetv3_fold_3.keras",
            "mobilenetv3_fold_4.keras",
            "mobilenetv3_fold_5.keras"
        ]
        
        for f in model_files:
            path = os.path.join(self.model_dir, f)
            if os.path.exists(path):
                try:
                    print(f"Loading {f}...")
                    model = tf.keras.models.load_model(path)
                    self.models.append(model)
                except Exception as e:
                    print(f"Failed to load {f}: {e}")
            else:
                print(f"Warning: Model file {f} not found.")

        if not self.models:
            print("⚠️ No models loaded! Demo mode logic would be needed (not implemented).")
        else:
            print(f"Successfully loaded {len(self.models)} models.")

    # -------------------------------
    # Find last Conv2D layer (Grad-CAM)
    # -------------------------------
    def find_last_conv_layer(self, model):
        # Specific known last layers for MobileNetV3 to try first
        target_layers = ["Conv_1", "conv_1", "expanded_conv_15_project"]
        for name in target_layers:
            try:
                layer = model.get_layer(name)
                if isinstance(layer, tf.keras.layers.Conv2D):
                    return name
            except:
                continue
                
        # Fallback: Just return the string name of the very last Conv2D layer in the list
        last_conv = None
        for layer in model.layers:
            if isinstance(layer, tf.keras.layers.Conv2D):
                last_conv = layer.name
        return last_conv

    # -------------------------------
    # Grad-CAM
    # -------------------------------
    def make_gradcam_heatmap(self, img_array, pred_index):
        if not self.viz_model or not self.last_conv_layer_name:
             return None

        grad_model = tf.keras.models.Model(
            inputs=self.viz_model.inputs,
            outputs=[
                self.viz_model.get_layer(self.last_conv_layer_name).output,
                self.viz_model.output
            ]
        )

        with tf.GradientTape() as tape:
            conv_out, preds = grad_model(img_array)
            if isinstance(preds, list):
                preds = preds[0]
            class_score = preds[:, pred_index]

        grads = tape.gradient(class_score, conv_out)
        pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))

        conv_out = conv_out[0]
        heatmap = tf.reduce_sum(conv_out * pooled_grads, axis=-1)

        heatmap = tf.maximum(heatmap, 0)
        heatmap /= (tf.reduce_max(heatmap) + 1e-8)

        return heatmap.numpy()

    # -------------------------------
    # Prediction pipeline (Ensemble)
    # -------------------------------
    def predict(self, img_array, original_image_bgr):
        """
        Returns:
            label (str)
            confidence (float)
            gradcam_overlay (np.ndarray)
        """
        if not self.models:
            raise Exception("No models loaded for inference.")

        # -------------------------------
        # ENSEMBLE INFERENCE
        # -------------------------------
        print(f"Running ensemble inference on shape: {img_array.shape}")
        
        all_preds = []
        for i, model in enumerate(self.models):
            try:
                # verbosity=0 to keep logs clean
                p = model.predict(img_array, verbose=0)[0] 
                all_preds.append(p)
            except Exception as e:
                print(f"Model {i+1} failed: {e}")

        if not all_preds:
            raise Exception("All models failed inference.")

        # Soft Voting: Average probabilities
        avg_preds = np.mean(all_preds, axis=0)
        print("\n--- DEBUG INFERENCE ---")
        print("Raw Probability Vector:", avg_preds)
        
        pred_index = int(np.argmax(avg_preds))
        confidence = float(avg_preds[pred_index])
        
        print(f"Predicted Class Index: {pred_index}")
        print(f"Confidence Score: {confidence:.4f}")
        print("-----------------------\n")

        # -------------------------------
        # Threshold Logic REMOVED per user request
        # -------------------------------
        # THRESH = 0.65
        # if confidence < THRESH:
        #     label = "Uncertain"
        #     print(f"Confidence {confidence:.2f} < {THRESH}. Labeling as Uncertain.")
        # else:
        label = CLASSES[pred_index]
        print(f"Inferred Class: {label} (Idx: {pred_index})")

        # -------------------------------
        # Grad-CAM overlay
        # -------------------------------
        # Generate heatmap using the dominant class index, 
        # using the first model (Fold 1) as representative.
        heatmap = None
        try:
            # We visualize the class that had the highest average probability
            heatmap = self.make_gradcam_heatmap(img_array, pred_index)
            
            if heatmap is not None:
                heatmap = cv2.resize(
                    heatmap,
                    (original_image_bgr.shape[1], original_image_bgr.shape[0])
                )
        except Exception as e:
            print(f"Grad-CAM failed: {e}")
            heatmap = None

        if heatmap is not None:
            heatmap = np.uint8(255 * heatmap)
            heatmap = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)
            # Fix RGB/BGR compatibility
            heatmap = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)

            overlay = cv2.addWeighted(
                original_image_bgr, 0.6,
                heatmap, 0.4,
                0
            )
        else:
             overlay = original_image_bgr

        return label, confidence, overlay
