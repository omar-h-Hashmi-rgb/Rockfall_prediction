#!/usr/bin/env python3
"""
Generate sample data for testing the system
"""

import os
import sys
import json
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.synthetic.dem_data import save_dem_data
from data.synthetic.sensor_data import save_sensor_data
from utils.database import Database

def generate_environmental_data():
    """Generate sample environmental data"""
    data = []
    base_time = datetime.now() - timedelta(days=7)
    
    for i in range(168):  # 7 days * 24 hours
        timestamp = base_time + timedelta(hours=i)
        
        # Simulate realistic mining area weather
        temp_base = 22 + 8 * (i % 24) / 24  # Daily temperature cycle
        
        data.append({
            "timestamp": timestamp.isoformat(),
            "subdivision": "Mining_District_A",
            "temperature": round(temp_base + (i % 3 - 1) * 2, 1),
            "humidity": round(45 + 30 * (i % 17) / 17, 1),
            "rainfall": round(max(0, (i % 23 - 20) * 0.5), 1),
            "wind_speed": round(8 + 12 * (i % 11) / 11, 1),
            "atmospheric_pressure": round(1013 + 20 * ((i % 19) / 19 - 0.5), 2),
            "visibility": round(8 + 7 * (i % 13) / 13, 1),
            "uv_index": max(0, round(8 * (i % 24 - 6) / 12, 1)) if 6 <= i % 24 <= 18 else 0
        })
    
    return data

def main():
    print("🔧 Generating sample data for rockfall prediction system...")
    print("-" * 60)
    
    # Create data directories
    os.makedirs('data', exist_ok=True)
    os.makedirs('data/synthetic', exist_ok=True)
    
    # Generate DEM data
    print("🗺️  Generating Digital Elevation Model data...")
    dem_data = save_dem_data('data/synthetic/dem_data.json')
    print(f"   ✅ DEM data saved with {dem_data['grid_size']}x{dem_data['grid_size']} grid")
    
    # Generate sensor data
    print("📡 Generating geotechnical sensor data...")
    sensor_data = save_sensor_data('data/synthetic/sensor_data.json')
    print(f"   ✅ Sensor data saved for {sensor_data['metadata']['num_sensors']} sensors")
    
    # Generate environmental data
    print("🌤️  Generating environmental data...")
    env_data = generate_environmental_data()
    with open('data/Sub_Division_IMD.json', 'w') as f:
        json.dump(env_data, f, indent=2)
    print(f"   ✅ Environmental data saved with {len(env_data)} records")
    
    # Initialize database with sample data
    print("💾 Initializing database with sample data...")
    try:
        db = Database()
        
        # Add some sample predictions
        for i in range(10):
            sample_prediction = {
                "risk_class": ["Low", "Medium", "High"][i % 3],
                "risk_probability": 0.1 + (i * 0.08),
                "coordinates": {
                    "lat": 28.6139 + (i * 0.001),
                    "lon": 77.2090 + (i * 0.001),
                    "sector": f"Sector {(i % 4) + 1}"
                },
                "alert_required": i % 3 == 2,
                "timestamp": datetime.now() - timedelta(hours=i)
            }
            db.save_prediction(sample_prediction)
        
        print("   ✅ Database initialized with sample predictions")
        
    except Exception as e:
        print(f"   ⚠️  Database initialization skipped: {e}")
    
    print("\n🎉 Sample data generation completed!")
    print("\n📁 Generated files:")
    print("   • data/synthetic/dem_data.json")
    print("   • data/synthetic/sensor_data.json")
    print("   • data/Sub_Division_IMD.json")
    print("\n💡 You can now:")
    print("   1. Place your drone images in data/DroneImages/FilteredData/")
    print("   2. Replace Sub_Division_IMD.json with your actual data")
    print("   3. Run the training script: python scripts/train_model.py")
    print("   4. Start the application: docker-compose up")

if __name__ == "__main__":
    main()