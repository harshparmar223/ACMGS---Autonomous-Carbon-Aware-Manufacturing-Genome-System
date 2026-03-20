"""
ESP32 Integration Test Suite
Tests the real-time sensor data pipeline with ACMGS
"""

import asyncio
import aiohttp
import json
from datetime import datetime

# Server URL
SERVER_URL = "http://localhost:8000"

async def test_health():
    """Test server health endpoint"""
    print("\n" + "="*60)
    print("TEST 1: Server Health Check")
    print("="*60)
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{SERVER_URL}/api/health") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print(f"✓ Health Check: Status {resp.status}")
                    print(f"  Status: {data.get('status')}")
                    print(f"  Buffer size: {data.get('buffer_size')}")
                    return True
                else:
                    print(f"✗ Health Check failed: Status {resp.status}")
                    return False
    except Exception as e:
        print(f"✗ Connection error: {e}")
        return False

async def test_latest_data():
    """Test latest sensor data endpoint"""
    print("\n" + "="*60)
    print("TEST 2: Fetch Latest Sensor Data")
    print("="*60)
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{SERVER_URL}/api/latest") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print(f"✓ Latest Data Retrieved:")
                    print(f"  Temperature: {data.get('temperature', 'N/A')}°C")
                    print(f"  Humidity: {data.get('humidity', 'N/A')}%")
                    print(f"  Current: {data.get('current', 'N/A')}A")
                    print(f"  Timestamp: {data.get('timestamp', 'N/A')}")
                    return True
                else:
                    print(f"✗ Failed: Status {resp.status}")
                    return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

async def test_stats():
    """Test statistics endpoint"""
    print("\n" + "="*60)
    print("TEST 3: Fetch Statistics")
    print("="*60)
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{SERVER_URL}/api/stats") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print(f"✓ Stats Retrieved:")
                    print(f"  Readings: {data.get('readings', 'N/A')}")
                    stats = data.get('stats', {})
                    if stats:
                        print(f"  Temperature - Avg: {stats.get('temperature', {}).get('mean', 'N/A'):.2f}°C")
                        print(f"  Current - Avg: {stats.get('current', {}).get('mean', 'N/A'):.3f}A")
                    return True
                else:
                    print(f"✗ Failed: Status {resp.status}")
                    return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

async def test_sensor_data_format():
    """Test sending valid sensor data"""
    print("\n" + "="*60)
    print("TEST 4: Sensor Data Format Validation")
    print("="*60)
    
    import time
    test_data = {
        "temperature": 23.5,
        "humidity": 45.0,
        "current": 4.75,
        "timestamp": int(time.time() * 1000),  # milliseconds
        "rssi": -60,
        "ip": "10.191.49.147"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{SERVER_URL}/api/sensor-data",
                json=test_data,
                headers={"Content-Type": "application/json"}
            ) as resp:
                if resp.status == 200:
                    response = await resp.json()
                    print(f"✓ Test data accepted: Status {resp.status}")
                    print(f"  Temperature: {response.get('temperature')}°C")
                    print(f"  Current: {response.get('current')}A")
                    return True
                else:
                    print(f"✗ Test data rejected: Status {resp.status}")
                    text = await resp.text()
                    print(f"  Error: {text[:200]}")
                    return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

async def test_websocket_connection():
    """Test WebSocket connection"""
    print("\n" + "="*60)
    print("TEST 5: WebSocket Real-Time Streaming")
    print("="*60)
    
    try:
        async with aiohttp.ClientSession() as session:
            ws_url = SERVER_URL.replace("http", "ws") + "/ws"
            try:
                async with session.ws_connect(ws_url, timeout=aiohttp.ClientTimeout(total=5)) as ws:
                    print(f"✓ WebSocket connected: {ws_url}")
                    
                    # Wait for 2 messages with timeout
                    messages_received = 0
                    print("  Waiting for real-time data...")
                    
                    try:
                        async with asyncio.timeout(5):
                            async for msg in ws:
                                if msg.type == aiohttp.WSMsgType.TEXT:
                                    data = json.loads(msg.data)
                                    messages_received += 1
                                    
                                    if data.get('type') == 'init':
                                        print(f"  [INIT] Received buffer with data")
                                    else:
                                        print(f"  [{messages_received}] {data.get('temperature', 'N/A')}°C, "
                                              f"{data.get('current', 'N/A')}A")
                                    
                                    if messages_received >= 1:
                                        break
                                elif msg.type == aiohttp.WSMsgType.ERROR:
                                    print(f"✗ WebSocket error")
                                    return False
                    except asyncio.TimeoutError:
                        pass
                    
                    if messages_received > 0:
                        print(f"✓ Received {messages_received} real-time message(s)")
                        return True
                    else:
                        print(f"✓ WebSocket connection established (no messages yet)")
                        return True
            except (aiohttp.ClientConnectorError, ConnectionRefusedError) as e:
                print(f"⚠ Could not connect to WebSocket: {e}")
                return False
                
    except Exception as e:
        print(f"✗ WebSocket error: {e}")
        return False

async def run_all_tests():
    """Run all tests"""
    print("\n╔════════════════════════════════════════════════════════════╗")
    print("║     ACMGS ESP32 Integration Test Suite                   ║")
    print(f"║     {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}                                  ║")
    print("╚════════════════════════════════════════════════════════════╝")
    
    results = {}
    
    # Run tests
    results['health'] = await test_health()
    results['latest'] = await test_latest_data()
    results['stats'] = await test_stats()
    results['format'] = await test_sensor_data_format()
    results['websocket'] = await test_websocket_connection()
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! System is operational.")
    else:
        print(f"\n⚠ {total - passed} test(s) failed. Check server logs.")
    
    print("="*60 + "\n")

if __name__ == "__main__":
    asyncio.run(run_all_tests())
