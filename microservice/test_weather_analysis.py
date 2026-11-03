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
        """Test wind speed boundary values

        Uses a gathering event because markets have an extra strong-wind rule.
        """
        # Just below 6 m/s
        result1 = calculate_suitability_score(20, 0.1, 5.9, 'gathering')
        assert result1['suitability_score'] == 100

        # At 6 m/s
        result2 = calculate_suitability_score(20, 0.1, 6, 'gathering')
        assert result2['suitability_score'] == 90

        # Just below 10 m/s
        result3 = calculate_suitability_score(20, 0.1, 9.9, 'gathering')
        assert result3['suitability_score'] == 90

        # At 10 m/s
        result4 = calculate_suitability_score(20, 0.1, 10, 'gathering')
        assert result4['suitability_score'] == 80

        # Just below 15 m/s
        result5 = calculate_suitability_score(20, 0.1, 14.9, 'gathering')
        assert result5['suitability_score'] == 80

        # At 15 m/s
        result6 = calculate_suitability_score(20, 0.1, 15, 'gathering')
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

    def test_risk_factors_object_present(self):
        """Test that risk_factors object is included in response"""
        result = calculate_suitability_score(
            temperature=20,
            rain_probability=0.5,
            wind_speed=8,
            event_type='market'
        )

        assert 'risk_factors' in result
        assert isinstance(result['risk_factors'], dict)

    def test_rain_deduction_calculation(self):
        """Test rain deduction calculation"""
        # No rain deduction
        result1 = calculate_suitability_score(20, 0.1, 5, 'market')
        assert result1['risk_factors']['rain_deduction'] == 0

        # Low rain deduction
        result2 = calculate_suitability_score(20, 0.3, 5, 'market')
        assert result2['risk_factors']['rain_deduction'] == 10

        # Medium rain deduction
        result3 = calculate_suitability_score(20, 0.5, 5, 'market')
        assert result3['risk_factors']['rain_deduction'] == 25

        # High rain deduction
        result4 = calculate_suitability_score(20, 0.8, 5, 'market')
        assert result4['risk_factors']['rain_deduction'] == 40

    def test_wind_deduction_calculation(self):
        """Test wind deduction calculation"""
        # No wind deduction
        result1 = calculate_suitability_score(20, 0.1, 5, 'market')
        assert result1['risk_factors']['wind_deduction'] == 0

        # Low wind deduction
        result2 = calculate_suitability_score(20, 0.1, 8, 'market')
        assert result2['risk_factors']['wind_deduction'] == 10

        # Medium wind deduction
        result3 = calculate_suitability_score(20, 0.1, 12, 'market')
        assert result3['risk_factors']['wind_deduction'] == 20

        # High wind deduction
        result4 = calculate_suitability_score(20, 0.1, 20, 'market')
        assert result4['risk_factors']['wind_deduction'] == 35

    def test_temperature_deduction_calculation(self):
        """Test temperature deduction calculation"""
        # Ideal temperature - no deduction
        result1 = calculate_suitability_score(20, 0.1, 5, 'market')
        assert result1['risk_factors']['temperature_deduction'] == 0

        # Slightly cold - low deduction
        result2 = calculate_suitability_score(8, 0.1, 5, 'market')
        assert result2['risk_factors']['temperature_deduction'] == 10

        # Slightly hot - low deduction
        result3 = calculate_suitability_score(32, 0.1, 5, 'market')
        assert result3['risk_factors']['temperature_deduction'] == 10

        # Very cold - high deduction
        result4 = calculate_suitability_score(0, 0.1, 5, 'market')
        assert result4['risk_factors']['temperature_deduction'] == 25

        # Very hot - high deduction
        result5 = calculate_suitability_score(40, 0.1, 5, 'market')
        assert result5['risk_factors']['temperature_deduction'] == 25

    def test_event_type_deduction_sports(self):
        """Test event type deduction for sports with rain"""
        # Sports with high rain - should have event type deduction
        result1 = calculate_suitability_score(20, 0.5, 5, 'sports')
        assert result1['risk_factors']['event_type_deduction'] == 10

        # Sports with low rain - no event type deduction
        result2 = calculate_suitability_score(20, 0.1, 5, 'sports')
        assert result2['risk_factors']['event_type_deduction'] == 0

    def test_event_type_deduction_market(self):
        """Test event type deduction for market in light wind (no penalty)"""
        result1 = calculate_suitability_score(20, 0.5, 5, 'market')
        assert result1['risk_factors']['event_type_deduction'] == 0

        result2 = calculate_suitability_score(20, 0.8, 5, 'market')
        assert result2['risk_factors']['event_type_deduction'] == 0

    def test_event_type_deduction_gathering(self):
        """Test event type deduction for gathering at a comfortable temperature (no penalty)"""
        result1 = calculate_suitability_score(20, 0.5, 5, 'gathering')
        assert result1['risk_factors']['event_type_deduction'] == 0

        result2 = calculate_suitability_score(20, 0.8, 5, 'gathering')
        assert result2['risk_factors']['event_type_deduction'] == 0

    def test_total_deduction_calculation(self):
        """Test that total deduction equals sum of individual deductions"""
        result = calculate_suitability_score(
            temperature=15,
            rain_probability=0.5,
            wind_speed=8,
            event_type='sports'
        )

        rain_ded = result['risk_factors']['rain_deduction']
        wind_ded = result['risk_factors']['wind_deduction']
        temp_ded = result['risk_factors']['temperature_deduction']
        event_ded = result['risk_factors']['event_type_deduction']
        total_ded = result['risk_factors']['total_deduction']

        assert total_ded == rain_ded + wind_ded + temp_ded + event_ded

    def test_risk_factors_consistency_with_score(self):
        """Test that score calculation is consistent with risk factors"""
        result = calculate_suitability_score(
            temperature=15,
            rain_probability=0.5,
            wind_speed=8,
            event_type='sports'
        )

        total_deduction = result['risk_factors']['total_deduction']
        expected_score = 100 - total_deduction

        assert result['suitability_score'] == expected_score

    def test_risk_factors_with_all_deductions(self):
        """Test risk factors when all deductions apply"""
        result = calculate_suitability_score(
            temperature=40,
            rain_probability=0.8,
            wind_speed=20,
            event_type='sports'
        )

        # All deductions should be present
        assert result['risk_factors']['rain_deduction'] == 40
        assert result['risk_factors']['wind_deduction'] == 35
        assert result['risk_factors']['temperature_deduction'] == 25
        assert result['risk_factors']['event_type_deduction'] == 10
        assert result['risk_factors']['total_deduction'] == 110
        # Score should be capped at 0
        assert result['suitability_score'] == 0


class TestEventSpecificRules:
    """Tests for the event-specific weather risk rules"""

    def test_sports_rain_penalty_is_kept(self):
        result = calculate_suitability_score(20, 0.4, 5, 'sports')
        assert result['risk_factors']['event_type_deduction'] == 10

    def test_sports_has_no_wind_penalty(self):
        result = calculate_suitability_score(20, 0.1, 12, 'sports')
        assert result['risk_factors']['event_type_deduction'] == 0

    def test_market_strong_wind_penalty(self):
        result = calculate_suitability_score(20, 0.1, 10, 'market')
        # Wind: 20, Market wind penalty: 10 = 30 deduction
        assert result['risk_factors']['event_type_deduction'] == 10
        assert result['suitability_score'] == 70

    def test_market_wind_just_below_threshold(self):
        result = calculate_suitability_score(20, 0.1, 9.9, 'market')
        assert result['risk_factors']['event_type_deduction'] == 0

    def test_market_has_no_rain_penalty(self):
        result = calculate_suitability_score(20, 0.8, 5, 'market')
        assert result['risk_factors']['event_type_deduction'] == 0

    def test_gathering_cold_penalty(self):
        result = calculate_suitability_score(9.9, 0.1, 5, 'gathering')
        # Temp: 10, Gathering cold penalty: 10 = 20 deduction
        assert result['risk_factors']['event_type_deduction'] == 10
        assert result['suitability_score'] == 80

    def test_gathering_hot_penalty(self):
        result = calculate_suitability_score(30.1, 0.1, 5, 'gathering')
        # Temp: 10, Gathering heat penalty: 10 = 20 deduction
        assert result['risk_factors']['event_type_deduction'] == 10
        assert result['suitability_score'] == 80

    def test_gathering_comfortable_temperature_boundaries(self):
        result1 = calculate_suitability_score(10, 0.1, 5, 'gathering')
        assert result1['risk_factors']['event_type_deduction'] == 0

        result2 = calculate_suitability_score(30, 0.1, 5, 'gathering')
        assert result2['risk_factors']['event_type_deduction'] == 0

    def test_each_event_type_reacts_to_different_weather(self):
        # Windy day: only markets get the extra penalty
        windy = {t: calculate_suitability_score(20, 0.1, 12, t)['suitability_score']
                 for t in ['sports', 'market', 'gathering']}
        assert windy == {'sports': 80, 'market': 70, 'gathering': 80}

        # Rainy day: only sports get the extra penalty
        rainy = {t: calculate_suitability_score(20, 0.5, 5, t)['suitability_score']
                 for t in ['sports', 'market', 'gathering']}
        assert rainy == {'sports': 65, 'market': 75, 'gathering': 75}

        # Cold day: only gatherings get the extra penalty
        cold = {t: calculate_suitability_score(8, 0.1, 5, t)['suitability_score']
                for t in ['sports', 'market', 'gathering']}
        assert cold == {'sports': 90, 'market': 90, 'gathering': 80}

    def test_applied_rules_are_listed_in_risk_factors(self):
        result = calculate_suitability_score(20, 0.1, 12, 'market')
        rules = result['risk_factors']['event_type_rules']
        assert len(rules) == 1
        assert rules[0]['deduction'] == 10
        assert 'wind' in rules[0]['rule'].lower()

    def test_no_rules_listed_in_mild_weather(self):
        for event_type in ['sports', 'market', 'gathering']:
            result = calculate_suitability_score(20, 0.1, 5, event_type)
            assert result['risk_factors']['event_type_rules'] == []
            assert result['risk_factors']['event_type_deduction'] == 0

    def test_total_deduction_includes_event_penalty(self):
        result = calculate_suitability_score(20, 0.1, 12, 'market')
        factors = result['risk_factors']
        assert factors['total_deduction'] == (
            factors['rain_deduction'] + factors['wind_deduction']
            + factors['temperature_deduction'] + factors['event_type_deduction']
        )
        assert result['suitability_score'] == 100 - factors['total_deduction']

    def test_score_stays_between_0_and_100(self):
        for event_type in ['sports', 'market', 'gathering']:
            worst = calculate_suitability_score(40, 0.9, 25, event_type)
            assert worst['suitability_score'] == 0

            best = calculate_suitability_score(20, 0.0, 0, event_type)
            assert best['suitability_score'] == 100

    def test_event_type_is_case_insensitive_for_rules(self):
        result = calculate_suitability_score(20, 0.1, 12, 'Market')
        assert result['risk_factors']['event_type_deduction'] == 10