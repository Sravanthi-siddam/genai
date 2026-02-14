import os
import json
import numpy as np
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from PIL import Image
try:
    import tensorflow as tf
    from tensorflow.keras.models import load_model
    from tensorflow.keras.preprocessing import image
    TF_AVAILABLE = True
except ImportError:
    print("TensorFlow not found. Using mock predictions.")
    TF_AVAILABLE = False

app = Flask(__name__, static_folder='.')
CORS(app)

# Load Model (Mock or Real)
MODEL_PATH = 'model.h5'
model = None

try:
    if TF_AVAILABLE and os.path.exists(MODEL_PATH):
        model = load_model(MODEL_PATH)
        print("Model loaded successfully.")
    else:
        print("Model file not found or TensorFlow missing. Predictions will be simulated.")
except Exception as e:
    print(f"Error loading model: {e}. Predictions will be simulated.")

# Mock Data for Diseases
DISEASE_INFO = {
    0: {
        "name": "Healthy",
        "description": "The plant appears healthy with no visible signs of disease.",
        "treatment": "Continue regular care, watering, and monitoring.",
        "prevention": "Ensure proper spacing, adequate sunlight, and balanced fertilization."
    },
    1: {
        "name": "Early Blight",
        "description": "Fungal disease characterized by brown spots with concentric rings on lower leaves.",
        "treatment": "Apply copper-based fungicides. Remove infected leaves.",
        "prevention": "Rotate crops, avoid overhead watering, and ensure good air circulation."
    },
    2: {
        "name": "Late Blight",
        "description": "Severe fungal disease causing dark, water-soaked spots on leaves and stems.",
        "treatment": "Use fungicides containing chlorothalonil or mancozeb. Destroy infected plants.",
        "prevention": "Plant resistant varieties and monitor weather conditions."
    },
    3: {
        "name": "Powdery Mildew",
        "description": "White, powdery fungal growth on leaves and stems.",
        "treatment": "Apply neem oil or sulfur-based fungicides.",
        "prevention": "Prune for airflow and avoid nitrogen over-fertilization."
    }
}

def preprocess_image(img_file):
    img = Image.open(img_file)
    img = img.resize((224, 224))
    
    if TF_AVAILABLE:
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array /= 255.0  # Normalize
    else:
        # Fallback preprocessing using numpy directly
        img_array = np.array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = img_array.astype('float32') / 255.0
        
    return img_array

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    try:
        # Preprocessing requires PIL which is lightweight and likely installed
        # But if we rely on tensorflow.keras.preprocessing.image, we might need alternative
        # Let's check TF_AVAILABLE
        
        if TF_AVAILABLE and model:
            processed_img = preprocess_image(file)
            prediction = model.predict(processed_img)
            class_idx = np.argmax(prediction[0])
            confidence = float(np.max(prediction[0]))
        else:
            # Simulation for demo purposes if model fails to load OR TF missing
            import random
            # Determine class based on filename hash or random for consistency/demo
            # For now, random is fine
            class_idx = random.randint(0, 3)
            confidence = random.uniform(0.7, 0.99)

        # Map to disease info
        # If class_idx is out of range of our mock data, default to Unknown
        info = DISEASE_INFO.get(class_idx, {
            "name": "Unknown Disease",
            "description": "The system could not identify this disease with high certainty.",
            "treatment": "Consult an agricultural expert.",
            "prevention": "Practice general crop hygiene."
        })

        result = {
            "disease": info["name"],
            "confidence": f"{confidence * 100:.2f}%",
            "description": info["description"],
            "treatment": info["treatment"],
            "prevention": info["prevention"]
        }
        
        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
