import os
import keras
import tensorflow as tf

def check_load():
    print(f"TF Version: {tf.__version__}")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    models_dir = os.path.join(base_dir, "models")
    
    print(f"Checking models in: {models_dir}")
    if not os.path.exists(models_dir):
        print("Models directory not found!")
        return

    files = [f for f in os.listdir(models_dir) if f.endswith(".keras")]
    print(f"Found files: {files}")
    
    for f in files:
        path = os.path.join(models_dir, f)
        print(f"\nAttempting to load {f}...")
        try:
            # Try Keras 3 native load
            model = keras.models.load_model(path, compile=False)
            print("✅ Success with Keras 3")
        except Exception as e:
            print(f"❌ Failed: {e}")

if __name__ == "__main__":
    check_load()
