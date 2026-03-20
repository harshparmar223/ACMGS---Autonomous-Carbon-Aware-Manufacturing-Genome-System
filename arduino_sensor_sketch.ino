#include <DHT.h>

// ===== Sensor Configuration =====
#define DHTPIN 2              // DHT11 data pin
#define DHTTYPE DHT11         // DHT 11 (AM2302)
#define ACS712_PIN A0         // ACS712 analog input pin
#define BAUD_RATE 9600        // Serial communication speed

// ===== Sensor calibration =====
#define ACS712_SENSITIVITY 0.185  // 185mV/A for 5A model (adjust for 30A: 0.066)
#define ACS712_ZERO_OFFSET 512    // Analog read value at 0A (typically 512 for 5V)

// DHT sensor instance
DHT dht(DHTPIN, DHTTYPE);

// Sampling variables
unsigned long lastReadTime = 0;
const unsigned long SAMPLE_INTERVAL = 1000; // Read every 1 second

void setup() {
  Serial.begin(BAUD_RATE);
  dht.begin();
  
  delay(2000); // Wait for sensors to stabilize
  Serial.println("SENSORS_INITIALIZED");
}

void loop() {
  // Read sensors every SAMPLE_INTERVAL milliseconds
  if (millis() - lastReadTime >= SAMPLE_INTERVAL) {
    lastReadTime = millis();
    
    // Read temperature and humidity
    float humidity = dht.readHumidity();
    float temperature = dht.readTemperature();
    
    // Read current sensor (multiple samples for averaging)
    float current = readCurrent(10);
    
    // Send data in JSON format
    if (!isnan(humidity) && !isnan(temperature)) {
      Serial.print("{");
      Serial.print("\"temp\":");
      Serial.print(temperature);
      Serial.print(",\"humidity\":");
      Serial.print(humidity);
      Serial.print(",\"current\":");
      Serial.print(current);
      Serial.println("}");
    } else {
      Serial.println("{\"error\":\"DHT_READ_FAILED\"}");
    }
  }
}

// Function to read current with averaging
float readCurrent(int samples) {
  float sum = 0;
  
  for (int i = 0; i < samples; i++) {
    int rawValue = analogRead(ACS712_PIN);
    
    // Convert analog reading to voltage (0-5V)
    float voltage = (rawValue / 1023.0) * 5.0;
    
    // For 5A module: subtract 2.5V (middle voltage at 0A) and divide by sensitivity
    // For 30A module: subtract 2.5V and divide by 0.066
    float current_value = (voltage - 2.5) / ACS712_SENSITIVITY;
    
    sum += current_value;
    delayMicroseconds(200);
  }
  
  return sum / samples;
}
