from pymongo import MongoClient
from datetime import datetime
import os
from typing import Dict, List, Any, Optional
from bson import ObjectId

class Database:
    def __init__(self):
        self.client = MongoClient(os.getenv('MONGODB_URL', 'mongodb://localhost:27017'))
        self.db = self.client[os.getenv('DATABASE_NAME', 'rockfall_prediction')]
        
        # Collections
        self.predictions = self.db.predictions
        self.alerts = self.db.alerts
        self.sensor_data = self.db.sensor_data
        self.users = self.db.users
        self.configurations = self.db.configurations
        
    def save_prediction(self, prediction_data: Dict[str, Any]) -> str:
        """Save prediction results"""
        prediction_data['timestamp'] = datetime.utcnow()
        result = self.predictions.insert_one(prediction_data)
        return str(result.inserted_id)
    
    def save_alert(self, alert_data: Dict[str, Any]) -> str:
        """Save alert information"""
        alert_data['timestamp'] = datetime.utcnow()
        alert_data['status'] = 'sent'
        result = self.alerts.insert_one(alert_data)
        return str(result.inserted_id)
    
    def save_sensor_data(self, sensor_data: Dict[str, Any]) -> str:
        """Save sensor readings"""
        sensor_data['timestamp'] = datetime.utcnow()
        result = self.sensor_data.insert_one(sensor_data)
        return str(result.inserted_id)
    
    def get_recent_predictions(self, limit: int = 100) -> List[Dict]:
        """Get recent predictions"""
        return list(self.predictions.find().sort('timestamp', -1).limit(limit))
    
    def get_recent_alerts(self, limit: int = 50) -> List[Dict]:
        """Get recent alerts"""
        return list(self.alerts.find().sort('timestamp', -1).limit(limit))
    
    def get_sensor_data_range(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Get sensor data within date range"""
        return list(self.sensor_data.find({
            'timestamp': {'$gte': start_date, '$lte': end_date}
        }).sort('timestamp', -1))
    
    def get_predictions_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Get predictions within date range"""
        return list(self.predictions.find({
            'timestamp': {'$gte': start_date, '$lte': end_date}
        }).sort('timestamp', -1))
    
    def get_alerts_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Get alerts within date range"""
        return list(self.alerts.find({
            'timestamp': {'$gte': start_date, '$lte': end_date}
        }).sort('timestamp', -1))
    
    def get_risk_statistics(self) -> Dict[str, Any]:
        """Get risk statistics"""
        pipeline = [
            {
                '$group': {
                    '_id': '$risk_class',
                    'count': {'$sum': 1},
                    'avg_probability': {'$avg': '$risk_probability'}
                }
            }
        ]
        
        stats = list(self.predictions.aggregate(pipeline))
        return {stat['_id']: {'count': stat['count'], 'avg_probability': stat['avg_probability']} for stat in stats}
    
    def delete_prediction(self, prediction_id: str) -> bool:
        """Delete a prediction by ID"""
        try:
            result = self.predictions.delete_one({'_id': ObjectId(prediction_id)})
            return result.deleted_count > 0
        except:
            return False
    
    def save_configuration(self, config_data: Dict[str, Any]) -> str:
        """Save system configuration"""
        config_data['created_at'] = datetime.utcnow()
        result = self.configurations.insert_one(config_data)
        return str(result.inserted_id)
    
    def get_latest_configuration(self, config_type: str) -> Optional[Dict[str, Any]]:
        """Get latest configuration of specified type"""
        return self.configurations.find_one(
            {'type': config_type}, 
            sort=[('created_at', -1)]
        )