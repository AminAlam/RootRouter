#include <WiFi.h>
#include <WiFiClient.h>

const char* ssid = "";             // Replace with your Wi-Fi SSID
const char* password = "";     // Replace with your Wi-Fi password

const char* server = "192.168.1.40"; // Replace with your server address (e.g., "192.168.1.100")
const int httpPort = 8080;

const int AirValue = 520; // Dry soil value
const int WaterValue = 260; // Wet soil value
int intervals = (AirValue - WaterValue) / 3;
int soilMoistureValue = 0;

  String plantName = "Aloe Vera";      // Replace with your plant name
  String location = "Office";     // Replace with your plant's location


void setup() {
  Serial.begin(9600);
  delay(100);

  // Connect to Wi-Fi
  WiFi.begin(ssid, password);
  Serial.print("Connecting to Wi-Fi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConnected to Wi-Fi network.");
}

void loop() {
  // Read sensor value
  soilMoistureValue = analogRead(A0); // Ensure the sensor is connected to pin A0

  // Determine moisture level
  String moistureLevel;
  if (soilMoistureValue > WaterValue && soilMoistureValue < (WaterValue + intervals)) {
    moistureLevel = "Very Wet";
  } else if (soilMoistureValue >= (WaterValue + intervals) && soilMoistureValue <= (AirValue - intervals)) {
    moistureLevel = "Wet";
  } else if (soilMoistureValue > (AirValue - intervals) && soilMoistureValue <= AirValue) {
    moistureLevel = "Dry";
  } else {
    moistureLevel = "Unknown";
  }
 
  // Prepare data to send

  // Prepare JSON data
  String postData = "{";
  postData += "\"plant_name\":\"" + plantName + "\",";
  postData += "\"location\":\"" + location + "\",";
  postData += "\"moisture_value\":\"" + String(soilMoistureValue) + "\"";
  postData += "}";

  // Send data to server via HTTP
  if (WiFi.status() == WL_CONNECTED) {
    WiFiClient client;

    
    if (!client.connect(server, httpPort)) {
      Serial.println("Connection failed!");
      return;
    }

    // Make a HTTP POST request
    client.println("POST /receive_data HTTP/1.1"); // Ensure this endpoint matches your Flask app
    client.println("Host: " + String(server));
    client.println("Content-Type: application/json");
    client.println("Connection: close");
    client.print("Content-Length: ");
    client.println(postData.length());
    client.println();
    client.println(postData);

    // Read response
    while (client.connected()) {
      String line = client.readStringUntil('\n');
      if (line == "\r") {
        break;
      }
    }

    String response = client.readString();
    Serial.println(response);

    client.stop();
  } else {
    Serial.println("Wi-Fi not connected");
  }

  // Wait before next reading
  delay(60000); // Wait 1 minute
}