## ESP32 WiFi Configuration Issues - Quick Fix

### ⚠️ Your Error
```
E (24450) wifi11s: invalid config, cannot set config
```

This happens when WiFi configuration fails. Here's the fix:

---

### ✅ **Solution 1: Check WiFi Credentials** (Most Common)

Edit these lines in `esp32_sensor_sketch.ino`:

```cpp
const char* ssid = "POCO M4 Pro 5G Harsh";        // Exact name from your WiFi
const char* password = "YOUR_ACTUAL_PASSWORD";     // Check password carefully
const char* serverUrl = "http://192.168.1.100:8000/api/sensor-data";  // Your PC IP
```

**⚠️ Important:**
- SSID must be EXACT (check capitalization & spaces)
- Password must be EXACT (case-sensitive)
- No trailing spaces in either field
- Max length: SSID 32 chars, Password 64 chars

---

### ✅ **Solution 2: Set Server IP Address**

Find your PC's IP address:

**Windows PowerShell:**
```powershell
ipconfig
```
Look for "IPv4 Address" under your active network (usually `192.168.x.x`)

**In the code:**
```cpp
const char* serverUrl = "http://192.168.1.X:8000/api/sensor-data";
// Replace 192.168.1.X with your actual IP
```

---

### ✅ **Solution 3: Updated Code**

The fixed `esp32_sensor_sketch.ino` now includes:
- ✓ Better WiFi disconnect/reconnect handling
- ✓ Improved error messages
- ✓ ADC diagnostics
- ✓ Better sensor error handling
- ✓ Timeout protection

**Just re-upload the fixed sketch** (it's already saved)

---

### 🔧 **Step-by-Step Upload**

1. **Open Arduino IDE**
2. **File → Open → esp32_sensor_sketch.ino**
3. **Edit these 3 lines:**
   ```cpp
   const char* ssid = "POCO M4 Pro 5G Harsh";
   const char* password = "YOUR_PASSWORD";  // Change this!
   const char* serverUrl = "http://192.168.1.XXX:8000/api/sensor-data";  // Change IP!
   ```
4. **Tools → Board → ESP32 Dev Module**
5. **Tools → Port → COM4** (adjust your port)
6. **Upload (Ctrl+U)**
7. **Tools → Serial Monitor (115200 baud)**

---

### 📊 **Expected Output (Serial Monitor)**

```
===== ESP32 Sensor Module =====
Testing ACS712 ADC... 2045, 2046, 2047, 2048, 2049 (should be ~2048 at 0A)
Connecting to WiFi: POCO M4 Pro 5G Harsh
....... ✓ WiFi connected!
  IP address: 192.168.1.105
  Signal strength: -45 dBm

Setup complete. Reading sensors...
[timestamp] Temp: 25.5°C | Humidity: 45.2% | Current: 0.150A | Samples: 1
[timestamp] Temp: 25.5°C | Humidity: 45.2% | Current: 0.142A | Samples: 2
→ Sending: {"temperature":25.5,"humidity":45.2,"current":0.145,...}
← Response code: 200
```

---

### ❌ **If Still Getting WiFi Error**

Try these in order:

1. **Restart ESP32:**
   - Unplug USB
   - Wait 5 seconds
   - Plug back in

2. **Use WiFi AP Mode to Debug:**
   ```cpp
   #include <WiFi.h>
   
   void setup() {
     Serial.begin(115200);
     
     // Scan WiFi networks
     Serial.println("Available WiFi networks:");
     int n = WiFi.scanNetworks();
     for (int i = 0; i < n; i++) {
       Serial.print(i + 1);
       Serial.print(": ");
       Serial.print(WiFi.SSID(i));
       Serial.print(" (");
       Serial.print(WiFi.RSSI(i));
       Serial.println("dBm)");
     }
   }
   
   void loop() {}
   ```

3. **Check WiFi Band:**
   - ESP32 only supports 2.4GHz
   - If your WiFi is 5GHz only, it won't connect
   - Check WiFi settings to ensure 2.4GHz is enabled

4. **Check Power Supply:**
   - ESP32 needs stable 5V
   - Poor power causes WiFi failures
   - Use good quality USB cable

---

### 🔧 **ADC Test Output Explanation**

```
Testing ACS712 ADC... 2045, 2046, 2047, 2048, 2049 (should be ~2048 at 0A)
```

- **Good**: Values around 2048 ± 10 (no load)
- **Bad**: Values like 0, 4095, or way off
  - Check ACS712 wiring to GPIO32
  - Check 5V power to ACS712

---

### 💡 **WiFi Connection Timeout**

If it loops "Connecting to WiFi..." more than 30 times:

1. Recheck SSID spelling
2. Check password is correct
3. Check WiFi network isn't hidden
4. Try turning WiFi off/on on your phone
5. Restart WiFi router

---

### 📝 **Password Checklist**

- [ ] Password is EXACT (copy-paste if possible)
- [ ] No spaces before/after password
- [ ] Correct capitalization
- [ ] No special characters that might need escaping
- [ ] Not longer than 64 characters

---

### ✅ **Quick Test Without Server**

To test WiFi without needing the Python server:

```cpp
const char* serverUrl = "http://192.168.1.1:8000/api/sensor-data";  // Dummy URL
// Just comment out sendDataToServer() in loop()
```

This will test WiFi and sensors without needing the server.

---

## Next: Start Server

Once WiFi connects successfully:

```bash
python esp32_server.py
```

Then data will flow!

---

**Need help?** Check the detailed guide in `ESP32_SETUP.md`
