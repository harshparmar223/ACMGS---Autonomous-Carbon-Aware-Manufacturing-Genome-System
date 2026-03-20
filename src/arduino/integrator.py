"""
Real-time Arduino sensor integration with ACMGS system.
Bridges Arduino sensor data to optimization and prediction modules.
"""

import pandas as pd
import logging
from datetime import datetime
from typing import Dict, List, Optional
from .sensor_reader import ArduinoSensorReader, SensorDataLogger

logger = logging.getLogger(__name__)


class RealTimeDataIntegrator:
    """Integrates Arduino sensor data with ACMGS optimization engine."""
    
    def __init__(self, arduino_port: str = "COM3", log_data: bool = True):
        """
        Initialize real-time data integrator.
        
        Args:
            arduino_port: Serial port for Arduino (e.g., 'COM3', '/dev/ttyUSB0')
            log_data: Whether to log data to CSV
        """
        self.reader = ArduinoSensorReader(port=arduino_port)
        self.logger = SensorDataLogger() if log_data else None
        self.data_buffer: List[Dict] = []
        self.max_buffer_size = 3600  # 1 hour at 1 reading/sec
        
    def start(self) -> bool:
        """Start reading from Arduino."""
        if self.reader.connect():
            if self.logger:
                self.logger.start_logging()
            logger.info("Real-time data collection started")
            return True
        return False
    
    def get_latest_reading(self) -> Optional[Dict]:
        """Get the most recent sensor reading."""
        data = self.reader.read_sensor_data()
        if data:
            self.data_buffer.append(data)
            
            # Keep buffer size manageable
            if len(self.data_buffer) > self.max_buffer_size:
                self.data_buffer.pop(0)
            
            if self.logger:
                self.logger.log_data(data)
            
            return data
        return None
    
    def get_statistics(self, window_size: int = 60) -> Optional[Dict]:
        """
        Get statistics over the last N readings.
        
        Args:
            window_size: Number of recent readings to analyze
        
        Returns:
            Dictionary with min, max, avg, std for each sensor
        """
        if len(self.data_buffer) < window_size:
            window_size = len(self.data_buffer)
        
        if window_size == 0:
            return None
        
        recent_data = self.data_buffer[-window_size:]
        
        temps = [d.get('temp', 0) for d in recent_data]
        humidities = [d.get('humidity', 0) for d in recent_data]
        currents = [d.get('current', 0) for d in recent_data]
        
        return {
            'temperature': {
                'min': min(temps),
                'max': max(temps),
                'avg': sum(temps) / len(temps),
            },
            'humidity': {
                'min': min(humidities),
                'max': max(humidities),
                'avg': sum(humidities) / len(humidities),
            },
            'current': {
                'min': min(currents),
                'max': max(currents),
                'avg': sum(currents) / len(currents),
                'total': sum(currents),  # Total current consumption
            }
        }
    
    def to_dataframe(self, limit: Optional[int] = None) -> pd.DataFrame:
        """
        Convert buffered data to pandas DataFrame.
        
        Args:
            limit: Maximum number of rows to return
        
        Returns:
            DataFrame with columns: timestamp, temperature, humidity, current
        """
        data = self.data_buffer
        if limit:
            data = data[-limit:]
        
        if not data:
            return pd.DataFrame()
        
        return pd.DataFrame([
            {
                'timestamp': d.get('timestamp'),
                'temperature': d.get('temp'),
                'humidity': d.get('humidity'),
                'current': d.get('current')
            }
            for d in data
        ])
    
    def estimate_power_consumption(self, voltage: float = 230.0) -> Optional[Dict]:
        """
        Estimate power consumption from current readings.
        
        Args:
            voltage: Supply voltage (default 230V for AC, 48V for DC, 12V for low-power)
        
        Returns:
            Dictionary with power metrics
        """
        stats = self.get_statistics(window_size=60)
        if not stats:
            return None
        
        current_avg = stats['current']['avg']
        power_watts = current_avg * voltage
        
        return {
            'current_avg_A': current_avg,
            'voltage_V': voltage,
            'power_avg_W': power_watts,
            'power_avg_kW': power_watts / 1000,
            'energy_last_hour_kWh': (power_watts / 1000) * 1,  # Assuming ~1 hour of data
        }
    
    def stop(self):
        """Stop reading and close connections."""
        if self.logger:
            self.logger.stop_logging()
        self.reader.disconnect()
        logger.info("Real-time data collection stopped")
    
    def __enter__(self):
        """Context manager support."""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager cleanup."""
        self.stop()


class SensorDataValidator:
    """Validates sensor readings for anomalies."""
    
    @staticmethod
    def is_valid_temperature(temp: float, min_val: float = -10.0, max_val: float = 85.0) -> bool:
        """Check if temperature is within valid range."""
        return min_val <= temp <= max_val
    
    @staticmethod
    def is_valid_humidity(humidity: float, min_val: float = 0.0, max_val: float = 100.0) -> bool:
        """Check if humidity is within valid range."""
        return min_val <= humidity <= max_val
    
    @staticmethod
    def is_valid_current(current: float, max_expected: float = 100.0) -> bool:
        """Check if current is within valid range."""
        return -max_expected <= current <= max_expected
    
    @staticmethod
    def validate_reading(data: Dict) -> tuple:
        """
        Validate an entire sensor reading.
        
        Returns:
            (is_valid: bool, error_message: str or None)
        """
        if not data:
            return False, "Empty data"
        
        temp = data.get('temp')
        humidity = data.get('humidity')
        current = data.get('current')
        
        if not SensorDataValidator.is_valid_temperature(temp):
            return False, f"Invalid temperature: {temp}°C"
        
        if not SensorDataValidator.is_valid_humidity(humidity):
            return False, f"Invalid humidity: {humidity}%"
        
        if not SensorDataValidator.is_valid_current(current):
            return False, f"Invalid current: {current}A"
        
        return True, None


# Example usage
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    with RealTimeDataIntegrator(arduino_port="COM3") as integrator:
        import time
        
        # Read for 30 seconds
        start = time.time()
        while time.time() - start < 30:
            reading = integrator.get_latest_reading()
            if reading:
                is_valid, error = SensorDataValidator.validate_reading(reading)
                if is_valid:
                    print(f"Temp: {reading['temp']:.2f}°C | "
                          f"Humidity: {reading['humidity']:.2f}% | "
                          f"Current: {reading['current']:.3f}A")
            time.sleep(0.5)
        
        # Print statistics
        stats = integrator.get_statistics()
        if stats:
            print("\n=== Statistics ===")
            print(f"Temperature: {stats['temperature']['avg']:.2f}°C "
                  f"({stats['temperature']['min']:.2f}-{stats['temperature']['max']:.2f})")
            print(f"Humidity: {stats['humidity']['avg']:.2f}% "
                  f"({stats['humidity']['min']:.2f}-{stats['humidity']['max']:.2f})")
            print(f"Current: {stats['current']['avg']:.3f}A "
                  f"({stats['current']['min']:.3f}-{stats['current']['max']:.3f})")
        
        # Estimate power
        power = integrator.estimate_power_consumption(voltage=230.0)
        if power:
            print(f"\nPower Consumption: {power['power_avg_W']:.2f}W ({power['power_avg_kW']:.3f}kW)")
