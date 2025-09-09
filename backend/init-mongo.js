// MongoDB initialization script
db = db.getSiblingDB('rockfall_prediction');

// Create collections
db.createCollection('predictions');
db.createCollection('alerts');
db.createCollection('sensor_data');
db.createCollection('users');

// Create indexes for better performance
db.predictions.createIndex({ "timestamp": -1 });
db.predictions.createIndex({ "risk_class": 1 });
db.predictions.createIndex({ "coordinates.lat": 1, "coordinates.lon": 1 });

db.alerts.createIndex({ "timestamp": -1 });
db.alerts.createIndex({ "risk_class": 1 });

db.sensor_data.createIndex({ "timestamp": -1 });
db.sensor_data.createIndex({ "sensor_id": 1 });

db.users.createIndex({ "email": 1 }, { unique: true });

print('Database initialized successfully');