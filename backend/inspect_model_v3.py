import tensorflow as tf
import os

model_path = "models/mobilenetv3_fold_1.keras"
try:
    model = tf.keras.models.load_model(model_path)
    print("ALL Conv2D Layers Names:")
    names = []
    for i, layer in enumerate(model.layers):
        if isinstance(layer, tf.keras.layers.Conv2D):
            names.append(layer.name)
            
    print(names)
    print(f"Total Conv2D: {len(names)}")
    print(f"Last One: {names[-1] if names else 'None'}")
except Exception as e:
    print(e)
