"""
Unit tests for Flask routes API endpoints
"""

import pytest
import json
from app import app


@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestHealthEndpoint:
    """Test suite for GET /health endpoint"""
    
    def test_health_endpoint_returns_200(self, client):
        """Test that health endpoint returns HTTP 200"""
        response = client.get('/health')
        assert response.status_code == 200
    
    def test_health_endpoint_returns_correct_json(self, client):
        """Test that health endpoint returns correct JSON structure"""
        response = client.get('/health')
        data = json.loads(response.data)
        assert data == {"status": "ok"}
    
    def test_health_endpoint_content_type(self, client):
        """Test that health endpoint returns JSON content type"""
        response = client.get('/health')
        assert response.content_type == 'application/json'


class TestAnalyzeEndpoint:
    """Test suite for POST /analyze endpoint"""
    
    def test_valid_weather_data_returns_200(self, client):
        """Test that valid weather data returns HTTP 200"""
        payload = {
            "temperature": 22,
            "rain_probability": 0.65,
            "wind_speed": 8,
            "event_type": "sports"
        }
        response = client.post('/analyze',
                              data=json.dumps(payload),
                              content_type='application/json')
        assert response.status_code == 200
    
    def test_response_contains_required_fields(self, client):
        """Test that response contains suitability_score, risk_level, and recommendation"""
        payload = {
            "temperature": 22,
            "rain_probability": 0.65,
            "wind_speed": 8,
            "event_type": "sports"
        }
        response = client.post('/analyze',
                              data=json.dumps(payload),
                              content_type='application/json')
        data = json.loads(response.data)
        assert 'suitability_score' in data
        assert 'risk_level' in data
        assert 'recommendation' in data
    
    def test_good_weather_produces_correct_score(self, client):
        """Test that good weather produces high score"""
        payload = {
            "temperature": 22,
            "rain_probability": 0.1,
            "wind_speed": 3,
            "event_type": "sports"
        }
        response = client.post('/analyze',
                              data=json.dumps(payload),
                              content_type='application/json')
        data = json.loads(response.data)
        assert data['suitability_score'] == 100
        assert data['risk_level'] == "Low Risk"
    
    def test_bad_weather_produces_low_score(self, client):
        """Test that bad weather produces low score"""
        payload = {
            "temperature": 40,
            "rain_probability": 0.8,
            "wind_speed": 20,
            "event_type": "sports"
        }
        response = client.post('/analyze',
                              data=json.dumps(payload),
                              content_type='application/json')
        data = json.loads(response.data)
        assert data['suitability_score'] == 0
        assert data['risk_level'] == "High Risk"
    
    def test_sports_event_with_rain(self, client):
        """Test that sports event with rain has extra deduction"""
        payload = {
            "temperature": 20,
            "rain_probability": 0.6,
            "wind_speed": 5,
            "event_type": "sports"
        }
        response = client.post('/analyze',
                              data=json.dumps(payload),
                              content_type='application/json')
        data = json.loads(response.data)
        # Rain: 25, Wind: 0, Temp: 0, Sports penalty: 10 = 35 deduction
        assert data['suitability_score'] == 65
    
    def test_market_event_with_rain(self, client):
        """Test that market event with rain has no extra deduction"""
        payload = {
            "temperature": 20,
            "rain_probability": 0.6,
            "wind_speed": 5,
            "event_type": "market"
        }
        response = client.post('/analyze',
                              data=json.dumps(payload),
                              content_type='application/json')
        data = json.loads(response.data)
        # Rain: 25, Wind: 0, Temp: 0 = 25 deduction
        assert data['suitability_score'] == 75
    
    def test_missing_temperature_returns_400(self, client):
        """Test that missing temperature returns HTTP 400"""
        payload = {
            "rain_probability": 0.5,
            "wind_speed": 5,
            "event_type": "sports"
        }
        response = client.post('/analyze',
                              data=json.dumps(payload),
                              content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'temperature' in data['error']
    
    def test_missing_rain_probability_returns_400(self, client):
        """Test that missing rain_probability returns HTTP 400"""
        payload = {
            "temperature": 20,
            "wind_speed": 5,
            "event_type": "sports"
        }
        response = client.post('/analyze',
                              data=json.dumps(payload),
                              content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'rain_probability' in data['error']
    
    def test_missing_wind_speed_returns_400(self, client):
        """Test that missing wind_speed returns HTTP 400"""
        payload = {
            "temperature": 20,
            "rain_probability": 0.5,
            "event_type": "sports"
        }
        response = client.post('/analyze',
                              data=json.dumps(payload),
                              content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'wind_speed' in data['error']
    
    def test_missing_event_type_returns_400(self, client):
        """Test that missing event_type returns HTTP 400"""
        payload = {
            "temperature": 20,
            "rain_probability": 0.5,
            "wind_speed": 5
        }
        response = client.post('/analyze',
                              data=json.dumps(payload),
                              content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'event_type' in data['error']
    
    def test_invalid_rain_probability_negative_returns_400(self, client):
        """Test that negative rain_probability returns HTTP 400"""
        payload = {
            "temperature": 20,
            "rain_probability": -0.1,
            "wind_speed": 5,
            "event_type": "sports"
        }
        response = client.post('/analyze',
                              data=json.dumps(payload),
                              content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'between 0 and 1' in data['error']
    
    def test_invalid_rain_probability_above_one_returns_400(self, client):
        """Test that rain_probability above 1 returns HTTP 400"""
        payload = {
            "temperature": 20,
            "rain_probability": 1.5,
            "wind_speed": 5,
            "event_type": "sports"
        }
        response = client.post('/analyze',
                              data=json.dumps(payload),
                              content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'between 0 and 1' in data['error']
    
    def test_negative_wind_speed_returns_400(self, client):
        """Test that negative wind_speed returns HTTP 400"""
        payload = {
            "temperature": 20,
            "rain_probability": 0.5,
            "wind_speed": -5,
            "event_type": "sports"
        }
        response = client.post('/analyze',
                              data=json.dumps(payload),
                              content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'cannot be negative' in data['error']
    
    def test_unsupported_event_type_returns_400(self, client):
        """Test that unsupported event_type returns HTTP 400"""
        payload = {
            "temperature": 20,
            "rain_probability": 0.5,
            "wind_speed": 5,
            "event_type": "concert"
        }
        response = client.post('/analyze',
                              data=json.dumps(payload),
                              content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Event type must be one of' in data['error']
    
    def test_malformed_json_returns_400(self, client):
        """Test that malformed JSON returns HTTP 400"""
        response = client.post('/analyze',
                              data='{"temperature": 20, "rain_probability": 0.5',
                              content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Invalid JSON' in data['error']
    
    def test_non_json_request_returns_400(self, client):
        """Test that non-JSON request returns HTTP 400"""
        response = client.post('/analyze',
                              data='plain text',
                              content_type='text/plain')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'must be JSON' in data['error']
    
    def test_json_array_returns_400(self, client):
        """Test that JSON array instead of object returns HTTP 400"""
        payload = [20, 0.5, 5, "sports"]
        response = client.post('/analyze',
                              data=json.dumps(payload),
                              content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'must be a JSON object' in data['error']
    
    def test_boolean_temperature_returns_400(self, client):
        """Test that boolean temperature returns HTTP 400"""
        payload = {
            "temperature": True,
            "rain_probability": 0.5,
            "wind_speed": 5,
            "event_type": "sports"
        }
        response = client.post('/analyze',
                              data=json.dumps(payload),
                              content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Boolean' in data['error']
    
    def test_nan_temperature_returns_400(self, client):
        """Test that NaN temperature returns HTTP 400"""
        payload = {
            "temperature": float('nan'),
            "rain_probability": 0.5,
            "wind_speed": 5,
            "event_type": "sports"
        }
        response = client.post('/analyze',
                              data=json.dumps(payload),
                              content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'finite' in data['error']
    
    def test_infinity_temperature_returns_400(self, client):
        """Test that infinity temperature returns HTTP 400"""
        payload = {
            "temperature": float('inf'),
            "rain_probability": 0.5,
            "wind_speed": 5,
            "event_type": "sports"
        }
        response = client.post('/analyze',
                              data=json.dumps(payload),
                              content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'finite' in data['error']
    
    def test_non_string_event_type_returns_400(self, client):
        """Test that non-string event_type returns HTTP 400"""
        payload = {
            "temperature": 20,
            "rain_probability": 0.5,
            "wind_speed": 5,
            "event_type": 123
        }
        response = client.post('/analyze',
                              data=json.dumps(payload),
                              content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'must be a string' in data['error']
    
    def test_case_insensitive_event_type(self, client):
        """Test that event_type is case insensitive"""
        payload1 = {
            "temperature": 20,
            "rain_probability": 0.1,
            "wind_speed": 5,
            "event_type": "SPORTS"
        }
        payload2 = {
            "temperature": 20,
            "rain_probability": 0.1,
            "wind_speed": 5,
            "event_type": "sports"
        }
        
        response1 = client.post('/analyze',
                               data=json.dumps(payload1),
                               content_type='application/json')
        response2 = client.post('/analyze',
                               data=json.dumps(payload2),
                               content_type='application/json')
        
        data1 = json.loads(response1.data)
        data2 = json.loads(response2.data)
        assert data1['suitability_score'] == data2['suitability_score']
    
    def test_example_from_requirements(self, client):
        """Test the example from the requirements"""
        payload = {
            "temperature": 22,
            "rain_probability": 0.65,
            "wind_speed": 8,
            "event_type": "sports"
        }
        response = client.post('/analyze',
                              data=json.dumps(payload),
                              content_type='application/json')
        data = json.loads(response.data)
        # Rain: 25, Wind: 10, Temp: 0, Sports penalty: 10 = 45 deduction
        # Score: 100 - 45 = 55
        assert data['suitability_score'] == 55
        assert data['risk_level'] == "Moderate Risk"
