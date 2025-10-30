🌾 AgriNova: ML-Based Aphid Risk Prediction and Farmer Advisory System
🧠 Overview

AgriNova is an AI-powered pest prediction and advisory system that forecasts aphid infestations based on real-time weather data and machine learning algorithms. The system helps farmers make data-driven pest management decisions, reducing unnecessary pesticide use and promoting sustainable agriculture.

🚀 Features

🌤 Real-time Weather Integration: Fetches live meteorological data (temperature, humidity, rainfall, wind speed) via APIs.

🤖 ML-Powered Prediction: Predicts aphid risk using a trained Random Forest Classifier model.

🧩 Country- and Crop-Based Risk Estimation: Automatically detects regional coordinates and climate type.

📊 Interactive Farmer Dashboard: Displays weather insights, risk level, and pesticide recommendations.

🔔 Smart Alerts: Provides AI-driven notifications for high-risk conditions.

🌱 Sustainable Agriculture Support: Reduces excessive pesticide use and enhances eco-friendly farming practices.

🏗️ System Architecture

The system follows a modular pipeline:

Data Source Layer: Weather data from OpenWeather API / IoT sensors.

Preprocessing Layer: Cleaning, normalization, and feature extraction using Python (Pandas, NumPy).

Machine Learning Layer: Random Forest Classifier trained on historical pest-weather data.

Prediction Engine: Generates risk scores and alerts for specific crops and regions.

Frontend Dashboard: Developed with HTML, CSS, and JavaScript to visualize predictions.

Backend API: Flask server for handling user requests and model inference.


2️⃣ Install Dependencies
pip install -r requirements.txt

3️⃣ Train the Model

Run the training script to build the Random Forest Classifier:

python train.py


This will generate the trained model file:
aphid_risk_predictor.joblib

4️⃣ Start the Flask Server
python server.py


By default, the backend will run on http://127.0.0.1:5000/.

5️⃣ Run Frontend

Open index.html in your web browser to access the farmer dashboard.

🧪 API Usage

Endpoint:

POST /api/predict


Request Body (JSON):

{
  "country": "India",
  "crop": "Wheat"
}


Response Example:

{
  "risk": 0.72,
  "country": "India",
  "crop": "Wheat",
  "weather": {
    "temperature": 29,
    "humidity": 68,
    "rainfall": 10,
    "wind_speed": 7
  }
}

📈 Model Evaluation
Metric     	Result
Accuracy   	93.4%
Precision	  91.2%
Recall	    90.7%
F1-Score	  90.9%


🌍 Future Enhancements

Integration with IoT pest traps for automated data collection.

Addition of LSTM models for temporal weather forecasting.

Mobile app version with regional language voice alerts.

Integration of satellite imagery for more localized pest detection.



🧾 License

This project is licensed under the MIT License — free to use and modify with attribution.
