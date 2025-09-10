from pymongo import MongoClient, IndexModel, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from .config import settings
import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.client: Optional[MongoClient] = None
        self.db = None
        self._connect()
    
    def _connect(self):
        """Establish database connection."""
        try:
            self.client = MongoClient(
                settings.mongodb_uri,
                serverSelectionTimeoutMS=5000,  # 5 second timeout
                connectTimeoutMS=5000,
                socketTimeoutMS=5000
            )
            
            # Test the connection
            self.client.admin.command('ismaster')
            
            self.db = self.client[settings.mongodb_db]
            self._setup_collections()
            
            logger.info(f"Connected to MongoDB: {settings.mongodb_db}")
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    def _setup_collections(self):
        """Setup collections and indexes."""
        # Sensors collection with time-series indexing
        sensors_indexes = [
            IndexModel([("timestamp", DESCENDING)]),
            IndexModel([("sensor_type", ASCENDING), ("timestamp", DESCENDING)])
        ]
        self.db.sensors.create_indexes(sensors_indexes)
        
        # Alerts collection with timestamp indexing
        alerts_indexes = [
            IndexModel([("timestamp", DESCENDING)]),
            IndexModel([("type", ASCENDING), ("timestamp", DESCENDING)])
        ]
        self.db.alerts.create_indexes(alerts_indexes)
        
        # Users collection
        users_indexes = [
            IndexModel([("username", ASCENDING)], unique=True),
            IndexModel([("email", ASCENDING)], unique=True)
        ]
        self.db.users.create_indexes(users_indexes)
    
    def get_collection(self, name: str):
        """Get a collection by name."""
        if self.db is None:
            self._connect()
        return self.db[name]
    
    def close_connection(self):
        """Close database connection."""
        if self.client is not None:
            self.client.close()
            logger.info("Database connection closed")

# Global database instance
db_instance = Database()

# Collection shortcuts
sensors_col = db_instance.get_collection('sensors')
alerts_col = db_instance.get_collection('alerts')
users_col = db_instance.get_collection('users')
predictions_col = db_instance.get_collection('predictions')

# Health check function
def check_db_health():
    """Check database connectivity."""
    try:
        db_instance.client.admin.command('ismaster')
        return {"status": "healthy", "timestamp": datetime.utcnow()}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e), "timestamp": datetime.utcnow()}

# Cleanup function for graceful shutdown
def cleanup_db():
    """Cleanup database connections."""
    db_instance.close_connection()
