import pytest
from datetime import datetime
from main import app, db, PlantData


def test_plant_data_model():
    """Test the PlantData model."""
    with app.app_context():
        # Create a new PlantData instance with a timestamp
        test_timestamp = datetime.utcnow()
        plant_data = PlantData(
            plant_name='Test Plant',
            location='Test Location',
            moisture_value=300,
            timestamp=test_timestamp
        )

        # Check that the attributes are set correctly
        assert plant_data.plant_name == 'Test Plant'
        assert plant_data.location == 'Test Location'
        assert plant_data.moisture_value == 300
        assert plant_data.timestamp == test_timestamp
        assert isinstance(plant_data.timestamp, datetime)

        # Check the representation
        assert "PlantData" in repr(plant_data)
        assert "Test Plant" in repr(plant_data)


def test_plant_data_crud(client):
    """Test CRUD operations for the PlantData model."""
    with app.app_context():
        # Create
        plant_data = PlantData(
            plant_name='CRUD Test Plant',
            location='CRUD Test Location',
            moisture_value=350
        )
        db.session.add(plant_data)
        db.session.commit()

        # Read
        retrieved = PlantData.query.filter_by(
            plant_name='CRUD Test Plant').first()
        assert retrieved is not None
        assert retrieved.location == 'CRUD Test Location'
        assert retrieved.moisture_value == 350

        # Update
        retrieved.moisture_value = 400
        db.session.commit()
        updated = PlantData.query.filter_by(
            plant_name='CRUD Test Plant').first()
        assert updated.moisture_value == 400

        # Delete
        db.session.delete(updated)
        db.session.commit()
        deleted = PlantData.query.filter_by(
            plant_name='CRUD Test Plant').first()
        assert deleted is None
