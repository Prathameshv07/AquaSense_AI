# AquaSense AI

![AquaSense AI Banner](https://github.com/user-attachments/assets/6f9fd12a-c29d-44e3-9384-b22361716c78)

## Overview
AquaSense AI is an advanced water quality analysis platform built with Django that leverages 10 different machine learning models to provide accurate water quality assessments and remediation recommendations.

## Features
- **Multi-parameter Analysis:** Process 7 critical water parameters (temperature, dissolved oxygen, pH, conductivity, BOD, nitrate, total coliform)
- **IoT Integration:** Connect with sensor data for 4 key parameters in real-time
- **Advanced Prediction System:** Primary Gradient Boosting Regression model with ensemble assessment from 10 different ML models
- **Comprehensive Remediation Guidance:**
  - Ayurvedic treatment recommendations
  - Scientific intervention protocols
  - Cross-verification techniques
- **User-friendly Dashboard:** Visualize water quality metrics and predictions
- **Educational Resources:** Dedicated sections explaining water quality challenges, vision, and mission
- **User Support:** Firebase-connected contact system for inquiries and feedback

## Tech Stack
- **Backend:** Django, PostgreSQL
- **ML Implementation:** scikit-learn, joblib for model serialization
- **Frontend:** HTML, CSS, Bootstrap
- **Cloud Services:** Firebase (for contact system)

## Live Demo
Check out the live application: [AquaSense AI](https://aquasense-ai.onrender.com/)

## Installation and Setup
```bash
# Clone the repository
git clone https://github.com/your-username/aquasense-ai.git

# Navigate to project directory
cd aquasense-ai

# Create and activate virtual environment
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up database
python manage.py migrate

# Run the application
python manage.py runserver
