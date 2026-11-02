"""
Unit tests for weather analysis module
"""

import pytest
from app.weather_analysis import calculate_suitability_score, ValidationError


class TestWeatherAnalysis:
    """Test suite for weather suitability calculations"""
    
    def test_good_weather_conditions(self):
        """Test with ideal weather conditions"""
        result = calculate_suitability_score(
            temperature=22,
            rain_probability=0.1,
            wind_speed=3,
            event_type='sports'
        )
        
        assert result['suitability_score'] == 100
        assert result['risk_level'] == "Low Risk"
        assert "favorable" in result['recommendation'].lower()
    
    def test_bad_weather_conditions(self):
        """Test with poor weather conditions"""
        result = calculate_suitability_score(
            temperature=40,
            rain_probability=0.8,
            wind_speed=20,
            event_type='sports'
        )
        
        assert result['suitability_score'] == 0
        assert result['risk_level'] == "High Risk"
        assert "unfavorable" in result['recommendation'].lower()
    
    def test_moderate_weather_conditions(self):
        """Test with moderate weather conditions"""
        result = calculate_suitability_score(
            temperature=15,
            rain_probability=0.5,
            wind_speed=8,
            event_type='market'
        )
        
        # Rain: 25, Wind: 10, Temp: 0 = 35 deduction
        assert result['suitability_score'] == 65
        assert result['risk_level'] == "Moderate Risk"
        assert "acceptable" in result['recommendation'].lower()
    
    def test_sports_event_with_rain(self):
        """Test sports event with high rain probability (extra deduction)"""
        result = calculate_suitability_score(
            temperature=20,
            rain_probability=0.6,
            wind_speed=5,
            event_type='sports'
        )
        
        # Rain: 25, Wind: 0, Temp: 0, Sports rain penalty: 10 = 35 deduction
        assert result['suitability_score'] == 65
    
    def test_market_event_with_rain(self):
        """Test market event with high rain probability (no extra deduction)"""
        result = calculate_suitability_score(
            temperature=20,
            rain_probability=0.6,
            wind_speed=5,
            event_type='market'
        )
        
        # Rain: 25, Wind: 0, Temp: 0 = 25 deduction
        assert result['suitability_score'] == 75
    
    def test_gathering_event_with_rain(self):
        """Test gathering event with high rain probability (no extra deduction)"""
        result = calculate_suitability_score(
            temperature=20,
            rain_probability=0.6,
            wind_speed=5,
            event_type='gathering'
        )
        
        # Rain: 25, Wind: 0, Temp: 0 = 25 deduction
        assert result['suitability_score'] == 75
    
    def test_rain_probability_boundaries(self):
        """Test rain probability boundary values"""
        # Just below 0.2
        result1 = calculate_suitability_score(20, 0.19, 5, 'market')
        assert result1['suitability_score'] == 100
        
        # At 0.2
        result2 = calculate_suitability_score(20, 0.2, 5, 'market')
        assert result2['suitability_score'] == 90
        
        # Just below 0.4
        result3 = calculate_suitability_score(20, 0.39, 5, 'market')
        assert result3['suitability_score'] == 90
        
        # At 0.4
        result4 = calculate_suitability_score(20, 0.4, 5, 'market')
        assert result4['suitability_score'] == 75
        
        # Just below 0.7
        result5 = calculate_suitability_score(20, 0.69, 5, 'market')
        assert result5['suitability_score'] == 75
        
        # At 0.7
        result6 = calculate_suitability_score(20, 0.7, 5, 'market')
        assert result6['suitability_score'] == 60
    
    def test_wind_speed_boundaries(self):
        """Test wind speed boundary values"""
        # Just below 6 m/s
        result1 = calculate_suitability_score(20, 0.1, 5.9, 'market')
        assert result1['suitability_score'] == 100
        
        # At 6 m/s
        result2 = calculate_suitability_score(20, 0.1, 6, 'market')
        assert result2['suitability_score'] == 90
        
        # Just below 10 m/s
        result3 = calculate_suitability_score(20, 0.1, 9.9, 'market')
        assert result3['suitability_score'] == 90
        
        # At 10 m/s
        result4 = calculate_suitability_score(20, 0.1, 10, 'market')
        assert result4['suitability_score'] == 80
        
        # Just below 15 m/s
        result5 = calculate_suitability_score(20, 0.1, 14.9, 'market')
        assert result5['suitability_score'] == 80
        
        # At 15 m/s
        result6 = calculate_suitability_score(20, 0.1, 15, 'market')
        assert result6['suitability_score'] == 65
    
    def test_temperature_boundaries(self):
        """Test temperature boundary values"""
        # At 10°C (ideal range start)
        result1 = calculate_suitability_score(10, 0.1, 5, 'market')
        assert result1['suitability_score'] == 100
        
        # Just below 10°C
        result2 = calculate_suitability_score(9.9, 0.1, 5, 'market')
        assert result2['suitability_score'] == 90
        
        # At 5°C
        result3 = calculate_suitability_score(5, 0.1, 5, 'market')
        assert result3['suitability_score'] == 90
        
        # Just below 5°C
        result4 = calculate_suitability_score(4.9, 0.1, 5, 'market')
        assert result4['suitability_score'] == 75
        
        # At 30°C (ideal range end)
        result5 = calculate_suitability_score(30, 0.1, 5, 'market')
        assert result5['suitability_score'] == 100
        
        # Just above 30°C
        result6 = calculate_suitability_score(30.1, 0.1, 5, 'market')
        assert result6['suitability_score'] == 90
        
        # At 35°C
        result7 = calculate_suitability_score(35, 0.1, 5, 'market')
        assert result7['suitability_score'] == 90
        
        # Just above 35°C
        result8 = calculate_suitability_score(35.1, 0.1, 5, 'market')
        assert result8['suitability_score'] == 75
    
    def test_score_never_below_zero(self):
        """Test that score never goes below 0"""
        result = calculate_suitability_score(
            temperature=-10,
            rain_probability=1.0,
            wind_speed=30,
            event_type='sports'
        )
        
        assert result['suitability_score'] == 0
    
    def test_score_never_above_100(self):
        """Test that score never goes above 100"""
        result = calculate_suitability_score(
            temperature=25,
            rain_probability=0,
            wind_speed=0,
            event_type='market'
        )
        
        assert result['suitability_score'] == 100
    
    def test_missing_temperature(self):
        """Test validation error for missing temperature"""
        with pytest.raises(ValidationError) as exc_info:
            calculate_suitability_score(
                temperature=None,
                rain_probability=0.5,
                wind_speed=5,
                event_type='sports'
            )
        
        assert "Temperature is required" in str(exc_info.value)
    
    def test_missing_rain_probability(self):
        """Test validation error for missing rain probability"""
        with pytest.raises(ValidationError) as exc_info:
            calculate_suitability_score(
                temperature=20,
                rain_probability=None,
                wind_speed=5,
                event_type='sports'
            )
        
        assert "Rain probability is required" in str(exc_info.value)
    
    def test_missing_wind_speed(self):
        """Test validation error for missing wind speed"""
        with pytest.raises(ValidationError) as exc_info:
            calculate_suitability_score(
                temperature=20,
                rain_probability=0.5,
                wind_speed=None,
                event_type='sports'
            )
        
        assert "Wind speed is required" in str(exc_info.value)
    
    def test_missing_event_type(self):
        """Test validation error for missing event type"""
        with pytest.raises(ValidationError) as exc_info:
            calculate_suitability_score(
                temperature=20,
                rain_probability=0.5,
                wind_speed=5,
                event_type=None
            )
        
        assert "Event type is required" in str(exc_info.value)
    
    def test_invalid_rain_probability_negative(self):
        """Test validation error for negative rain probability"""
        with pytest.raises(ValidationError) as exc_info:
            calculate_suitability_score(
                temperature=20,
                rain_probability=-0.1,
                wind_speed=5,
                event_type='sports'
            )
        
        assert "between 0 and 1" in str(exc_info.value)
    
    def test_invalid_rain_probability_above_one(self):
        """Test validation error for rain probability above 1"""
        with pytest.raises(ValidationError) as exc_info:
            calculate_suitability_score(
                temperature=20,
                rain_probability=1.5,
                wind_speed=5,
                event_type='sports'
            )
        
        assert "between 0 and 1" in str(exc_info.value)
    
    def test_invalid_wind_speed_negative(self):
        """Test validation error for negative wind speed"""
        with pytest.raises(ValidationError) as exc_info:
            calculate_suitability_score(
                temperature=20,
                rain_probability=0.5,
                wind_speed=-5,
                event_type='sports'
            )
        
        assert "cannot be negative" in str(exc_info.value)
    
    def test_invalid_event_type(self):
        """Test validation error for unsupported event type"""
        with pytest.raises(ValidationError) as exc_info:
            calculate_suitability_score(
                temperature=20,
                rain_probability=0.5,
                wind_speed=5,
                event_type='concert'
            )
        
        assert "Event type must be one of" in str(exc_info.value)
    
    def test_case_insensitive_event_type(self):
        """Test that event type is case insensitive"""
        result1 = calculate_suitability_score(20, 0.1, 5, 'SPORTS')
        result2 = calculate_suitability_score(20, 0.1, 5, 'Sports')
        result3 = calculate_suitability_score(20, 0.1, 5, 'sports')
        
        assert result1['suitability_score'] == result2['suitability_score']
        assert result2['suitability_score'] == result3['suitability_score']
    
    def test_risk_level_thresholds(self):
        """Test risk level classification thresholds"""
        # Low Risk threshold (75)
        result1 = calculate_suitability_score(20, 0.1, 5, 'market')
        assert result1['risk_level'] == "Low Risk"
        
        # Moderate Risk threshold (40-74)
        result2 = calculate_suitability_score(20, 0.5, 8, 'market')
        assert result2['risk_level'] == "Moderate Risk"
        
        # High Risk threshold (0-39)
        result3 = calculate_suitability_score(40, 0.8, 20, 'market')
        assert result3['risk_level'] == "High Risk"
