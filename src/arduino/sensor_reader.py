"""
Arduino Sensor Data Reader
Receives real-time current and temperature data from ACS712 + DHT11 sensors
via serial connection.
"""

import serial
import json
import logging
from typing import Dict, Optional, Tuple
from datetime import datetime
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)


class ArduinoSensorReader:
    """Reads real-time sensor data from Arduino via serial connection."""
    
    def __init__(self, port: str = "COM3", baudrate: int = 9600, timeout: int = 1):
        """
        Initialize Arduino sensor reader.
        
        Args:
            port: Serial port (e.g., 'COM3' on Windows, '/dev/ttyUSB0' on Linux)
            baudrate: Serial communication speed (default 9600)
            timeout: Read timeout in seconds
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_conn = None
        self.connected = False
        
    def connect(self) -> bool:
        """Establish serial connection to Arduino."""
        try:
            self.serial_conn = serial.Serial(
                self.port,
                self.baudrate,
                timeout=self.timeout
            )
            # Wait for Arduino to initialize
            import time
            time.sleep(2)
            
            # Read initialization message
            if self.serial_conn.in_waiting:
                init_msg = self.serial_conn.readline().decode().strip()
                logger.info(f"Arduino initialized: {init_msg}")
            
            self.connected = True
            logger.info(f"Connected to Arduino on {self.port}")
            return True
            
        except serial.SerialException as e:
            logger.error(f"Failed to connect to Arduino: {e}")
            self.connected = False
            return False
    
    def read_sensor_data(self) -> Optional[Dict]:
        """
        Read one sample of sensor data from Arduino.
        
        Returns:
            Dictionary with keys: 'temp', 'humidity', 'current', 'timestamp'
            Returns None if read fails
        """
        if not self.connected or not self.serial_conn:
            logger.warning("Serial connection not established")
            return None
        
        try:
            if self.serial_conn.in_waiting:
                line = self.serial_conn.readline().decode().strip()
                
                if line:
                    data = json.loads(line)
                    
                    # Add timestamp
                    data['timestamp'] = datetime.now().isoformat()
                    
                    return data
                    
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            logger.warning(f"Failed to parse sensor data: {e}")
            return None
        
        return None
    
    def read_continuous(self, duration_seconds: int = 60, callback=None):
        """
        Read sensor data continuously for a specified duration.
        
        Args:
            duration_seconds: How long to read data
            callback: Optional function to call with each data point
                     signature: callback(data_dict)
        
        Yields:
            Sensor data dictionaries
        """
        import time
        start_time = time.time()
        
        while time.time() - start_time < duration_seconds:
            data = self.read_sensor_data()
            if data:
                if callback:
                    callback(data)
                yield data
            else:
                time.sleep(0.1)
    
    def disconnect(self):
        """Close serial connection."""
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
            self.connected = False
            logger.info("Disconnected from Arduino")
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()


class SensorDataLogger:
    """Logs sensor data to CSV file."""
    
    def __init__(self, log_dir: str = "data/real_time"):
        """
        Initialize sensor data logger.
        
        Args:
            log_dir: Directory to store CSV files
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.csv_file = None
        self.writer = None
    
    def start_logging(self, filename: Optional[str] = None) -> str:
        """
        Start logging to a new CSV file.
        
        Args:
            filename: Custom filename (without extension)
        
        Returns:
            Path to the CSV file
        """
        import csv
        
        if filename is None:
            filename = f"sensor_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        csv_path = self.log_dir / f"{filename}.csv"
        
        self.csv_file = open(csv_path, 'w', newline='')
        self.writer = csv.DictWriter(
            self.csv_file,
            fieldnames=['timestamp', 'temperature', 'humidity', 'current']
        )
        self.writer.writeheader()
        
        logger.info(f"Started logging to {csv_path}")
        return str(csv_path)
    
    def log_data(self, data: Dict):
        """Log a single data point to CSV."""
        if self.writer:
            self.writer.writerow({
                'timestamp': data.get('timestamp'),
                'temperature': data.get('temp'),
                'humidity': data.get('humidity'),
                'current': data.get('current')
            })
            self.csv_file.flush()
    
    def stop_logging(self):
        """Close the CSV file."""
        if self.csv_file:
            self.csv_file.close()
            logger.info("Stopped logging")


# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Read sensor data for 30 seconds
    reader = ArduinoSensorReader(port="COM3", baudrate=9600)
    logger = logging.getLogger(__name__)
    
    if reader.connect():
        data_logger = SensorDataLogger()
        csv_file = data_logger.start_logging("sensor_test")
        
        try:
            for data in reader.read_continuous(duration_seconds=30):
                print(f"Temp: {data.get('temp'):.2f}°C | "
                      f"Humidity: {data.get('humidity'):.2f}% | "
                      f"Current: {data.get('current'):.3f}A")
                data_logger.log_data(data)
        finally:
            data_logger.stop_logging()
            reader.disconnect()
