from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from typing import List, Optional
from datetime import datetime, timedelta
import logging

from ..schemas import SensorRecord, SensorBatch, SensorType, SensorStats
from ..db import sensors_col

router = APIRouter(prefix='/api/sensors', tags=['sensors'])
logger = logging.getLogger(__name__)

@router.post('', response_model=dict)
async def ingest_sensor_data(
    record: SensorRecord,
    background_tasks: BackgroundTasks
):
    """Ingest a single sensor reading."""
    
    try:
        # Convert to dict and add metadata
        sensor_data = record.model_dump()
        sensor_data['created_at'] = datetime.utcnow()
        
        # Insert into database
        result = sensors_col.insert_one(sensor_data)
        
        # Process in background (e.g., trigger alerts if needed)
        background_tasks.add_task(process_sensor_reading, sensor_data)
        
        return {
            'status': 'success',
            'id': str(result.inserted_id),
            'timestamp': sensor_data['timestamp'],
            'message': 'Sensor data ingested successfully'
        }
        
    except Exception as e:
        logger.error(f"Sensor data ingestion failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to ingest sensor data: {str(e)}"
        )

@router.post('/batch', response_model=dict)
async def ingest_sensor_batch(
    batch: SensorBatch,
    background_tasks: BackgroundTasks
):
    """Ingest multiple sensor readings."""
    
    try:
        # Convert records to dict format
        sensor_records = []
        for record in batch.records:
            sensor_data = record.model_dump()
            sensor_data['created_at'] = datetime.utcnow()
            sensor_records.append(sensor_data)
        
        # Bulk insert
        result = sensors_col.insert_many(sensor_records)
        
        # Process batch in background
        background_tasks.add_task(process_sensor_batch, sensor_records)
        
        return {
            'status': 'success',
            'inserted_count': len(result.inserted_ids),
            'ids': [str(id) for id in result.inserted_ids],
            'message': f'Batch of {len(result.inserted_ids)} sensor readings ingested'
        }
        
    except Exception as e:
        logger.error(f"Sensor batch ingestion failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to ingest sensor batch: {str(e)}"
        )

@router.get('', response_model=dict)
async def get_sensor_data(
    limit: int = Query(default=200, le=1000, description="Maximum number of records to return"),
    sensor_type: Optional[SensorType] = Query(default=None, description="Filter by sensor type"),
    start_time: Optional[datetime] = Query(default=None, description="Start time filter"),
    end_time: Optional[datetime] = Query(default=None, description="End time filter"),
    location: Optional[str] = Query(default=None, description="Filter by location")
):
    """Retrieve sensor data with optional filters."""
    
    try:
        # Build query filter
        query_filter = {}
        
        if sensor_type:
            query_filter['sensor_type'] = sensor_type
        
        if location:
            query_filter['location'] = location
        
        if start_time or end_time:
            time_filter = {}
            if start_time:
                time_filter['$gte'] = start_time
            if end_time:
                time_filter['$lte'] = end_time
            query_filter['timestamp'] = time_filter
        
        # Query database
        cursor = sensors_col.find(query_filter).sort('timestamp', -1).limit(limit)
        
        records = []
        for doc in cursor:
            doc['_id'] = str(doc['_id'])  # Convert ObjectId to string
            records.append(doc)
        
        return {
            'records': records,
            'count': len(records),
            'filters': query_filter,
            'timestamp': datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Failed to retrieve sensor data: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Could not retrieve sensor data: {str(e)}"
        )

@router.get('/latest', response_model=dict)
async def get_latest_readings():
    """Get the latest reading for each sensor type."""
    
    try:
        # Get latest reading for each sensor type
        pipeline = [
            {
                '$match': {
                    'sensor_type': {'$exists': True, '$ne': None}
                }
            },
            {
                '$sort': {'timestamp': -1}
            },
            {
                '$group': {
                    '_id': '$sensor_type',
                    'latest_record': {'$first': '$$ROOT'}
                }
            }
        ]
        
        results = list(sensors_col.aggregate(pipeline))
        
        latest_readings = {}
        for result in results:
            sensor_type = result['_id']
            record = result['latest_record']
            record['_id'] = str(record['_id'])
            latest_readings[sensor_type] = record
        
        return {
            'latest_readings': latest_readings,
            'sensor_count': len(latest_readings),
            'timestamp': datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Failed to get latest readings: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Could not get latest readings: {str(e)}"
        )

@router.get('/statistics', response_model=List[SensorStats])
async def get_sensor_statistics(
    hours: int = Query(default=24, description="Hours to look back for statistics")
):
    """Get sensor statistics for the specified time period."""
    
    try:
        # Calculate time range
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)
        
        # Aggregation pipeline for statistics
        pipeline = [
            {
                '$match': {
                    'timestamp': {'$gte': start_time, '$lte': end_time},
                    'sensor_type': {'$exists': True, '$ne': None}
                }
            },
            {
                '$group': {
                    '_id': '$sensor_type',
                    'count': {'$sum': 1},
                    'displacement_values': {'$push': '$displacement'},
                    'strain_values': {'$push': '$strain'},
                    'pore_pressure_values': {'$push': '$pore_pressure'},
                    'vibrations_values': {'$push': '$vibrations'},
                    'last_reading': {'$max': '$timestamp'}
                }
            }
        ]
        
        results = list(sensors_col.aggregate(pipeline))
        
        statistics = []
        for result in results:
            sensor_type = result['_id']
            
            # Calculate statistics for each sensor type's primary metric
            values = []
            if sensor_type == SensorType.DISPLACEMENT:
                values = [v for v in result['displacement_values'] if v is not None]
            elif sensor_type == SensorType.STRAIN:
                values = [v for v in result['strain_values'] if v is not None]
            elif sensor_type == SensorType.PORE_PRESSURE:
                values = [v for v in result['pore_pressure_values'] if v is not None]
            elif sensor_type == SensorType.VIBRATIONS:
                values = [v for v in result['vibrations_values'] if v is not None]
            
            if values:
                stats = SensorStats(
                    sensor_type=sensor_type,
                    count=result['count'],
                    avg_value=sum(values) / len(values),
                    min_value=min(values),
                    max_value=max(values),
                    last_reading=result['last_reading']
                )
                statistics.append(stats)
        
        return statistics
        
    except Exception as e:
        logger.error(f"Failed to get sensor statistics: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Could not get sensor statistics: {str(e)}"
        )

@router.get('/health')
async def sensor_system_health():
    """Check sensor system health."""
    
    try:
        # Check recent data availability
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        recent_count = sensors_col.count_documents({
            'timestamp': {'$gte': one_hour_ago}
        })
        
        # Get sensor type distribution
        sensor_distribution = list(sensors_col.aggregate([
            {
                '$group': {
                    '_id': '$sensor_type',
                    'count': {'$sum': 1},
                    'last_reading': {'$max': '$timestamp'}
                }
            }
        ]))
        
        # Check for stale sensors (no data in last 6 hours)
        six_hours_ago = datetime.utcnow() - timedelta(hours=6)
        stale_sensors = []
        
        for sensor in sensor_distribution:
            if sensor['last_reading'] < six_hours_ago:
                stale_sensors.append(sensor['_id'])
        
        # Determine health status
        status = 'healthy'
        if recent_count == 0:
            status = 'critical'
        elif len(stale_sensors) > 0:
            status = 'warning'
        
        return {
            'status': status,
            'recent_readings_1h': recent_count,
            'sensor_distribution': sensor_distribution,
            'stale_sensors': stale_sensors,
            'total_sensors': len(sensor_distribution),
            'timestamp': datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Sensor health check failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Sensor health check failed: {str(e)}"
        )

# Background task functions
async def process_sensor_reading(sensor_data: dict):
    """Process individual sensor reading for alerts."""
    try:
        # Check for anomalous readings that might indicate risk
        alerts_triggered = []
        
        # Displacement alerts
        if sensor_data.get('displacement', 0) > 10:  # > 10mm
            alerts_triggered.append('high_displacement')
        
        # Vibration alerts
        if sensor_data.get('vibrations', 0) > 1.0:  # High vibration
            alerts_triggered.append('high_vibration')
        
        # Strain alerts
        if sensor_data.get('strain', 0) > 2.0:  # High strain
            alerts_triggered.append('high_strain')
        
        # Log alerts if any
        if alerts_triggered:
            from ..db import alerts_col
            
            alert_record = {
                'type': 'sensor_alert',
                'timestamp': datetime.utcnow(),
                'sensor_data': sensor_data,
                'alerts': alerts_triggered,
                'severity': 'high' if len(alerts_triggered) > 1 else 'medium'
            }
            
            alerts_col.insert_one(alert_record)
            logger.info(f"Sensor alerts triggered: {alerts_triggered}")
        
    except Exception as e:
        logger.error(f"Failed to process sensor reading: {e}")

async def process_sensor_batch(sensor_records: List[dict]):
    """Process batch of sensor readings."""
    try:
        # Analyze batch for patterns
        high_risk_count = 0
        total_displacement = 0
        total_vibrations = 0
        
        for record in sensor_records:
            displacement = record.get('displacement', 0)
            vibrations = record.get('vibrations', 0)
            
            total_displacement += displacement
            total_vibrations += vibrations
            
            if displacement > 10 or vibrations > 1.0:
                high_risk_count += 1
        
        # Log batch analysis
        if high_risk_count > 0:
            from ..db import alerts_col
            
            alert_record = {
                'type': 'batch_sensor_alert',
                'timestamp': datetime.utcnow(),
                'batch_size': len(sensor_records),
                'high_risk_count': high_risk_count,
                'avg_displacement': total_displacement / len(sensor_records),
                'avg_vibrations': total_vibrations / len(sensor_records),
                'risk_percentage': (high_risk_count / len(sensor_records)) * 100
            }
            
            alerts_col.insert_one(alert_record)
            logger.info(f"Batch analysis: {high_risk_count}/{len(sensor_records)} high-risk readings")
        
    except Exception as e:
        logger.error(f"Failed to process sensor batch: {e}")