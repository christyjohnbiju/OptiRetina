import tensorflow as tf
import os

model_path = "models/mobilenetv3_fold_1.keras"
try:
    model = tf.keras.models.load_model(model_path)
    print("ALL Conv2D Layers:")
    for i, layer in enumerate(model.layers):
        if isinstance(layer, tf.keras.layers.Conv2D):
            print(f"Index: {i}, Name: {layer.name}, Output Shape: {layer.output_shape}")
except Exception as e:
    print(e)
