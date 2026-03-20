#include <WiFi.h>
#include <HTTPClient.h>
#include <DHT.h>
#include <ArduinoJson.h>
#include <time.h>

// ===== WiFi Configuration =====
const char* ssid = "POCO M4 Pro 5G Harsh";         // WiFi SSID (EXACT NAME)
const char* password = "Harsh@12345";              // WiFi password
const char* serverUrl = "http://10.194.49.55:8000/api/sensor-data";  // CHANGE THIS

// ===== Sensor Configuration =====
#define DHTPIN 4              // DHT11 data pin (GPIO4)
#define DHTTYPE DHT11
#define ACS712_PIN 32         // ACS712 analog input (GPIO32)
#define BAUD_RATE 115200

// ===== ACS712 Calibration =====
#define ACS712_SENSITIVITY 0.185  // mV/A for 5A model (0.066 for 30A)
#define ACS712_VREF 1.8           // Midpoint voltage (0A reference)

// Sensor initialization
DHT dht(DHTPIN, DHTTYPE);
WiFiClient wifiClient;
HTTPClient http;

// Timing variables
unsigned long lastReadTime = 0;
unsigned long lastSendTime = 0;
unsigned long lastWiFiCheck = 0;

const unsigned long SAMPLE_INTERVAL = 1000;    // Read sensor every 1s
const unsigned long SEND_INTERVAL = 5000;      // Send to server every 5s
const unsigned long WIFI_CHECK_INTERVAL = 30000; // Check WiFi every 30s

// Ring buffer for sensor readings
#define BUFFER_SIZE 10
struct SensorReading {
  float temp;
  float humidity;
  float current;
  unsigned long timestamp;
  bool valid;
};

SensorReading readings[BUFFER_SIZE];
int readIndex = 0;

// Connection status tracking
bool lastWiFiStatus = false;
int failCount = 0;

void setup() {
  Serial.begin(BAUD_RATE);
  delay(1000);
  
  Serial.println("\n\n╔════════════════════════════════════╗");
  Serial.println("║   ESP32 ACMGS Sensor Module v2.0   ║");
  Serial.println("║   Fixed WiFi + Sensor Integration   ║");
  Serial.println("╚════════════════════════════════════╝");
  
  // Initialize buffer
  for (int i = 0; i < BUFFER_SIZE; i++) {
    readings[i].valid = false;
  }
  
  // Initialize DHT11
  Serial.println("\n[SETUP] Initializing DHT11 sensor...");
  dht.begin();
  delay(1000);  // Give DHT time to warm up
  Serial.println("✓ DHT11 initialized");
  
  // Initialize ADC
  Serial.println("[SETUP] Configuring ACS712 ADC...");
  analogSetWidth(12);              // 12-bit (0-4095)
  analogSetAttenuation(ADC_11db);  // 0-3.6V range
  Serial.println("✓ ACS712 ADC initialized");
  
  // Test ADC readings
  testADC();
  
  // Connect WiFi
  Serial.println("[SETUP] Initializing WiFi...");
  connectToWiFi();
  
  Serial.println("\n╔════════════════════════════════════╗");
  Serial.println("║       Setup Complete - Running      ║");
  Serial.println("╚════════════════════════════════════╝\n");
}

void loop() {
  // Maintain WiFi connection
  if (millis() - lastWiFiCheck >= WIFI_CHECK_INTERVAL) {
    lastWiFiCheck = millis();
    maintainWiFi();
  }
  
  // Read sensors every 1 second
  if (millis() - lastReadTime >= SAMPLE_INTERVAL) {
    lastReadTime = millis();
    readSensors();
  }
  
  // Send averaged data every 5 seconds
  if (millis() - lastSendTime >= SEND_INTERVAL) {
    lastSendTime = millis();
    if (WiFi.status() == WL_CONNECTED) {
      sendDataToServer();
    }
  }
  
  // Small delay to prevent watchdog timeout
  delay(10);
}

// ===================== WiFi Management =====================

void connectToWiFi() {
  Serial.println("╭─ WiFi Connection ─────────────────");
  Serial.print("  SSID: ");
  Serial.println(ssid);
  Serial.print("  Scanning for network...");
  
  // Disconnect any previous connection
  WiFi.disconnect(true);  // true = turn off radio
  delay(500);
  
  // Set WiFi to station mode
  WiFi.mode(WIFI_STA);
  delay(100);
  
  // Scan for network
  int n = WiFi.scanNetworks();
  boolean found = false;
  
  Serial.print(" Found ");
  Serial.print(n);
  Serial.println(" networks");
  
  for (int i = 0; i < n; i++) {
    if (strcmp(WiFi.SSID(i).c_str(), ssid) == 0) {
      found = true;
      int rssi = WiFi.RSSI(i);
      Serial.print("  ✓ Network found: ");
      Serial.print(WiFi.SSID(i));
      Serial.print(" (");
      Serial.print(rssi);
      Serial.println(" dBm)");
      break;
    }
  }
  
  if (!found) {
    Serial.print("  ✗ Network '");
    Serial.print(ssid);
    Serial.println("' NOT FOUND!");
    Serial.println("  Available networks:");
    for (int i = 0; i < min(n, 10); i++) {
      Serial.print("    - ");
      Serial.println(WiFi.SSID(i));
    }
  }
  
  // Attempt connection
  Serial.print("  Connecting");
  WiFi.begin(ssid, password);
  
  int attempts = 0;
  const int MAX_ATTEMPTS = 40;
  
  while (WiFi.status() != WL_CONNECTED && attempts < MAX_ATTEMPTS) {
    delay(500);
    Serial.print(".");
    attempts++;
    
    // Check if stuck
    if (attempts == 20) {
      Serial.println("\n  ⚠ Connection slow, retrying...");
      WiFi.begin(ssid, password);
    }
  }
  
  Serial.println();
  
  if (WiFi.status() == WL_CONNECTED) {
    lastWiFiStatus = true;
    failCount = 0;
    
    Serial.println("╭─ WiFi Connected ──────────────────");
    Serial.print("  IP Address: ");
    Serial.println(WiFi.localIP());
    Serial.print("  Signal Strength: ");
    Serial.print(WiFi.RSSI());
    Serial.println(" dBm");
    Serial.println("╰────────────────────────────────────");
  } else {
    lastWiFiStatus = false;
    
    Serial.println("╭─ WiFi Connection FAILED ──────────");
    wl_status_t status = WiFi.status();
    Serial.print("  Status Code: ");
    Serial.println(status);
    switch (status) {
      case WL_NO_SSID_AVAIL:
        Serial.println("  Reason: SSID not found");
        Serial.println("  Action: Check WiFi name (SSID)");
        break;
      case WL_CONNECT_FAILED:
        Serial.println("  Reason: Connection failed");
        Serial.println("  Action: Check password");
        break;
      case WL_DISCONNECTED:
        Serial.println("  Reason: Disconnected");
        Serial.println("  Action: Will retry automatically");
        break;
      default:
        Serial.println("  Reason: Unknown error");
        break;
    }
    Serial.println("╰────────────────────────────────────");
  }
}

void maintainWiFi() {
  wl_status_t status = WiFi.status();
  
  if (status != WL_CONNECTED) {
    failCount++;
    
    if (failCount == 1) {
      Serial.println("⚠ WiFi disconnected, attempting reconnect...");
      connectToWiFi();
    } else if (failCount > 5) {
      Serial.println("⚠ Multiple WiFi failures, full reset...");
      WiFi.disconnect(true);
      delay(1000);
      connectToWiFi();
      failCount = 0;
    }
  } else {
    failCount = 0;
  }
}

// ===================== Sensor Reading =====================

void testADC() {
  Serial.println("[TEST] ACS712 ADC sampling...");
  Serial.print("  10 samples: ");
  
  float sum = 0;
  for (int i = 0; i < 10; i++) {
    int raw = analogRead(ACS712_PIN);
    float voltage = (raw / 4095.0) * 3.6;
    Serial.print(raw);
    if (i < 9) Serial.print(", ");
    sum += raw;
  }
  Serial.println();
  
  float avg = sum / 10;
  Serial.print("  Average: ");
  Serial.print((int)avg);
  Serial.print(" (should be ~2048, voltage: ");
  Serial.print((avg / 4095.0) * 3.6, 2);
  Serial.println("V)");
  
  if (avg < 1500 || avg > 2500) {
    Serial.println("  ⚠ WARNING: ADC reading seems wrong!");
    Serial.println("     Check ACS712 wiring to GPIO32");
    Serial.println("     Check 5V power to ACS712");
  } else {
    Serial.println("  ✓ ADC looks good!");
  }
}

void readSensors() {
  // Read DHT11
  float humidity = dht.readHumidity();
  float temperature = dht.readTemperature();
  
  // Check for sensor errors
  if (isnan(humidity) || isnan(temperature)) {
    Serial.println("⚠ DHT11 read error");
    readings[readIndex].valid = false;
    readIndex = (readIndex + 1) % BUFFER_SIZE;
    return;
  }
  
  // Validate values
  if (temperature < -20 || temperature > 80) {
    Serial.print("⚠ Temperature out of range: ");
    Serial.println(temperature);
    readings[readIndex].valid = false;
    readIndex = (readIndex + 1) % BUFFER_SIZE;
    return;
  }
  
  // Read current
  float current = readCurrentRMS(8);
  
  // Store reading
  readings[readIndex].temp = temperature;
  readings[readIndex].humidity = humidity;
  readings[readIndex].current = current;
  readings[readIndex].timestamp = millis();
  readings[readIndex].valid = true;
  
  // Print current reading
  static int printCounter = 0;
  if (++printCounter >= 5) {  // Print every 5 readings (every ~5s)
    printCounter = 0;
    Serial.print("[");
    Serial.print(millis() / 1000);
    Serial.print("s] T:");
    Serial.print(temperature, 1);
    Serial.print("°C H:");
    Serial.print(humidity, 0);
    Serial.print("% I:");
    Serial.print(current, 3);
    Serial.print("A ");
    Serial.print(readIndex + 1);
    Serial.print("/");
    Serial.println(BUFFER_SIZE);
  }
  
  readIndex = (readIndex + 1) % BUFFER_SIZE;
}

float readCurrentRMS(int samples) {
  float sumSquares = 0;
  
  for (int i = 0; i < samples; i++) {
    int rawADC = analogRead(ACS712_PIN);
    
    // Convert ADC to voltage (0-4095 = 0-3.6V)
    float voltage = (rawADC / 4095.0) * 3.6;
    
    // Convert to current
    // ACS712: 1.8V = 0A, 0.185V per Ampere
    float current = (voltage - ACS712_VREF) / ACS712_SENSITIVITY;
    
    // RMS calculation
    sumSquares += (current * current);
    
    delayMicroseconds(50);
  }
  
  float rms = sqrt(sumSquares / samples);
  
  // Filter noise below 0.05A
  if (rms < 0.05) {
    rms = 0.0;
  }
  
  return rms;
}

// ===================== Server Communication =====================

void sendDataToServer() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("✗ WiFi not connected");
    return;
  }
  
  // Calculate averages from valid readings
  float sumTemp = 0, sumHumidity = 0, sumCurrent = 0;
  int validCount = 0;
  
  for (int i = 0; i < BUFFER_SIZE; i++) {
    if (readings[i].valid) {
      sumTemp += readings[i].temp;
      sumHumidity += readings[i].humidity;
      sumCurrent += readings[i].current;
      validCount++;
    }
  }
  
  if (validCount == 0) {
    Serial.println("✗ No valid readings to send");
    return;
  }
  
  float avgTemp = sumTemp / validCount;
  float avgHumidity = sumHumidity / validCount;
  float avgCurrent = sumCurrent / validCount;
  
  // Build JSON
  StaticJsonDocument<256> doc;
  doc["temperature"] = avgTemp;
  doc["humidity"] = avgHumidity;
  doc["current"] = avgCurrent;
  doc["timestamp"] = millis();
  doc["rssi"] = WiFi.RSSI();
  doc["ip"] = WiFi.localIP().toString();
  
  String payload;
  serializeJson(doc, payload);
  
  // Send HTTP POST
  http.begin(wifiClient, serverUrl);
  http.addHeader("Content-Type", "application/json");
  http.setTimeout(3000);
  
  Serial.print("→ POST [");
  Serial.print(validCount);
  Serial.print(" samples] ");
  
  int code = http.POST(payload);
  
  if (code > 0) {
    Serial.print("✓ HTTP ");
    Serial.println(code);
  } else {
    Serial.print("✗ Error: ");
    Serial.println(http.errorToString(code).c_str());
  }
  
  http.end();
}

