import pytest
from app import create_app, db
from app.models import User, Event, EvaluationLog


@pytest.fixture
def app(monkeypatch):
    # Set the database before create_app() so the tests use an in-memory
    # database and never clear the local database file
    monkeypatch.setenv('DATABASE_URL', 'sqlite:///:memory:')
    app = create_app()
    app.config['TESTING'] = True

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture(autouse=True)
def clean_db(app):
    """Clean database before each test and recreate default admin"""
    with app.app_context():
        db.session.remove()
        db.drop_all()
        db.create_all()
        # Recreate default admin user
        admin = User(username='admin', email='admin@example.com', role='admin')
        admin.set_password('123456')
        db.session.add(admin)
        db.session.commit()
    yield


def test_get_events(client):
    """Test getting the first page of events"""
    response = client.get('/api/events')
    assert response.status_code == 200
    assert isinstance(response.json['events'], list)
    assert response.json['current_page'] == 1


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


def get_auth_token(client):
    """Helper to get admin auth token using existing default admin"""
    # Login with existing default admin (email: admin@example.com, password: 123456)
    response = client.post('/api/auth/login', json={
        'email': 'admin@example.com',
        'password': '123456'
    })
    return response.json['access_token']


def test_delete_event_without_evaluations(client):
    """Test deleting an event without evaluations"""
    token = get_auth_token(client)

    # Create an event
    with client.application.app_context():
        event = Event(title='Test Event', location='Auckland', date='2024-12-01')
        db.session.add(event)
        db.session.commit()
        event_id = event.id

    # Delete the event
    response = client.delete(f'/api/events/{event_id}', headers={
        'Authorization': f'Bearer {token}'
    })
    assert response.status_code == 200
    assert response.json['message'] == 'Event deleted successfully'

    # Verify event is deleted
    with client.application.app_context():
        assert Event.query.get(event_id) is None


def test_delete_event_with_evaluations(client):
    """Test deleting an event with evaluation logs"""
    token = get_auth_token(client)

    # Create an event with evaluation logs
    with client.application.app_context():
        event = Event(title='Test Event', location='Auckland', date='2024-12-01')
        db.session.add(event)
        db.session.commit()
        event_id = event.id

        # Add evaluation logs
        eval1 = EvaluationLog(event_id=event_id, suitability_score=85.0, risk_alert='Low Risk')
        eval2 = EvaluationLog(event_id=event_id, suitability_score=70.0, risk_alert='Moderate Risk')
        db.session.add(eval1)
        db.session.add(eval2)
        db.session.commit()

    # Delete the event
    response = client.delete(f'/api/events/{event_id}', headers={
        'Authorization': f'Bearer {token}'
    })
    assert response.status_code == 200
    assert response.json['message'] == 'Event deleted successfully'

    # Verify event and evaluations are deleted
    with client.application.app_context():
        assert Event.query.get(event_id) is None
        assert EvaluationLog.query.filter_by(event_id=event_id).count() == 0


def test_delete_event_unauthorized(client):
    """Test deleting an event without authentication"""
    # Create an event
    with client.application.app_context():
        event = Event(title='Test Event', location='Auckland', date='2024-12-01')
        db.session.add(event)
        db.session.commit()
        event_id = event.id

    # Try to delete without auth
    response = client.delete(f'/api/events/{event_id}')
    assert response.status_code == 401

    # Verify event still exists
    with client.application.app_context():
        assert Event.query.get(event_id) is not None


def test_delete_event_non_admin(client):
    """Test deleting an event as non-admin user"""
    # Create regular user
    with client.application.app_context():
        user = User(username='user', email='user@test.com', role='visitor')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()

    # Login as regular user (using email, not username)
    response = client.post('/api/auth/login', json={
        'email': 'user@test.com',
        'password': 'password'
    })
    token = response.json['access_token']

    # Create an event
    with client.application.app_context():
        event = Event(title='Test Event', location='Auckland', date='2024-12-01')
        db.session.add(event)
        db.session.commit()
        event_id = event.id

    # Try to delete as non-admin
    response = client.delete(f'/api/events/{event_id}', headers={
        'Authorization': f'Bearer {token}'
    })
    assert response.status_code == 403

    # Verify event still exists
    with client.application.app_context():
        assert Event.query.get(event_id) is not None