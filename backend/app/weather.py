import os
import requests
from flask import jsonify

OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')
OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5"


def get_weather_by_location(location):
    """
    Fetch current weather data for a given location using OpenWeatherMap API.
    
    Args:
        location (str): City name (e.g., "London", "New York")
    
    Returns:
        dict: Weather data or error message
    """
    if not OPENWEATHER_API_KEY:
        return {'error': 'OpenWeatherMap API key not configured'}
    
    try:
        url = f"{OPENWEATHER_BASE_URL}/weather"
        params = {
            'q': location,
            'appid': OPENWEATHER_API_KEY,
            'units': 'metric'  # Use metric units (Celsius)
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Extract relevant weather information
        weather_data = {
            'location': data['name'],
            'country': data['sys']['country'],
            'temperature': data['main']['temp'],
            'feels_like': data['main']['feels_like'],
            'humidity': data['main']['humidity'],
            'pressure': data['main']['pressure'],
            'wind_speed': data['wind']['speed'],
            'wind_direction': data['wind'].get('deg', 0),
            'weather_main': data['weather'][0]['main'],
            'weather_description': data['weather'][0]['description'],
            'visibility': data.get('visibility', 0) / 1000,  # Convert to km
            'clouds': data['clouds']['all']
        }
        
        return weather_data
        
    except requests.exceptions.RequestException as e:
        return {'error': f'Failed to fetch weather data: {str(e)}'}
    except KeyError as e:
        return {'error': f'Invalid weather data format: {str(e)}'}
    except Exception as e:
        return {'error': f'Unexpected error: {str(e)}'}


def get_weather_forecast(location, days=5):
    """
    Fetch weather forecast for a given location using OpenWeatherMap API.
    
    Args:
        location (str): City name (e.g., "London", "New York")
        days (int): Number of days for forecast (max 5)
    
    Returns:
        dict: Weather forecast data or error message
    """
    if not OPENWEATHER_API_KEY:
        return {'error': 'OpenWeatherMap API key not configured'}
    
    try:
        url = f"{OPENWEATHER_BASE_URL}/forecast"
        params = {
            'q': location,
            'appid': OPENWEATHER_API_KEY,
            'units': 'metric',
            'cnt': days * 8  # 8 forecasts per day (3-hour intervals)
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Extract forecast data
        forecast_data = {
            'location': data['city']['name'],
            'country': data['city']['country'],
            'forecasts': []
        }
        
        for item in data['list']:
            forecast = {
                'datetime': item['dt_txt'],
                'temperature': item['main']['temp'],
                'feels_like': item['main']['feels_like'],
                'humidity': item['main']['humidity'],
                'wind_speed': item['wind']['speed'],
                'weather_main': item['weather'][0]['main'],
                'weather_description': item['weather'][0]['description']
            }
            forecast_data['forecasts'].append(forecast)
        
        return forecast_data
        
    except requests.exceptions.RequestException as e:
        return {'error': f'Failed to fetch forecast data: {str(e)}'}
    except KeyError as e:
        return {'error': f'Invalid forecast data format: {str(e)}'}
    except Exception as e:
        return {'error': f'Unexpected error: {str(e)}'}
