from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import numpy as np

from ..utils.database import Database

router = APIRouter(prefix="/sensors", tags=["sensors"])

# Global instances
db = Database()

@router.post("/data", response_model=Dict[str, Any])
async def save_sensor_reading(sensor_data: Dict[str, Any]):
    """Save a new sensor reading"""
    try:
        # Validate required fields
        required_fields = ['sensor_id', 'readings']
        for field in required_fields:
            if field not in sensor_data:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Add timestamp if not provided
        if 'timestamp' not in sensor_data:
            sensor_data['timestamp'] = datetime.utcnow()
        
        # Validate sensor readings
        readings = sensor_data['readings']
        expected_readings = ['displacement', 'strain', 'pore_pressure', 'vibration']
        
        for reading_type in expected_readings:
            if reading_type not in readings:
                readings[reading_type] = 0.0
        
        # Add data quality metrics
        sensor_data['data_quality'] = {
            'completeness': len([r for r in expected_readings if readings.get(r) is not None]) / len(expected_readings),
            'anomaly_score': calculate_anomaly_score(readings),
            'calibration_status': sensor_data.get('calibration_status', 'unknown')
        }
        
        # Save to database
        reading_id = db.save_sensor_data(sensor_data)
        
        return {
            'id': reading_id,
            'status': 'saved',
            'sensor_id': sensor_data['sensor_id'],
            'timestamp': sensor_data['timestamp'].isoformat() if isinstance(sensor_data['timestamp'], datetime) else sensor_data['timestamp']
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sensor data error: {str(e)}")

@router.get("/data", response_model=List[Dict[str, Any]])
async def get_sensor_data(
    hours: int = 24, 
    sensor_id: Optional[str] = None,
    reading_type: Optional[str] = None
):
    """Get sensor data for the specified time period"""
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(hours=hours)
        
        sensor_data = db.get_sensor_data_range(start_date, end_date)
        
        # Filter by sensor_id if specified
        if sensor_id:
            sensor_data = [s for s in sensor_data if s.get('sensor_id') == sensor_id]
        
        # Filter by reading type if specified
        if reading_type:
            filtered_data = []
            for data in sensor_data:
                readings = data.get('readings', {})
                if reading_type in readings:
                    filtered_reading = {
                        'sensor_id': data.get('sensor_id'),
                        'timestamp': data.get('timestamp'),
                        'reading_type': reading_type,
                        'value': readings[reading_type],
                        'unit': get_reading_unit(reading_type)
                    }
                    filtered_data.append(filtered_reading)
            sensor_data = filtered_data
        
        # Convert ObjectId to string and format timestamps
        for data in sensor_data:
            if '_id' in data:
                data['_id'] = str(data['_id'])
            if isinstance(data.get('timestamp'), datetime):
                data['timestamp'] = data['timestamp'].isoformat()
        
        return sensor_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sensor data retrieval error: {str(e)}")

@router.get("/status", response_model=Dict[str, Any])
async def get_sensor_status():
    """Get overall sensor network status"""
    try:
        # Get recent sensor data (last hour)
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(hours=1)
        
        recent_data = db.get_sensor_data_range(start_date, end_date)
        
        # Analyze sensor status
        sensor_status = {}
        total_sensors = 0
        active_sensors = 0
        
        # Group data by sensor
        for data in recent_data:
            sensor_id = data.get('sensor_id')
            if sensor_id:
                total_sensors += 1
                
                # Check if sensor is active (has recent data)
                timestamp = data.get('timestamp')
                if isinstance(timestamp, datetime):
                    time_diff = datetime.utcnow() - timestamp
                    is_active = time_diff.total_seconds() < 3600  # Active if data within last hour
                else:
                    is_active = False
                
                if is_active:
                    active_sensors += 1
                
                # Determine sensor health
                readings = data.get('readings', {})
                data_quality = data.get('data_quality', {})
                
                health_score = calculate_sensor_health(readings, data_quality)
                
                sensor_status[sensor_id] = {
                    'status': 'active' if is_active else 'inactive',
                    'last_reading': timestamp.isoformat() if isinstance(timestamp, datetime) else timestamp,
                    'health_score': health_score,
                    'readings': readings,
                    'location': data.get('location', 'Unknown')
                }
        
        # Calculate network statistics
        network_stats = {
            'total_sensors': len(sensor_status),
            'active_sensors': sum(1 for s in sensor_status.values() if s['status'] == 'active'),
            'inactive_sensors': sum(1 for s in sensor_status.values() if s['status'] == 'inactive'),
            'average_health_score': np.mean([s['health_score'] for s in sensor_status.values()]) if sensor_status else 0,
            'last_updated': datetime.utcnow().isoformat()
        }
        
        return {
            'network_stats': network_stats,
            'sensor_details': sensor_status
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sensor status error: {str(e)}")

@router.get("/statistics", response_model=Dict[str, Any])
async def get_sensor_statistics(days: int = 7, sensor_id: Optional[str] = None):
    """Get sensor statistics for the specified period"""
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        sensor_data = db.get_sensor_data_range(start_date, end_date)
        
        # Filter by sensor_id if specified
        if sensor_id:
            sensor_data = [s for s in sensor_data if s.get('sensor_id') == sensor_id]
        
        if not sensor_data:
            return {
                'total_readings': 0,
                'average_values': {},
                'trends': {},
                'anomalies_detected': 0,
                'data_quality_score': 0
            }
        
        # Calculate statistics
        reading_types = ['displacement', 'strain', 'pore_pressure', 'vibration']
        average_values = {}
        trends = {}
        total_anomalies = 0
        quality_scores = []
        
        for reading_type in reading_types:
            values = []
            timestamps = []
            
            for data in sensor_data:
                readings = data.get('readings', {})
                if reading_type in readings and readings[reading_type] is not None:
                    values.append(readings[reading_type])
                    timestamps.append(data.get('timestamp'))
            
            if values:
                average_values[reading_type] = {
                    'mean': np.mean(values),
                    'std': np.std(values),
                    'min': np.min(values),
                    'max': np.max(values),
                    'unit': get_reading_unit(reading_type)
                }
                
                # Calculate trend (simple linear regression slope)
                if len(values) > 1:
                    x = np.arange(len(values))
                    trend_slope = np.polyfit(x, values, 1)[0]
                    trends[reading_type] = {
                        'slope': float(trend_slope),
                        'direction': 'increasing' if trend_slope > 0 else 'decreasing' if trend_slope < 0 else 'stable'
                    }
        
        # Count anomalies
        for data in sensor_data:
            data_quality = data.get('data_quality', {})
            if data_quality.get('anomaly_score', 0) > 0.7:
                total_anomalies += 1
            
            quality_scores.append(data_quality.get('completeness', 1.0))
        
        overall_quality = np.mean(quality_scores) if quality_scores else 1.0
        
        return {
            'total_readings': len(sensor_data),
            'period_days': days,
            'average_values': average_values,
            'trends': trends,
            'anomalies_detected': total_anomalies,
            'data_quality_score': round(overall_quality * 100, 2),
            'sensor_id': sensor_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Statistics error: {str(e)}")

def calculate_anomaly_score(readings: Dict[str, float]) -> float:
    """Calculate anomaly score for sensor readings"""
    try:
        # Simple anomaly detection based on expected ranges
        expected_ranges = {
            'displacement': (0, 10),  # mm
            'strain': (0, 500),       # micro-strain
            'pore_pressure': (0, 500), # kPa
            'vibration': (0, 1.0)     # g
        }
        
        anomaly_scores = []
        
        for reading_type, value in readings.items():
            if reading_type in expected_ranges and value is not None:
                min_val, max_val = expected_ranges[reading_type]
                
                if value < min_val or value > max_val:
                    # Severe anomaly
                    anomaly_scores.append(1.0)
                elif value < min_val * 0.1 or value > max_val * 0.9:
                    # Moderate anomaly
                    anomaly_scores.append(0.7)
                else:
                    # Normal range
                    anomaly_scores.append(0.0)
        
        return np.mean(anomaly_scores) if anomaly_scores else 0.0
        
    except Exception:
        return 0.0

def calculate_sensor_health(readings: Dict[str, float], data_quality: Dict[str, Any]) -> float:
    """Calculate overall sensor health score"""
    try:
        health_factors = []
        
        # Data completeness factor
        completeness = data_quality.get('completeness', 1.0)
        health_factors.append(completeness)
        
        # Anomaly factor (inverse of anomaly score)
        anomaly_score = data_quality.get('anomaly_score', 0.0)
        health_factors.append(1.0 - anomaly_score)
        
        # Calibration factor
        calibration_status = data_quality.get('calibration_status', 'unknown')
        if calibration_status == 'calibrated':
            health_factors.append(1.0)
        elif calibration_status == 'needs_calibration':
            health_factors.append(0.7)
        else:
            health_factors.append(0.8)
        
        # Reading validity factor
        valid_readings = sum(1 for v in readings.values() if v is not None and v >= 0)
        total_readings = len(readings)
        validity_factor = valid_readings / total_readings if total_readings > 0 else 1.0
        health_factors.append(validity_factor)
        
        return np.mean(health_factors)
        
    except Exception:
        return 0.5  # Default moderate health score

def get_reading_unit(reading_type: str) -> str:
    """Get the unit for a specific reading type"""
    units = {
        'displacement': 'mm',
        'strain': 'μs',
        'pore_pressure': 'kPa',
        'vibration': 'g'
    }
    return units.get(reading_type, '')