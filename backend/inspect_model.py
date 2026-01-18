import tensorflow as tf
import os

model_path = "models/mobilenetv3_fold_1.keras"
if not os.path.exists(model_path):
    print("Model not found")
else:
    try:
        model = tf.keras.models.load_model(model_path)
        print("Model Loaded Successfully.")
        print("Last 10 layers:")
        for layer in model.layers[-10:]:
            print(f"Name: {layer.name}, Type: {type(layer)}")
            
        # Also try to specifically find the last Conv2D
        print("\nSearching for last Conv2D layer...")
        for layer in reversed(model.layers):
            if isinstance(layer, tf.keras.layers.Conv2D):
                print(f"FOUND: {layer.name}")
                break
                
    except Exception as e:
        print(f"Error: {e}")
