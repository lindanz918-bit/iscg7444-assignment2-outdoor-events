import pytest
from app import create_app, db
from app.models import Event


@pytest.fixture
def client(monkeypatch):
    # Use an in-memory database so the tests never touch the local database file
    monkeypatch.setenv('DATABASE_URL', 'sqlite:///:memory:')
    app = create_app()
    app.config['TESTING'] = True

    # Add 23 events: 3 pages with the default limit of 10
    with app.app_context():
        for number in range(1, 24):
            db.session.add(Event(title=f'Event {number}', location='Auckland', date='2026-12-01'))
        db.session.commit()

    with app.test_client() as client:
        yield client
    with app.app_context():
        db.drop_all()


def test_default_page_and_limit(client):
    response = client.get('/api/events')
    data = response.json
    assert response.status_code == 200
    assert len(data['events']) == 10
    assert data['current_page'] == 1
    assert data['limit'] == 10
    assert data['total_items'] == 23
    assert data['total_pages'] == 3
    assert data['events'][0]['title'] == 'Event 1'


def test_second_page(client):
    data = client.get('/api/events?page=2').json
    assert [event['title'] for event in data['events']][0] == 'Event 11'
    assert len(data['events']) == 10
    assert data['current_page'] == 2


def test_last_page_has_remaining_events(client):
    data = client.get('/api/events?page=3').json
    assert len(data['events']) == 3
    assert data['events'][-1]['title'] == 'Event 23'


def test_custom_limit(client):
    data = client.get('/api/events?page=1&limit=5').json
    assert len(data['events']) == 5
    assert data['limit'] == 5
    assert data['total_pages'] == 5


def test_page_after_the_last_page_is_empty(client):
    response = client.get('/api/events?page=10')
    assert response.status_code == 200
    assert response.json['events'] == []
    assert response.json['total_items'] == 23


@pytest.mark.parametrize('query', [
    'page=0',
    'page=-1',
    'page=abc',
    'page=1.5',
    'limit=0',
    'limit=-5',
    'limit=abc',
    'limit=101',
])
def test_invalid_page_or_limit_returns_400(client, query):
    response = client.get(f'/api/events?{query}')
    assert response.status_code == 400
    assert 'error' in response.json


def test_maximum_limit_is_allowed(client):
    data = client.get('/api/events?limit=100').json
    assert len(data['events']) == 23
    assert data['total_pages'] == 1


def test_empty_parameters_use_defaults(client):
    data = client.get('/api/events?page=&limit=').json
    assert data['current_page'] == 1
    assert data['limit'] == 10