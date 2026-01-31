#!/usr/bin/env python3
"""
Setup MongoDB Atlas database with initial collections and sample data.
Free tier optimized - minimal data seeding.
"""

from pymongo import MongoClient
from datetime import datetime, timedelta
import random
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB Atlas connection string from environment variable
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/rockfall')

def setup_database():
    """Setup database with collections and indexes."""
    print("Connecting to MongoDB Atlas...")
    
    try:
        client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
        
        # Test connection
        client.admin.command('ping')
        print("✅ Connected to MongoDB Atlas!")
        
        # Get database
        db = client['rockfall']
        print(f"✅ Using database: rockfall")
        
        # Create collections
        collections = ['sensors', 'predictions', 'alerts', 'users']
        
        for collection_name in collections:
            if collection_name not in db.list_collection_names():
                db.create_collection(collection_name)
                print(f"✅ Created collection: {collection_name}")
            else:
                print(f"ℹ️  Collection already exists: {collection_name}")
        
        # Create indexes for sensors collection
        print("\n📊 Creating indexes...")
        db.sensors.create_index([("timestamp", -1)])
        db.sensors.create_index([("sensor_type", 1), ("timestamp", -1)])
        print("✅ Sensors indexes created")
        
        # Create indexes for predictions collection
        db.predictions.create_index([("timestamp", -1)])
        db.predictions.create_index([("risk_class", 1)])
        print("✅ Predictions indexes created")
        
        # Create indexes for alerts collection
        db.alerts.create_index([("timestamp", -1)])
        db.alerts.create_index([("type", 1), ("timestamp", -1)])
        print("✅ Alerts indexes created")
        
        return db
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def seed_minimal_data(db):
    """Seed database with minimal sample data (free tier optimized)."""
    print("\n🌱 Seeding minimal sample data...")
    
    # Check if data already exists
    if db.sensors.count_documents({}) > 0:
        print("ℹ️  Data already exists. Skipping seeding.")
        return
    
    # Generate 10 sensor readings (last 10 hours)
    sensor_data = []
    sensor_types = ['displacement', 'strain', 'pore_pressure', 'vibrations']
    
    for i in range(10):
        timestamp = datetime.utcnow() - timedelta(hours=10-i)
        
        sensor_data.append({
            'timestamp': timestamp,
            'sensor_type': random.choice(sensor_types),
            'displacement': round(random.uniform(1.5, 4.0), 2),
            'strain': round(random.uniform(0.3, 1.2), 2),
            'pore_pressure': round(random.uniform(0.8, 2.0), 2),
            'vibrations': round(random.uniform(0.2, 0.8), 2),
            'location': 'Site-A',
            'sensor_id': f'SENSOR-{random.randint(1,5):03d}',
            'created_at': timestamp
        })
    
    db.sensors.insert_many(sensor_data)
    print(f"✅ Inserted {len(sensor_data)} sensor readings")
    
    # Generate 5 predictions
    predictions_data = []
    risk_levels = ['LOW', 'LOW', 'MEDIUM', 'MEDIUM', 'HIGH']
    
    for i in range(5):
        timestamp = datetime.utcnow() - timedelta(hours=5-i)
        risk = risk_levels[i]
        prob = 0.2 if risk == 'LOW' else (0.5 if risk == 'MEDIUM' else 0.8)
        
        predictions_data.append({
            'timestamp': timestamp,
            'probability': prob,
            'risk_class': risk,
            'model_version': '1.0',
            'features_used': ['displacement', 'strain', 'pore_pressure', 'vibrations'],
            'location': 'Site-A'
        })
    
    db.predictions.insert_many(predictions_data)
    print(f"✅ Inserted {len(predictions_data)} predictions")
    
    # Generate 2 alerts
    alerts_data = [
        {
            'alert_id': 'alert-001',
            'timestamp': datetime.utcnow() - timedelta(hours=2),
            'type': 'alert',
            'message': 'High risk detected at Site-A',
            'probability': 0.8,
            'risk_level': 'HIGH',
            'channels': ['email'],
            'results': {'email': True},
            'status': 'sent',
            'location': 'Site-A'
        },
        {
            'alert_id': 'alert-002',
            'timestamp': datetime.utcnow() - timedelta(hours=6),
            'type': 'alert',
            'message': 'Medium risk detected at Site-A',
            'probability': 0.5,
            'risk_level': 'MEDIUM',
            'channels': ['email'],
            'results': {'email': True},
            'status': 'sent',
            'location': 'Site-A'
        }
    ]
    
    db.alerts.insert_many(alerts_data)
    print(f"✅ Inserted {len(alerts_data)} alerts")
    
    print("\n✅ Database seeding completed!")
    print(f"📊 Total documents: {db.sensors.count_documents({}) + db.predictions.count_documents({}) + db.alerts.count_documents({})}")

def main():
    """Main setup function."""
    print("🚀 MongoDB Atlas Setup for RockGuard AI")
    print("=" * 50)
    
    db = setup_database()
    
    if db is not None:
        seed_minimal_data(db)
        
        # Display summary
        print("\n📊 Database Summary:")
        print(f"  - Sensors: {db.sensors.count_documents({})} documents")
        print(f"  - Predictions: {db.predictions.count_documents({})} documents")
        print(f"  - Alerts: {db.alerts.count_documents({})} documents")
        print(f"  - Users: {db.users.count_documents({})} documents")
        
        print("\n✅ MongoDB Atlas setup complete!")
        print("🔗 Connection string configured via environment variables")
    else:
        print("\n❌ Setup failed!")

if __name__ == "__main__":
    main()
