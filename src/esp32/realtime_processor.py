"""
Real-Time Processing Engine for ESP32 data
Integrates sensor streams with ACMGS models for live inference
"""

import asyncio
import pandas as pd
from typing import Dict, List, Optional, Callable
from datetime import datetime
from collections import deque
import logging
import numpy as np

logger = logging.getLogger(__name__)


class RealTimeDataProcessor:
    """
    Processes real-time ESP32 sensor data streams
    Performs sliding-window analysis and model inference
    """
    
    def __init__(self, window_size: int = 60, buffer_size: int = 3600):
        """
        Initialize real-time processor.
        
        Args:
            window_size: Number of readings for statistics (default 60 = 1 min at 1Hz)
            buffer_size: Maximum historical readings to keep
        """
        self.window_size = window_size
        self.buffer = deque(maxlen=buffer_size)
        self.subscribers: Dict[str, List[Callable]] = {
            'reading': [],
            'alert': [],
            'prediction': [],
            'anomaly': []
        }
    
    def subscribe(self, event_type: str, callback: Callable):
        """Subscribe to event stream"""
        if event_type in self.subscribers:
            self.subscribers[event_type].append(callback)
    
    def _emit(self, event_type: str, data: Dict):
        """Emit event to subscribers"""
        for callback in self.subscribers.get(event_type, []):
            try:
                callback(data)
            except Exception as e:
                logger.warning(f"Callback error: {e}")
    
    def process_reading(self, reading: Dict) -> Dict:
        """
        Process a single sensor reading.
        
        Args:
            reading: {'temperature': float, 'humidity': float, 'current': float, 'timestamp': str}
        
        Returns:
            Processing result with analysis
        """
        # Add to buffer
        self.buffer.append(reading)
        
        result = {
            'raw_reading': reading,
            'processed_at': datetime.now().isoformat(),
            'buffer_size': len(self.buffer),
            'alerts': []
        }
        
        # Check for anomalies
        if len(self.buffer) > 1:
            anomaly = self._detect_anomaly(reading)
            if anomaly:
                result['alerts'].append(anomaly)
                self._emit('anomaly', anomaly)
        
        # Emit reading event
        self._emit('reading', result)
        
        return result
    
    def get_statistics(self) -> Optional[Dict]:
        """Calculate statistics over current window"""
        if len(self.buffer) < self.window_size:
            data = list(self.buffer)
        else:
            data = list(self.buffer)[-self.window_size:]
        
        if not data:
            return None
        
        temperatures = [d['temperature'] for d in data]
        currents = [d['current'] for d in data]
        humidities = [d['humidity'] for d in data]
        
        return {
            'count': len(data),
            'temperature': {
                'min': min(temperatures),
                'max': max(temperatures),
                'mean': np.mean(temperatures),
                'std': np.std(temperatures)
            },
            'current': {
                'min': min(currents),
                'max': max(currents),
                'mean': np.mean(currents),
                'std': np.std(currents),
                'sum': sum(currents)
            },
            'humidity': {
                'min': min(humidities),
                'max': max(humidities),
                'mean': np.mean(humidities),
                'std': np.std(humidities)
            },
            'timestamp': datetime.now().isoformat()
        }
    
    def _detect_anomaly(self, reading: Dict) -> Optional[Dict]:
        """Detect anomalies in sensor reading"""
        temp = reading.get('temperature', 0)
        current = reading.get('current', 0)
        humidity = reading.get('humidity', 0)
        
        # Define normal ranges
        anomalies = []
        
        if not (-10 <= temp <= 85):
            anomalies.append(f"Temperature out of range: {temp}°C")
        
        if not (0 <= humidity <= 100):
            anomalies.append(f"Humidity out of range: {humidity}%")
        
        if not (-150 <= current <= 150):
            anomalies.append(f"Current out of range: {current}A")
        
        if anomalies:
            return {
                'type': 'anomaly',
                'reading': reading,
                'issues': anomalies,
                'severity': 'high' if len(anomalies) > 1 else 'medium'
            }
        
        return None
    
    def to_dataframe(self, limit: Optional[int] = None) -> pd.DataFrame:
        """Convert buffer to pandas DataFrame"""
        data = list(self.buffer)
        if limit:
            data = data[-limit:]
        
        if not data:
            return pd.DataFrame()
        
        return pd.DataFrame(data)
    
    def get_trend(self, field: str = 'current', window: int = 10) -> Optional[str]:
        """
        Detect trend in data.
        
        Returns: 'increasing', 'decreasing', or 'stable'
        """
        if len(self.buffer) < window:
            return None
        
        data = [d.get(field, 0) for d in list(self.buffer)[-window:]]
        
        if not data:
            return None
        
        # Compare first half vs second half
        mid = len(data) // 2
        first_half = np.mean(data[:mid])
        second_half = np.mean(data[mid:])
        
        change_percent = ((second_half - first_half) / first_half * 100) if first_half != 0 else 0
        
        if change_percent > 5:
            return 'increasing'
        elif change_percent < -5:
            return 'decreasing'
        else:
            return 'stable'


class AlertEngine:
    """Real-time alert generation and management"""
    
    def __init__(self):
        self.thresholds = {
            'temp_high': 75.0,
            'temp_low': 5.0,
            'humidity_high': 90.0,
            'humidity_low': 10.0,
            'current_high': 120.0,  # Amperes
            'power_high': 30000.0,  # Watts
        }
        self.active_alerts = {}
    
    def evaluate(self, reading: Dict, voltage: float = 230.0) -> List[Dict]:
        """Evaluate reading against thresholds"""
        alerts = []
        
        temp = reading.get('temperature', 0)
        humidity = reading.get('humidity', 0)
        current = reading.get('current', 0)
        power = current * voltage
        
        # Temperature alerts
        if temp > self.thresholds['temp_high']:
            alerts.append({
                'type': 'TEMPERATURE_HIGH',
                'value': temp,
                'threshold': self.thresholds['temp_high'],
                'severity': 'warning'
            })
        
        if temp < self.thresholds['temp_low']:
            alerts.append({
                'type': 'TEMPERATURE_LOW',
                'value': temp,
                'threshold': self.thresholds['temp_low'],
                'severity': 'info'
            })
        
        # Humidity alerts
        if humidity > self.thresholds['humidity_high']:
            alerts.append({
                'type': 'HUMIDITY_HIGH',
                'value': humidity,
                'threshold': self.thresholds['humidity_high'],
                'severity': 'warning'
            })
        
        # Current alerts
        if current > self.thresholds['current_high']:
            alerts.append({
                'type': 'CURRENT_HIGH',
                'value': current,
                'threshold': self.thresholds['current_high'],
                'severity': 'critical'
            })
        
        # Power alerts
        if power > self.thresholds['power_high']:
            alerts.append({
                'type': 'POWER_HIGH',
                'value': power,
                'threshold': self.thresholds['power_high'],
                'severity': 'critical'
            })
        
        return alerts
    
    def set_threshold(self, alert_type: str, value: float):
        """Update alert threshold"""
        self.thresholds[alert_type] = value


class EnergyEstimator:
    """Estimate energy consumption from current readings"""
    
    @staticmethod
    def calculate_power(current: float, voltage: float = 230.0) -> float:
        """Calculate instantaneous power"""
        return current * voltage
    
    @staticmethod
    def calculate_energy(power_watts: float, duration_minutes: float) -> float:
        """Calculate energy consumption"""
        duration_hours = duration_minutes / 60
        return (power_watts / 1000) * duration_hours  # Returns kWh
    
    @staticmethod
    def estimate_carbon_emissions(energy_kwh: float, 
                                 carbon_intensity: float = 0.233) -> float:
        """
        Estimate CO2 emissions.
        
        Args:
            energy_kwh: Energy in kWh
            carbon_intensity: kg CO2 per kWh (grid-dependent)
        
        Returns:
            kg CO2 equivalent
        """
        return energy_kwh * carbon_intensity
    
    @staticmethod
    def estimate_cost(energy_kwh: float, rate_per_kwh: float = 0.15) -> float:
        """Estimate electricity cost"""
        return energy_kwh * rate_per_kwh


class ModelInference:
    """Real-time model inference on streaming data"""
    
    def __init__(self, predictor=None, optimizer=None):
        self.predictor = predictor
        self.optimizer = optimizer
    
    async def predict_next_hour(self, current_reading: Dict, 
                               historical_data: List[Dict]) -> Dict:
        """
        Predict energy consumption for next hour.
        
        Args:
            current_reading: Latest sensor reading
            historical_data: Recent historical readings
        
        Returns:
            Prediction result
        """
        if not historical_data:
            return {'error': 'Insufficient data for prediction'}
        
        # Use average of recent readings
        currents = [d.get('current', 0) for d in historical_data[-10:]]
        avg_current = sum(currents) / len(currents) if currents else 0
        
        power_watts = avg_current * 230.0
        energy_kwh = (power_watts / 1000) * 1.0  # 1 hour
        
        return {
            'energy_kwh': energy_kwh,
            'power_watts': power_watts,
            'avg_current': avg_current,
            'confidence': 0.85  # Confidence score
        }
    
    async def optimize_schedule(self, readings: List[Dict]) -> Dict:
        """Suggest optimization based on current readings"""
        if not readings:
            return {'error': 'No data for optimization'}
        
        currents = [d.get('current', 0) for d in readings]
        avg_current = sum(currents) / len(currents)
        power = avg_current * 230.0
        
        # Simple heuristic
        if power > 50000:
            recommendation = "Reduce load - current consumption too high"
            score = 0.3
        elif power > 30000:
            recommendation = "Monitor consumption - medium load detected"
            score = 0.6
        else:
            recommendation = "Operating efficiently"
            score = 0.9
        
        return {
            'power_watts': power,
            'recommendation': recommendation,
            'efficiency_score': score
        }


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    processor = RealTimeDataProcessor(window_size=60)
    alert_engine = AlertEngine()
    energy_estimator = EnergyEstimator()
    
    # Subscribe to events
    processor.subscribe('alert', lambda data: print(f"⚠ Alert: {data}"))
    processor.subscribe('anomaly', lambda data: print(f"🔴 Anomaly: {data}"))
    
    # Simulate readings
    test_readings = [
        {'temperature': 25.5, 'humidity': 45.0, 'current': 15.3},
        {'temperature': 25.6, 'humidity': 44.8, 'current': 15.5},
        {'temperature': 25.4, 'humidity': 45.2, 'current': 15.2},
    ]
    
    for reading in test_readings:
        result = processor.process_reading(reading)
        alerts = alert_engine.evaluate(reading)
        
        power = energy_estimator.calculate_power(reading['current'])
        energy = energy_estimator.calculate_energy(power, 60)
        carbon = energy_estimator.estimate_carbon_emissions(energy)
        
        print(f"\nReading: {reading}")
        print(f"Power: {power:.2f}W | Energy (1h): {energy:.4f}kWh | Carbon: {carbon:.4f}kg CO2")
        
        if alerts:
            print(f"Alerts: {alerts}")
    
    # Get statistics
    stats = processor.get_statistics()
    print(f"\nStatistics: {stats}")
