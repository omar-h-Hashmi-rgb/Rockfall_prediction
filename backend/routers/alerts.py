from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from typing import List, Optional
from datetime import datetime, timedelta
import uuid
import logging

from ..schemas import (
    AlertRequest, 
    AlertResponse, 
    AlertHistory,
    RiskLevel,
    AlertChannel
)
from ..services.alerts import alert_manager, send_alert
from ..db import alerts_col

router = APIRouter(prefix='/api/alerts', tags=['alerts'])
logger = logging.getLogger(__name__)

@router.post('', response_model=AlertResponse)
async def trigger_alert(
    request: AlertRequest,
    background_tasks: BackgroundTasks
):
    """Trigger an alert through specified channels."""
    
    try:
        # Generate alert ID
        alert_id = str(uuid.uuid4())
        
        # Send alert
        results = send_alert(
            message=request.message,
            risk_level=request.risk_level or "MEDIUM",
            probability=request.probability,
            channels=request.channels,
            location=request.location,
            metadata=request.metadata
        )
        
        # Determine overall status
        status = "success" if any(results.values()) else "failed"
        
        # Create response
        response = AlertResponse(
            alert_id=alert_id,
            status=status,
            results=results,
            message=request.message
        )
        
        # Log alert in background
        background_tasks.add_task(
            log_alert_to_database,
            alert_id,
            request,
            results,
            status
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Alert triggering failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to trigger alert: {str(e)}"
        )

@router.get('', response_model=List[AlertHistory])
async def get_alert_history(
    limit: int = Query(default=100, le=500, description="Maximum number of alerts to return"),
    alert_type: Optional[str] = Query(default=None, description="Filter by alert type"),
    risk_level: Optional[RiskLevel] = Query(default=None, description="Filter by risk level"),
    start_time: Optional[datetime] = Query(default=None, description="Start time filter"),
    end_time: Optional[datetime] = Query(default=None, description="End time filter"),
    location: Optional[str] = Query(default=None, description="Filter by location")
):
    """Get alert history with optional filters."""
    
    try:
        # Build query filter
        query_filter = {}
        
        if alert_type:
            query_filter['type'] = alert_type
        
        if risk_level:
            query_filter['risk_level'] = risk_level
        
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
        cursor = alerts_col.find(query_filter).sort('timestamp', -1).limit(limit)
        
        alerts = []
        for doc in cursor:
            # Convert to AlertHistory format
            if doc.get('type') == 'alert':
                try:
                    alert = AlertHistory(
                        alert_id=doc.get('alert_id', str(doc['_id'])),
                        message=doc.get('message', ''),
                        probability=doc.get('probability', 0.0),
                        risk_level=doc.get('risk_level', 'MEDIUM'),
                        channels=doc.get('channels', []),
                        results=doc.get('results', {}),
                        timestamp=doc.get('timestamp', datetime.utcnow()),
                        location=doc.get('location'),
                        metadata=doc.get('metadata', {})
                    )
                    alerts.append(alert)
                except Exception as e:
                    logger.warning(f"Could not parse alert record: {e}")
                    continue
        
        return alerts
        
    except Exception as e:
        logger.error(f"Failed to get alert history: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Could not get alert history: {str(e)}"
        )

@router.get('/statistics')
async def get_alert_statistics(
    hours: int = Query(default=24, description="Hours to look back for statistics")
):
    """Get alert statistics for the specified time period."""
    
    try:
        # Calculate time range
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)
        
        # Get total alerts in time range
        total_alerts = alerts_col.count_documents({
            'type': 'alert',
            'timestamp': {'$gte': start_time, '$lte': end_time}
        })
        
        # Get alerts by risk level
        risk_level_stats = list(alerts_col.aggregate([
            {
                '$match': {
                    'type': 'alert',
                    'timestamp': {'$gte': start_time, '$lte': end_time}
                }
            },
            {
                '$group': {
                    '_id': '$risk_level',
                    'count': {'$sum': 1},
                    'avg_probability': {'$avg': '$probability'}
                }
            }
        ]))
        
        # Get channel success rates
        channel_stats = list(alerts_col.aggregate([
            {
                '$match': {
                    'type': 'alert',
                    'timestamp': {'$gte': start_time, '$lte': end_time},
                    'results': {'$exists': True}
                }
            },
            {
                '$project': {
                    'email_success': '$results.email',
                    'sms_success': '$results.sms'
                }
            },
            {
                '$group': {
                    '_id': None,
                    'email_attempts': {
                        '$sum': {
                            '$cond': [{'$ne': ['$email_success', None]}, 1, 0]
                        }
                    },
                    'email_successes': {
                        '$sum': {
                            '$cond': ['$email_success', 1, 0]
                        }
                    },
                    'sms_attempts': {
                        '$sum': {
                            '$cond': [{'$ne': ['$sms_success', None]}, 1, 0]
                        }
                    },
                    'sms_successes': {
                        '$sum': {
                            '$cond': ['$sms_success', 1, 0]
                        }
                    }
                }
            }
        ]))
        
        # Get hourly distribution
        hourly_stats = list(alerts_col.aggregate([
            {
                '$match': {
                    'type': 'alert',
                    'timestamp': {'$gte': start_time, '$lte': end_time}
                }
            },
            {
                '$group': {
                    '_id': {'$hour': '$timestamp'},
                    'count': {'$sum': 1},
                    'avg_probability': {'$avg': '$probability'}
                }
            },
            {
                '$sort': {'_id': 1}
            }
        ]))
        
        # Calculate success rates
        channel_success_rates = {}
        if channel_stats:
            stats = channel_stats[0]
            
            if stats['email_attempts'] > 0:
                channel_success_rates['email'] = {
                    'success_rate': stats['email_successes'] / stats['email_attempts'],
                    'attempts': stats['email_attempts'],
                    'successes': stats['email_successes']
                }
            
            if stats['sms_attempts'] > 0:
                channel_success_rates['sms'] = {
                    'success_rate': stats['sms_successes'] / stats['sms_attempts'],
                    'attempts': stats['sms_attempts'],
                    'successes': stats['sms_successes']
                }
        
        return {
            'time_range': {
                'start': start_time,
                'end': end_time,
                'hours': hours
            },
            'total_alerts': total_alerts,
            'risk_level_distribution': risk_level_stats,
            'channel_success_rates': channel_success_rates,
            'hourly_distribution': hourly_stats,
            'timestamp': datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Failed to get alert statistics: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Could not get alert statistics: {str(e)}"
        )

@router.get('/recent-high-risk')
async def get_recent_high_risk_alerts(
    limit: int = Query(default=10, le=50)
):
    """Get recent high-risk alerts."""
    
    try:
        # Query for high-risk alerts
        cursor = alerts_col.find({
            'type': 'alert',
            'risk_level': 'HIGH'
        }).sort('timestamp', -1).limit(limit)
        
        alerts = []
        for doc in cursor:
            doc['_id'] = str(doc['_id'])
            alerts.append(doc)
        
        return {
            'high_risk_alerts': alerts,
            'count': len(alerts),
            'timestamp': datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Failed to get high-risk alerts: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Could not get high-risk alerts: {str(e)}"
        )

@router.post('/test')
async def test_alert_channels(
    channels: List[AlertChannel],
    background_tasks: BackgroundTasks
):
    """Test alert channels with a test message."""
    
    try:
        test_message = "This is a test alert from the Rockfall Prediction System."
        
        # Send test alert
        results = send_alert(
            message=test_message,
            risk_level="LOW",
            probability=0.1,
            channels=channels,
            location="Test Location"
        )
        
        # Log test alert
        background_tasks.add_task(
            log_test_alert,
            channels,
            results
        )
        
        return {
            'status': 'test_completed',
            'channels_tested': channels,
            'results': results,
            'timestamp': datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Alert channel test failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Alert channel test failed: {str(e)}"
        )

@router.get('/health')
async def alert_system_health():
    """Check alert system health."""
    
    try:
        # Get health from alert manager
        health = alert_manager.health_check()
        
        # Add database statistics
        recent_alerts = alerts_col.count_documents({
            'type': 'alert',
            'timestamp': {'$gte': datetime.utcnow() - timedelta(hours=24)}
        })
        
        failed_alerts = alerts_col.count_documents({
            'type': 'alert',
            'timestamp': {'$gte': datetime.utcnow() - timedelta(hours=24)},
            '$or': [
                {'results.email': False},
                {'results.sms': False}
            ]
        })
        
        health['database_stats'] = {
            'recent_alerts_24h': recent_alerts,
            'failed_alerts_24h': failed_alerts,
            'failure_rate': failed_alerts / recent_alerts if recent_alerts > 0 else 0
        }
        
        return health
        
    except Exception as e:
        logger.error(f"Alert system health check failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Alert system health check failed: {str(e)}"
        )

# Background task functions
async def log_alert_to_database(
    alert_id: str,
    request: AlertRequest,
    results: dict,
    status: str
):
    """Log alert to database."""
    try:
        alert_record = {
            'type': 'alert',
            'alert_id': alert_id,
            'timestamp': datetime.utcnow(),
            'message': request.message,
            'probability': request.probability,
            'risk_level': request.risk_level or "MEDIUM",
            'channels': request.channels,
            'location': request.location,
            'metadata': request.metadata,
            'results': results,
            'status': status
        }
        
        alerts_col.insert_one(alert_record)
        logger.info(f"Alert {alert_id} logged to database")
        
    except Exception as e:
        logger.error(f"Failed to log alert to database: {e}")

async def log_test_alert(channels: List[AlertChannel], results: dict):
    """Log test alert to database."""
    try:
        test_record = {
            'type': 'test_alert',
            'timestamp': datetime.utcnow(),
            'channels_tested': channels,
            'results': results,
            'test_success': any(results.values())
        }
        
        alerts_col.insert_one(test_record)
        logger.info(f"Test alert logged: {results}")
        
    except Exception as e:
        logger.error(f"Failed to log test alert: {e}")