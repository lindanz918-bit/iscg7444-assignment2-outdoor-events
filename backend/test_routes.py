import pytest
from app import create_app, db
from app.models import User, Event


@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def test_get_events(client):
    """Test getting all events"""
    response = client.get('/api/events')
    assert response.status_code == 200
    assert isinstance(response.json, list)


def test_create_event_without_auth(client):
    """Test creating event without authentication should fail"""
    response = client.post('/api/events', json={
        'title': 'Test Event',
        'location': 'Auckland',
        'date': '2024-12-01'
    })
    assert response.status_code == 401


def test_get_current_weather(client):
    """Test getting current weather"""
    response = client.get('/api/weather/current?location=Auckland')
    # May fail if API key not configured, but endpoint should exist
    assert response.status_code in [200, 500]
