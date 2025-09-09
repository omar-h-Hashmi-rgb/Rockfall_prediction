import numpy as np
import json
from datetime import datetime, timedelta
from typing import Dict, List

def generate_sensor_readings(num_sensors: int = 20, days: int = 7) -> Dict:
    """Generate synthetic geotechnical sensor data"""
    
    sensors = []
    
    for sensor_id in range(1, num_sensors + 1):
        # Sensor location (distributed around the pit)
        angle = (sensor_id / num_sensors) * 2 * np.pi
        radius = np.random.uniform(100, 400)  # Distance from pit center
        x = 500 + radius * np.cos(angle)
        y = 500 + radius * np.sin(angle)
        
        # Generate time series data
        timestamps = []
        displacement_data = []
        strain_data = []
        pore_pressure_data = []
        vibration_data = []
        
        current_time = datetime.now() - timedelta(days=days)
        
        # Base values for this sensor
        base_displacement = np.random.uniform(0.5, 3.0)  # mm
        base_strain = np.random.uniform(50, 200)  # micro-strain
        base_pressure = np.random.uniform(150, 300)  # kPa
        base_vibration = np.random.uniform(0.01, 0.1)  # g
        
        for hour in range(days * 24):
            timestamp = current_time + timedelta(hours=hour)
            timestamps.append(timestamp.isoformat())
            
            # Add trends and noise
            trend_factor = 1 + (hour / (days * 24)) * 0.1  # Slight increasing trend
            noise_factor = 1 + np.random.normal(0, 0.1)
            
            # Simulate daily cycles
            daily_cycle = 1 + 0.05 * np.sin(2 * np.pi * hour / 24)
            
            displacement = base_displacement * trend_factor * noise_factor * daily_cycle
            strain = base_strain * trend_factor * noise_factor * daily_cycle
            pressure = base_pressure * (1 + np.random.normal(0, 0.05))
            vibration = base_vibration * noise_factor * (1 + 0.3 * np.random.exponential(0.1))
            
            displacement_data.append(max(0, displacement))
            strain_data.append(max(0, strain))
            pore_pressure_data.append(max(0, pressure))
            vibration_data.append(max(0, vibration))
        
        sensor = {
            'sensor_id': f"SENSOR_{sensor_id:03d}",
            'type': 'geotechnical',
            'location': {
                'x': round(x, 2),
                'y': round(y, 2),
                'elevation': round(np.random.uniform(1400, 1600), 2)
            },
            'measurements': {
                'timestamps': timestamps,
                'displacement_mm': displacement_data,
                'strain_microstrain': strain_data,
                'pore_pressure_kpa': pore_pressure_data,
                'vibration_g': vibration_data
            },
            'status': np.random.choice(['active', 'active', 'maintenance'], p=[0.85, 0.1, 0.05]),
            'last_calibration': (datetime.now() - timedelta(days=np.random.randint(1, 90))).isoformat()
        }
        
        sensors.append(sensor)
    
    return {
        'sensors': sensors,
        'metadata': {
            'generation_date': datetime.now().isoformat(),
            'num_sensors': num_sensors,
            'time_period_days': days,
            'sampling_frequency': '1 hour',
            'measurement_units': {
                'displacement': 'mm',
                'strain': 'micro-strain',
                'pore_pressure': 'kPa',
                'vibration': 'g (gravitational acceleration)'
            }
        }
    }

def save_sensor_data(filename: str = "sensor_data.json"):
    """Save sensor data to JSON file"""
    sensor_data = generate_sensor_readings()
    with open(filename, 'w') as f:
        json.dump(sensor_data, f, indent=2)
    return sensor_data

if __name__ == "__main__":
    data = save_sensor_data()
    print(f"Generated data for {data['metadata']['num_sensors']} sensors")
    print(f"Time period: {data['metadata']['time_period_days']} days")
    print(f"Total measurements per sensor: {len(data['sensors'][0]['measurements']['timestamps'])}")