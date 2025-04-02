# AquaSense AI

![AquaSense AI Banner](https://github.com/user-attachments/assets/6f9fd12a-c29d-44e3-9384-b22361716c78)

## Overview
AquaSense AI is an water quality analysis platform built with Django that leverages multiple machine learning models to provide accurate water quality assessments and remediation recommendations.

## Features
- **Multi-parameter Analysis:** Process 7 critical water parameters (temperature, dissolved oxygen, pH, conductivity, BOD, nitrate, total coliform)
- **IoT Integration:** Connect with sensor data for 4 key parameters in real-time
- **Advanced Prediction System:** Gradient Boosting Regression model used for accurate prediction
- **Comprehensive Remediation Guidance:**
  - Ayurvedic treatment recommendations
  - Scientific intervention protocols
  - Cross-verification techniques
- **Educational Resources:** Dedicated sections explaining water quality challenges, vision, and mission
- **User Support:** Firebase-connected contact system for inquiries and feedback

## Tech Stack
- **Backend:** Django
- **ML Implementation:** scikit-learn, pickle for model serialization
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
```

## Usage
1. Enter water parameter values manually or connect IoT sensors
2. View ML-powered water quality predictions
3. Access remediation recommendations
4. Generate comprehensive reports

## Screenshots
### 1. Manual Input

![manual](https://github.com/user-attachments/assets/df31e7af-4b72-48de-92ac-9447d8b133f9)

### 2. IoT Input

![iot](https://github.com/user-attachments/assets/7fadf649-f8d2-4940-8a6f-ec680bfee360)

## Future Enhancements
- Mobile application integration
- Additional parameter support
- Enhanced visualization tools
- Community feature for data sharing

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## License
This project is licensed under the MIT License - see the LICENSE file for details.
