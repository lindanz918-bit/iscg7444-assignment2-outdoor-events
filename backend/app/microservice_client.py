import os
import requests
import json

MICROSERVICE_URL = os.getenv('MICROSERVICE_URL', 'http://localhost:5001')


def call_microservice_analyze(temperature, rain_probability, wind_speed, event_type):
    """
    Call the microservice's analyze endpoint to evaluate event suitability.
    
    Args:
        temperature (float): Temperature in Celsius
        rain_probability (float): Rain probability between 0 and 1
        wind_speed (float): Wind speed in m/s
        event_type (str): Type of event (sports, market, gathering)
    
    Returns:
        dict: Analysis result from microservice or error message
    """
    try:
        url = f"{MICROSERVICE_URL}/analyze"
        payload = {
            'temperature': temperature,
            'rain_probability': rain_probability,
            'wind_speed': wind_speed,
            'event_type': event_type
        }
        
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        
        return response.json()
        
    except requests.exceptions.RequestException as e:
        return {'error': f'Failed to connect to microservice: {str(e)}'}
    except json.JSONDecodeError as e:
        return {'error': f'Invalid response from microservice: {str(e)}'}
    except Exception as e:
        return {'error': f'Unexpected error: {str(e)}'}


def check_microservice_health():
    """
    Check if the microservice is healthy and accessible.
    
    Returns:
        bool: True if microservice is healthy, False otherwise
    """
    try:
        url = f"{MICROSERVICE_URL}/health"
        response = requests.get(url, timeout=5)
        return response.status_code == 200
    except Exception:
        return False
