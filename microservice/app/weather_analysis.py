"""
Weather Suitability and Risk Analysis Module

This module provides functions to calculate weather suitability scores
and determine risk levels for outdoor events based on weather conditions.
"""


class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass


def validate_inputs(temperature, rain_probability, wind_speed, event_type):
    """
    Validate input parameters for weather analysis.
    
    Args:
        temperature (float): Temperature in Celsius
        rain_probability (float): Rain probability between 0 and 1
        wind_speed (float): Wind speed in m/s
        event_type (str): Type of event (sports, market, gathering)
    
    Raises:
        ValidationError: If any input is invalid
    """
    # Check for missing values
    if temperature is None:
        raise ValidationError("Temperature is required")
    if rain_probability is None:
        raise ValidationError("Rain probability is required")
    if wind_speed is None:
        raise ValidationError("Wind speed is required")
    if event_type is None:
        raise ValidationError("Event type is required")
    
    # Validate rain probability range
    if not isinstance(rain_probability, (int, float)):
        raise ValidationError("Rain probability must be a number")
    if rain_probability < 0 or rain_probability > 1:
        raise ValidationError("Rain probability must be between 0 and 1")
    
    # Validate wind speed
    if not isinstance(wind_speed, (int, float)):
        raise ValidationError("Wind speed must be a number")
    if wind_speed < 0:
        raise ValidationError("Wind speed cannot be negative")
    
    # Validate temperature
    if not isinstance(temperature, (int, float)):
        raise ValidationError("Temperature must be a number")
    
    # Validate event type
    valid_event_types = ['sports', 'market', 'gathering']
    if event_type.lower() not in valid_event_types:
        raise ValidationError(f"Event type must be one of: {', '.join(valid_event_types)}")


def calculate_suitability_score(temperature, rain_probability, wind_speed, event_type):
    """
    Calculate weather suitability score for an outdoor event.
    
    Args:
        temperature (float): Temperature in Celsius
        rain_probability (float): Rain probability between 0 and 1
        wind_speed (float): Wind speed in m/s
        event_type (str): Type of event (sports, market, gathering)
    
    Returns:
        dict: Dictionary containing:
            - suitability_score (int): Score between 0 and 100
            - risk_level (str): Low Risk, Moderate Risk, or High Risk
            - recommendation (str): Text recommendation based on risk level
            - risk_factors (dict): Detailed breakdown of risk deductions
    
    Raises:
        ValidationError: If any input is invalid
    """
    # Validate inputs
    validate_inputs(temperature, rain_probability, wind_speed, event_type)
    
    # Normalize event type to lowercase
    event_type = event_type.lower()
    
    # Start with a perfect score of 100
    score = 100
    
    # Rain probability deductions
    if rain_probability < 0.2:
        rain_deduction = 0
    elif rain_probability < 0.4:
        rain_deduction = 10
    elif rain_probability < 0.7:
        rain_deduction = 25
    else:
        rain_deduction = 40
    
    score -= rain_deduction
    
    # Wind speed deductions
    if wind_speed < 6:
        wind_deduction = 0
    elif wind_speed < 10:
        wind_deduction = 10
    elif wind_speed < 15:
        wind_deduction = 20
    else:
        wind_deduction = 35
    
    score -= wind_deduction
    
    # Temperature deductions
    if 10 <= temperature <= 30:
        temp_deduction = 0
    elif (5 <= temperature < 10) or (30 < temperature <= 35):
        temp_deduction = 10
    else:
        temp_deduction = 25
    
    score -= temp_deduction
    
    # Event type specific deductions
    # Sports events are more sensitive to rain
    event_type_deduction = 0
    if event_type == 'sports' and rain_probability >= 0.4:
        event_type_deduction = 10
        score -= event_type_deduction
    
    # Ensure score stays within 0-100 range
    score = max(0, min(100, score))
    
    # Determine risk level and recommendation
    if score >= 75:
        risk_level = "Low Risk"
        recommendation = "Weather conditions are favorable for the event. Proceed as planned."
    elif score >= 40:
        risk_level = "Moderate Risk"
        recommendation = "Weather conditions are acceptable but may impact the event. Consider contingency plans."
    else:
        risk_level = "High Risk"
        recommendation = "Weather conditions are unfavorable. Consider rescheduling or implementing significant contingency measures."
    
    return {
        "suitability_score": int(score),
        "risk_level": risk_level,
        "recommendation": recommendation,
        "risk_factors": {
            "rain_deduction": rain_deduction,
            "wind_deduction": wind_deduction,
            "temperature_deduction": temp_deduction,
            "event_type_deduction": event_type_deduction,
            "total_deduction": rain_deduction + wind_deduction + temp_deduction + event_type_deduction
        }
    }
