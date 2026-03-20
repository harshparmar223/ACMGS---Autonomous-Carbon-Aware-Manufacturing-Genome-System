"""
ESP32 + ACMGS Integration Examples
Demonstrates real-time model inference with ESP32 sensor data
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

import asyncio
import logging
from datetime import datetime

# ACMGS modules
from esp32.realtime_processor import (
    RealTimeDataProcessor,
    AlertEngine,
    EnergyEstimator,
    ModelInference
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ===== Example 1: Real-time Energy Monitoring =====
async def example_energy_monitoring():
    """
    Monitor energy consumption in real-time with alerts.
    """
    print("\n" + "="*60)
    print("Example 1: Real-Time Energy Monitoring")
    print("="*60)
    
    processor = RealTimeDataProcessor(window_size=60)
    alert_engine = AlertEngine()
    estimator = EnergyEstimator()
    
    # Subscribe to alerts
    def on_alert(alert):
        print(f"🔴 ALERT: {alert}")
    
    processor.subscribe('alert', on_alert)
    
    # Simulate sensor readings
    test_readings = [
        {'temperature': 25.5, 'humidity': 45.0, 'current': 15.3},
        {'temperature': 25.6, 'humidity': 44.8, 'current': 15.5},
        {'temperature': 25.4, 'humidity': 45.2, 'current': 15.2},
        {'temperature': 30.2, 'humidity': 55.0, 'current': 45.0},  # High temp alert
        {'temperature': 35.5, 'humidity': 65.0, 'current': 65.0},  # Multiple alerts
    ]
    
    for i, reading in enumerate(test_readings):
        reading['timestamp'] = datetime.now().isoformat()
        
        # Process reading
        result = processor.process_reading(reading)
        
        # Check for alerts
        alerts = alert_engine.evaluate(reading, voltage=230.0)
        
        # Calculate energy
        power = estimator.calculate_power(reading['current'])
        energy_per_hour = estimator.calculate_energy(power, 60)
        carbon = estimator.estimate_carbon_emissions(energy_per_hour)
        cost = estimator.estimate_cost(energy_per_hour)
        
        print(f"\n[{i+1}] Reading: T={reading['temperature']}°C, I={reading['current']}A")
        print(f"    Power: {power:.2f}W | Energy/h: {energy_per_hour:.4f}kWh | "
              f"Carbon: {carbon:.4f}kg CO2 | Cost: ${cost:.4f}")
        
        if alerts:
            for alert in alerts:
                print(f"    ⚠ {alert['type']}: {alert['value']:.1f} > {alert['threshold']:.1f}")
    
    # Final statistics
    stats = processor.get_statistics()
    print(f"\nFinal Statistics:")
    print(f"  Avg Temperature: {stats['temperature']['mean']:.2f}°C ± {stats['temperature']['std']:.2f}")
    print(f"  Avg Current: {stats['current']['mean']:.3f}A ± {stats['current']['std']:.3f}")


# ===== Example 2: Real-time Prediction =====
async def example_prediction():
    """
    Predict energy consumption based on current reading.
    """
    print("\n" + "="*60)
    print("Example 2: Real-Time Energy Prediction")
    print("="*60)
    
    processor = RealTimeDataProcessor(window_size=60)
    inference = ModelInference()
    
    # Simulate readings
    readings_data = [
        {'temperature': 25.0, 'humidity': 45.0, 'current': 20.0},
        {'temperature': 25.1, 'humidity': 44.9, 'current': 20.5},
        {'temperature': 25.2, 'humidity': 45.1, 'current': 20.2},
        {'temperature': 25.0, 'humidity': 45.0, 'current': 20.1},
        {'temperature': 25.1, 'humidity': 44.9, 'current': 20.3},
    ]
    
    for reading in readings_data:
        reading['timestamp'] = datetime.now().isoformat()
        processor.process_reading(reading)
    
    # Get historical data
    buffer_data = list(processor.buffer)
    current_reading = buffer_data[-1]
    
    # Predict next hour
    prediction = await inference.predict_next_hour(current_reading, buffer_data)
    
    print(f"\nCurrent Reading: {current_reading}")
    print(f"\nPrediction for next hour:")
    print(f"  Average Current: {prediction['avg_current']:.3f}A")
    print(f"  Average Power: {prediction['power_watts']:.2f}W")
    print(f"  Predicted Energy: {prediction['energy_kwh']:.4f}kWh")
    print(f"  Confidence: {prediction['confidence']*100:.1f}%")
    
    # Estimate cost and carbon
    estimated_cost = prediction['energy_kwh'] * 0.15
    estimated_carbon = prediction['energy_kwh'] * 0.233
    
    print(f"\nEstimates:")
    print(f"  Cost (1 hour): ${estimated_cost:.4f}")
    print(f"  Carbon (1 hour): {estimated_carbon:.4f}kg CO2")


# ===== Example 3: Optimization Scoring =====
async def example_optimization():
    """
    Score current performance and suggest optimizations.
    """
    print("\n" + "="*60)
    print("Example 3: Real-Time Optimization Scoring")
    print("="*60)
    
    processor = RealTimeDataProcessor()
    inference = ModelInference()
    
    # Different load scenarios
    scenarios = [
        {
            'name': 'Low Load',
            'readings': [
                {'temperature': 25.0, 'humidity': 45.0, 'current': 10.0},
                {'temperature': 25.1, 'humidity': 44.9, 'current': 10.2},
            ]
        },
        {
            'name': 'Medium Load',
            'readings': [
                {'temperature': 28.0, 'humidity': 50.0, 'current': 35.0},
                {'temperature': 28.2, 'humidity': 50.2, 'current': 35.5},
            ]
        },
        {
            'name': 'High Load',
            'readings': [
                {'temperature': 35.0, 'humidity': 65.0, 'current': 60.0},
                {'temperature': 35.5, 'humidity': 65.5, 'current': 62.0},
            ]
        },
    ]
    
    for scenario in scenarios:
        processor = RealTimeDataProcessor()
        
        for reading in scenario['readings']:
            reading['timestamp'] = datetime.now().isoformat()
            processor.process_reading(reading)
        
        buffer_data = list(processor.buffer)
        
        # Get optimization recommendation
        optimization = await inference.optimize_schedule(buffer_data)
        
        print(f"\n{scenario['name']}:")
        print(f"  Power: {optimization['power_watts']:.2f}W")
        print(f"  Efficiency Score: {optimization['efficiency_score']:.2f}/1.00")
        print(f"  Recommendation: {optimization['recommendation']}")


# ===== Example 4: Real-time Anomaly Detection =====
async def example_anomaly_detection():
    """
    Detect anomalies in sensor readings.
    """
    print("\n" + "="*60)
    print("Example 4: Real-Time Anomaly Detection")
    print("="*60)
    
    processor = RealTimeDataProcessor()
    anomaly_log = []
    
    def on_anomaly(data):
        anomaly_log.append(data)
        print(f"\n🔴 ANOMALY DETECTED:")
        for issue in data['issues']:
            print(f"    - {issue}")
    
    processor.subscribe('anomaly', on_anomaly)
    
    # Normal readings
    normal_readings = [
        {'temperature': 25.0, 'humidity': 45.0, 'current': 20.0},
        {'temperature': 25.1, 'humidity': 44.9, 'current': 20.2},
        {'temperature': 25.0, 'humidity': 45.0, 'current': 20.1},
    ]
    
    # Anomalous readings
    anomalous_readings = [
        {'temperature': -15.0, 'humidity': 45.0, 'current': 20.0},  # Temp too low
        {'temperature': 25.0, 'humidity': 150.0, 'current': 20.0},  # Humidity too high
        {'temperature': 25.0, 'humidity': 45.0, 'current': 200.0},  # Current too high
    ]
    
    print("Processing normal readings...")
    for reading in normal_readings:
        reading['timestamp'] = datetime.now().isoformat()
        processor.process_reading(reading)
    print("✓ All normal")
    
    print("\nProcessing anomalous readings...")
    for reading in anomalous_readings:
        reading['timestamp'] = datetime.now().isoformat()
        processor.process_reading(reading)
    
    print(f"\nTotal anomalies detected: {len(anomaly_log)}")


# ===== Example 5: Data Streaming & Export =====
async def example_data_export():
    """
    Collect data and export to different formats.
    """
    print("\n" + "="*60)
    print("Example 5: Data Streaming & Export")
    print("="*60)
    
    processor = RealTimeDataProcessor(buffer_size=100)
    
    # Simulate continuous data stream
    import random
    
    print("Simulating 30 seconds of data...")
    for i in range(30):
        reading = {
            'temperature': 25 + random.gauss(0, 2),
            'humidity': 45 + random.gauss(0, 5),
            'current': 20 + random.gauss(0, 3),
            'timestamp': datetime.now().isoformat()
        }
        processor.process_reading(reading)
        await asyncio.sleep(0.1)  # Simulate 100ms intervals
    
    # Export to DataFrame
    df = processor.to_dataframe()
    
    print(f"\nCollected {len(df)} readings")
    print(f"\nDataFrame head:")
    print(df.head().to_string())
    
    # Save to CSV
    csv_path = "data/real_time/esp32_example_export.csv"
    df.to_csv(csv_path, index=False)
    print(f"\n✓ Exported to {csv_path}")
    
    # Statistics
    stats = processor.get_statistics()
    print(f"\nStatistics:")
    print(f"  Temperature: {stats['temperature']['mean']:.2f}°C ± {stats['temperature']['std']:.2f}")
    print(f"  Current: {stats['current']['mean']:.3f}A ± {stats['current']['std']:.3f}")
    print(f"  Humidity: {stats['humidity']['mean']:.1f}% ± {stats['humidity']['std']:.1f}")
    
    # Trend detection
    trend = processor.get_trend('current', window=10)
    print(f"  Current trend: {trend}")


# ===== Example 6: Server Integration =====
async def example_server_integration():
    """
    Connect to real ESP32 server and process live data.
    """
    print("\n" + "="*60)
    print("Example 6: ESP32 Server Integration")
    print("="*60)
    
    print("\nTo integrate with real server:")
    print("  1. Start ESP32 server: python esp32_server.py")
    print("  2. Simulate ESP32 data: python esp32_client.py simulate")
    print("  3. Monitor data: python esp32_client.py")
    
    print("\nCode example:")
    print("""
    from esp32_client import ESP32ServerClient
    
    async with ESP32ServerClient(base_url="http://localhost:8000") as client:
        # Get real-time data
        latest = await client.get_latest()
        
        # Process with ACMGS
        processor = RealTimeDataProcessor()
        result = processor.process_reading(latest)
        
        # Get predictions
        prediction = await client.predict_energy(duration_hours=1.0)
        print(f"Predicted energy: {prediction['predicted_energy_kwh']:.4f}kWh")
    """)


# ===== Main Runner =====
async def main():
    """Run all examples"""
    examples = [
        ("Energy Monitoring", example_energy_monitoring),
        ("Prediction", example_prediction),
        ("Optimization", example_optimization),
        ("Anomaly Detection", example_anomaly_detection),
        ("Data Export", example_data_export),
        ("Server Integration", example_server_integration),
    ]
    
    print("\n" + "="*60)
    print("ESP32 + ACMGS Integration Examples")
    print("="*60)
    
    for name, example_func in examples:
        try:
            await example_func()
        except Exception as e:
            logger.error(f"Error in {name}: {e}")
    
    print("\n" + "="*60)
    print("Examples Complete!")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
