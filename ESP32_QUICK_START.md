# ESP32 Real-Time Processing - Quick Start

## What's New

✅ **ESP32 Arduino Firmware** - WiFi sensor streaming  
✅ **Python Real-Time Server** - FastAPI with WebSocket streaming  
✅ **Real-Time Processing Engine** - Alert, energy, prediction, anomaly detection  
✅ **Client Library** - Async client for data & predictions  
✅ **Complete Documentation** - Wiring, setup, integration  

---

## 30-Minute Setup

### 1. Arduino IDE (5 min)

```
1. Download Arduino IDE (arduino.cc)
2. Preferences → Add ESP32 board URL:
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
3. Tools → Board Manager → Install "ESP32 by Espressif Systems"
4. Tools → Manage Libraries → Install:
   - DHT sensor library (Adafruit)
   - ArduinoJson (Benoit Blanchon)
```

### 2. Upload ESP32 Code (5 min)

```
1. Open: esp32_sensor_sketch.ino
2. Edit (3 lines):
   const char* ssid = "YOUR_SSID";
   const char* password = "YOUR_PASSWORD";
   const char* serverUrl = "http://192.168.1.100:8000/api/sensor-data";
3. Tools → Board → ESP32 Dev Module
4. Tools → Port → Select your COM port
5. Upload (Ctrl+U)
6. Tools → Serial Monitor (115200 baud) to verify
```

### 3. Wire Hardware (5 min)

```
ESP32:
  GPIO4  → DHT11 data pin
  GPIO32 → ACS712 output
  5V     → ACS712 VCC
  3.3V   → DHT11 VCC
  GND    → Both GND
```

### 4. Start Python Server (5 min)

```bash
# Install dependencies
pip install -r requirements.txt

# Start server
python esp32_server.py

# Should show:
# Starting ACMGS Real-Time ESP32 Server on http://0.0.0.0:8000
```

### 5. Test Connection (5 min)

```bash
# In another terminal, simulate ESP32 data
python esp32_client.py simulate

# In another terminal, monitor real-time stream
python esp32_client.py

# Or open browser: http://localhost:8000/docs
```

---

## Real-Time Data Flow

```
ESP32 (every 1s)
├─ Read ACS712 (current)
├─ Read DHT11 (temperature, humidity)
└─ Every 5s: Send JSON to server

Server (receive)
├─ FastAPI endpoint: POST /api/sensor-data
├─ Process through models
├─ Generate alerts
├─ Calculate predictions
└─ WebSocket broadcast to clients

Clients (real-time)
├─ Web dashboard
├─ Python clients
└─ Legacy systems
```

---

## Quick API Reference

### REST Endpoints

```bash
# Get latest reading
curl http://localhost:8000/api/latest

# Get statistics (last 60 readings)
curl http://localhost:8000/api/stats?window=60

# Predict energy for next hour
curl -X POST http://localhost:8000/api/predict?duration_hours=1

# Health check
curl http://localhost:8000/api/health

# API docs (interactive)
http://localhost:8000/docs
```

### Python Client

```python
import asyncio
from esp32_client import ESP32ServerClient

async def main():
    async with ESP32ServerClient() as client:
        latest = await client.get_latest()
        print(f"Temp: {latest['temperature']}°C")
        print(f"Current: {latest['current']}A")
        print(f"Power: {latest['power_watts']:.2f}W")

asyncio.run(main())
```

### Real-Time Processing

```python
from src.esp32.realtime_processor import (
    RealTimeDataProcessor,
    AlertEngine,
    EnergyEstimator
)

processor = RealTimeDataProcessor()
alerts = AlertEngine()
energy = EnergyEstimator()

# Process incoming ESP32 data
reading = {
    'temperature': 25.3,
    'humidity': 45.2,
    'current': 15.5,
}

processor.process_reading(reading)
alert_list = alerts.evaluate(reading)
power = energy.calculate_power(reading['current'])
```

---

## WebSocket Real-Time Streaming

```python
import asyncio
from esp32_client import ESP32ServerClient

async def stream():
    client = ESP32ServerClient()
    await client.connect()
    
    async def callback(data):
        print(f"Real-time update: {data}")
    
    await client.stream_data(callback=callback)

asyncio.run(stream())
```

---

## Integration Examples

### With Energy DNA Model

```python
from src.energy_dna.model import EnergyDNAModel
from src.esp32.realtime_processor import RealTimeDataProcessor

processor = RealTimeDataProcessor()
model = EnergyDNAModel()

# Collect real data
reading = {...}
processor.process_reading(reading)

# Get statistics for model
stats = processor.get_statistics()

# Encode genome with real data
encoded = model.encode(stats)
```

### With Optimizer

```python
from src.optimization.optimizer import Optimizer
from esp32_client import ESP32ServerClient

async def optimize_schedule():
    client = ESP32ServerClient()
    await client.connect()
    
    stats = await client.get_stats(window=60)
    
    optimizer = Optimizer()
    solution = optimizer.optimize(
        energy_constraint=stats['current']['mean'] * 230,
        carbon_limit=50.0
    )

asyncio.run(optimize_schedule())
```

### With Prediction

```python
from src.prediction.predictor import Predictor
from esp32_client import ESP32ServerClient

async def predict():
    client = ESP32ServerClient()
    await client.connect()
    
    latest = await client.get_latest()
    
    predictor = Predictor()
    prediction = predictor.predict({
        'current': latest['current'],
        'temperature': latest['temperature'],
        'humidity': latest['humidity']
    })

asyncio.run(predict())
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| ESP32 won't upload | Check COM port, select ESP32 board type |
| "WiFi connection loops" | Verify SSID/password are correct |
| "Connection refused" | Is server running? Check IP address |
| Zero current readings | Check ACS712 wiring and 5V supply |
| No data in server | Check ESP32 Serial Monitor for errors |

---

## File Structure

```
├── esp32_sensor_sketch.ino              # Upload to ESP32
├── esp32_server.py                      # Run on PC/Server
├── esp32_client.py                      # Test/monitor
├── src/esp32/
│   ├── __init__.py
│   └── realtime_processor.py            # Streaming processor
├── ESP32_SETUP.md                       # Full documentation
└── requirements.txt                     # pip install -r requirements.txt
```

---

## Next: Integration with ACMGS

Once data is flowing:

1. **Real-time Predictions**: Feed sensor data → prediction model
2. **Live Optimization**: Current load → optimize schedule
3. **Energy DNA**: Real data → update genome
4. **Carbon Scheduler**: Power metrics → adjust schedule
5. **Dashboard**: WebSocket → real-time visualization

---

## Support

- **Full docs**: See `ESP32_SETUP.md`
- **Examples**: See `examples_esp32_integration.py` (coming soon)
- **API docs**: `http://localhost:8000/docs` (when server running)

---

**Ready to stream real-time data!**

Start with: `python esp32_server.py` + upload `esp32_sensor_sketch.ino` to ESP32
