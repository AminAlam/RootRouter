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
    plant_data = PlantData.query.order_by(PlantData.timestamp.desc()).all()
    return render_template('index.html', plant_data=plant_data)

if __name__ == '__main__':
    # Create database tables within an application context
    with app.app_context():
        db.create_all()
    # Run app with SSL context (use your own cert.pem and key.pem files)
    # app.run(host='0.0.0.0', port=443, ssl_context=('cert.pem', 'key.pem'))
    app.run(host='0.0.0.0', port=8080)