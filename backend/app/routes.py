from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from . import db
from .models import Event, User, EvaluationLog
from .weather import get_weather_by_location, get_weather_forecast
from .microservice_client import call_microservice_analyze
import json

events_bp = Blueprint('events', __name__)
weather_bp = Blueprint('weather', __name__)
evaluation_bp = Blueprint('evaluation', __name__)


def admin_required():
    """Check if current user is admin"""
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)
    if not user or user.role != 'admin':
        return False
    return True


@events_bp.route('/api/events', methods=['GET'])
def get_events():
    """Retrieve a list of all events"""
    events = Event.query.all()
    return jsonify([event.to_dict() for event in events]), 200


@events_bp.route('/api/events/<int:event_id>', methods=['GET'])
def get_event(event_id):
    """Retrieve details for a specific event"""
    event = Event.query.get_or_404(event_id)
    return jsonify(event.to_dict()), 200


@events_bp.route('/api/events', methods=['POST'])
@jwt_required()
def create_event():
    """Create a new event (admin only)"""
    if not admin_required():
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Validate required fields
    required_fields = ['title', 'location', 'date']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({'error': f'{field} is required'}), 400
    
    event = Event(
        title=data['title'],
        description=data.get('description', ''),
        location=data['location'],
        date=data['date'],
        time=data.get('time', '')
    )
    
    db.session.add(event)
    db.session.commit()
    
    return jsonify(event.to_dict()), 201


@events_bp.route('/api/events/<int:event_id>', methods=['PUT'])
@jwt_required()
def update_event(event_id):
    """Update event information (admin only)"""
    if not admin_required():
        return jsonify({'error': 'Admin access required'}), 403
    
    event = Event.query.get_or_404(event_id)
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Update fields if provided
    if 'title' in data:
        event.title = data['title']
    if 'description' in data:
        event.description = data['description']
    if 'location' in data:
        event.location = data['location']
    if 'date' in data:
        event.date = data['date']
    if 'time' in data:
        event.time = data['time']
    
    db.session.commit()
    
    return jsonify(event.to_dict()), 200


@events_bp.route('/api/events/<int:event_id>', methods=['DELETE'])
@jwt_required()
def delete_event(event_id):
    """Delete an event (admin only)"""
    if not admin_required():
        return jsonify({'error': 'Admin access required'}), 403
    
    event = Event.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    
    return jsonify({'message': 'Event deleted successfully'}), 200


@weather_bp.route('/api/weather/current', methods=['GET'])
def get_current_weather():
    """Get current weather for a location"""
    location = request.args.get('location')
    
    if not location:
        return jsonify({'error': 'Location parameter is required'}), 400
    
    weather_data = get_weather_by_location(location)
    
    if 'error' in weather_data:
        return jsonify(weather_data), 500
    
    return jsonify(weather_data), 200


@weather_bp.route('/api/weather/forecast', methods=['GET'])
def get_weather_forecast_endpoint():
    """Get weather forecast for a location"""
    location = request.args.get('location')
    days = request.args.get('days', 5, type=int)
    
    if not location:
        return jsonify({'error': 'Location parameter is required'}), 400
    
    if days < 1 or days > 5:
        return jsonify({'error': 'Days parameter must be between 1 and 5'}), 400
    
    forecast_data = get_weather_forecast(location, days)
    
    if 'error' in forecast_data:
        return jsonify(forecast_data), 500
    
    return jsonify(forecast_data), 200


@evaluation_bp.route('/api/evaluation/evaluate/<int:event_id>', methods=['POST'])
def evaluate_event(event_id):
    """
    Evaluate event suitability by fetching weather data and calling microservice.
    
    Expects JSON body with:
    - event_type (str): Type of event (sports, market, gathering)
    
    Returns:
    - suitability_score (int): Score between 0 and 100
    - risk_level (str): Low Risk, Moderate Risk, or High Risk
    - recommendation (str): Text recommendation
    - weather_data (dict): Weather data used for evaluation
    """
    event = Event.query.get_or_404(event_id)  # type: ignore
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    event_type = data.get('event_type')
    if not event_type:
        return jsonify({'error': 'event_type is required'}), 400
    
    # Fetch weather data for event location
    weather_data = get_weather_by_location(event.location)
    
    if 'error' in weather_data:
        return jsonify(weather_data), 500
    
    # Extract required weather parameters
    temperature = weather_data.get('temperature', 0.0)
    wind_speed = weather_data.get('wind_speed', 0.0)
    
    # Calculate rain probability from weather description
    weather_main = weather_data.get('weather_main', '').lower()
    if 'rain' in weather_main or 'drizzle' in weather_main or 'thunderstorm' in weather_main:
        rain_probability = 0.8
    elif 'clouds' in weather_main:
        rain_probability = 0.3
    else:
        rain_probability = 0.1
    
    # Call microservice for analysis
    analysis_result = call_microservice_analyze(
        temperature=temperature,
        rain_probability=rain_probability,
        wind_speed=wind_speed,
        event_type=event_type
    )
    
    if 'error' in analysis_result:
        return jsonify(analysis_result), 500
    
    # Save evaluation log to database
    evaluation_log = EvaluationLog(
        event_id=event_id,
        suitability_score=analysis_result.get('suitability_score', 0),
        risk_alert=analysis_result.get('risk_level', ''),
        weather_data=json.dumps(weather_data)
    )
    
    db.session.add(evaluation_log)
    db.session.commit()
    
    # Return aggregated result
    return jsonify({
        'event_id': event_id,
        'event': event.to_dict(),
        'evaluation': analysis_result,
        'weather_data': weather_data,
        'evaluated_at': evaluation_log.evaluated_at.isoformat()
    }), 200


@evaluation_bp.route('/api/evaluation/events/<int:event_id>', methods=['GET'])
def get_event_evaluation(event_id):
    """
    Get the latest evaluation result for a specific event.
    
    Returns:
    - event details
    - latest evaluation log
    - aggregated data for frontend display
    """
    event = Event.query.get_or_404(event_id)  # type: ignore
    
    # Get the latest evaluation log for this event
    latest_evaluation = EvaluationLog.query.filter_by(event_id=event_id).order_by(EvaluationLog.evaluated_at.desc()).first()  # type: ignore
    
    if not latest_evaluation:
        return jsonify({
            'event': event.to_dict(),
            'evaluation': None,
            'message': 'No evaluation found for this event'
        }), 200
    
    result = {
        'event': event.to_dict(),
        'evaluation': {
            'suitability_score': latest_evaluation.suitability_score,
            'risk_alert': latest_evaluation.risk_alert,
            'weather_data': json.loads(latest_evaluation.weather_data) if latest_evaluation.weather_data else None,
            'evaluated_at': latest_evaluation.evaluated_at.isoformat()
        }
    }
    
    return jsonify(result), 200


@evaluation_bp.route('/api/evaluation/events', methods=['GET'])
def get_all_evaluations():
    """
    Get all events with their latest evaluation results.
    
    Returns:
    - List of events with their evaluation data aggregated
    """
    events = Event.query.all()  # type: ignore
    results = []
    
    for event in events:
        latest_evaluation = EvaluationLog.query.filter_by(event_id=event.id).order_by(EvaluationLog.evaluated_at.desc()).first()  # type: ignore
        
        event_data = {
            'event': event.to_dict(),
            'evaluation': None
        }
        
        if latest_evaluation:
            event_data['evaluation'] = {
                'suitability_score': latest_evaluation.suitability_score,
                'risk_alert': latest_evaluation.risk_alert,
                'weather_data': json.loads(latest_evaluation.weather_data) if latest_evaluation.weather_data else None,
                'evaluated_at': latest_evaluation.evaluated_at.isoformat()
            }
        
        results.append(event_data)
    
    return jsonify(results), 200
