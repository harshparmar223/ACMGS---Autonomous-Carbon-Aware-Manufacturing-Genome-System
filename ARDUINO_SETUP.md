# Arduino Sensor Integration Guide

## Hardware Setup

### Components Required
- **Arduino Uno/Nano/Mega**
- **ACS712 Current Sensor** (5A or 30A model)
- **DHT11 Temperature & Humidity Sensor**
- **Jumper wires**
- **USB cable** (for Arduino programming & power)
- Optional: **10kΩ pull-up resistor** (for DHT11)

### Wiring Diagram

#### ACS712 Current Sensor
```
ACS712 Pin  →  Arduino Pin
VCC (+5V)   →  5V
GND         →  GND
OUT         →  A0 (Analog 0)
```

#### DHT11 Temperature/Humidity Sensor
```
DHT11 Pin   →  Arduino Pin
VCC (+5V)   →  5V
GND         →  GND
DATA        →  D2 (Digital 2)
            →  10kΩ resistor (optional, between DATA and VCC)
```

### Arduino Pinout Summary
```
A0  - ACS712 OUT (Current)
D2  - DHT11 DATA (Temperature & Humidity)
5V  - Power for both sensors
GND - Common ground
```

## Software Setup

### 1. Arduino IDE Installation
- Download from [arduino.cc](https://www.arduino.cc/en/software)
- Install the board (Tools → Board → Arduino AVR Boards)

### 2. Required Libraries
Install in Arduino IDE (Sketch → Include Library → Manage Libraries):
- **DHT sensor library** by Adafruit
- **Adafruit Unified Sensor Library** (dependency for DHT)

### 3. Upload Arduino Sketch
1. Open Arduino IDE
2. Copy contents of `arduino_sensor_sketch.ino`
3. Paste into Arduino IDE
4. Select Board: Tools → Board → Arduino Uno (or your board)
5. Select Port: Tools → Port → COM3 (or your port)
6. Click Upload (or Ctrl+U)

### 4. Verify Serial Connection
1. Tools → Serial Monitor
2. Set baud rate to 9600
3. You should see JSON data like:
```json
{"temp":25.30,"humidity":45.20,"current":2.150}
```

## Python Integration

### 1. Install Dependencies
```bash
pip install pyserial pandas
```

### 2. Basic Usage

#### Simple Reading
```python
from src.arduino.sensor_reader import ArduinoSensorReader

reader = ArduinoSensorReader(port="COM3", baudrate=9600)
reader.connect()

# Read one sample
data = reader.read_sensor_data()
print(f"Temperature: {data['temp']}°C")
print(f"Humidity: {data['humidity']}%")
print(f"Current: {data['current']}A")

reader.disconnect()
```

#### Continuous Reading with Logging
```python
from src.arduino.sensor_reader import ArduinoSensorReader, SensorDataLogger

reader = ArduinoSensorReader(port="COM3")
logger = SensorDataLogger(log_dir="data/real_time")

reader.connect()
csv_file = logger.start_logging("my_measurements")

try:
    for data in reader.read_continuous(duration_seconds=300):
        print(f"Temp: {data['temp']:.2f}°C | Current: {data['current']:.3f}A")
        logger.log_data(data)
finally:
    logger.stop_logging()
    reader.disconnect()
```

#### Real-Time Integration
```python
from src.arduino.integrator import RealTimeDataIntegrator, SensorDataValidator

with RealTimeDataIntegrator(arduino_port="COM3") as integrator:
    # Collect data for 60 seconds
    import time
    start = time.time()
    
    while time.time() - start < 60:
        reading = integrator.get_latest_reading()
        if reading:
            is_valid, error = SensorDataValidator.validate_reading(reading)
            if is_valid:
                print(f"Current: {reading['current']:.3f}A")
    
    # Get statistics
    stats = integrator.get_statistics(window_size=60)
    print(f"Average Current: {stats['current']['avg']:.3f}A")
    
    # Estimate power (assuming 230V AC supply)
    power = integrator.estimate_power_consumption(voltage=230.0)
    print(f"Power: {power['power_avg_W']:.2f}W")
```

### 3. Finding Your Serial Port

**Windows (PowerShell):**
```powershell
Get-WmiObject Win32_SerialPort | Select-Object Name, Description
```

**Linux/Mac:**
```bash
ls /dev/tty* | grep USB
# or
ls /dev/ttyACM*
```

## Configuration & Calibration

### ACS712 Calibration
The sketch uses **0.185 mV/A** (5A model). Adjust for different models:
- **5A model**: 0.185 mV/A
- **30A model**: 0.066 mV/A
- **20A model**: 0.100 mV/A

Edit `arduino_sensor_sketch.ino`:
```cpp
#define ACS712_SENSITIVITY 0.185  // Change this value
```

### DHT11 Specifications
- Temperature: -10 to +50°C (±2°C)
- Humidity: 20-90% RH (±5%)
- Reading interval: 1 second minimum

## Integration with ACMGS System

### Option 1: Real-Time Energy Monitoring
```python
# In your optimization loop
from src.arduino.integrator import RealTimeDataIntegrator

integrator = RealTimeDataIntegrator(arduino_port="COM3")
integrator.start()

# During optimization
current_reading = integrator.get_latest_reading()
power_estimate = integrator.estimate_power_consumption(voltage=230.0)

# Feed to optimizer
# ...

integrator.stop()
```

### Option 2: Log and Post-Process
```python
# Collect data first
# Then analyze with existing simulation modules
df = integrator.to_dataframe()
df.to_csv("data/real_time/measurements.csv", index=False)

# Use with your prediction module
from src.prediction.predictor import Predictor
predictor = Predictor()
# ... process real data
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Port not found" | Check COM port in Device Manager (Windows) or `ls /dev/tty*` (Linux) |
| Serial garbage characters | Ensure baud rate is 9600 in both Arduino and Python |
| DHT11 read failures | Add capacitor (100nF) between data and GND; use stable 5V supply |
| Incorrect current readings | Recalibrate ACS712 sensitivity; check zero-offset at 0A condition |
| Module not found | Ensure `src/arduino/__init__.py` exists and package is in PYTHONPATH |

## Real-Time Data Format

### JSON Output (from Arduino)
```json
{
  "temp": 25.30,
  "humidity": 45.20,
  "current": 2.150
}
```

### CSV Output (from Python Logger)
```
timestamp,temperature,humidity,current
2024-03-20T14:30:45.123456,25.30,45.20,2.150
2024-03-20T14:30:46.234567,25.31,45.19,2.151
```

## Support
For sensor documentation:
- **DHT11**: https://www.adafruit.com/product/386
- **ACS712**: https://www.allegromicro.com/en/products/sense/current-sensor-ics/zero-to-fifty-amp-integrated-conductor-amplifier-bipolar-hall-sensor/acs712

---
**Last Updated**: March 20, 2026
