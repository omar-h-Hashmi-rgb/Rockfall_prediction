// MongoDB initialization script for rockfall prediction system

// Switch to the rockfall database
db = db.getSiblingDB('rockfall_db');

// Create collections with proper indexes
db.createCollection('sensors');
db.createCollection('alerts');
db.createCollection('predictions');
db.createCollection('users');

// Create indexes for sensors collection
db.sensors.createIndex({ "timestamp": -1 });
db.sensors.createIndex({ "sensor_type": 1, "timestamp": -1 });
db.sensors.createIndex({ "location": 1 });
db.sensors.createIndex({ "sensor_id": 1 });

// Create indexes for alerts collection
db.alerts.createIndex({ "timestamp": -1 });
db.alerts.createIndex({ "type": 1, "timestamp": -1 });
db.alerts.createIndex({ "risk_level": 1 });
db.alerts.createIndex({ "location": 1 });

// Create indexes for predictions collection
db.predictions.createIndex({ "timestamp": -1 });
db.predictions.createIndex({ "risk_class": 1 });
db.predictions.createIndex({ "probability": 1 });

// Create indexes for users collection
db.users.createIndex({ "username": 1 }, { unique: true });
db.users.createIndex({ "email": 1 }, { unique: true });

// Insert default admin user
db.users.insertOne({
  username: "admin",
  email: "admin@rockfall.system",
  password_hash: "hashed_password_here", // In production, use proper hashing
  role: "admin",
  created_at: new Date(),
  is_active: true,
  permissions: ["read", "write", "admin"]
});

// Insert sample demo user
db.users.insertOne({
  username: "demo_user",
  email: "demo@rockfall.system", 
  password_hash: "demo_password_hash",
  role: "operator",
  created_at: new Date(),
  is_active: true,
  permissions: ["read", "write"]
});

print("✅ Rockfall database initialized successfully!");
print("📊 Collections created: sensors, alerts, predictions, users");
print("🔍 Indexes created for optimal query performance");
print("👤 Default users created: admin, demo_user");