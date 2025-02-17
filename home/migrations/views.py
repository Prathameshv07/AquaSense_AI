import numpy as np
import pandas as pd
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import time
import os
import pickle
from concurrent.futures import ThreadPoolExecutor
from django.shortcuts import render
from django.utils.safestring import mark_safe
from firebase_admin import db
import uuid  # For generating unique message IDs
# from django.shortcuts import redirect
# from .forms import IoTInputForm
# from .models import IoTInput
# from django.core.mail import send_mail
# from joblib import Parallel, delayed
# from django.conf import settings
# import requests
import firebase_admin
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

# Define dictionary-based suggestions for each parameter
suggestion_rules = {
    "Temperature": [
        {
            "range": (0, 10), 
            "ayurvedic": mark_safe('Avoid drinking cold water in winters, store in clay pots'), 
            "scientific": mark_safe('Let water reach room temperature before drinking'), 
            "cross_verification": mark_safe('Use a digital thermometer')
        },
        {
            "range": (10, 20),
            "ayurvedic": mark_safe('Store in copper vessels to retain minerals'), 
            "scientific": mark_safe('Insulate pipes to avoid cooling too much <a href="https://www.youtube.com/watch?v=b8y9BVefZAU">Know more</a>'), 
            "cross_verification": mark_safe('Compare with another water source')
        },
        {   
            "range": (20, 30), 
            "ayurvedic": mark_safe('✅ No action needed'), 
            "scientific": mark_safe('✅ No action needed'), 
            "cross_verification": mark_safe('✅ Compare water from different sources')
        },
        {   
            "range": (30, 40), 
            "ayurvedic": mark_safe('Add Tulsi leaves to cool naturally'), 
            "scientific": mark_safe('Store in glass bottles instead of plastic'), 
            "cross_verification": mark_safe('Use a temperature probe <a href="https://www.youtube.com/watch?v=1yBaK2ZpCFE">Know more</a>')
        },
        {
            "range": (40, float('inf')), 
            "ayurvedic": mark_safe('Cool water naturally in earthen pots'), 
            "scientific": mark_safe('Use an RO system with a cooling feature'), 
            "cross_verification": mark_safe('Measure after keeping in shade')
        }
    ],
    
    "Dissolved Oxygen": [
        {
            "range": (10, float('inf')), 
            "ayurvedic": mark_safe('✅ No action needed'), 
            "scientific": mark_safe('✅ No action needed'), 
            "cross_verification": mark_safe('Use an oxygen meter <a href="https://www.youtube.com/watch?v=afsSETS3FkQ">Know more</a>')
        },
        {
            "range": (6, 10), 
            "ayurvedic": mark_safe('Store in copper vessels to maintain quality'), 
            "scientific": mark_safe('✅ No action needed'), 
            "cross_verification": mark_safe('Compare with aerated water')
        },
        {
            "range": (4, 6), 
            "ayurvedic": mark_safe('Aerate by pouring water between containers'), 
            "scientific": mark_safe('Use an air bubbler or waterfall filter <a href="https://www.youtube.com/watch?v=i4AyFzkIYpI">Know more</a>'), 
            "cross_verification": mark_safe('Observe fish behavior')
        },
        {
            "range": (2, 4), 
            "ayurvedic": mark_safe('Use activated charcoal filtration <a href="https://www.youtube.com/watch?v=ilXeKg9IwaY">Know more</a>'), 
            "scientific": mark_safe('Add hydrogen peroxide (3%) in small doses <a href="https://www.fishsens.com/use-hydrogen-peroxide-to-boost-dissolved-oxygen-levels-in-an-emergency/">know more</a>'), 
            "cross_verification": mark_safe('Check for unpleasant odor')
        },
        {
            "range": (0, 2), 
            "ayurvedic": mark_safe('Avoid drinking, switch to another source'), 
            "scientific": mark_safe('Use oxygen tablets (Na₂O₂, from medical stores) <a href="https://www.youtube.com/watch?v=6hw8yK1V64g">Know more</a>'), 
            "cross_verification": mark_safe('Send water for lab analysis')
        }
    ],

    "pH": [
        {
            "range": (0, 5.5), 
            "ayurvedic": mark_safe('Add Tulsi or Neem leaves'), 
            "scientific": mark_safe('Add baking soda (food-grade, safe) <a href="https://www.youtube.com/watch?v=oh3J06VfHTE">Know more</a>'), 
            "cross_verification": mark_safe('Use pH strips (easily available) <a href="https://www.youtube.com/watch?v=up7Y9k0lzEs">Know more</a>')
        },
        {
            "range": (5.5, 6.5), 
            "ayurvedic": mark_safe('Store in copper vessels'), 
            "scientific": mark_safe('Use calcium carbonate tablets'), 
            "cross_verification": mark_safe('Compare with bottled water')
        },
        {
            "range": (6.5, 7.5), 
            "ayurvedic": mark_safe('✅ No action needed'), 
            "scientific": mark_safe('✅ No action needed'), 
            "cross_verification": mark_safe('pH meter or litmus paper')
        },
        {
            "range": (7.5, 8.5), 
            "ayurvedic": mark_safe('Add lemon drops to balance pH'), 
            "scientific": mark_safe('Use alum (fitkari) small dose'), 
            "cross_verification": mark_safe('Compare with rainwater pH')
        },
        {
            "range": (8.5, float('inf')), 
            "ayurvedic": mark_safe('Use clay pot storage'), 
            "scientific": mark_safe('Use food-grade vinegar drops <a href="http://youtube.com/watch?v=8QVoUEyYFHM">Know more</a>'), 
            "cross_verification": mark_safe('Verify with a TDS meter')
        }
    ],

    "Conductivity": [
        {
            "range": (0, 50), 
            "ayurvedic": mark_safe('Store in copper vessels'), 
            "scientific": mark_safe('Add electrolyte tablets (ORS, medical store)'), 
            "cross_verification": mark_safe('Use a TDS meter')
        },
        {
            "range": (50, 500), 
            "ayurvedic": mark_safe('✅ No action needed'), 
            "scientific": mark_safe('✅ No action needed'), 
            "cross_verification": mark_safe('Compare TDS with RO water')
        },
        {
            "range": (500, 1000), 
            "ayurvedic": mark_safe('Use Tulsi leaves to absorb minor contaminants'), 
            "scientific": mark_safe('Use activated carbon filtration <a href="https://www.youtube.com/watch?v=Ge6pOJcT5i4">Know more</a>'), 
            "cross_verification": mark_safe('Compare with tap water')
        },
        {
            "range": (1000, 2000), 
            "ayurvedic": mark_safe('Store in earthen pots'), 
            "scientific": mark_safe('Use RO system or ion-exchange filter'), 
            "cross_verification": mark_safe('Use a digital TDS meter')
        },
        {
            "range": (2000, float('inf')), 
            "ayurvedic": mark_safe('Avoid drinking directly'), 
            "scientific": mark_safe('Use Reverse Osmosis (RO) with remineralization'), 
            "cross_verification": mark_safe('Lab testing recommended')
        }
    ],

    "BOD": [
        {
            "range": (0, 2), 
            "ayurvedic": mark_safe('✅ No action needed'), 
            "scientific": mark_safe('✅ No action needed'), 
            "cross_verification": mark_safe('Compare with natural spring water')
        },
        {
            "range": (2, 4), 
            "ayurvedic": mark_safe('Use natural bio-filters like plants <a href="https://www.youtube.com/watch?v=VFiPRE-x-UM">Know more</a>'), 
            "scientific": mark_safe('Use UV filtration <a href="https://www.youtube.com/watch?v=723XDGMP-28">Know more</a>'), 
            "cross_verification": mark_safe('Check for slight odor')
        },
        {
            "range": (4, 6), 
            "ayurvedic": mark_safe('Use activated charcoal <a href="https://www.youtube.com/watch?v=yoitlwJl_SU">Know more</a>'), 
            "scientific": mark_safe('Use chlorine drops (available in medical stores)'), 
            "cross_verification": mark_safe('Compare with purified water')
        },
        {
            "range": (6, 10), 
            "ayurvedic": mark_safe('Use drumstick (Moringa) seed powder <a href="https://www.youtube.com/watch?v=BnsjGDBlg84">Know more</a>'), 
            "scientific": mark_safe('Use ozone treatment <a href="https://www.youtube.com/watch?v=8BsCGonAWXE">Know more</a>'), 
            "cross_verification": mark_safe('Lab testing suggested')
        },
        {
            "range": (10, float('inf')), 
            "ayurvedic": mark_safe('Avoid consumption, seek alternative sources'), 
            "scientific": mark_safe('Use advanced bio-remediation methods'), 
            "cross_verification": mark_safe('Professional lab testing needed')
        }
    ],

    "Nitrate": [
        {
            "range": (0, 1), 
            "ayurvedic": mark_safe('✅ No action needed'), 
            "scientific": mark_safe('✅ No action needed'), 
            "cross_verification": mark_safe('Use nitrate test strips')
        },
        {
            "range": (1, 5), 
            "ayurvedic": mark_safe('Store in copper vessels'), 
            "scientific": mark_safe('Use activated carbon filter <a href="https://www.youtube.com/watch?v=3ehdx27olJQ">Know more</a>'), 
            "cross_verification": mark_safe('Compare with bottled water')
        },
        {
            "range": (5, 10), 
            "ayurvedic": mark_safe('Use drumstick seed powder'), 
            "scientific": mark_safe('Use ion-exchange resin filters'), 
            "cross_verification": mark_safe('Lab testing recommended')
        },
        {   
            "range": (10, 25), 
            "ayurvedic": mark_safe('Avoid drinking directly'), 
            "scientific": mark_safe('Use Reverse Osmosis (RO) system'), 
            "cross_verification": mark_safe('Professional water analysis suggested')
        },
        {
            "range": (25, float('inf')), 
            "ayurvedic": mark_safe('Avoid drinking completely'), 
            "scientific": mark_safe('Use a specialized nitrate removal system'), 
            "cross_verification": mark_safe('Mandatory lab testing')
        }
    ],

    "Total Coliform": [
        {
            "range": (0, 1), 
            "ayurvedic": mark_safe('✅ No action needed'), 
            "scientific": mark_safe('✅ No action needed'), 
            "cross_verification": mark_safe('Use coliform test kits')
        },
        {
            "range": (1, 10), 
            "ayurvedic": mark_safe('Boil water before drinking'), 
            "scientific": mark_safe('Use UV sterilization <a href="https://www.youtube.com/watch?v=zZwI2LW0JHY">Know more</a>'), 
            "cross_verification": mark_safe('Check for odor')
        },
        {
            "range": (10, 100), 
            "ayurvedic": mark_safe('Use Tulsi leaves'), 
            "scientific": mark_safe('Use chlorine tablets (available in pharmacies)'), 
            "cross_verification": mark_safe('Use a coliform test kit')
        },
        {
            "range": (100, 1000), 
            "ayurvedic": mark_safe('Avoid drinking directly'), 
            "scientific": mark_safe('Use advanced RO filtration'), 
            "cross_verification": mark_safe('Lab testing mandatory')
        },
        {
            "range": (1000, float('inf')), 
            "ayurvedic": mark_safe('Do not use for drinking'), 
            "scientific": mark_safe('Seek government-approved water treatment'), 
            "cross_verification": mark_safe('Urgent professional testing needed')
        }
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
    # Convert suggestion_rules into a list of dictionaries for the template
    formatted_suggestions = []
    for parameter, cases in suggestion_rules.items():
        for case in cases:
            formatted_suggestions.append({
                "parameter": parameter,
                "range": case["range"],
                "ayurvedic": case["ayurvedic"],
                "scientific": case["scientific"],
                "cross_verification": case["cross_verification"]
            })

    return render(request, 'suggestions.html', {"suggestions": formatted_suggestions})
