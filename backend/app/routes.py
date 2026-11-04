from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from . import db
from .models import Event, User, EvaluationLog, EVENT_TYPES
from .weather import get_weather_by_location, get_weather_forecast
from .microservice_client import call_microservice_analyze
from flasgger import swag_from
import json

events_bp = Blueprint('events', __name__)
weather_bp = Blueprint('weather', __name__)
evaluation_bp = Blueprint('evaluation', __name__)


def admin_required():
    """Check if current user is admin"""
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)  # type: ignore
    if not user or user.role != 'admin':
        return False
    return True


def parse_event_type(value):
    """Return the event type in lowercase, or None if it is not a supported type."""
    if not isinstance(value, str):
        return None
    value = value.strip().lower()
    return value if value in EVENT_TYPES else None


EVENT_TYPE_ERROR = f"event_type must be one of: {', '.join(EVENT_TYPES)}"


DEFAULT_PAGE_LIMIT = 10
MAX_PAGE_LIMIT = 100


def parse_positive_int(name, default, maximum=None):
    """
    Read an optional positive integer query parameter.

    Returns:
        tuple: (value, error message). The error message is None when the value is valid.
    """
    raw_value = request.args.get(name)
    if raw_value is None or raw_value.strip() == '':
        return default, None
    try:
        value = int(raw_value)
    except ValueError:
        return None, f'{name} must be a whole number'
    if value < 1:
        return None, f'{name} must be 1 or greater'
    if maximum is not None and value > maximum:
        return None, f'{name} must be {maximum} or less'
    return value, None


@events_bp.route('/api/events', methods=['GET'])
@swag_from({
    'tags': ['Events'],
    'summary': 'Get events (paginated)',
    'description': 'Retrieve one page of events, with pagination metadata',
    'parameters': [
        {
            'name': 'page',
            'in': 'query',
            'type': 'integer',
            'required': False,
            'default': 1,
            'description': 'Page number, starting from 1'
        },
        {
            'name': 'limit',
            'in': 'query',
            'type': 'integer',
            'required': False,
            'default': DEFAULT_PAGE_LIMIT,
            'description': f'Number of events per page (1-{MAX_PAGE_LIMIT})'
        }
    ],
    'responses': {
        200: {
            'description': 'One page of events with pagination metadata',
            'schema': {
                'type': 'object',
                'properties': {
                    'events': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'id': {'type': 'integer', 'example': 1},
                                'title': {'type': 'string', 'example': 'Summer Music Festival'},
                                'description': {'type': 'string', 'example': 'Annual outdoor music festival'},
                                'location': {'type': 'string', 'example': 'Central Park, Auckland'},
                                'date': {'type': 'string', 'example': '2024-12-15'},
                                'time': {'type': 'string', 'example': '14:00'},
                                'event_type': {'type': 'string', 'enum': ['sports', 'market', 'gathering'], 'example': 'sports'}
                            }
                        }
                    },
                    'total_items': {'type': 'integer', 'example': 23},
                    'total_pages': {'type': 'integer', 'example': 3},
                    'current_page': {'type': 'integer', 'example': 1},
                    'limit': {'type': 'integer', 'example': 10}
                }
            }
        },
        400: {
            'description': 'Bad request - page or limit is not a valid number',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'limit must be 100 or less'}
                }
            }
        }
    }
})
def get_events():
    """Retrieve one page of events (?page=1&limit=10) with pagination metadata"""
    page, error = parse_positive_int('page', default=1)
    if error:
        return jsonify({'error': error}), 400

    limit, error = parse_positive_int('limit', default=DEFAULT_PAGE_LIMIT, maximum=MAX_PAGE_LIMIT)
    if error:
        return jsonify({'error': error}), 400

    total_items = Event.query.count()  # type: ignore
    total_pages = (total_items + limit - 1) // limit  # round up

    # Only fetch the events for the requested page
    events = (
        Event.query.order_by(Event.id)  # type: ignore
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    return jsonify({
        'events': [event.to_dict() for event in events],
        'total_items': total_items,
        'total_pages': total_pages,
        'current_page': page,
        'limit': limit
    }), 200


@events_bp.route('/api/events/<int:event_id>', methods=['GET'])
@swag_from({
    'tags': ['Events'],
    'summary': 'Get event by ID',
    'description': 'Retrieve details for a specific event',
    'parameters': [
        {
            'name': 'event_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID of the event to retrieve'
        }
    ],
    'responses': {
        200: {
            'description': 'Event details',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer', 'example': 1},
                    'title': {'type': 'string', 'example': 'Summer Music Festival'},
                    'description': {'type': 'string', 'example': 'Annual outdoor music festival'},
                    'location': {'type': 'string', 'example': 'Central Park, Auckland'},
                    'date': {'type': 'string', 'example': '2024-12-15'},
                    'time': {'type': 'string', 'example': '14:00'},
                    'event_type': {'type': 'string', 'enum': ['sports', 'market', 'gathering'], 'example': 'sports'}
                }
            }
        },
        404: {
            'description': 'Event not found'
        }
    }
})
def get_event(event_id):
    """Retrieve details for a specific event"""
    event = Event.query.get_or_404(event_id)  # type: ignore
    return jsonify(event.to_dict()), 200


@events_bp.route('/api/events', methods=['POST'])
@jwt_required()
@swag_from({
    'tags': ['Events'],
    'summary': 'Create event',
    'description': 'Create a new event (admin only)',
    'security': [{'Bearer': []}],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'title': {'type': 'string', 'example': 'Summer Music Festival'},
                    'description': {'type': 'string', 'example': 'Annual outdoor music festival'},
                    'location': {'type': 'string', 'example': 'Central Park, Auckland'},
                    'date': {'type': 'string', 'example': '2024-12-15'},
                    'time': {'type': 'string', 'example': '14:00'},
                    'event_type': {'type': 'string', 'enum': ['sports', 'market', 'gathering'], 'example': 'sports'}
                },
                'required': ['title', 'location', 'date']
            }
        }
    ],
    'responses': {
        201: {
            'description': 'Event created successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer', 'example': 1},
                    'title': {'type': 'string', 'example': 'Summer Music Festival'},
                    'description': {'type': 'string', 'example': 'Annual outdoor music festival'},
                    'location': {'type': 'string', 'example': 'Central Park, Auckland'},
                    'date': {'type': 'string', 'example': '2024-12-15'},
                    'time': {'type': 'string', 'example': '14:00'},
                    'event_type': {'type': 'string', 'enum': ['sports', 'market', 'gathering'], 'example': 'sports'}
                }
            }
        },
        400: {
            'description': 'Bad request - missing required fields',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'title is required'}
                }
            }
        },
        401: {
            'description': 'Unauthorized - missing or invalid token'
        },
        403: {
            'description': 'Forbidden - admin access required',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'Admin access required'}
                }
            }
        }
    }
})
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

    # event_type is optional, but must be a supported type when provided
    event_type = None
    if data.get('event_type'):
        event_type = parse_event_type(data['event_type'])
        if event_type is None:
            return jsonify({'error': EVENT_TYPE_ERROR}), 400

    event = Event(
        title=data['title'],
        description=data.get('description', ''),
        location=data['location'],
        date=data['date'],
        time=data.get('time', ''),
        event_type=event_type
    )

    db.session.add(event)
    db.session.commit()

    return jsonify(event.to_dict()), 201


@events_bp.route('/api/events/<int:event_id>', methods=['PUT'])
@jwt_required()
@swag_from({
    'tags': ['Events'],
    'summary': 'Update event',
    'description': 'Update event information (admin only)',
    'security': [{'Bearer': []}],
    'parameters': [
        {
            'name': 'event_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID of the event to update'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'title': {'type': 'string', 'example': 'Summer Music Festival 2024'},
                    'description': {'type': 'string', 'example': 'Updated description'},
                    'location': {'type': 'string', 'example': 'Albert Park, Auckland'},
                    'date': {'type': 'string', 'example': '2024-12-20'},
                    'time': {'type': 'string', 'example': '15:00'},
                    'event_type': {'type': 'string', 'enum': ['sports', 'market', 'gathering'], 'example': 'sports'}
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Event updated successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer', 'example': 1},
                    'title': {'type': 'string', 'example': 'Summer Music Festival 2024'},
                    'description': {'type': 'string', 'example': 'Updated description'},
                    'location': {'type': 'string', 'example': 'Albert Park, Auckland'},
                    'date': {'type': 'string', 'example': '2024-12-20'},
                    'time': {'type': 'string', 'example': '15:00'},
                    'event_type': {'type': 'string', 'enum': ['sports', 'market', 'gathering'], 'example': 'sports'}
                }
            }
        },
        400: {
            'description': 'Bad request - no data provided'
        },
        401: {
            'description': 'Unauthorized - missing or invalid token'
        },
        403: {
            'description': 'Forbidden - admin access required'
        },
        404: {
            'description': 'Event not found'
        }
    }
})
def update_event(event_id):
    """Update event information (admin only)"""
    if not admin_required():
        return jsonify({'error': 'Admin access required'}), 403

    event = Event.query.get_or_404(event_id)  # type: ignore
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
    if 'event_type' in data:
        if data['event_type']:
            event_type = parse_event_type(data['event_type'])
            if event_type is None:
                return jsonify({'error': EVENT_TYPE_ERROR}), 400
            event.event_type = event_type
        else:
            event.event_type = None

    db.session.commit()

    return jsonify(event.to_dict()), 200


@events_bp.route('/api/events/<int:event_id>', methods=['DELETE'])
@jwt_required()
@swag_from({
    'tags': ['Events'],
    'summary': 'Delete event',
    'description': 'Delete an event (admin only)',
    'security': [{'Bearer': []}],
    'parameters': [
        {
            'name': 'event_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID of the event to delete'
        }
    ],
    'responses': {
        200: {
            'description': 'Event deleted successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': 'Event deleted successfully'}
                }
            }
        },
        401: {
            'description': 'Unauthorized - missing or invalid token'
        },
        403: {
            'description': 'Forbidden - admin access required'
        },
        404: {
            'description': 'Event not found'
        }
    }
})
def delete_event(event_id):
    """Delete an event (admin only)"""
    if not admin_required():
        return jsonify({'error': 'Admin access required'}), 403

    event = Event.query.get_or_404(event_id)  # type: ignore

    try:
        # Delete all related EvaluationLog records first
        EvaluationLog.query.filter_by(event_id=event_id).delete()  # type: ignore
        # Then delete the event
        db.session.delete(event)
        db.session.commit()
        return jsonify({'message': 'Event deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete event'}), 500


@weather_bp.route('/api/weather/current', methods=['GET'])
@swag_from({
    'tags': ['Weather'],
    'summary': 'Get current weather',
    'description': 'Get current weather for a location',
    'parameters': [
        {
            'name': 'location',
            'in': 'query',
            'type': 'string',
            'required': True,
            'description': 'Location name (e.g., Auckland, New Zealand)',
            'example': 'Auckland'
        }
    ],
    'responses': {
        200: {
            'description': 'Current weather data',
            'schema': {
                'type': 'object',
                'properties': {
                    'location': {'type': 'string', 'example': 'Auckland'},
                    'temperature': {'type': 'number', 'example': 22.5},
                    'weather_main': {'type': 'string', 'example': 'Clear'},
                    'weather_description': {'type': 'string', 'example': 'clear sky'},
                    'humidity': {'type': 'integer', 'example': 65},
                    'wind_speed': {'type': 'number', 'example': 3.5}
                }
            }
        },
        400: {
            'description': 'Bad request - missing location parameter',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'Location parameter is required'}
                }
            }
        },
        500: {
            'description': 'Internal server error - weather service error',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'Failed to fetch weather data'}
                }
            }
        }
    }
})
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
@swag_from({
    'tags': ['Weather'],
    'summary': 'Get weather forecast',
    'description': 'Get weather forecast for a location for up to 5 days',
    'parameters': [
        {
            'name': 'location',
            'in': 'query',
            'type': 'string',
            'required': True,
            'description': 'Location name (e.g., Auckland, New Zealand)',
            'example': 'Auckland'
        },
        {
            'name': 'days',
            'in': 'query',
            'type': 'integer',
            'required': False,
            'description': 'Number of days for forecast (1-5)',
            'default': 5,
            'example': 3
        }
    ],
    'responses': {
        200: {
            'description': 'Weather forecast data',
            'schema': {
                'type': 'object',
                'properties': {
                    'location': {'type': 'string', 'example': 'Auckland'},
                    'forecast': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'date': {'type': 'string', 'example': '2024-12-16'},
                                'temperature': {'type': 'number', 'example': 23.0},
                                'weather_main': {'type': 'string', 'example': 'Clouds'},
                                'weather_description': {'type': 'string', 'example': 'few clouds'}
                            }
                        }
                    }
                }
            }
        },
        400: {
            'description': 'Bad request - missing location or invalid days parameter',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'Location parameter is required'}
                }
            }
        },
        500: {
            'description': 'Internal server error - weather service error'
        }
    }
})
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
@swag_from({
    'tags': ['Evaluation'],
    'summary': 'Evaluate event suitability',
    'description': 'Evaluate event suitability by fetching weather data and calling microservice. Uses the event type stored on the event.',
    'parameters': [
        {
            'name': 'event_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID of the event to evaluate'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': False,
            'schema': {
                'type': 'object',
                'properties': {
                    'event_type': {
                        'type': 'string',
                        'enum': ['sports', 'market', 'gathering'],
                        'example': 'sports',
                        'description': 'Only used if the event has no stored event_type'
                    }
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Evaluation result',
            'schema': {
                'type': 'object',
                'properties': {
                    'event_id': {'type': 'integer', 'example': 1},
                    'event': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'integer', 'example': 1},
                            'title': {'type': 'string', 'example': 'Summer Music Festival'},
                            'location': {'type': 'string', 'example': 'Central Park, Auckland'},
                            'date': {'type': 'string', 'example': '2024-12-15'}
                        }
                    },
                    'evaluation': {
                        'type': 'object',
                        'properties': {
                            'suitability_score': {'type': 'integer', 'example': 85},
                            'risk_level': {'type': 'string', 'example': 'Low Risk'},
                            'recommendation': {'type': 'string', 'example': 'Conditions are favorable for the event'}
                        }
                    },
                    'weather_data': {
                        'type': 'object',
                        'properties': {
                            'temperature': {'type': 'number', 'example': 22.5},
                            'weather_main': {'type': 'string', 'example': 'Clear'},
                            'wind_speed': {'type': 'number', 'example': 3.5}
                        }
                    },
                    'evaluated_at': {'type': 'string', 'example': '2024-12-15T10:30:00'}
                }
            }
        },
        400: {
            'description': 'Bad request - the event has no event_type and none was provided'
        },
        404: {
            'description': 'Event not found'
        },
        500: {
            'description': 'Internal server error - weather or microservice error'
        }
    }
})
def evaluate_event(event_id):
    """
    Evaluate event suitability by fetching weather data and calling microservice.

    Uses the event_type stored on the event. A JSON body with
    event_type (sports, market, gathering) is only needed for older
    events that do not have a stored event type.

    Returns:
    - suitability_score (int): Score between 0 and 100
    - risk_level (str): Low Risk, Moderate Risk, or High Risk
    - recommendation (str): Text recommendation
    - weather_data (dict): Weather data used for evaluation
    """
    event = Event.query.get_or_404(event_id)  # type: ignore
    data = request.get_json(silent=True) or {}

    # Use the event type stored on the event. The request body is only used
    # as a fallback for older events that were created without an event type.
    event_type = event.event_type or parse_event_type(data.get('event_type'))
    if not event_type:
        return jsonify({
            'error': 'This event has no event_type. Set it on the event, or send a valid event_type '
                     f"({', '.join(EVENT_TYPES)}) in the request body."
        }), 400

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
@swag_from({
    'tags': ['Evaluation'],
    'summary': 'Get event evaluation',
    'description': 'Get the latest evaluation result for a specific event',
    'parameters': [
        {
            'name': 'event_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID of the event'
        }
    ],
    'responses': {
        200: {
            'description': 'Event evaluation data',
            'schema': {
                'type': 'object',
                'properties': {
                    'event': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'integer', 'example': 1},
                            'title': {'type': 'string', 'example': 'Summer Music Festival'},
                            'location': {'type': 'string', 'example': 'Central Park, Auckland'},
                            'date': {'type': 'string', 'example': '2024-12-15'}
                        }
                    },
                    'evaluation': {
                        'type': 'object',
                        'properties': {
                            'suitability_score': {'type': 'integer', 'example': 85},
                            'risk_alert': {'type': 'string', 'example': 'Low Risk'},
                            'weather_data': {
                                'type': 'object',
                                'properties': {
                                    'temperature': {'type': 'number', 'example': 22.5},
                                    'weather_main': {'type': 'string', 'example': 'Clear'}
                                }
                            },
                            'evaluated_at': {'type': 'string', 'example': '2024-12-15T10:30:00'}
                        }
                    },
                    'message': {'type': 'string', 'example': 'No evaluation found for this event'}
                }
            }
        },
        404: {
            'description': 'Event not found'
        }
    }
})
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
    latest_evaluation = EvaluationLog.query.filter_by(event_id=event_id).order_by(
        EvaluationLog.evaluated_at.desc()).first()  # type: ignore

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
@swag_from({
    'tags': ['Evaluation'],
    'summary': 'Get all evaluations',
    'description': 'Get all events with their latest evaluation results',
    'responses': {
        200: {
            'description': 'List of events with evaluation data',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'event': {
                            'type': 'object',
                            'properties': {
                                'id': {'type': 'integer', 'example': 1},
                                'title': {'type': 'string', 'example': 'Summer Music Festival'},
                                'location': {'type': 'string', 'example': 'Central Park, Auckland'},
                                'date': {'type': 'string', 'example': '2024-12-15'}
                            }
                        },
                        'evaluation': {
                            'type': 'object',
                            'properties': {
                                'suitability_score': {'type': 'integer', 'example': 85},
                                'risk_alert': {'type': 'string', 'example': 'Low Risk'},
                                'weather_data': {
                                    'type': 'object',
                                    'properties': {
                                        'temperature': {'type': 'number', 'example': 22.5}
                                    }
                                },
                                'evaluated_at': {'type': 'string', 'example': '2024-12-15T10:30:00'}
                            }
                        }
                    }
                }
            }
        }
    }
})
def get_all_evaluations():
    """
    Get all events with their latest evaluation results.

    Returns:
    - List of events with their evaluation data aggregated
    """
    events = Event.query.all()  # type: ignore
    results = []

    for event in events:
        latest_evaluation = EvaluationLog.query.filter_by(event_id=event.id).order_by(
            EvaluationLog.evaluated_at.desc()).first()  # type: ignore

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