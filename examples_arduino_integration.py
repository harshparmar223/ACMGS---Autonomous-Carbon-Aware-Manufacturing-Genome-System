"""
Integration examples: Using Arduino sensor data with ACMGS modules
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from arduino.integrator import RealTimeDataIntegrator, SensorDataValidator


# Example 1: Real-time Carbon Scheduling
def integrate_with_carbon_scheduler():
    """
    Integrate Arduino power measurements with carbon scheduler.
    Adjust manufacturing schedule based on real-time power consumption.
    """
    from carbon_scheduler.scheduler import CarbonScheduler
    
    scheduler = CarbonScheduler()
    integrator = RealTimeDataIntegrator(arduino_port="COM3")
    integrator.start()
    
    try:
        # Get real-time power measurement
        reading = integrator.get_latest_reading()
        if reading:
            current_amps = reading['current']
            power_watts = current_amps * 230.0  # Assuming 230V AC
            
            # Pass to scheduler for carbon-aware optimization
            # This would adjust manufacturing schedule based on current load
            print(f"Current Power Draw: {power_watts:.2f}W")
            # scheduler.optimize_with_current_load(power_watts)
    
    finally:
        integrator.stop()


# Example 2: Real-time Energy Prediction
def integrate_with_prediction_module():
    """
    Use Arduino sensor data to train prediction models.
    """
    from prediction.predictor import Predictor
    import pandas as pd
    
    integrator = RealTimeDataIntegrator(arduino_port="COM3")
    integrator.start()
    
    try:
        # Collect real data for a period
        import time
        duration = 300  # 5 minutes
        start = time.time()
        
        while time.time() - start < duration:
            reading = integrator.get_latest_reading()
            time.sleep(1)
        
        # Convert to DataFrame for prediction module
        df = integrator.to_dataframe()
        
        # Use real data for prediction training
        # predictor = Predictor()
        # predictor.train_with_real_data(df)
        
        print(f"Collected {len(df)} real measurements")
        print(f"Avg Power: {(df['current'].mean() * 230):.2f}W")
    
    finally:
        integrator.stop()


# Example 3: Real-time Optimization
def integrate_with_optimizer():
    """
    Feed real-time power data into genetic algorithm optimizer.
    """
    from optimization.optimizer import Optimizer
    
    integrator = RealTimeDataIntegrator(arduino_port="COM3")
    integrator.start()
    
    try:
        # Continuous optimization loop
        iteration = 0
        
        while iteration < 10:
            # Get latest measurements
            reading = integrator.get_latest_reading()
            stats = integrator.get_statistics(window_size=30)
            
            if stats:
                # Calculate real power metrics
                avg_current = stats['current']['avg']
                avg_power = avg_current * 230.0  # Assuming 230V
                
                print(f"Iteration {iteration}: "
                      f"Avg Current: {avg_current:.3f}A, "
                      f"Power: {avg_power:.2f}W")
                
                # Feed to optimizer
                # optimizer = Optimizer()
                # solution = optimizer.optimize(
                #     energy_constraint=avg_power * 0.95,  # 5% margin
                #     carbon_limit=...
                # )
                
                iteration += 1
    
    finally:
        integrator.stop()


# Example 4: Monitor and Alert
def monitoring_with_alerts():
    """
    Monitor sensor readings and trigger alerts on anomalies.
    """
    from arduino.integrator import SensorDataValidator
    import time
    
    integrator = RealTimeDataIntegrator(arduino_port="COM3")
    integrator.start()
    
    CURRENT_LIMIT = 50.0  # Amps
    TEMP_LIMIT = 60.0    # Celsius
    
    try:
        while True:
            reading = integrator.get_latest_reading()
            
            if reading:
                # Validate reading
                is_valid, error = SensorDataValidator.validate_reading(reading)
                
                if not is_valid:
                    print(f"⚠ ALERT: {error}")
                    continue
                
                # Check thresholds
                current = reading['current']
                temp = reading['temp']
                
                if current > CURRENT_LIMIT:
                    print(f"🔴 CRITICAL: Current {current:.3f}A exceeds limit {CURRENT_LIMIT}A")
                    # trigger_shutdown()
                
                if temp > TEMP_LIMIT:
                    print(f"🟠 WARNING: Temperature {temp:.2f}°C exceeds limit {TEMP_LIMIT}°C")
                    # reduce_load()
                
                time.sleep(1)
    
    except KeyboardInterrupt:
        print("\nMonitoring stopped")
    finally:
        integrator.stop()


# Example 5: Data Export for Analysis
def export_data_for_analysis():
    """
    Collect Arduino data and export to formats compatible with analysis tools.
    """
    import csv
    from datetime import datetime
    
    integrator = RealTimeDataIntegrator(arduino_port="COM3", log_data=True)
    integrator.start()
    
    # Custom export formats
    
    try:
        # Let integrator.logger handle CSV
        # Collect data
        import time
        duration = 600  # 10 minutes
        start = time.time()
        
        while time.time() - start < duration:
            reading = integrator.get_latest_reading()
            time.sleep(1)
        
        # Export to DataFrame
        df = integrator.to_dataframe()
        
        # Export as different formats
        df.to_csv("data/real_time/arduino_data.csv", index=False)
        
        # Convert to energy consumption
        df['power_W'] = df['current'] * 230.0
        df['energy_Wh'] = df['power_W'] / 3600  # Per second to Wh
        
        # Resample to hourly
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
        
        hourly = df.resample('1H').agg({
            'temperature': 'mean',
            'humidity': 'mean',
            'current': 'mean',
            'power_W': 'sum',  # Total power in period
            'energy_Wh': 'sum'  # Total energy in period
        })
        
        hourly.to_csv("data/real_time/arduino_hourly_summary.csv")
        
        print("Data exported successfully:")
        print(f"  - Raw data: data/real_time/arduino_data.csv")
        print(f"  - Hourly summary: data/real_time/arduino_hourly_summary.csv")
        
    finally:
        integrator.stop()


# Example 6: Integration with Dashboard
def integrate_with_dashboard():
    """
    Stream Arduino data to Streamlit dashboard for real-time visualization.
    """
    # This would be added to your dashboard/app.py
    
    dashboard_code = '''
import streamlit as st
import plotly.graph_objects as go
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / '..' / 'src'))

from arduino.integrator import RealTimeDataIntegrator

st.set_page_config(page_title="Real-Time Sensors", layout="wide")
st.title("🔌 Real-Time Arduino Sensors")

integrator = RealTimeDataIntegrator(arduino_port="COM3")
integrator.start()

col1, col2, col3 = st.columns(3)

with col1:
    temp_placeholder = st.empty()
with col2:
    humidity_placeholder = st.empty()
with col3:
    current_placeholder = st.empty()

chart_placeholder = st.empty()

try:
    while True:
        reading = integrator.get_latest_reading()
        
        if reading:
            # Update metrics
            with col1:
                temp_placeholder.metric(
                    "Temperature",
                    f"{reading['temp']:.1f}°C"
                )
            with col2:
                humidity_placeholder.metric(
                    "Humidity",
                    f"{reading['humidity']:.1f}%"
                )
            with col3:
                current_placeholder.metric(
                    "Current",
                    f"{reading['current']:.3f}A"
                )
            
            # Update chart
            df = integrator.to_dataframe(limit=100)
            if not df.empty:
                fig = go.Figure()
                
                fig.add_trace(go.Scatter(
                    x=df['timestamp'],
                    y=df['temperature'],
                    name='Temperature (°C)',
                    yaxis='y1'
                ))
                
                fig.add_trace(go.Scatter(
                    x=df['timestamp'],
                    y=df['current'],
                    name='Current (A)',
                    yaxis='y2'
                ))
                
                fig.update_layout(
                    title="Real-Time Readings",
                    xaxis=dict(title="Time"),
                    yaxis=dict(title="Temperature (°C)"),
                    yaxis2=dict(title="Current (A)", overlaying='y', side='right'),
                    hovermode='x unified'
                )
                
                chart_placeholder.plotly_chart(fig, use_container_width=True)
        
        st.write("Last update: " + str(reading.get('timestamp', '')))
        
finally:
    integrator.stop()
'''
    
    return dashboard_code


if __name__ == "__main__":
    import time
    
    print("ACMGS + Arduino Integration Examples\n")
    print("1. Carbon Scheduler Integration")
    print("2. Prediction Module Integration")
    print("3. Optimizer Integration")
    print("4. Real-time Monitoring")
    print("5. Data Export")
    print("6. Dashboard Integration (see code)")
    
    # Uncomment to run specific example:
    # integrate_with_carbon_scheduler()
    # integrate_with_prediction_module()
    # integrate_with_optimizer()
    # monitoring_with_alerts()
    # export_data_for_analysis()
