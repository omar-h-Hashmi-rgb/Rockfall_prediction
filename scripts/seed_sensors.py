#!/usr/bin/env python3
"""
Synthetic sensor data generator for the AI-based rockfall prediction system.
Generates realistic time-series data for displacement, strain, pore pressure, and vibrations.
"""

from __future__ import annotations
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import argparse
import json

def generate_sensor_data(
    sensor_type: str,
    duration_hours: int = 168,  # 1 week default
    frequency_minutes: int = 60,  # 1 hour intervals
    base_value: float = None,
    noise_level: float = 0.2,
    trend_factor: float = 0.0,
    seasonal_factor: float = 0.1,
    anomaly_probability: float = 0.05,
    seed: int = 42
) -> pd.DataFrame:
    """Generate synthetic sensor data with realistic patterns."""
    
    np.random.seed(seed)
    
    # Calculate number of data points
    total_minutes = duration_hours * 60
    num_points = total_minutes // frequency_minutes
    
    # Create time index
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=duration_hours)
    timestamps = pd.date_range(
        start=start_time, 
        end=end_time, 
        periods=num_points
    )
    
    # Set base values for different sensor types
    base_values = {
        'displacement': 2.0,    # mm
        'strain': 0.5,          # strain units
        'pore_pressure': 1.2,   # pressure units
        'vibrations': 0.3       # vibration units
    }
    
    if base_value is None:
        base_value = base_values.get(sensor_type, 1.0)
    
    # Generate base signal
    t = np.arange(num_points)
    
    # Trend component (long-term drift)
    trend = trend_factor * t / num_points
    
    # Seasonal component (daily and weekly cycles)
    daily_cycle = seasonal_factor * np.sin(2 * np.pi * t / (24 * 60 / frequency_minutes))
    weekly_cycle = seasonal_factor * 0.5 * np.sin(2 * np.pi * t / (7 * 24 * 60 / frequency_minutes))
    seasonal = daily_cycle + weekly_cycle
    
    # Noise component
    noise = np.random.normal(0, noise_level, num_points)
    
    # Base signal
    values = base_value + trend + seasonal + noise
    
    # Add random walk component for more realistic behavior
    walk_strength = noise_level * 0.5
    random_walk = np.cumsum(np.random.normal(0, walk_strength, num_points))
    values += random_walk
    
    # Add occasional anomalies
    anomaly_indices = np.random.choice(
        num_points, 
        size=int(num_points * anomaly_probability), 
        replace=False
    )
    
    for idx in anomaly_indices:
        # Random spike or dip
        anomaly_magnitude = np.random.choice([-1, 1]) * np.random.uniform(2, 5) * noise_level
        values[idx] += anomaly_magnitude
    
    # Ensure non-negative values where appropriate
    if sensor_type in ['displacement', 'strain', 'pore_pressure', 'vibrations']:
        values = np.maximum(values, 0.01)  # Small positive minimum
    
    # Add sensor-specific patterns
    if sensor_type == 'displacement':
        # Displacement might have sudden jumps due to geological events
        event_indices = np.random.choice(num_points, size=max(1, num_points // 100), replace=False)
        for idx in event_indices:
            jump_size = np.random.uniform(0.5, 3.0)
            values[idx:] += jump_size
    
    elif sensor_type == 'vibrations':
        # Vibrations might have bursts of activity
        burst_indices = np.random.choice(num_points, size=num_points // 50, replace=False)
        for idx in burst_indices:
            burst_duration = min(10, num_points - idx)
            burst_values = np.random.gamma(2, 0.5, burst_duration)
            values[idx:idx+burst_duration] += burst_values
    
    elif sensor_type == 'pore_pressure':
        # Pore pressure might respond to rainfall (simplified)
        rain_events = np.random.choice(num_points, size=num_points // 20, replace=False)
        for idx in rain_events:
            response_duration = min(24, num_points - idx)  # 24-hour response
            pressure_increase = np.random.uniform(0.2, 0.8)
            decay = np.exp(-np.arange(response_duration) / 10)  # Exponential decay
            values[idx:idx+response_duration] += pressure_increase * decay
    
    # Create DataFrame
    df = pd.DataFrame({
        'timestamp': timestamps,
        'value': values,
        'sensor_type': sensor_type
    })
    
    return df

def generate_environmental_data(
    duration_hours: int = 168,
    frequency_minutes: int = 60,
    seed: int = 42
) -> dict:
    """Generate synthetic environmental data (JSON format)."""
    
    np.random.seed(seed)
    
    # Calculate number of data points
    total_minutes = duration_hours * 60
    num_points = total_minutes // frequency_minutes
    
    # Create time index
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=duration_hours)
    timestamps = pd.date_range(
        start=start_time,
        end=end_time, 
        periods=num_points
    )
    
    records = []
    
    for i, timestamp in enumerate(timestamps):
        # Generate realistic weather patterns
        hour_of_day = timestamp.hour
        day_of_year = timestamp.dayofyear
        
        # Temperature with daily and seasonal cycles
        base_temp = 20 + 10 * np.sin(2 * np.pi * day_of_year / 365.25)  # Seasonal
        daily_temp_variation = 8 * np.sin(2 * np.pi * (hour_of_day - 6) / 24)  # Daily
        temp_noise = np.random.normal(0, 2)
        temperature = base_temp + daily_temp_variation + temp_noise
        
        # Rainfall (occasional events)
        if np.random.random() < 0.1:  # 10% chance of rain
            rainfall = np.random.exponential(5)  # Exponential distribution
        else:
            rainfall = 0.0
        
        # Humidity (inversely related to temperature, with rain effects)
        base_humidity = 70 - (temperature - 20) * 2
        if rainfall > 0:
            base_humidity += 20  # Higher humidity during rain
        humidity = np.clip(base_humidity + np.random.normal(0, 5), 0, 100)
        
        # Wind speed (more variable during rain)
        base_wind = 5 + np.random.gamma(2, 2)
        if rainfall > 0:
            base_wind *= np.random.uniform(1.5, 3.0)  # Higher wind during rain
        wind_speed = max(0, base_wind)
        
        # Atmospheric pressure (varies slowly)
        pressure_base = 1013.25
        pressure_variation = 10 * np.sin(2 * np.pi * i / (48 * 60 / frequency_minutes))  # 48-hour cycle
        pressure = pressure_base + pressure_variation + np.random.normal(0, 2)
        
        # Ambient vibrations (lower at night, higher during day/activity)
        if 6 <= hour_of_day <= 22:  # Day time
            ambient_vibration = 0.3 + np.random.gamma(1.5, 0.2)
        else:  # Night time
            ambient_vibration = 0.1 + np.random.gamma(1, 0.1)
        
        record = {
            'timestamp': timestamp.isoformat(),
            'rainfall_mm': round(rainfall, 2),
            'temperature_c': round(temperature, 1),
            'humidity': round(humidity, 1),
            'wind_speed': round(wind_speed, 1),
            'pressure': round(pressure, 2),
            'vibrations': round(ambient_vibration, 3)
        }
        
        records.append(record)
    
    return {
        'metadata': {
            'generated_at': datetime.now().isoformat(),
            'duration_hours': duration_hours,
            'frequency_minutes': frequency_minutes,
            'num_records': len(records),
            'description': 'Synthetic environmental data for rockfall prediction system'
        },
        'records': records
    }

def main():
    """Main function to generate all synthetic data."""
    
    parser = argparse.ArgumentParser(description='Generate synthetic sensor data')
    parser.add_argument(
        '--duration', 
        type=int, 
        default=168, 
        help='Duration in hours (default: 168 = 1 week)'
    )
    parser.add_argument(
        '--frequency', 
        type=int, 
        default=60, 
        help='Frequency in minutes (default: 60 = hourly)'
    )
    parser.add_argument(
        '--output-dir', 
        type=str, 
        default='data', 
        help='Output directory (default: data)'
    )
    parser.add_argument(
        '--seed', 
        type=int, 
        default=42, 
        help='Random seed for reproducibility (default: 42)'
    )
    parser.add_argument(
        '--noise', 
        type=float, 
        default=0.2, 
        help='Noise level (default: 0.2)'
    )
    
    args = parser.parse_args()
    
    # Create output directories
    output_dir = Path(args.output_dir)
    sensors_dir = output_dir / 'sensors'
    sensors_dir.mkdir(parents=True, exist_ok=True)
    
    print("🚀 Generating synthetic sensor data...")
    print(f"📁 Output directory: {output_dir}")
    print(f"⏰ Duration: {args.duration} hours")
    print(f"📊 Frequency: {args.frequency} minutes")
    print(f"🎲 Seed: {args.seed}")
    
    # Generate sensor data
    sensor_types = ['displacement', 'strain', 'pore_pressure', 'vibrations']
    
    for sensor_type in sensor_types:
        print(f"📡 Generating {sensor_type} data...")
        
        df = generate_sensor_data(
            sensor_type=sensor_type,
            duration_hours=args.duration,
            frequency_minutes=args.frequency,
            noise_level=args.noise,
            seed=args.seed
        )
        
        # Save to CSV
        output_path = sensors_dir / f"{sensor_type}.csv"
        df.to_csv(output_path, index=False)
        
        print(f"  ✅ Saved {len(df)} records to {output_path}")
        print(f"  📊 Value range: {df['value'].min():.3f} - {df['value'].max():.3f}")
    
    # Generate environmental data
    print("🌦️ Generating environmental data...")
    
    env_data = generate_environmental_data(
        duration_hours=args.duration,
        frequency_minutes=args.frequency,
        seed=args.seed
    )
    
    # Save environmental data
    env_path = output_dir / 'Sub_Division_IMD.json'
    with open(env_path, 'w') as f:
        json.dump(env_data, f, indent=2)
    
    print(f"  ✅ Saved {len(env_data['records'])} records to {env_path}")
    
    # Generate summary
    print("\n📋 Data Generation Summary:")
    print("="*50)
    print(f"📁 Sensor CSV files: {len(sensor_types)}")
    print(f"🌦️ Environmental JSON: 1 file")
    print(f"📊 Total records per type: {len(df)}")
    print(f"⏰ Time range: {args.duration} hours")
    print(f"🎯 Purpose: Training & testing rockfall prediction model")
    
    # Show file sizes
    print(f"\n📂 Generated files:")
    for sensor_type in sensor_types:
        file_path = sensors_dir / f"{sensor_type}.csv"
        size_kb = file_path.stat().st_size / 1024
        print(f"  📄 {file_path.name}: {size_kb:.1f} KB")
    
    env_size_kb = env_path.stat().st_size / 1024
    print(f"  📄 {env_path.name}: {env_size_kb:.1f} KB")
    
    print(f"\n✨ Data generation completed successfully!")
    print(f"🔧 Next steps:")
    print(f"  1. Train the ML model: python ml/train.py")
    print(f"  2. Start the API: uvicorn backend.main:app --reload")
    print(f"  3. Launch the UI: streamlit run streamlit_app/app.py")

if __name__ == '__main__':
    main()