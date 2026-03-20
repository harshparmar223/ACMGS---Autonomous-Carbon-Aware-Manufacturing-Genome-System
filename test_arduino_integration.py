"""
Test script for Arduino ACS712 + DHT11 sensor integration
Run this to verify your setup is working correctly
"""

import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from arduino.integrator import RealTimeDataIntegrator, SensorDataValidator
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/arduino_test.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def test_arduino_connection(port: str = "COM3", duration: int = 30):
    """
    Test Arduino sensor connection and data collection.
    
    Args:
        port: Serial port (default COM3)
        duration: Duration in seconds to collect data
    """
    logger.info("=" * 60)
    logger.info("Arduino Sensor Integration Test")
    logger.info("=" * 60)
    logger.info(f"Port: {port}, Duration: {duration}s")
    
    try:
        with RealTimeDataIntegrator(arduino_port=port, log_data=True) as integrator:
            if not integrator.reader.connected:
                logger.error(f"Failed to connect to Arduino on {port}")
                logger.info("Troubleshooting:")
                logger.info("1. Check Arduino is plugged in via USB")
                logger.info("2. Verify port in Arduino IDE Tools → Port")
                logger.info("3. On Windows, check Device Manager for COM ports")
                logger.info("4. On Linux/Mac, run: ls /dev/tty*")
                return False
            
            logger.info("✓ Arduino connected successfully")
            logger.info("\nCollecting sensor data...")
            logger.info("-" * 60)
            
            data_count = 0
            valid_count = 0
            error_count = 0
            
            start_time = time.time()
            
            while time.time() - start_time < duration:
                reading = integrator.get_latest_reading()
                
                if reading:
                    data_count += 1
                    is_valid, error_msg = SensorDataValidator.validate_reading(reading)
                    
                    if is_valid:
                        valid_count += 1
                        temp = reading['temp']
                        humidity = reading['humidity']
                        current = reading['current']
                        
                        # Display with nice formatting
                        print(f"[{data_count:3d}] Temp: {temp:6.2f}°C | "
                              f"Humidity: {humidity:6.2f}% | "
                              f"Current: {current:7.3f}A")
                        
                    else:
                        error_count += 1
                        logger.warning(f"Invalid reading: {error_msg}")
                
                time.sleep(0.5)
            
            logger.info("-" * 60)
            logger.info("\n=== Test Results ===")
            logger.info(f"Total readings: {data_count}")
            logger.info(f"Valid readings: {valid_count}")
            logger.info(f"Invalid readings: {error_count}")
            
            if data_count > 0:
                success_rate = (valid_count / data_count) * 100
                logger.info(f"Success rate: {success_rate:.1f}%")
            
            # Print statistics
            stats = integrator.get_statistics()
            if stats:
                logger.info("\n=== Statistics (Last 60 readings) ===")
                logger.info(f"Temperature:")
                logger.info(f"  Min: {stats['temperature']['min']:.2f}°C")
                logger.info(f"  Max: {stats['temperature']['max']:.2f}°C")
                logger.info(f"  Avg: {stats['temperature']['avg']:.2f}°C")
                
                logger.info(f"Humidity:")
                logger.info(f"  Min: {stats['humidity']['min']:.2f}%")
                logger.info(f"  Max: {stats['humidity']['max']:.2f}%")
                logger.info(f"  Avg: {stats['humidity']['avg']:.2f}%")
                
                logger.info(f"Current:")
                logger.info(f"  Min: {stats['current']['min']:.3f}A")
                logger.info(f"  Max: {stats['current']['max']:.3f}A")
                logger.info(f"  Avg: {stats['current']['avg']:.3f}A")
                logger.info(f"  Total: {stats['current']['total']:.1f}A·s")
            
            # Estimate power consumption
            power = integrator.estimate_power_consumption(voltage=230.0)
            if power:
                logger.info("\n=== Power Estimation (230V AC) ===")
                logger.info(f"Average Current: {power['current_avg_A']:.3f}A")
                logger.info(f"Average Power: {power['power_avg_W']:.2f}W ({power['power_avg_kW']:.3f}kW)")
                logger.info(f"Estimated Energy (1 hour): {power['energy_last_hour_kWh']:.4f}kWh")
            
            # Export to DataFrame
            logger.info("\n=== Data Export ===")
            df = integrator.to_dataframe()
            if not df.empty:
                logger.info(f"Exported {len(df)} rows to DataFrame")
                logger.info(f"Columns: {', '.join(df.columns)}")
                logger.info("Sample data:")
                logger.info(df.head().to_string())
            
            logger.info("\n" + "=" * 60)
            logger.info("✓ Test completed successfully!")
            logger.info(f"Data logged to: data/real_time/sensor_data_*.csv")
            logger.info("=" * 60)
            
            return True
    
    except Exception as e:
        logger.error(f"Test failed with error: {e}", exc_info=True)
        return False


def test_multiple_ports():
    """Try to find and connect to Arduino on common ports."""
    common_ports = ["COM3", "COM4", "COM5", "/dev/ttyUSB0", "/dev/ttyACM0"]
    
    logger.info("Scanning for Arduino on common ports...")
    
    for port in common_ports:
        logger.info(f"Trying {port}...", end=" ")
        integrator = RealTimeDataIntegrator(arduino_port=port)
        
        if integrator.reader.connect():
            logger.info(f"✓ Found Arduino on {port}")
            integrator.reader.disconnect()
            return port
        else:
            logger.info("✗ Not found")
    
    logger.warning("Arduino not found on common ports")
    return None


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Arduino sensor connection")
    parser.add_argument("--port", default="COM3", help="Serial port (default: COM3)")
    parser.add_argument("--duration", type=int, default=30, help="Duration in seconds (default: 30)")
    parser.add_argument("--auto-detect", action="store_true", help="Auto-detect Arduino port")
    
    args = parser.parse_args()
    
    if args.auto_detect:
        port = test_multiple_ports()
        if not port:
            logger.error("Could not find Arduino. Please specify port with --port")
            sys.exit(1)
    else:
        port = args.port
    
    success = test_arduino_connection(port=port, duration=args.duration)
    sys.exit(0 if success else 1)
