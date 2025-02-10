import numpy as np
import pandas as pd
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import time
import os
import pickle
from sklearn.ensemble import RandomForestRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import GradientBoostingRegressor
from catboost import CatBoostRegressor
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import ElasticNet
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
import lightgbm as lgb
from sklearn.svm import SVR
from concurrent.futures import ThreadPoolExecutor
from django.shortcuts import render
# from django.shortcuts import redirect
# from .forms import IoTInputForm
# from .models import IoTInput
# from django.core.mail import send_mail
# from joblib import Parallel, delayed
# from django.conf import settings
# import requests
# import firebase_admin
from firebase_admin import db
import uuid  # For generating unique message IDs


# Define dictionary-based suggestions for each parameter
suggestion_rules = {
    "Temperature": [
        {"range": (0, 10), "ayurvedic": "Avoid drinking cold water in winters, store in clay pots", 
         "scientific": "Let water reach room temperature before drinking", "cross_verification": "Use a digital thermometer"},
        {"range": (10, 20), "ayurvedic": "Store in copper vessels to retain minerals", 
         "scientific": "Insulate pipes to avoid cooling too much", "cross_verification": "Compare with another water source"},
        {"range": (20, 30), "ayurvedic": "✅ No action needed", "scientific": "✅ No action needed", 
         "cross_verification": "✅ Compare water from different sources"},
        {"range": (30, 40), "ayurvedic": "Add Tulsi leaves to cool naturally", 
         "scientific": "Store in glass bottles instead of plastic", "cross_verification": "Use a temperature probe"},
        {"range": (40, float('inf')), "ayurvedic": "Cool water naturally in earthen pots", 
         "scientific": "Use an RO system with a cooling feature", "cross_verification": "Measure after keeping in shade"}
    ],
    
    "Dissolved Oxygen": [
        {"range": (10, float('inf')), "ayurvedic": "✅ No action needed", "scientific": "✅ No action needed", 
         "cross_verification": "Use an oxygen meter"},
        {"range": (6, 10), "ayurvedic": "Store in copper vessels to maintain quality", 
         "scientific": "✅ No action needed", "cross_verification": "Compare with aerated water"},
        {"range": (4, 6), "ayurvedic": "Aerate by pouring water between containers", 
         "scientific": "Use an air bubbler or waterfall filter", "cross_verification": "Observe fish behavior"},
        {"range": (2, 4), "ayurvedic": "Use activated charcoal filtration", 
         "scientific": "Add hydrogen peroxide (3%) in small doses", "cross_verification": "Check for unpleasant odor"},
        {"range": (0, 2), "ayurvedic": "Avoid drinking, switch to another source", 
         "scientific": "Use oxygen tablets (Na₂O₂, from medical stores)", "cross_verification": "Send water for lab analysis"}
    ],

    "pH": [
        {"range": (0, 5.5), "ayurvedic": "Add Tulsi or Neem leaves", 
         "scientific": "Add baking soda (food-grade, safe)", "cross_verification": "Use pH strips (easily available)"},
        {"range": (5.5, 6.5), "ayurvedic": "Store in copper vessels", 
         "scientific": "Use calcium carbonate tablets", "cross_verification": "Compare with bottled water"},
        {"range": (6.5, 7.5), "ayurvedic": "✅ No action needed", "scientific": "✅ No action needed", 
         "cross_verification": "pH meter or litmus paper"},
        {"range": (7.5, 8.5), "ayurvedic": "Add lemon drops to balance pH", 
         "scientific": "Use alum (fitkari) small dose", "cross_verification": "Compare with rainwater pH"},
        {"range": (8.5, float('inf')), "ayurvedic": "Use clay pot storage", 
         "scientific": "Use food-grade vinegar drops", "cross_verification": "Verify with a TDS meter"}
    ],

    "Conductivity": [
        {"range": (0, 50), "ayurvedic": "Store in copper vessels", 
         "scientific": "Add electrolyte tablets (ORS, medical store)", "cross_verification": "Use a TDS meter"},
        {"range": (50, 500), "ayurvedic": "✅ No action needed", "scientific": "✅ No action needed", 
         "cross_verification": "Compare TDS with RO water"},
        {"range": (500, 1000), "ayurvedic": "Use Tulsi leaves to absorb minor contaminants", 
         "scientific": "Use activated carbon filtration", "cross_verification": "Compare with tap water"},
        {"range": (1000, 2000), "ayurvedic": "Store in earthen pots", 
         "scientific": "Use RO system or ion-exchange filter", "cross_verification": "Use a digital TDS meter"},
        {"range": (2000, float('inf')), "ayurvedic": "Avoid drinking directly", 
         "scientific": "Use Reverse Osmosis (RO) with remineralization", "cross_verification": "Lab testing recommended"}
    ],

    "BOD": [
        {"range": (0, 2), "ayurvedic": "✅ No action needed", "scientific": "✅ No action needed", 
         "cross_verification": "Compare with natural spring water"},
        {"range": (2, 4), "ayurvedic": "Use natural bio-filters like plants", 
         "scientific": "Use UV filtration", "cross_verification": "Check for slight odor"},
        {"range": (4, 6), "ayurvedic": "Use activated charcoal", 
         "scientific": "Use chlorine drops (available in medical stores)", "cross_verification": "Compare with purified water"},
        {"range": (6, 10), "ayurvedic": "Use drumstick (Moringa) seed powder", 
         "scientific": "Use ozone treatment", "cross_verification": "Lab testing suggested"},
        {"range": (10, float('inf')), "ayurvedic": "Avoid consumption, seek alternative sources", 
         "scientific": "Use advanced bio-remediation methods", "cross_verification": "Professional lab testing needed"}
    ],

    "Nitrate": [
        {"range": (0, 1), "ayurvedic": "✅ No action needed", "scientific": "✅ No action needed", 
         "cross_verification": "Use nitrate test strips"},
        {"range": (1, 5), "ayurvedic": "Store in copper vessels", 
         "scientific": "Use activated carbon filter", "cross_verification": "Compare with bottled water"},
        {"range": (5, 10), "ayurvedic": "Use drumstick seed powder", 
         "scientific": "Use ion-exchange resin filters", "cross_verification": "Lab testing recommended"},
        {"range": (10, 25), "ayurvedic": "Avoid drinking directly", 
         "scientific": "Use Reverse Osmosis (RO) system", "cross_verification": "Professional water analysis suggested"},
        {"range": (25, float('inf')), "ayurvedic": "Avoid drinking completely", 
         "scientific": "Use a specialized nitrate removal system", "cross_verification": "Mandatory lab testing"}
    ],

    "Total Coliform": [
        {"range": (0, 1), "ayurvedic": "✅ No action needed", "scientific": "✅ No action needed", 
         "cross_verification": "Use coliform test kits"},
        {"range": (1, 10), "ayurvedic": "Boil water before drinking", 
         "scientific": "Use UV sterilization", "cross_verification": "Check for odor"},
        {"range": (10, 100), "ayurvedic": "Use Tulsi leaves", 
         "scientific": "Use chlorine tablets (available in pharmacies)", "cross_verification": "Use a coliform test kit"},
        {"range": (100, 1000), "ayurvedic": "Avoid drinking directly", 
         "scientific": "Use advanced RO filtration", "cross_verification": "Lab testing mandatory"},
        {"range": (1000, float('inf')), "ayurvedic": "Do not use for drinking", 
         "scientific": "Seek government-approved water treatment", "cross_verification": "Urgent professional testing needed"}
    ]
}

def contact(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")

        print(name, "\n\n", email, "\n\n", message)

        try:
            # Get reference to Firebase database
            ref = db.reference("contact_messages")

            # Generate a unique ID for each message
            message_id = str(uuid.uuid4())

            # Save data to Firebase
            ref.child(message_id).set({
                "name": name,
                "email": email,
                "message": message
            })

            return render(request, "contact.html", {"success": True})
        except Exception as e:
            return render(request, "contact.html", {"error": str(e)})

    return render(request, "contact.html")
    
# Function to classify WQI
def classify_wqi(wqi_value):
    if 91 <= wqi_value <= 100:
        return "Excellent"
    elif 71 <= wqi_value < 91:
        return "Good"
    elif 51 <= wqi_value < 71:
        return "Average"
    elif 26 <= wqi_value < 51:
        return "Fair"
    else:
        return "Poor"

# Function to find the correct suggestion based on parameter value
def get_suggestion(parameter, value):
    for rule in suggestion_rules.get(parameter, []):
        if rule["range"][0] <= value < rule["range"][1]:  # Check if value is in range
            return {
                "parameter": parameter,
                "range": f"{value}",
                "ayurvedic": rule["ayurvedic"],
                "scientific": rule["scientific"],
                "cross_verification": rule["cross_verification"]
            }
    return None  # Return None if no match found

def load_and_predict(model_file, input_features_df):
    """Load model and make prediction."""
    with open(model_file, "rb") as file:
        model = pickle.load(file)
        wqi_value = round(model.predict(input_features_df)[0], 2)
        # return model_file, wqi_value, classify_wqi(wqi_value)
        return wqi_value, classify_wqi(wqi_value)

def manual_predict_suggest(request):
    """Handles input from manual_input.html and predicts WQI using multiple models."""
    
    # Check if the request is from 'manual_input.html'
    source = request.POST.get("source", "")
    if source != "manual_input":
        return render(request, "suggestions.html")  # If not from manual_input, render suggestion.html

    # Extract input values from form
    try:
        temperature = float(request.POST.get("temp", 0))
        dissolved_oxygen = float(request.POST.get("DO", 0))
        pH = float(request.POST.get("pH", 0))
        conductivity = float(request.POST.get("cond", 0))
        bod = float(request.POST.get("BOD", 0))
        nitrate = float(request.POST.get("Nitrate", 0))
        total_coliform = float(request.POST.get("TotalColiform", 0))

        input_values = np.array([[temperature, dissolved_oxygen, pH, conductivity, bod, nitrate, total_coliform]])
        feature_columns = ["Temperature", "Dissolved Oxygen", "pH", "Conductivity", "BOD", "Nitrate", "Total Coliform"]
        input_features_df = pd.DataFrame(input_values, columns = feature_columns)
    
    except ValueError:
        return render(request, "auto_suggest.html", {"error": "Invalid input values"})

    # Load ML models and get predictions
    model_path = "static/model/eight parameter/"

    # Mapping model filenames to full model names
    model_name_mapping = {
        "SVR_model.pkl": "Support Vector Regressor",
        "CBR_model.pkl": "CatBoost Regressor",
        "DTR_model.pkl": "Decision Tree Regressor",
        "ENR_model.pkl": "ElasticNet Regressor",
        "GBR_model.pkl": "Gradient Boosting Regressor",
        "HGB_model.pkl": "Hist Gradient Boosting Regressor",
        "LGB_model.pkl": "LightGBM Regressor",
        "LR_model.pkl": "Linear Regression",
        "PolyR_model.pkl": "Polynomial Regression",
        "RFR_model.pkl": "Random Forest Regressor"
    }

    model_names = list(model_name_mapping.keys())  # Model filenames

    predictions = {}

    # Use threading to load models & predict in parallel
    with ThreadPoolExecutor() as executor:
        futures = {}
        for model_name in model_names:
            model_file = os.path.join(model_path, model_name)
            if os.path.exists(model_file):
                futures[model_name] = executor.submit(load_and_predict, model_file, input_features_df)

        for model_name, future in futures.items():
            wqi_value, classification = future.result()
            
            # Use full model name instead of filename
            full_model_name = model_name_mapping.get(model_name, model_name)  # Default to filename if missing
            
            predictions[full_model_name] = {
                "wqi": wqi_value,
                "classification": classification
            } 

    # Generate parameter-based suggestions
    parameter_values = {
        "Temperature": temperature,
        "Dissolved Oxygen": dissolved_oxygen,
        "pH": pH,
        "Conductivity": conductivity,
        "BOD": bod,
        "Nitrate": nitrate,
        "Total Coliform": total_coliform
    }

    suggestions = []

    for param, value in parameter_values.items():
        suggestion = get_suggestion(param, value)
        if suggestion:
            suggestions.append(suggestion)
        

    # Pass data to the template
    context = {
        "predictions": predictions,  # Dictionary of WQI values & classification for all models
        "suggestions": suggestions,  # List of parameter-based improvement methods
        "input_values": parameter_values  # User input values
    }

    return render(request, "auto_suggest.html", context)

def iot_predict_suggest(request):
    """Handles input from manual_input.html and predicts WQI using multiple models."""
    
    # Check if the request is from 'manual_input.html'
    source = request.POST.get("source", "")
    if source != "iot_input":
        return render(request, "suggestions.html")  # If not from manual_input, render suggestion.html

    # Extract input values from form
    try:
        temperature = float(request.POST.get("temp", 0))
        dissolved_oxygen = float(request.POST.get("DO", 0))
        pH = float(request.POST.get("pH", 0))
        conductivity = float(request.POST.get("cond", 0))

        input_values = np.array([[temperature, dissolved_oxygen, pH, conductivity]])
        feature_columns = ["Temperature", "Dissolved Oxygen", "pH", "Conductivity"]
        input_features_df = pd.DataFrame(input_values, columns = feature_columns)
    
    except ValueError:
        return render(request, "auto_suggest.html", {"error": "Invalid input values"})

    # Load ML models and get predictions
    model_path = "static/model/four parameter/"

    # Mapping model filenames to full model names
    model_name_mapping = {
        "SVR_model.pkl": "Support Vector Regressor",
        "CBR_model.pkl": "CatBoost Regressor",
        "DTR_model.pkl": "Decision Tree Regressor",
        "ENR_model.pkl": "ElasticNet Regressor",
        "GBR_model.pkl": "Gradient Boosting Regressor",
        "HGB_model.pkl": "Hist Gradient Boosting Regressor",
        "LGB_model.pkl": "LightGBM Regressor",
        "LR_model.pkl": "Linear Regression",
        "PolyR_model.pkl": "Polynomial Regression",
        "RFR_model.pkl": "Random Forest Regressor"
    }

    model_names = list(model_name_mapping.keys())  # Model filenames

    predictions = {}

    # Use threading to load models & predict in parallel
    with ThreadPoolExecutor() as executor:
        futures = {}
        for model_name in model_names:
            model_file = os.path.join(model_path, model_name)
            if os.path.exists(model_file):
                futures[model_name] = executor.submit(load_and_predict, model_file, input_features_df)

        for model_name, future in futures.items():
            wqi_value, classification = future.result()
            
            # Use full model name instead of filename
            full_model_name = model_name_mapping.get(model_name, model_name)  # Default to filename if missing
            
            predictions[full_model_name] = {
                "wqi": wqi_value,
                "classification": classification
            } 

    # Generate parameter-based suggestions
    parameter_values = {
        "Temperature": temperature,
        "Dissolved Oxygen": dissolved_oxygen,
        "pH": pH,
        "Conductivity": conductivity
    }

    suggestions = []

    for param, value in parameter_values.items():
        suggestion = get_suggestion(param, value)
        if suggestion:
            suggestions.append(suggestion)
        

    # Pass data to the template
    context = {
        "predictions": predictions,  # Dictionary of WQI values & classification for all models
        "suggestions": suggestions,  # List of parameter-based improvement methods
        "input_values": parameter_values  # User input values
    }

    return render(request, "auto_suggest.html", context)

eight_gbr_model_path = os.path.join("static", "model", "eight parameter", "GBR_model.pkl")

four_gbr_model_path = os.path.join("static", "model", "four parameter", "GBR_model.pkl")

with open(eight_gbr_model_path, "rb") as file:
    eight_gbr_model = pickle.load(file)

with open(four_gbr_model_path, "rb") as file:
    four_gbr_model = pickle.load(file)
    
def safe_float(value):
    try:
        return float(value)
    except ValueError:
        return None

def manual_wqi_prediction(request):
    if request.method == "POST":
        try:

            temp = safe_float(request.POST.get("temp", 0))
            do = safe_float(request.POST.get("DO", 0))
            ph = safe_float(request.POST.get("pH", 0))
            conductivity = safe_float(request.POST.get("cond", 0))
            bod = safe_float(request.POST.get("BOD", 0))
            nitrate = safe_float(request.POST.get("Nitrate", 0))
            total_coliform = safe_float(request.POST.get("TotalColiform", 0))
            
            input_features = np.array([[temp, do, ph, conductivity, bod, nitrate, total_coliform]])
            feature_columns = ["Temperature", "Dissolved Oxygen", "pH", "Conductivity", "BOD", "Nitrate", "Total Coliform"]
            input_features_df = pd.DataFrame(input_features, columns = feature_columns)
            wqi_value = round(eight_gbr_model.predict(input_features_df)[0], 2)

            # Determine WQI category & color
            if 91 <= wqi_value <= 100:
                category = "Excellent"
                color = "green"
            elif 71 <= wqi_value < 91:
                category = "Good"
                color = "lightgreen"
            elif 51 <= wqi_value < 71:
                category = "Average"
                color = "yellow"
            elif 26 <= wqi_value < 51:
                category = "Fair"
                color = "orange"
            else:
                category = "Poor"
                color = "red"

            return JsonResponse({"wqi": wqi_value, "category": category, "color": color})
        
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request"}, status=400)

def iot_wqi_prediction(request):
    if request.method == "POST":
        try:

            temp = safe_float(request.POST.get("temp", 0))
            do = safe_float(request.POST.get("DO", 0))
            ph = safe_float(request.POST.get("pH", 0))
            conductivity = safe_float(request.POST.get("cond", 0))
            
            input_features = np.array([[temp, do, ph, conductivity]])
            feature_columns = ["Temperature", "Dissolved Oxygen", "pH", "Conductivity"]
            input_features_df = pd.DataFrame(input_features, columns = feature_columns)
            wqi_value = round(four_gbr_model.predict(input_features_df)[0], 2)

            # Determine WQI category & color
            if 91 <= wqi_value <= 100:
                category = "Excellent"
                color = "green"
            elif 71 <= wqi_value < 91:
                category = "Good"
                color = "lightgreen"
            elif 51 <= wqi_value < 71:
                category = "Average"
                color = "yellow"
            elif 26 <= wqi_value < 51:
                category = "Fair"
                color = "orange"
            else:
                category = "Poor"
                color = "red"

            return JsonResponse({"wqi": wqi_value, "category": category, "color": color})
        
        except Exception as e:
            return JsonResponse({"iot error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request"}, status=400)

iot_data_storage = {}  # Temporary storage for IoT data (use database for persistence)

@csrf_exempt
def iot_data(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            # Validate the data
            required_fields = ["temperature", "pH", "conductivity", "dissolved_oxygen"]
            if not all(field in data for field in required_fields):
                return JsonResponse({"status": "error", "message": "Missing required fields"}, status=400)

            # Store the data in memory or database
            global iot_data_storage
            iot_data_storage = data
            return JsonResponse({"status": "success", "message": "Data received"})

        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON format"}, status=400)

    elif request.method == 'GET':
        # Long polling: Wait for data to be available
        start_time = time.time()
        while time.time() - start_time < 600:  # Wait for up to 10 minutes
            if iot_data_storage:
                data = iot_data_storage
                iot_data_storage = {}  # Clear after sending
                return JsonResponse({"status": "success", "data": data})
            time.sleep(1)  # Sleep briefly to avoid high CPU usage

        # Timeout
        return JsonResponse({"status": "timeout", "message": "No data received within the timeout period"})

    return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)

def home(request):
    return render(request, 'home.html')

def manual_input(request): 
    return render(request, 'manual_input.html')

def iot_input(request):
    return render(request, 'iot_input.html')

def suggestions(request):
    return render(request, 'suggestions.html')
