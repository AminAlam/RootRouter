from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
import datetime

app = Flask(__name__)

# Configurations
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///plants.db'
db = SQLAlchemy(app)

# Database model
class PlantData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    plant_name = db.Column(db.String(100))
    location = db.Column(db.String(100))
    moisture_value = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f"<PlantData {self.plant_name}>"

# Function to determine moisture status
def get_moisture_status(moisture_value):
    if moisture_value > 3000:
        return {"class": "dry", "text": "Dry"}
    elif moisture_value > 2400:
        return {"class": "not-so-wet", "text": "Not So Wet"}
    elif moisture_value > 2100:
        return {"class": "wet", "text": "Wet"}
    else:  # moisture_value <= 2100
        return {"class": "very-wet", "text": "Very Wet"}

# Function to determine threshold values for status calculations
def get_moisture_thresholds():
    return {
        "very_wet": 2100,
        "wet": 2400,
        "not_so_wet": 3000,
        "dry": float('inf')
    }

# Route to receive data from Arduino
@app.route('/receive_data', methods=['POST'])
def receive_data():
    data = request.get_json()
    if data:
        plant_name = data.get('plant_name')
        location = data.get('location')
        moisture_value = data.get('moisture_value')
        
        if plant_name and location and moisture_value:
            new_entry = PlantData(
                plant_name=plant_name,
                location=location,
                moisture_value=int(moisture_value)
            )
            db.session.add(new_entry)
            db.session.commit()
            return 'Data received and stored', 200
        else:
            return 'Invalid data', 400
    else:
        return 'No JSON data received', 400

# Route to display data
@app.route('/')
def index():
    # Check if time_range parameter is provided
    time_range = request.args.get('time_range', 'all')
    
    # By default, get all data ordered by timestamp
    query = PlantData.query
    
    # If time_range is specified and not 'all', filter by date
    if time_range != 'all' and time_range.isdigit():
        days = int(time_range)
        cutoff_date = datetime.datetime.utcnow() - datetime.timedelta(days=days)
        query = query.filter(PlantData.timestamp >= cutoff_date)
    
    # Get data ordered by timestamp
    plant_data_raw = query.order_by(PlantData.timestamp.desc()).all()
    
    # Add moisture status to each data point
    plant_data = []
    for data in plant_data_raw:
        data_dict = {
            'id': data.id,
            'plant_name': data.plant_name,
            'location': data.location,
            'moisture_value': data.moisture_value,
            'timestamp': data.timestamp,
            'moisture_status': get_moisture_status(data.moisture_value)
        }
        plant_data.append(data_dict)
    
    return render_template('index.html', plant_data=plant_data)

if __name__ == '__main__':
    # Create database tables within an application context
    with app.app_context():
        db.create_all()
    # Run app with SSL context (use your own cert.pem and key.pem files)
    # app.run(host='0.0.0.0', port=443, ssl_context=('cert.pem', 'key.pem'))
    app.run(host='0.0.0.0', port=8080)

def run():
    """Entry point for the application script"""
    # with app.app_context():
    #     db.create_all()
    app.run(host='0.0.0.0', port=8080)