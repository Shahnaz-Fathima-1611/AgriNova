import pandas as pd
import numpy as np
import random
import requests
import joblib
from datetime import datetime
from geopy.geocoders import Nominatim
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestRegressor
from math import radians, sin, cos, sqrt, asin

# List of countries with approximate centroids (from your original data)
countries_coords = {
    "USA": (39.5, -98.35), "Canada": (56.1, -106.3), "Brazil": (-14.2, -51.9),
    "Argentina": (-38.4, -63.6), "Mexico": (23.6, -102.5), "Chile": (-35.7, -71.5),
    "Colombia": (4.6, -74.1), "Peru": (-9.2, -75.0), "Venezuela": (6.4, -66.6),
    "UK": (55.4, -3.4), "France": (46.2, 2.2), "Germany": (51.2, 10.4),
    "Italy": (41.9, 12.6), "Spain": (40.5, -3.7), "Portugal": (39.4, -8.2),
    "Netherlands": (52.1, 5.3), "Belgium": (50.8, 4.5), "Sweden": (60.1, 18.6),
    "Norway": (60.5, 8.5), "Finland": (64.0, 26.0), "Poland": (51.9, 19.1),
    "Russia": (61.5, 105.3), "Ukraine": (48.4, 31.2), "Turkey": (38.9, 35.2),
    "India": (20.6, 78.9), "China": (35.9, 104.2), "Japan": (36.2, 138.3),
    "South Korea": (36.5, 127.9), "Indonesia": (-0.8, 113.9), "Thailand": (15.8, 101.0),
    "Vietnam": (14.1, 108.3), "Philippines": (12.9, 121.8), "Malaysia": (4.2, 101.9),
    "Australia": (-25.3, 133.8), "New Zealand": (-40.9, 174.9), "South Africa": (-30.6, 22.9),
    "Egypt": (26.8, 30.8), "Nigeria": (9.1, 8.7), "Kenya": (0.0, 37.9),
    "Ethiopia": (9.1, 40.5), "Ghana": (7.9, -1.0), "Morocco": (31.8, -7.1),
    "Saudi Arabia": (23.9, 45.1), "Iran": (32.4, 53.7), "Pakistan": (30.4, 69.3),
    "Bangladesh": (23.7, 90.4), "Nepal": (28.4, 84.1), "Sri Lanka": (7.9, 80.8)
}

# Climate zones for each country
country_climates = {
    "Brazil": "tropical", "Indonesia": "tropical", "Thailand": "tropical",
    "Vietnam": "tropical", "Philippines": "tropical", "Malaysia": "tropical",
    "India": "tropical", "Sri Lanka": "tropical", "Nigeria": "tropical",
    "Ghana": "tropical", "Kenya": "tropical", "Ethiopia": "tropical",
    "USA": "temperate", "China": "temperate", "Japan": "temperate",
    "South Korea": "temperate", "UK": "temperate", "France": "temperate",
    "Germany": "temperate", "Italy": "temperate", "Spain": "temperate",
    "Portugal": "temperate", "Netherlands": "temperate", "Belgium": "temperate",
    "Poland": "temperate", "Ukraine": "temperate", "Turkey": "temperate",
    "Argentina": "temperate", "Chile": "temperate", "Australia": "temperate",
    "New Zealand": "temperate", "South Africa": "temperate",
    "Canada": "continental", "Russia": "continental", "Sweden": "continental",
    "Norway": "continental", "Finland": "continental",
    "Egypt": "arid", "Saudi Arabia": "arid", "Iran": "arid", "Pakistan": "arid",
    "Mexico": "arid", "Morocco": "arid",
    "Colombia": "highland", "Peru": "highland", "Venezuela": "highland", "Nepal": "highland"
}

# Historical infestation baseline per country with all climate zones included
historical_baseline = {}
for country in countries_coords.keys():
    climate = country_climates.get(country, "temperate")
    if climate == "tropical":
        historical_baseline[country] = random.uniform(0.4, 0.8)
    elif climate == "arid":
        historical_baseline[country] = random.uniform(0.1, 0.4)
    elif climate == "continental":
        historical_baseline[country] = random.uniform(0.3, 0.6)
    elif climate == "highland":
        historical_baseline[country] = random.uniform(0.2, 0.5)
    else:  # temperate
        historical_baseline[country] = random.uniform(0.2, 0.6)

# List of crop types with susceptibility factors
crops_susceptibility = {
    "Wheat": 0.8, "Rice": 0.6, "Maize": 0.7, "Soybean": 0.9, 
    "Cotton": 0.5, "Potato": 0.4, "Barley": 0.7, "Sugarcane": 0.3
}

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate Haversine distance between two points"""
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    return c * 6371  # Earth radius in km

def find_nearest_countries(target_lat, target_lon, k=5):
    """Find k nearest countries to target coordinates"""
    distances = []
    for country, (lat, lon) in countries_coords.items():
        distance = haversine_distance(target_lat, target_lon, lat, lon)
        distances.append((country, distance, lat, lon))
    
    distances.sort(key=lambda x: x[1])
    return distances[:k]

def get_country_coordinates(country_name):
    """Get coordinates for a country using geocoding API"""
    try:
        geolocator = Nominatim(user_agent="aphid_risk_predictor")
        location = geolocator.geocode(country_name)
        if location:
            return location.latitude, location.longitude
        else:
            return None
    except:
        return None

def get_weather_data(lat, lon):
    """Get current weather data using OpenWeatherMap API"""
    # You need to get a free API key from https://openweathermap.org/api
    API_KEY = "6772a1310aa389da3aae23fabf744da1"  # Replace with your actual API key
    
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
        response = requests.get(url)
        data = response.json()
        
        if response.status_code == 200:
            return {
                'temperature': data['main']['temp'],
                'humidity': data['main']['humidity'],
                'rainfall': data.get('rain', {}).get('1h', 0) if 'rain' in data else 0,
                'wind_speed': data['wind']['speed'],
                'description': data['weather'][0]['description']
            }
        else:
            return None
    except:
        return None

def predict_aphid_risk(country, lat, lon, crop_type, weather_data, model, encoders):
    """Predict aphid risk using the trained model"""
    le_country = encoders['country_encoder']
    le_climate = encoders['climate_encoder']
    le_crop = encoders['crop_encoder']
    
    current_date = datetime.now()
    month = current_date.month
    
    # Handle unknown country using nearest neighbors
    if country not in le_country.classes_:
        print(f"⚠️  Country '{country}' not in training data. Using nearest neighbors...")
        nearest_countries = find_nearest_countries(lat, lon)
        
        if not nearest_countries:
            raise ValueError(f"No nearest countries found for coordinates: {lat}, {lon}")
        
        nearest_names = [country for country, dist, lat, lon in nearest_countries]
        print(f"   Nearest countries: {nearest_names}")
        
        # Average historical infestation from nearest countries
        historical_avg = np.mean([historical_baseline.get(c, 0.3) for c in nearest_names])
        
        # Use climate from the closest country with proper error handling
        closest_country = nearest_names[0]
        climate = country_climates.get(closest_country)
        
        if climate is None:
            raise ValueError(f"No climate data found for nearest country: {closest_country}")
        
        country_encoded = le_country.transform([closest_country])[0]
    else:
        climate = country_climates.get(country)
        if climate is None:
            raise ValueError(f"No climate data found for country: {country}")
        
        historical_avg = historical_baseline.get(country, 0.3)
        country_encoded = le_country.transform([country])[0]
    
    # Encode climate and crop
    climate_encoded = le_climate.transform([climate])[0]
    crop_encoded = le_crop.transform([crop_type])[0]
    crop_susceptibility = crops_susceptibility.get(crop_type, 0.5)
    
    # Prepare feature vector with correct column names
    features = pd.DataFrame([{
        'temperature': weather_data['temperature'],
        'humidity': weather_data['humidity'],
        'rainfall': weather_data['rainfall'],
        'wind_speed': weather_data['wind_speed'],
        'month': month,
        'historical_infestation': historical_avg,
        'country_encoded': country_encoded,
        'climate_encoded': climate_encoded,
        'crop_encoded': crop_encoded
    }])
    
    # Make prediction
    prediction = model.predict(features)[0]
    return max(0, min(1, prediction))

def main():
    """Main function to run the aphid risk prediction system"""
    print("🌾 Aphid Risk Prediction System")
    print("=" * 40)
    
    # Load model and encoders
    try:
        model = joblib.load('aphid_risk_predictor.joblib')
        encoders = joblib.load('encoders.joblib')
        print("✅ Model and encoders loaded successfully")
    except FileNotFoundError:
        print("❌ Model files not found. Please train the model first.")
        return
    
    # Get user input
    country_name = input("\nEnter country name: ").strip()
    
    # Get coordinates for the country
    print(f"📍 Getting coordinates for {country_name}...")
    coords = get_country_coordinates(country_name)
    
    if not coords:
        print("❌ Could not find coordinates for this country. Please try again.")
        return
    
    lat, lon = coords
    print(f"   Coordinates: Latitude {lat:.4f}, Longitude {lon:.4f}")

    # Get weather data
    print("🌤️  Fetching current weather data...")
    weather_data = get_weather_data(lat, lon)
    
    if not weather_data:
        print("❌ Could not fetch weather data. Using default values...")
        # Fallback to default weather data based on climate
        nearest_countries = find_nearest_countries(lat, lon, k=1)
        
        if not nearest_countries:
            print("❌ Could not find nearest countries for weather estimation.")
            return
        
        closest_country = nearest_countries[0][0]
        climate = country_climates.get(closest_country)
        
        if climate is None:
            print(f"❌ No climate data found for nearest country: {closest_country}")
            return
        
        # Simple weather generation based on climate
        if climate == "tropical":
            weather_data = {
                'temperature': round(random.uniform(25, 35), 1),
                'humidity': round(random.uniform(60, 85), 1),
                'rainfall': round(random.uniform(5, 50), 1),
                'wind_speed': round(random.uniform(5, 15), 1),
                'description': 'estimated based on climate'
            }
        elif climate == "arid":
            weather_data = {
                'temperature': round(random.uniform(20, 45), 1),
                'humidity': round(random.uniform(10, 40), 1),
                'rainfall': round(random.uniform(0, 10), 1),
                'wind_speed': round(random.uniform(8, 25), 1),
                'description': 'estimated based on climate'
            }
        elif climate == "continental":
            weather_data = {
                'temperature': round(random.uniform(5, 25), 1),
                'humidity': round(random.uniform(40, 70), 1),
                'rainfall': round(random.uniform(0, 30), 1),
                'wind_speed': round(random.uniform(5, 20), 1),
                'description': 'estimated based on climate'
            }
        elif climate == "highland":
            weather_data = {
                'temperature': round(random.uniform(8, 20), 1),
                'humidity': round(random.uniform(50, 80), 1),
                'rainfall': round(random.uniform(10, 60), 1),
                'wind_speed': round(random.uniform(3, 12), 1),
                'description': 'estimated based on climate'
            }
        else:  # temperate
            weather_data = {
                'temperature': round(random.uniform(15, 28), 1),
                'humidity': round(random.uniform(40, 70), 1),
                'rainfall': round(random.uniform(0, 20), 1),
                'wind_speed': round(random.uniform(3, 12), 1),
                'description': 'estimated based on climate'
            }
    
    print(f"   Weather: {weather_data['temperature']}°C, {weather_data['humidity']}% humidity")
    print(f"   Rainfall: {weather_data['rainfall']}mm, Wind: {weather_data['wind_speed']} m/s")
    
    # Show available crops for selection
    print("\n🌱 Available crops:")
    for i, crop in enumerate(crops_susceptibility.keys(), 1):
        print(f"   {i}. {crop}")
    
    # Get crop selection
    try:
        crop_choice = int(input("\nSelect crop (enter number): "))
        crop_list = list(crops_susceptibility.keys())
        if 1 <= crop_choice <= len(crop_list):
            selected_crop = crop_list[crop_choice - 1]
            print(f"   Selected: {selected_crop}")
        else:
            print("❌ Invalid selection. Using Wheat as default.")
            selected_crop = "Wheat"
    except:
        print("❌ Invalid input. Using Wheat as default.")
        selected_crop = "Wheat"
    
    # Predict risk
    print("\n🔮 Predicting aphid risk...")
    try:
        risk_score = predict_aphid_risk(
            country_name, lat, lon, selected_crop, weather_data, model, encoders
        )
    except ValueError as e:
        print(f"❌ Error: {e}")
        return
    except Exception as e:
        print(f"❌ Unexpected error during prediction: {e}")
        return
    
    # Display results
    print("\n" + "=" * 40)
    print("📊 PREDICTION RESULTS")
    print("=" * 40)
    print(f"Country: {country_name}")
    print(f"Location: {lat:.4f}, {lon:.4f}")
    print(f"Crop: {selected_crop}")
    print(f"Current weather: {weather_data['temperature']}°C, {weather_data['humidity']}% humidity")
    print(f"Rainfall: {weather_data['rainfall']}mm, Wind: {weather_data['wind_speed']} m/s")
    print(f"Weather source: {weather_data['description']}")
    
    print(f"\n🎯 Aphid Risk Score: {risk_score:.3f}")
    
    # Risk interpretation
    if risk_score < 0.3:
        print("✅ LOW RISK: Favorable conditions for crop growth")
    elif risk_score < 0.6:
        print("⚠️  MODERATE RISK: Monitor crop health regularly")
    else:
        print("🚨 HIGH RISK: Consider preventive measures")
    
    print("\n💡 Recommended actions:")
    if risk_score > 0.5:
        print("   - Increase monitoring frequency")
        print("   - Consider biological controls")
        print("   - Check for early signs of infestation")
        print("   - Implement integrated pest management strategies")
    elif risk_score > 0.3:
        print("   - Maintain regular monitoring schedule")
        print("   - Watch for environmental changes")

if __name__ == "__main__":
    main()