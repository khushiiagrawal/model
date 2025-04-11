import os
import numpy as np
from flask import Flask, render_template, request, redirect, url_for
from PIL import Image
import io
import uuid
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from tensorflow.keras.applications.resnet50 import preprocess_input
import gdown  # Add this import for downloading from Google Drive

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Class names based on the new model's categories
class_names = [
    'E-waste', 'Organics', 'aerosol_cans', 'automobile wastes', 'battery waste',
    'cardboard_boxes', 'clothing', 'food_and_organic_waste', 'glass waste',
    'glass_containers', 'light bulbs', 'metal waste', 'metal_cans',
    'paper_and_print', 'paper_cups', 'plastic disposables', 'plastic waste',
    'plastic_bags', 'plastic_bottles', 'plastic_detergent_bottles',
    'plastic_food_containers', 'shoes', 'steel_food_cans',
    'styrofoam_containers', 'utensils'
]

# --- NEW: Mapping to Functional Categories ---
functional_categories_map = {
    'E-waste': ['Recyclable (Special Handling)', 'Resellable'],
    'Organics': ['Biodegradable (Compostable)'],
    'aerosol_cans': ['Recyclable (Empty, Check Local)'],
    'automobile wastes': ['Recyclable (Special Handling)', 'Resellable (Parts)'],
    'battery waste': ['Recyclable (Special Handling)'],
    'cardboard_boxes': ['Recyclable', 'Biodegradable'],
    'clothing': ['Reusable', 'Resellable', 'Biodegradable (Natural Fibers)', 'Recyclable (Textile Programs)'],
    'food_and_organic_waste': ['Biodegradable (Compostable)'],
    'glass waste': ['Recyclable'],
    'glass_containers': ['Recyclable', 'Reusable', 'Resellable'],
    'light bulbs': ['Recyclable (Special Handling)'],
    'metal waste': ['Recyclable', 'Resellable'],
    'metal_cans': ['Recyclable'],
    'paper_and_print': ['Recyclable', 'Biodegradable'],
    'paper_cups': ['Recyclable (Check Local)', 'Biodegradable (If unlined)'],
    'plastic disposables': ['Check Local (Often Not Recyclable)'],
    'plastic waste': ['Check Local (Depends on Type)'], # Too general
    'plastic_bags': ['Recyclable (Special Programs)'],
    'plastic_bottles': ['Recyclable'],
    'plastic_detergent_bottles': ['Recyclable (Check Local)', 'Reusable (Non-food)'],
    'plastic_food_containers': ['Recyclable (Check Type/Local)', 'Reusable'],
    'shoes': ['Reusable', 'Resellable', 'Recyclable (Special Programs)'],
    'steel_food_cans': ['Recyclable'],
    'styrofoam_containers': ['Check Local (Often Not Recyclable)'],
    'utensils': ['Reusable', 'Resellable (Metal)', 'Check Local (Plastic)']
}
# Ensure all classes have an entry, add default if missing (optional safety net)
for cls in class_names:
    if cls not in functional_categories_map:
        functional_categories_map[cls] = ['Check Local Guidelines']
# --- End NEW Mapping ---

# Path to the model
MODEL_URL = 'https://drive.google.com/uc?id=1vFqMSple_RQm_nG-pPP_1obnMeIsYqgI'
MODEL_PATH = '3RVision_2.keras'

# Download and load the model
def download_and_load_model():
    try:
        # Download the model if it doesn't exist
        if not os.path.exists(MODEL_PATH):
            print("Downloading model...")
            try:
                gdown.download(MODEL_URL, MODEL_PATH, quiet=False)
                if not os.path.exists(MODEL_PATH):
                    raise Exception("Model file was not downloaded successfully")
            except Exception as download_error:
                print(f"Error downloading model: {download_error}")
                return None
        
        # Verify the file exists and has content
        if not os.path.exists(MODEL_PATH):
            raise Exception("Model file not found")
        
        file_size = os.path.getsize(MODEL_PATH)
        if file_size == 0:
            raise Exception("Downloaded model file is empty")
        
        print(f"Model file size: {file_size / (1024*1024):.2f} MB")
        
        # Load the model
        try:
            model = load_model(MODEL_PATH)
            print("Model loaded successfully.")
            return model
        except Exception as load_error:
            print(f"Error loading model file: {load_error}")
            # If loading fails, remove the potentially corrupted file
            if os.path.exists(MODEL_PATH):
                os.remove(MODEL_PATH)
                print("Removed potentially corrupted model file")
            return None
            
    except Exception as e:
        print(f"Error in model setup: {e}")
        return None

# Load the model
model = download_and_load_model()

# Add a route to check model status
@app.route('/model-status')
def model_status():
    if model is None:
        return {"status": "error", "message": "Model not loaded"}, 500
    return {"status": "ok", "message": "Model loaded successfully"}, 200

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def preprocess_image(image_path, target_size=(224, 224)):
    """Preprocess the image using ResNet50 standards."""
    # Load the image using Keras utility
    img = load_img(image_path, target_size=target_size)
    
    # Convert the image to a numpy array
    img_array = img_to_array(img)
    
    # Add a batch dimension
    img_array = np.expand_dims(img_array, axis=0)
    
    # Preprocess the image using ResNet50's specific function
    img_array = preprocess_input(img_array)
    
    return img_array

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    
    file = request.files['file']
    
    if file.filename == '':
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        # Create a unique filename
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Save the file
        file.save(file_path)
        
        # Ensure model is loaded before predicting
        if model is None:
            print("Model not loaded, cannot predict.")
            return redirect(url_for('index'))

        try:
            # Make prediction using the loaded Keras model
            preprocessed_img = preprocess_image(file_path)
            
            # --- DEBUGGING: Check preprocessed image --- 
            # print(f"DEBUG: Preprocessed image shape: {preprocessed_img.shape}, dtype: {preprocessed_img.dtype}")
            # Add stats for the preprocessed array
            # print(f"DEBUG: Preprocessed stats: mean={np.mean(preprocessed_img):.4f}, std={np.std(preprocessed_img):.4f}, min={np.min(preprocessed_img):.4f}, max={np.max(preprocessed_img):.4f}")
            # --- END DEBUGGING --- 
            
            predictions = model.predict(preprocessed_img)
            
            # --- DEBUGGING: Check raw model output --- 
            # print(f"DEBUG: Raw predictions vector: {predictions[0]}") 
            # --- END DEBUGGING --- 
            
            predicted_class_idx = np.argmax(predictions[0])
            predicted_class = class_names[predicted_class_idx]
            confidence = float(predictions[0][predicted_class_idx]) * 100
            
            # --- NEW: Get Functional Categories ---
            functional_cats = functional_categories_map.get(predicted_class, ['Check Local Guidelines']) # Use .get for safety
            # --- End NEW ---

            return render_template('result.html', 
                                filename=filename, 
                                predicted_class=predicted_class,
                                confidence=confidence,
                                functional_categories=functional_cats)
        except Exception as e:
            # In case of error during prediction
            print(f"Error during prediction: {e}")
            # Log the full traceback for debugging
            import traceback
            traceback.print_exc()
            return redirect(url_for('index'))
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Make sure the app runs only if the model loaded successfully
    if model is not None:
        app.run(debug=True)
    else:
        print("Application cannot start because the model failed to load.") 