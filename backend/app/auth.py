from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from . import db
from .models import User
from flasgger import swag_from

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/register', methods=['POST'])
@swag_from({
    'tags': ['Authentication'],
    'summary': 'Register a new user',
    'description': 'Create a new user account with username, email, and password',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'username': {'type': 'string', 'example': 'john_doe'},
                    'email': {'type': 'string', 'example': 'john@example.com'},
                    'password': {'type': 'string', 'example': 'securepassword123'}
                },
                'required': ['username', 'email', 'password']
            }
        }
    ],
    'responses': {
        201: {
            'description': 'User registered successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': 'User registered successfully'},
                    'user': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'integer', 'example': 1},
                            'username': {'type': 'string', 'example': 'john_doe'},
                            'email': {'type': 'string', 'example': 'john@example.com'},
                            'role': {'type': 'string', 'example': 'user'}
                        }
                    }
                }
            }
        },
        400: {
            'description': 'Bad request - missing fields or user already exists',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'Username already exists'}
                }
            }
        }
    }
})
def register():
    data = request.get_json()
    
    # Validate input
    if not data or not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Username, email, and password are required'}), 400
    
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    # Check if user already exists
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already exists'}), 400
    
    # Create new user
    user = User(username=username, email=email)
    user.set_password(password)
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        'message': 'User registered successfully',
        'user': user.to_dict()
    }), 201


@auth_bp.route('/login', methods=['POST'])
@swag_from({
    'tags': ['Authentication'],
    'summary': 'Login user',
    'description': 'Authenticate a user with email and password and return a JWT access token',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'email': {'type': 'string', 'example': 'john@example.com'},
                    'password': {'type': 'string', 'example': 'securepassword123'}
                },
                'required': ['email', 'password']
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Login successful',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': 'Login successful'},
                    'access_token': {'type': 'string', 'example': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'},
                    'user': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'integer', 'example': 1},
                            'username': {'type': 'string', 'example': 'john_doe'},
                            'email': {'type': 'string', 'example': 'john@example.com'},
                            'role': {'type': 'string', 'example': 'user'}
                        }
                    }
                }
            }
        },
        400: {
            'description': 'Bad request - missing fields',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'Email and password are required'}
                }
            }
        },
        401: {
            'description': 'Unauthorized - invalid credentials',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'Invalid email or password'}
                }
            }
        }
    }
})
def login():
    data = request.get_json()
    
    # Validate input
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password are required'}), 400
    
    email = data.get('email')
    password = data.get('password')
    
    # Find user by email
    user = User.query.filter_by(email=email).first()
    
    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid email or password'}), 401
    
    # Create access token
    access_token = create_access_token(identity=str(user.id))
    
    return jsonify({
        'message': 'Login successful',
        'access_token': access_token,
        'user': user.to_dict()
    }), 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
@swag_from({
    'tags': ['Authentication'],
    'summary': 'Get current user',
    'description': 'Retrieve the currently authenticated user information',
    'security': [{'Bearer': []}],
    'responses': {
        200: {
            'description': 'Current user information',
            'schema': {
                'type': 'object',
                'properties': {
                    'user': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'integer', 'example': 1},
                            'username': {'type': 'string', 'example': 'john_doe'},
                            'email': {'type': 'string', 'example': 'john@example.com'},
                            'role': {'type': 'string', 'example': 'user'}
                        }
                    }
                }
            }
        },
        401: {
            'description': 'Unauthorized - missing or invalid token',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'Missing Authorization Header'}
                }
            }
        },
        404: {
            'description': 'User not found',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'User not found'}
                }
            }
        }
    }
})
def get_current_user():
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'user': user.to_dict()
    }), 200
