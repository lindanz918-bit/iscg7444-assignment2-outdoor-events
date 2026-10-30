from flask import Blueprint, request, jsonify
from . import db
from .models import Event

events_bp = Blueprint('events', __name__)


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
def create_event():
    """Create a new event"""
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
def update_event(event_id):
    """Update event information"""
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
def delete_event(event_id):
    """Delete an event"""
    event = Event.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    
    return jsonify({'message': 'Event deleted successfully'}), 200
