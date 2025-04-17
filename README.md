# 🌱 RootRouter

![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/AminAlam/RootRouter/tests.yml?branch=main)

RootRouter is an IoT plant moisture monitoring system that helps you keep your plants healthy by tracking soil moisture levels over time.

## 📋 Features

- **Real-time Moisture Monitoring**: Track soil moisture levels for multiple plants
- **Interactive Dashboard**: Visualize moisture data with filterable charts
- **Plant-specific Tracking**: Monitor different plants individually
- **Status Indicators**: Visual indicators for moisture levels (Very Wet, Wet, Dry, Unknown)
- **Arduino Integration**: Seamless data collection from Arduino-based moisture sensors

## 🛠️ Architecture

RootRouter consists of two main components:

1. **Sensor Module**: Arduino Nano ESP-based moisture sensors that collect and send data
2. **Server Module**: Flask-based web server that stores data and provides the monitoring dashboard

## 📊 Screenshots

![Dashboard Screenshot](docs/images/dashboard.png)

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Arduino IDE
- Arduino Nano ESP or compatible board
- Soil moisture sensors

### Server Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/AminAlam/RootRouter.git
   cd RootRouter
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Start the server:
   ```bash
   cd server/src
   python3 main.py
   ```

5. Access the dashboard at `http://localhost:8080`


### Arduino Setup

1. Open the Arduino sketch in the Arduino IDE:
   ```
   sensor/arduino_nano_esp/arduino_nano_esp.ino
   ```

2. Update the Wi-Fi credentials and server address in the sketch:
   ```cpp
   const char* ssid = "YourWiFiName";
   const char* password = "YourWiFiPassword";
   const char* server = "YourServerIP"; // Example: "192.168.1.100"
   ```

3. Connect the soil moisture sensor to your Arduino (analog pin A0)

4. Upload the sketch to your Arduino board

5. Place the sensor in your plant's soil and power on the device

## 🧪 Testing

Run the automated tests with:

```bash
cd server/tests
pytest
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Developed with ❤️ by [Amin Alam](https://github.com/AminAlam) 