from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

db = SQLAlchemy()
jwt = JWTManager()


def create_app():
    app = Flask(__name__)

    # Configure database connection (prioritizes DATABASE_URL from .env; defaults to local SQLite)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///outdoor_events.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-secret-key')
    
    # JWT Configuration
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False  # Token doesn't expire

    # initial DB
    db.init_app(app)
    jwt.init_app(app)

    # Automatically create database tables
    with app.app_context():
        from . import models  # Import model file
        db.create_all()  # Generate an SQLite database file locally
        
        # Create a default administrator user (if it does not exist)
        from .models import User
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(username='admin', email='admin@example.com', role='admin')
            admin.set_password('123456')
            db.session.add(admin)
            db.session.commit()
            print('Admin user created: username=admin, password=123456')

    # Registration Blueprint
    from .routes import events_bp
    from .auth import auth_bp
    app.register_blueprint(events_bp)
    app.register_blueprint(auth_bp)

    return app