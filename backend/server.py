from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
from aphid_predict import get_country_coordinates, get_weather_data, predict_aphid_risk, crops_susceptibility, country_climates, countries_coords

app = Flask(__name__)
CORS(app)

# Load model and encoders once at startup
try:
    model = joblib.load('aphid_risk_predictor.joblib')
    encoders = joblib.load('encoders.joblib')
except Exception as e:
    model = None
    encoders = None
    print(f"Model loading error: {e}")

@app.route('/api/predict', methods=['POST'])
def api_predict():
    data = request.get_json()
    country = data.get('country')
    crop = data.get('crop')
    # Validate country name
    if not country or not isinstance(country, str) or country.strip() == "":
        return jsonify({'error': 'Country name is required and must be valid.'}), 400
    coords = get_country_coordinates(country)
    if not coords:
        return jsonify({'error': f'Could not find coordinates for country: {country}'}), 400
    lat, lon = coords
    weather = get_weather_data(lat, lon)
    if not weather:
        # fallback to climate-based defaults
        climate = country_climates.get(country, 'temperate')
        if climate == "tropical":
            weather = {'temperature': 30, 'humidity': 75, 'rainfall': 20, 'wind_speed': 10, 'description': 'default'}
        elif climate == "arid":
            weather = {'temperature': 35, 'humidity': 20, 'rainfall': 2, 'wind_speed': 15, 'description': 'default'}
        elif climate == "continental":
            weather = {'temperature': 15, 'humidity': 55, 'rainfall': 10, 'wind_speed': 10, 'description': 'default'}
        elif climate == "highland":
            weather = {'temperature': 12, 'humidity': 65, 'rainfall': 25, 'wind_speed': 7, 'description': 'default'}
        else:
            weather = {'temperature': 20, 'humidity': 60, 'rainfall': 8, 'wind_speed': 8, 'description': 'default'}
    if not model or not encoders:
        return jsonify({'error': 'Model not loaded'}), 500
    try:
        risk = predict_aphid_risk(country, lat, lon, crop, weather, model, encoders)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    return jsonify({
        'risk': round(risk, 2),
        'country': country,
        'crop': crop,
        'weather': weather
    })

if __name__ == '__main__':
    app.run(debug=True)
