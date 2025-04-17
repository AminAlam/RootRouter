import json
import pytest
from main import app, db, PlantData


def test_index_route(client):
    """Test the index route."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'RootRouter Dashboard' in response.data
    assert b'Plant Moisture Monitor' in response.data


def test_receive_data_valid(client):
    """Test receiving valid data from an Arduino."""
    test_data = {
        'plant_name': 'Test Plant 3',
        'location': 'Test Location 3',
        'moisture_value': 450
    }

    response = client.post('/receive_data',
                           data=json.dumps(test_data),
                           content_type='application/json')

    assert response.status_code == 200
    assert b'Data received and stored' in response.data

    # Verify the data was stored in the database
    with app.app_context():
        plant_data = PlantData.query.filter_by(
            plant_name='Test Plant 3').first()
        assert plant_data is not None
        assert plant_data.location == 'Test Location 3'
        assert plant_data.moisture_value == 450


def test_receive_data_invalid(client):
    """Test receiving invalid data (missing fields)."""
    # Missing moisture_value
    test_data = {
        'plant_name': 'Test Plant 4',
        'location': 'Test Location 4'
    }

    response = client.post('/receive_data',
                           data=json.dumps(test_data),
                           content_type='application/json')

    assert response.status_code == 400
    assert b'Invalid data' in response.data


def test_receive_data_no_json(client):
    """Test receiving non-JSON data."""
    response = client.post('/receive_data',
                           data='This is not JSON',
                           content_type='text/plain')

    assert response.status_code == 415  # Unsupported Media Type
    assert b'Unsupported Media Type' in response.data
    assert b'application/json' in response.data
