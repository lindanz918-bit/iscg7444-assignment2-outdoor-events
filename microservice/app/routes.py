from app import app
from flask import jsonify, request
from app.weather_analysis import calculate_suitability_score, ValidationError
import math

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"}), 200

@app.route('/analyze', methods=['POST'])
def analyze():
    """
    Analyze weather suitability for an outdoor event.
    
    Expects JSON body with:
    - temperature (float): Temperature in Celsius
    - rain_probability (float): Rain probability between 0 and 1
    - wind_speed (float): Wind speed in m/s
    - event_type (str): Type of event (sports, market, gathering)
    
    Returns:
    - suitability_score (int): Score between 0 and 100
    - risk_level (str): Low Risk, Moderate Risk, or High Risk
    - recommendation (str): Text recommendation
    """
    # Check if request has JSON data
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    # Parse JSON body
    try:
        data = request.get_json()
    except Exception:
        return jsonify({"error": "Invalid JSON format"}), 400
    
    # Check if data is a dictionary/object
    if not isinstance(data, dict):
        return jsonify({"error": "Request body must be a JSON object"}), 400
    
    # Extract required fields
    temperature = data.get('temperature')
    rain_probability = data.get('rain_probability')
    wind_speed = data.get('wind_speed')
    event_type = data.get('event_type')
    
    # Check for missing fields
    missing_fields = []
    if temperature is None:
        missing_fields.append('temperature')
    if rain_probability is None:
        missing_fields.append('rain_probability')
    if wind_speed is None:
        missing_fields.append('wind_speed')
    if event_type is None:
        missing_fields.append('event_type')
    
    if missing_fields:
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400
    
    # Validate that values are not booleans
    if isinstance(temperature, bool) or isinstance(rain_probability, bool) or isinstance(wind_speed, bool):
        return jsonify({"error": "Boolean values are not allowed for numeric fields"}), 400
    
    # Validate that values are finite numbers
    try:
        if not isinstance(temperature, (int, float)):
            return jsonify({"error": "Temperature must be a number"}), 400
        if not isinstance(rain_probability, (int, float)):
            return jsonify({"error": "Rain probability must be a number"}), 400
        if not isinstance(wind_speed, (int, float)):
            return jsonify({"error": "Wind speed must be a number"}), 400
        
        # Check for finite values (reject NaN and Infinity)
        if not math.isfinite(temperature):
            return jsonify({"error": "Temperature must be a finite number"}), 400
        if not math.isfinite(rain_probability):
            return jsonify({"error": "Rain probability must be a finite number"}), 400
        if not math.isfinite(wind_speed):
            return jsonify({"error": "Wind speed must be a finite number"}), 400
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid numeric values"}), 400
    
    # Validate event type is a string
    if not isinstance(event_type, str):
        return jsonify({"error": "Event type must be a string"}), 400
    
    # Call the calculation function
    try:
        result = calculate_suitability_score(
            temperature=temperature,
            rain_probability=rain_probability,
            wind_speed=wind_speed,
            event_type=event_type
        )
        return jsonify(result), 200
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500