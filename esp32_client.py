"""
Client for ESP32 real-time server
Test and demonstrate streaming data processing
"""

import asyncio
import aiohttp
import json
import websockets
from typing import Dict, List, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ESP32ServerClient:
    """Client for connecting to ESP32 real-time server"""
    
    def __init__(self, base_url: str = "http://localhost:8001"):
        """
        Initialize client.
        
        Args:
            base_url: Server URL (default localhost:8001)
        """
        self.base_url = base_url
        self.ws_url = base_url.replace("http://", "ws://") + "/ws"
        self.session = None
    
    async def connect(self):
        """Create HTTP session"""
        self.session = aiohttp.ClientSession()
        logger.info(f"Connected to {self.base_url}")
    
    async def disconnect(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
    
    async def health_check(self) -> Dict:
        """Check server health"""
        async with self.session.get(f"{self.base_url}/api/health") as resp:
            return await resp.json()
    
    async def get_latest(self) -> Dict:
        """Get latest sensor reading"""
        async with self.session.get(f"{self.base_url}/api/latest") as resp:
            return await resp.json()
    
    async def get_stats(self, window: int = 60) -> Dict:
        """Get statistics"""
        async with self.session.get(
            f"{self.base_url}/api/stats?window={window}"
        ) as resp:
            return await resp.json()
    
    async def predict_energy(self, duration_hours: float = 1.0) -> Dict:
        """Predict energy consumption"""
        async with self.session.post(
            f"{self.base_url}/api/predict?duration_hours={duration_hours}"
        ) as resp:
            return await resp.json()
    
    async def stream_data(self, callback=None):
        """
        Stream real-time data via WebSocket.
        
        Args:
            callback: Function called with each data update
        """
        try:
            async with websockets.connect(self.ws_url) as websocket:
                logger.info("WebSocket connected")
                
                while True:
                    data = await websocket.recv()
                    data_dict = json.loads(data)
                    
                    if callback:
                        await callback(data_dict)
                    else:
                        logger.info(f"Received: {data_dict}")
        
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
    
    async def __aenter__(self):
        """Context manager entry"""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        await self.disconnect()


class ESP32StreamProcessor:
    """Process ESP32 data stream and trigger actions"""
    
    def __init__(self, client: ESP32ServerClient):
        self.client = client
        self.callbacks: Dict[str, List[callable]] = {
            'high_power': [],
            'high_temp': [],
            'prediction': [],
            'anomaly': []
        }
    
    def on(self, event: str, callback: callable):
        """Subscribe to event"""
        if event in self.callbacks:
            self.callbacks[event].append(callback)
    
    async def process_update(self, data: Dict):
        """Process incoming data update"""
        try:
            # Check for alerts
            if 'alert' in data:
                alert_level = data.get('alert_level', 'info')
                
                if alert_level == 'critical':
                    for callback in self.callbacks['high_power']:
                        await self._call(callback, data)
            
            # Check sensor readings
            sensor = data.get('sensor', {})
            if sensor.get('temperature', 0) > 60:
                for callback in self.callbacks['high_temp']:
                    await self._call(callback, data)
            
            # Check prediction
            prediction = data.get('prediction', {})
            if prediction:
                for callback in self.callbacks['prediction']:
                    await self._call(callback, prediction)
        
        except Exception as e:
            logger.warning(f"Error processing update: {e}")
    
    @staticmethod
    async def _call(callback, data):
        """Call callback (handle sync/async)"""
        if asyncio.iscoroutinefunction(callback):
            await callback(data)
        else:
            callback(data)


# Example test script
async def test_server(server_url: str = "http://localhost:8001"):
    """Test ESP32 server"""
    
    async with ESP32ServerClient(base_url=server_url) as client:
        # Check health
        print("=== Health Check ===")
        health = await client.health_check()
        print(json.dumps(health, indent=2))
        
        # Get latest reading
        print("\n=== Latest Reading ===")
        try:
            latest = await client.get_latest()
            print(json.dumps(latest, indent=2))
        except Exception as e:
            print(f"Error: {e}")
        
        # Get statistics
        print("\n=== Statistics (last 60 readings) ===")
        try:
            stats = await client.get_stats(window=60)
            print(json.dumps(stats, indent=2))
        except Exception as e:
            print(f"Error: {e}")
        
        # Predict energy
        print("\n=== Energy Prediction (1 hour) ===")
        try:
            prediction = await client.predict_energy(duration_hours=1.0)
            print(json.dumps(prediction, indent=2))
        except Exception as e:
            print(f"Error: {e}")
        
        # Stream data
        print("\n=== Real-Time Stream (10 seconds) ===")
        
        processor = ESP32StreamProcessor(client)
        
        # Define callbacks
        async def on_high_power(data):
            print(f"🔴 HIGH POWER ALERT: {data}")
        
        async def on_high_temp(data):
            temp = data['sensor']['temperature']
            print(f"🟠 HIGH TEMPERATURE: {temp}°C")
        
        async def on_prediction(prediction):
            print(f"📊 Prediction: Energy={prediction['energy_predicted']:.4f}kWh, "
                  f"Score={prediction['optimization_score']:.2f}")
        
        processor.on('high_power', on_high_power)
        processor.on('high_temp', on_high_temp)
        processor.on('prediction', on_prediction)
        
        # Stream with timeout
        try:
            stream_task = asyncio.create_task(
                client.stream_data(callback=processor.process_update)
            )
            await asyncio.wait_for(stream_task, timeout=10.0)
        except asyncio.TimeoutError:
            print("Stream timeout (expected)")
        except Exception as e:
            logger.warning(f"Stream error: {e}")


# Simulate ESP32 data for testing
async def simulate_esp32_data(server_url: str = "http://localhost:8001", 
                             duration_minutes: int = 5):
    """Simulate ESP32 sending data to server"""
    
    import aiohttp
    
    async with aiohttp.ClientSession() as session:
        import random
        import time
        
        print(f"Simulating ESP32 for {duration_minutes} minutes...")
        start_time = time.time()
        duration_seconds = duration_minutes * 60
        
        count = 0
        while time.time() - start_time < duration_seconds:
            # Simulate sensor readings with slight variation
            temp = 25 + random.gauss(0, 2)
            humidity = 45 + random.gauss(0, 5)
            current = 20 + random.gauss(0, 5)
            
            data = {
                "temperature": temp,
                "humidity": humidity,
                "current": current,
                "timestamp": int(time.time() * 1000),
                "rssi": -50 + random.randint(-20, 0),
                "ip": "192.168.1.100"
            }
            
            try:
                async with session.post(
                    f"{server_url}/api/sensor-data",
                    json=data
                ) as resp:
                    count += 1
                    if count % 10 == 0:
                        response = await resp.json()
                        print(f"[{count}] Sent: T={temp:.1f}°C, I={current:.1f}A | "
                              f"Response: {response['prediction']['recommendation']}")
            
            except Exception as e:
                print(f"Error sending data: {e}")
            
            await asyncio.sleep(1)  # Send every second
        
        print(f"Simulation complete. Sent {count} readings.")


if __name__ == "__main__":
    import sys
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    if len(sys.argv) > 1 and sys.argv[1] == "simulate":
        # Run simulation
        asyncio.run(simulate_esp32_data(duration_minutes=5))
    else:
        # Test server
        asyncio.run(test_server())
