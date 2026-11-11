# AquaSense AI

![AquaSense AI Banner](https://github.com/user-attachments/assets/6f9fd12a-c29d-44e3-9384-b22361716c78)

## Overview
AquaSense AI is a water quality analysis platform built with Django that leverages multiple machine learning models to provide accurate water quality assessments and remediation recommendations.

## Features
- **Multi-parameter Analysis:** Process 7 critical water parameters (temperature, dissolved oxygen, pH, conductivity, BOD, nitrate, total coliform)
- **IoT Integration:** Connect with sensor data for 4 key parameters in real-time
- **Model Comparison:** 10 regression models trained and compared for each input mode (`static/model/`); the best performer, Gradient Boosting Regression, powers the live predictions
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

## Publication

This project is the basis of the paper:

> **Water Quality Predictions: Manual vs IoT Approaches**, *International Journal of Scientific Research and Engineering Development (IJSRED)*, March 2025.

The reported Gradient Boosting model reached an R² score of 0.96.

## Screenshots
### 1. Manual Input

![manual](https://github.com/user-attachments/assets/df31e7af-4b72-48de-92ac-9447d8b133f9)

### 2. IoT Input

![iot](https://github.com/user-attachments/assets/7fadf649-f8d2-4940-8a6f-ec680bfee360)

## Demo & Documentation

- 🎥 [Video Preview](https://drive.google.com/file/d/1hsBX123J4670n8O-Ly-EnBvvP2Xz5e3D/view)
- 📄 [Project Documentation](https://drive.google.com/file/d/12yG0ZnVzYoj3hk2gMPXeR7GlgZtbmon5/view)

## Installation and Setup
```bash
# Clone the repository
git clone https://github.com/Prathameshv07/AquaSense_AI.git

# Navigate to project directory
cd AquaSense_AI

# Create and activate virtual environment
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables (Firebase is optional - only the contact form needs it)
cp .env.example .env

# Run the application (http://127.0.0.1:8000)
python manage.py runserver
```

## Project Structure

```
AquaSense_AI/
├── config/                 # Django settings, URLs, WSGI/ASGI
├── home/                   # Main app: views (prediction + suggestions), templates, URLs
├── static/
│   ├── model/
│   │   ├── eight parameter/   # 10 trained regressors for manual input (7 parameters)
│   │   └── four parameter/    # 10 trained regressors for IoT input (4 parameters)
│   ├── images/, home/, inputs/, suggests/   # Images and CSS
├── .env.example            # Environment variable template
├── vercel.json             # Vercel deployment config
├── requirements.txt
├── CITATION.cff
└── LICENSE
```

## Usage
1. Enter water parameter values manually or connect IoT sensors
2. View ML-powered water quality predictions
3. Access remediation recommendations
4. Generate comprehensive reports

## Future Enhancements
- Mobile application integration
- Additional parameter support
- Enhanced visualization tools
- Community feature for data sharing

## Citation

If you use or build on this project, please cite it. GitHub's **"Cite this repository"** button (generated from [`CITATION.cff`](CITATION.cff)) provides APA and BibTeX formats.

```bibtex
@software{vaidya_aquasenseai_2025,
  author = {Vaidya, Prathamesh Sarjerao},
  title  = {AquaSense AI: Water Quality Prediction from Manual and IoT Inputs},
  year   = {2025},
  url    = {https://github.com/Prathameshv07/AquaSense_AI}
}
```

## License

[![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc/4.0/)

© 2025 Prathamesh Sarjerao Vaidya. This work is licensed under the [Creative Commons Attribution-NonCommercial 4.0 International License](https://creativecommons.org/licenses/by-nc/4.0/). You may share and adapt it for **non-commercial** purposes, provided you **give appropriate credit** and indicate any changes. See [LICENSE](LICENSE) for details.
