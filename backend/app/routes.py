from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from . import db
from .models import Event, User

events_bp = Blueprint('events', __name__)


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
