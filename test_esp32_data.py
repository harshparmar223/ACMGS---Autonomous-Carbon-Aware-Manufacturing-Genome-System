#!/usr/bin/env python3
"""
Test script to simulate ESP32 sensor data posting to server
"""
import requests
import time
import json
import random
from datetime import datetime

ESP32_SERVER = "http://localhost:8000"

def send_sensor_data():
    """Send simulated sensor data to ESP32 server"""
    
    # Simulate realistic sensor values
    temperature = round(random.uniform(20, 50), 1)
    humidity = round(random.uniform(30, 80), 1)
    current = round(random.uniform(5, 150), 2)
    
    # Current timestamp in milliseconds
    timestamp = int(time.time() * 1000)
    
    payload = {
        "temperature": temperature,
        "humidity": humidity,
        "current": current,
        "timestamp": timestamp,
        "rssi": -45,  # WiFi signal strength (dBm)
        "ip": "192.168.1.100"
    }
    
    try:
        print(f"\n{'='*60}")
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Sending ESP32 Data")
        print(f"{'='*60}")
        print(f"Temperature: {temperature}°C")
        print(f"Humidity:    {humidity}%")
        print(f"Current:     {current}A")
        print(f"Timestamp:   {timestamp}")
        
        response = requests.post(
            f"{ESP32_SERVER}/api/sensor-data",
            json=payload,
            timeout=5
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n[OK] SUCCESS")
            print(f"Response: {json.dumps(result, indent=2)}")
            
            # Show prediction results
            if "prediction" in result:
                pred = result["prediction"]
                print(f"\n[PREDICTION] AI Predictions:")
                print(f"  Energy Predicted: {pred.get('energy_predicted', 0):.2f}")
                print(f"  Carbon Impact:    {pred.get('carbon_impact', 0):.4f} kg CO2")
                print(f"  Optimization:     {pred.get('optimization_score', 0):.2f}")
                print(f"  Recommendation:   {pred.get('recommendation', 'N/A')}")
            
            # Show alerts
            if "alert" in result:
                print(f"\n[ALERT] {result['alert']}")
                print(f"   Level: {result.get('alert_level', 'unknown')}")
                
            return True
        else:
            print(f"[ERROR] FAILED")
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"[ERROR] CONNECTION ERROR")
        print(f"Could not connect to {ESP32_SERVER}")
        print(f"Is the server running?")
        return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def get_server_stats():
    """Get server statistics"""
    try:
        response = requests.get(f"{ESP32_SERVER}/api/stats?window=10", timeout=5)
        if response.status_code == 200:
            stats = response.json()
            print(f"\n[STATS] Server Statistics (last 10 readings):")
            print(json.dumps(stats, indent=2))
    except Exception as e:
        print(f"Could not get stats: {e}")

def get_server_health():
    """Check server health"""
    try:
        response = requests.get(f"{ESP32_SERVER}/api/health", timeout=5)
        if response.status_code == 200:
            health = response.json()
            print(f"\n[HEALTH] Server Health:")
            print(json.dumps(health, indent=2))
            return True
    except Exception as e:
        print(f"Server health check failed: {e}")
    return False

if __name__ == "__main__":
    print("\n" + "="*60)
    print("  ESP32 SENSOR DATA TEST SIMULATOR")
    print("="*60)
    
    # Check server health first
    if not get_server_health():
        print("\n[WARNING] Server is not responding. Please start the server first:")
        print("   python esp32_server.py")
        exit(1)
    
    # Send data every 2 seconds for demo
    print("\n[INFO] Starting continuous data stream...")
    print("Press Ctrl+C to stop\n")
    
    try:
        count = 0
        while True:
            count += 1
            success = send_sensor_data()
            
            if success:
                get_server_stats()
            
            print(f"\n[{count}/inf] Waiting 2 seconds before next push...")
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\n\n[OK] Stopped")
        print("="*60)
