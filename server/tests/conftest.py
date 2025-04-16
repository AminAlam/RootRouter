import os
import sys
import pytest
import tempfile

# Add the src directory to the path so we can import the app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from main import app, db, PlantData

@pytest.fixture
def client():
    """Create a test client for the app."""
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
    })
    
    # Create the database and the tables
    with app.app_context():
        db.create_all()
        
        # Add some test data
        test_data = [
            PlantData(plant_name="Test Plant 1", location="Test Location 1", moisture_value=300),
            PlantData(plant_name="Test Plant 2", location="Test Location 2", moisture_value=400),
            PlantData(plant_name="Test Plant 1", location="Test Location 1", moisture_value=350),
        ]
        db.session.add_all(test_data)
        db.session.commit()
    
    with app.test_client() as client:
        yield client
    
    # Clean up
    with app.app_context():
        db.drop_all() 