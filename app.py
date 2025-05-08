import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
import requests
import json
import pickle
from datetime import datetime
import os
import sys
import logging

# Configure error handling and logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import functions from location_api.py
try:
    from location_api import (
        get_coordinates,
        find_collection_points,
        fetch_collection_dates,
        get_next_collection_date,
        format_collection_points,
        get_available_waste_types,
        translate_waste_type,
        fetch_collection_points,
        COLLECTION_POINTS_ENDPOINT,
        COLLECTION_DATES_ENDPOINT,
        handle_waste_disposal,
        create_interactive_map
    )
    logger.info(f"Successfully imported location_api functions")
    logger.info(f"Collection Points API: {COLLECTION_POINTS_ENDPOINT}")
    logger.info(f"Collection Dates API: {COLLECTION_DATES_ENDPOINT}")
except ImportError as e:
    st.error(f"Failed to import from location_api.py: {str(e)}")
    logger.error(f"Import error: {str(e)}")
    st.stop() # Stop execution if the core dependency is missing
except Exception as e:
    st.error(f"An unexpected error occurred while importing location_api.py: {str(e)}")
    logger.error(f"Unexpected error: {str(e)}")
    st.stop() # Stop execution on other import errors

# Page configuration
st.set_page_config(
    page_title="WasteWise - Your smart recycling assistant",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state if not already done
if 'waste_info_results' not in st.session_state:
    st.session_state.waste_info_results = None
    st.session_state.show_results = False

# Function to check if ML models are available (moved to app.py to be accessible by all pages)
def check_ml_models_available():
    """Check if ML model files exist"""
    required_files = ['waste_classifier.pkl', 'waste_vectorizer.pkl', 'waste_encoder.pkl']
    
    for file in required_files:
        if not os.path.exists(file):
            return False
    return True

# Function to check if TensorFlow is available
def check_tensorflow_available():
    """Check if TensorFlow is available"""
    try:
        import tensorflow
        return True
    except ImportError:
        return False

# Function to load the text model - fixed version
@st.cache_resource
def load_text_model():
    """Load text classification model with proper error handling"""
    try:
        if not check_ml_models_available():
            logger.warning("ML model files not found")
            return None, None, None
            
        with open('waste_classifier.pkl', 'rb') as f:
            model = pickle.load(f)
        with open('waste_vectorizer.pkl', 'rb') as f:
            vectorizer = pickle.load(f)
        with open('waste_encoder.pkl', 'rb') as f:
            encoder = pickle.load(f)
        return model, vectorizer, encoder
    except Exception as e:
        logger.error(f"Error loading text model: {str(e)}")
        return None, None, None

# Function to load the image model
@st.cache_resource
def load_image_model():
    """Load image classification model with proper error handling"""
    try:
        if not check_tensorflow_available():
            logger.warning("TensorFlow not available")
            return None
            
        if not os.path.exists("waste_image_classifier.h5"):
            logger.warning("Image model file not found")
            return None
            
        from tensorflow.keras.models import load_model
        return load_model("waste_image_classifier.h5")
    except Exception as e:
        logger.error(f"Error loading image model: {str(e)}")
        return None

# Rules-based fallback prediction when ML models aren't available
def rule_based_prediction(description):
    """Rule-based prediction for when ML models aren't available"""
    description = description.lower()
    
    # Keywords for each category
    keywords = {
        "Household waste 🗑": ["trash", "garbage", "waste", "dirty", "leftover", "broken", "ordinary"],
        "Paper 📄": ["paper", "newspaper", "magazine", "book", "printer", "envelope", "document"],
        "Cardboard 📦": ["cardboard", "carton", "box", "packaging", "thick paper"],
        "Glass 🍾": ["glass", "bottle", "jar", "container", "mirror", "window"],
        "Green waste 🌿": ["green", "grass", "leaf", "leaves", "plant", "garden", "flower", "vegetable", "fruit"],
        "Cans 🥫": ["can", "tin", "aluminum can", "soda", "drink can", "food can"],
        "Aluminium 🧴": ["aluminum", "foil", "tray", "container", "lid", "wrap", "packaging"],
        "Metal 🪙": ["metal", "iron", "steel", "scrap", "nails", "screws", "wire"],
        "Textiles 👕": ["textile", "clothes", "fabric", "shirt", "pants", "cloth", "cotton", "wool"],
        "Oil 🛢": ["oil", "cooking oil", "motor oil", "lubricant", "grease"],
        "Hazardous waste ⚠": ["battery", "chemical", "toxic", "medicine", "paint", "solvent", "cleaner"],
        "Foam packaging ☁": ["foam", "styrofoam", "polystyrene", "packing", "cushion", "insulation"]
    }
    
    # Score each category
    scores = {}
    for category, word_list in keywords.items():
        scores[category] = 0
        for word in word_list:
            if word in description:
                scores[category] += 1
    
    # Find best category
    if any(scores.values()):
        best_category = max(scores, key=scores.get)
        confidence = min(0.7, scores[best_category] / len(keywords[best_category]))
        return best_category, confidence
    else:
        return "Household waste 🗑", 0.3  # Default category

# Simple image-based prediction as fallback
def simple_image_prediction(image):
    """Simple color-based prediction as fallback for image classification"""
    try:
        # Convert to numpy array
        img_array = np.array(image)
        
        # Analyze average color
        avg_color = np.mean(img_array, axis=(0, 1))
        
        # Simple logic based on dominant color
        r, g, b = avg_color[:3]
        
        if g > r and g > b:  # Green dominant
            return "Green waste 🌿", 0.5
        elif b > r and b > g:  # Blue dominant
            return "Paper 📄", 0.4
        elif r > g and r > b:  # Red/Brown dominant
            return "Cardboard 📦", 0.4
        elif r > 200 and g > 200 and b > 200:  # Very light
            return "Foam packaging ☁", 0.4
        elif r < 50 and g < 50 and b < 50:  # Very dark
            return "Metal 🪙", 0.4
        else:
            return "Household waste 🗑", 0.3
    except Exception as e:
        logger.error(f"Error in color-based prediction: {str(e)}")
        return "Household waste 🗑", 0.3

# Enhanced predict_from_text function with fallback
def predict_from_text(description, model=None, vectorizer=None, encoder=None):
    """Predict waste type from text with fallback to rule-based"""
    if not description:
        return None, 0.0
    
    # Use ML model if available
    if model is not None and vectorizer is not None and encoder is not None:
        try:
            description = description.lower()
            X_new = vectorizer.transform([description])
            prediction = model.predict(X_new)[0]
            probabilities = model.predict_proba(X_new)[0]
            confidence = probabilities[prediction]
            
            # Get category from encoder and ensure it's in the right format
            category = encoder.inverse_transform([prediction])[0]

        # Map category to UI format with emojis if needed
            category_mapping = {
                "Household": "Household waste 🗑",
                "Paper": "Paper 📄",
                "Cardboard": "Cardboard 📦",
                "Glass": "Glass 🍾",
                 "Green": "Green waste 🌿",
                "Cans": "Cans 🥫",
                "Aluminium": "Aluminium 🧴",
                "Metal": "Metal 🪙",
                "Textiles": "Textiles 👕",
                "Oil": "Oil 🛢",
                "Hazardous": "Hazardous waste ⚠",
                "Foam packaging": "Foam packaging ☁"
            }

            ui_category = category_mapping.get(category, category)

            if confidence < 0.3:
                return "Unknown 🚫", float(confidence)

            return ui_category, float(confidence)

        except Exception as e:
            logger.error(f"Error in ML text prediction: {str(e)}")
            # Fall back to rule-based
            return rule_based_prediction(description)
    else:
        # Fall back to rule-based prediction
        logger.info("ML model not available, using rule-based prediction")
        return rule_based_prediction(description)

# Enhanced predict_from_image function with fallback
def predict_from_image(img, model=None, class_names=None):
    """Predict waste type from image with fallback to color-based"""
    if model is None or class_names is None:
        # Fallback to color-based prediction
        logger.info("Image model not available, using color-based prediction")
        return simple_image_prediction(img)
        
    try:
        # Ensure TensorFlow is imported
        import tensorflow as tf
        from tensorflow.keras.preprocessing import image as keras_image
        
        # Preprocess image
        img = img.resize((224, 224))
        img_array = keras_image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = img_array / 255.0
        
        # Make prediction
        predictions = model.predict(img_array)
        class_idx = np.argmax(predictions[0])
        confidence = float(np.max(predictions[0]))
        
        # Get class name
        if class_idx < len(class_names):
            category = class_names[class_idx]
            return category, confidence
        else:
            logger.error(f"Invalid class index: {class_idx}, max expected: {len(class_names)-1}")
            return simple_image_prediction(img)
            
    except Exception as e:
        logger.error(f"Error in image prediction: {str(e)}")
        return simple_image_prediction(img)

# Function to convert waste type selected in UI to API format
def convert_waste_type_to_api(ui_waste_type):
    mapping = {
        "Household waste 🗑": "Kehricht",
        "Paper 📄": "Papier",
        "Cardboard 📦": "Karton",
        "Glass 🍾": "Glas",
        "Green waste 🌿": "Grüngut",
        "Cans 🥫": "Dosen",
        "Aluminium 🧴": "Aluminium",
        "Metal 🪙": "Altmetall",
        "Textiles 👕": "Alttextilien",
        "Oil 🛢": "Altöl",
        "Hazardous waste ⚠": "Sonderabfall",
        "Foam packaging ☁": "Styropor"
    }
    return mapping.get(ui_waste_type, ui_waste_type)

# Convert API waste type to UI format (with emojis)
def convert_api_to_ui_waste_type(api_waste_type):
    mapping = {
        "Kehricht": "Household waste 🗑",
        "Papier": "Paper 📄",
        "Karton": "Cardboard 📦",
        "Glas": "Glass 🍾",
        "Grüngut": "Green waste 🌿",
        "Dosen": "Cans 🥫",
        "Aluminium": "Aluminium 🧴",
        "Altmetall": "Metal 🪙",
        "Alttextilien": "Textiles 👕",
        "Altöl": "Oil 🛢",
        "Sonderabfall": "Hazardous waste ⚠",
        "Styropor": "Foam packaging ☁"
    }
    return mapping.get(api_waste_type, api_waste_type)

# Define image class names (needed across pages)
IMAGE_CLASS_NAMES = [
    "Household waste 🗑", 
    "Paper 📄", 
    "Cardboard 📦", 
    "Glass 🍾", 
    "Green waste 🌿", 
    "Cans 🥫", 
    "Aluminium 🧴", 
    "Foam packaging ☁", 
    "Metal 🪙", 
    "Textiles 👕", 
    "Oil 🛢", 
    "Hazardous waste ⚠"
]

# Home page content
st.title("WasteWise - Your smart recycling assistant")
st.markdown("### Easily find where to dispose of your waste and contribute to a cleaner environment")

# Feature showcases with icons and descriptions
st.markdown("## 🧐 What can WasteWise do for you?")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🚮 Find Collection Points")
    st.markdown("""
    Simply tell us what waste you want to dispose of and your address in St. Gallen.
    We'll find the nearest collection points and upcoming collection dates for you.
    """)
    st.page_link("pages/2_🚮_Find_Collection_Point.py", label="Find Disposal Options", icon="🔍")
    
with col2:
    st.markdown("### 🔍 Identify Your Waste")
    st.markdown("""
    Not sure what type of waste you have? Upload a photo or describe it,
    and our AI will help you identify it and provide proper disposal instructions.
    """)
    st.page_link("pages/3_🔍_Identify_Waste.py", label="Identify Your Waste", icon="📸")

# Tips of the day
st.markdown("---")
st.subheader("💡 Tip of the Day")
tips_of_the_day = [
    "Recycling one aluminum can saves enough energy to run a TV for three hours.",
    "Paper can be recycled up to 7 times before the fibers become too short.",
    "Glass is 100% recyclable and can be recycled infinitely without losing its quality!",
    "A mobile phone contains more than 70 different materials, many of which are recyclable.",
    "Batteries contain toxic heavy metals, never throw them away with household waste.",
    "Consider putting a 'No Junk Mail' sticker on your mailbox to reduce paper waste.",
    "Composting can reduce the volume of your household waste by up to 30%.",
    "Remember to break down cardboard packaging before disposing of it to save space.",
    "LED bulbs are less harmful to the environment and last longer."
]
import random
st.info(random.choice(tips_of_the_day))

# Footer
st.markdown("---")
st.markdown("© 2025 WasteWise - University Project | [Contact](mailto:contact@wastewise.example.com) | [Legal notice](https://example.com)")
