# Arduino Sensor Integration - Quick Start

## What You Now Have

✓ **Arduino Sketch** (`arduino_sensor_sketch.ino`)
  - Reads current from ACS712 sensor
  - Reads temperature & humidity from DHT11 sensor
  - Sends JSON data via serial port at 1 reading/second

✓ **Python Modules** (`src/arduino/`)
  - `sensor_reader.py` - Low-level serial communication
  - `integrator.py` - High-level data integration & analysis
  - Real-time logging to CSV
  - Statistics calculation
  - Power estimation
  - Data validation

✓ **Documentation** (`ARDUINO_SETUP.md`)
  - Complete hardware wiring guide
  - Software setup instructions
  - Calibration steps
  - Troubleshooting

✓ **Test Script** (`test_arduino_integration.py`)
  - Verify connection
  - Collect test data
  - Display statistics

---

## Getting Started in 5 Minutes

### Step 1: Upload Arduino Code
1. Open Arduino IDE
2. Go to File → Open → `arduino_sensor_sketch.ino`
3. Click Upload (Ctrl+U)
4. Open Serial Monitor (Ctrl+Shift+M) - should see JSON data

### Step 2: Wire Sensors
See detailed wiring in `ARDUINO_SETUP.md` or run test script

**ACS712:** A0 (current)  
**DHT11:** D2 (temperature & humidity)

### Step 3: Install Python Dependencies
```bash
pip install pyserial pandas
```

### Step 4: Run Test
```bash
python test_arduino_integration.py --duration 30
```

---

## Usage Examples

### Basic Reading
```python
from src.arduino.sensor_reader import ArduinoSensorReader

reader = ArduinoSensorReader(port="COM3")
reader.connect()

data = reader.read_sensor_data()
print(f"Temp: {data['temp']}°C, Current: {data['current']}A")

reader.disconnect()
```

### Real-Time Integration (Recommended)
```python
from src.arduino.integrator import RealTimeDataIntegrator

with RealTimeDataIntegrator(arduino_port="COM3") as integrator:
    reading = integrator.get_latest_reading()
    stats = integrator.get_statistics(window_size=60)
    power = integrator.estimate_power_consumption(voltage=230.0)
    
    print(f"Current avg: {stats['current']['avg']:.3f}A")
    print(f"Power: {power['power_avg_W']:.2f}W")
```

### Continuous Data Logging
```python
from src.arduino.sensor_reader import ArduinoSensorReader, SensorDataLogger

reader = ArduinoSensorReader(port="COM3")
logger = SensorDataLogger(log_dir="data/real_time")

reader.connect()
csv_file = logger.start_logging()

for data in reader.read_continuous(duration_seconds=300):
    logger.log_data(data)

logger.stop_logging()
reader.disconnect()
```

---

## Finding Your Arduino Port

**Windows:**
```powershell
Get-WmiObject Win32_SerialPort | Select-Object Name
```

**Linux/Mac:**
```bash
ls /dev/tty*
```

---

## Common Issues & Fixes

| Issue | Fix |
|-------|-----|
| Port not found | Check Device Manager / `ls /dev/tty*` |
| Garbled characters | Ensure baud rate is 9600 everywhere |
| DHT11 errors | Check power supply, add 10kΩ pull-up resistor |
| Wrong current readings | Recalibrate ACS712 sensitivity constant |

See `ARDUINO_SETUP.md` for detailed troubleshooting

---

## Files Created

```
├── arduino_sensor_sketch.ino          # Arduino firmware
├── ARDUINO_SETUP.md                   # Full documentation
├── test_arduino_integration.py        # Test & verification script
├── requirements.txt                   # Updated with pyserial
└── src/arduino/
    ├── __init__.py
    ├── sensor_reader.py               # Serial communication
    └── integrator.py                  # Data integration
```

---

## Data Format

**Arduino sends JSON:**
```json
{"temp":25.30,"humidity":45.20,"current":2.150}
```

**Python logs to CSV:**
```csv
timestamp,temperature,humidity,current
2024-03-20T14:30:45.123456,25.30,45.20,2.150
```

---

## Next Steps

1. ✓ Upload Arduino code
2. ✓ Install Python dependencies (`pip install -r requirements.txt`)
3. ✓ Connect sensors to Arduino
4. ✓ Run test script to verify
5. → Integrate with your ACMGS optimization modules
6. → Use real-time power data in carbon scheduling

---

**Questions?** See `ARDUINO_SETUP.md` for comprehensive guide.
