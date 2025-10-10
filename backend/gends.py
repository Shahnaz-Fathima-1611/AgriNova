import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
from sklearn.preprocessing import LabelEncoder
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

# List of ~50 countries with approximate centroids (lat, lon)
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

# List of crop types with susceptibility factors (0-1)
crops_susceptibility = {
    "Wheat": 0.8, "Rice": 0.6, "Maize": 0.7, "Soybean": 0.9, 
    "Cotton": 0.5, "Potato": 0.4, "Barley": 0.7, "Sugarcane": 0.3
}

# Function to generate random weather values based on climate
def generate_weather(climate_zone, month):
    # Base values by climate
    if climate_zone == "tropical":
        temp = round(random.uniform(20, 35), 1)
        humidity = round(random.uniform(60, 95), 1)
        rainfall = round(random.uniform(5, 300) if month in [5, 6, 7, 8, 9] else random.uniform(0, 100), 1)
        wind = round(random.uniform(0, 15), 1)
    elif climate_zone == "temperate":
        seasonal_temp = 15 + 10 * np.sin(2 * np.pi * (month - 3) / 12)
        temp = round(random.uniform(seasonal_temp - 8, seasonal_temp + 8), 1)
        humidity = round(random.uniform(40, 85), 1)
        rainfall = round(random.uniform(0, 150), 1)
        wind = round(random.uniform(0, 20), 1)
    elif climate_zone == "continental":
        seasonal_temp = 10 + 15 * np.sin(2 * np.pi * (month - 3) / 12)
        temp = round(random.uniform(seasonal_temp - 12, seasonal_temp + 12), 1)
        humidity = round(random.uniform(30, 75), 1)
        rainfall = round(random.uniform(0, 100), 1)
        wind = round(random.uniform(0, 25), 1)
    elif climate_zone == "arid":
        temp = round(random.uniform(15, 45), 1)
        humidity = round(random.uniform(10, 50), 1)
        rainfall = round(random.uniform(0, 30), 1)
        wind = round(random.uniform(0, 30), 1)
    else:  # highland
        temp = round(random.uniform(5, 25), 1)
        humidity = round(random.uniform(50, 90), 1)
        rainfall = round(random.uniform(0, 200), 1)
        wind = round(random.uniform(0, 15), 1)
    
    return temp, humidity, rainfall, wind

# Function to calculate aphid risk based on environmental factors
def calculate_aphid_risk(temp, humidity, rainfall, wind, month, crop_susceptibility, historical_infestation):
    # Temperature factor: optimal between 20-25°C
    temp_factor = np.exp(-0.5 * ((temp - 22.5) / 8) ** 2)
    
    # Humidity factor: optimal between 60-80%
    if humidity < 60:
        humidity_factor = humidity / 60
    elif humidity > 80:
        humidity_factor = 1 - (humidity - 80) / 20
    else:
        humidity_factor = 1.0
    
    # Rainfall factor: negative correlation
    rainfall_factor = 1 / (1 + 0.1 * rainfall)
    
    # Wind factor: negative correlation
    wind_factor = 1 / (1 + 0.15 * wind)
    
    # Month factor: peaks in spring (months 4-6)
    month_factor = 0.5 + 0.5 * np.cos(2 * np.pi * (month - 4) / 12)
    
    # Calculate base risk
    base_risk = temp_factor * humidity_factor * rainfall_factor * wind_factor * month_factor
    
    # Apply crop susceptibility and historical infestation
    final_risk = base_risk * crop_susceptibility * (0.7 + 0.3 * historical_infestation)
    
    # Add some noise and ensure bounds
    final_risk += random.uniform(-0.05, 0.05)
    return max(0, min(1, final_risk))

# Generate 10000 records
records = []
start_date = datetime(2020, 1, 1)

# Create historical infestation baseline per country
historical_baseline = {}
for country in countries_coords.keys():
    climate = country_climates.get(country, "temperate")
    # Higher baseline for tropical regions
    if climate == "tropical":
        historical_baseline[country] = random.uniform(0.4, 0.8)
    elif climate == "arid":
        historical_baseline[country] = random.uniform(0.1, 0.4)
    else:
        historical_baseline[country] = random.uniform(0.2, 0.6)

for _ in range(10000):
    country, (lat, lon) = random.choice(list(countries_coords.items()))
    climate = country_climates.get(country, "temperate")
    
    # Add some random "jitter" to lat/lon
    lat += random.uniform(-2.0, 2.0)
    lon += random.uniform(-2.0, 2.0)
    
    # Random date within 4 years
    date = start_date + timedelta(days=random.randint(0, 1460))
    month = date.month
    
    # Generate weather based on climate and month
    temp, humidity, rainfall, wind = generate_weather(climate, month)
    
    # Random crop
    crop = random.choice(list(crops_susceptibility.keys()))
    crop_susceptibility = crops_susceptibility[crop]
    
    # Historical infestation with some yearly variation
    year_variation = random.uniform(-0.2, 0.2)
    historical_infestation = max(0, min(1, historical_baseline[country] + year_variation))
    
    # Calculate aphid risk
    aphid_risk = calculate_aphid_risk(temp, humidity, rainfall, wind, month, crop_susceptibility, historical_infestation)
    
    records.append({
        "country": country,
        "climate_zone": climate,
        "latitude": round(lat, 4),
        "longitude": round(lon, 4),
        "date": date.strftime("%Y-%m-%d"),
        "month": month,
        "temperature": temp,
        "humidity": humidity,
        "rainfall": rainfall,
        "wind_speed": wind,
        "crop_type": crop,
        "crop_susceptibility": crop_susceptibility,
        "historical_infestation": round(historical_infestation, 3),
        "aphid_risk": round(aphid_risk, 3)
    })

# Convert to DataFrame
df = pd.DataFrame(records)

# Encode categorical variables
le_country = LabelEncoder()
le_climate = LabelEncoder()
le_crop = LabelEncoder()

df['country_encoded'] = le_country.fit_transform(df['country'])
df['climate_encoded'] = le_climate.fit_transform(df['climate_zone'])
df['crop_encoded'] = le_crop.fit_transform(df['crop_type'])

# Save encoders for prediction
encoders = {
    'country_encoder': le_country,
    'climate_encoder': le_climate,
    'crop_encoder': le_crop
}
joblib.dump(encoders, 'encoders.joblib')

# Train Random Forest model
def train_aphid_model(df):
    feature_columns = [
        'temperature', 'humidity', 'rainfall', 'wind_speed', 'month',
        'historical_infestation', 'country_encoded', 'climate_encoded', 'crop_encoded'
    ]
    
    X = df[feature_columns]
    y = df['aphid_risk']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    train_score = model.score(X_train, y_train)
    test_score = model.score(X_test, y_test)
    print(f"Model R² score - Train: {train_score:.4f}, Test: {test_score:.4f}")
    
    joblib.dump(model, 'aphid_risk_predictor.joblib')
    return model

# Train and save model
print("Training model...")
model = train_aphid_model(df)

# Save dataset
df.to_csv("synthetic_aphid_dataset_with_risk1.csv", index=False)

print("✅ Synthetic dataset created with", len(df), "records")
print("✅ Model trained and saved")
print("✅ Encoders saved")
print("\nDataset preview:")
print(df[['country', 'climate_zone', 'month', 'temperature', 'humidity', 'historical_infestation', 'aphid_risk']].head(10))
print(f"\nAphid risk statistics:")
print(f"Mean: {df['aphid_risk'].mean():.3f}")
print(f"Min: {df['aphid_risk'].min():.3f}")
print(f"Max: {df['aphid_risk'].max():.3f}")
# Add this right after loading the model
print("Model feature names:", model.feature_names_in_)