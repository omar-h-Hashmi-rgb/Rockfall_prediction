from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from ..utils.database import Database
from ..utils.alert_system import AlertSystem

router = APIRouter(prefix="/alerts", tags=["alerts"])

# Global instances
db = Database()
alert_system = AlertSystem()

@router.post("/send", response_model=Dict[str, Any])
async def send_alert(alert_data: Dict[str, Any]):
    """Send a manual alert"""
    try:
        # Validate required fields
        required_fields = ['risk_class', 'risk_probability', 'message']
        for field in required_fields:
            if field not in alert_data:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Get recipients from request or use defaults
        recipients = alert_data.get('recipients', [
            {'email': 'safety@minesite.com', 'phone': '+1234567890'}
        ])
        
        # Send alerts
        results = alert_system.send_bulk_alerts(recipients, alert_data)
        
        # Save alert record
        alert_record = {
            'type': 'manual',
            'risk_class': alert_data['risk_class'],
            'risk_probability': alert_data['risk_probability'],
            'message': alert_data['message'],
            'recipients_count': len(recipients),
            'results': results,
            'timestamp': datetime.utcnow(),
            'sent_by': alert_data.get('sent_by', 'system')
        }
        
        alert_id = db.save_alert(alert_record)
        alert_record['id'] = alert_id
        
        return {
            'alert_id': alert_id,
            'status': 'sent',
            'results': results,
            'timestamp': alert_record['timestamp'].isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Alert sending error: {str(e)}")

@router.get("/recent", response_model=List[Dict[str, Any]])
async def get_recent_alerts(limit: int = 50, alert_type: Optional[str] = None):
    """Get recent alerts with optional type filtering"""
    try:
        alerts = db.get_recent_alerts(limit)
        
        # Filter by type if specified
        if alert_type:
            alerts = [a for a in alerts if a.get('type') == alert_type]
        
        # Convert ObjectId to string and format timestamps
        for alert in alerts:
            alert['_id'] = str(alert['_id'])
            if isinstance(alert.get('timestamp'), datetime):
                alert['timestamp'] = alert['timestamp'].isoformat()
        
        return alerts
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/statistics", response_model=Dict[str, Any])
async def get_alert_statistics(days: int = 30):
    """Get alert statistics for the specified period"""
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        alerts = db.get_alerts_by_date_range(start_date, end_date)
        
        if not alerts:
            return {
                'total_alerts': 0,
                'by_risk_level': {'Low': 0, 'Medium': 0, 'High': 0},
                'by_type': {'automatic': 0, 'manual': 0},
                'success_rate': 100,
                'total_emails_sent': 0,
                'total_sms_sent': 0
            }
        
        # Calculate statistics
        total_alerts = len(alerts)
        by_risk_level = {'Low': 0, 'Medium': 0, 'High': 0}
        by_type = {'automatic': 0, 'manual': 0}
        total_emails_sent = 0
        total_sms_sent = 0
        successful_alerts = 0
        
        for alert in alerts:
            # Risk level distribution
            risk_class = alert.get('risk_class', 'Low')
            if risk_class in by_risk_level:
                by_risk_level[risk_class] += 1
            
            # Alert type distribution
            alert_type = alert.get('type', 'automatic')
            if alert_type in by_type:
                by_type[alert_type] += 1
            
            # Count sent messages
            results = alert.get('results', {})
            total_emails_sent += results.get('email_sent', 0)
            total_sms_sent += results.get('sms_sent', 0)
            
            # Success rate (consider successful if at least one message was sent)
            if results.get('email_sent', 0) > 0 or results.get('sms_sent', 0) > 0:
                successful_alerts += 1
        
        success_rate = (successful_alerts / total_alerts * 100) if total_alerts > 0 else 100
        
        return {
            'total_alerts': total_alerts,
            'by_risk_level': by_risk_level,
            'by_type': by_type,
            'success_rate': round(success_rate, 2),
            'total_emails_sent': total_emails_sent,
            'total_sms_sent': total_sms_sent,
            'period_days': days
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Statistics error: {str(e)}")

@router.post("/test", response_model=Dict[str, Any])
async def test_alert_system(test_data: Dict[str, Any]):
    """Test the alert system with sample data"""
    try:
        test_alert = {
            'risk_class': 'High',
            'risk_probability': 0.85,
            'message': 'This is a test alert from the rockfall prediction system.',
            'sector': 'Test Sector',
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Use test recipients if provided, otherwise use defaults
        test_recipients = test_data.get('recipients', [
            {'email': 'test@example.com', 'phone': '+1234567890'}
        ])
        
        # Send test alerts
        results = alert_system.send_bulk_alerts(test_recipients, test_alert)
        
        return {
            'status': 'test_completed',
            'results': results,
            'message': 'Test alert sent successfully',
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Test error: {str(e)}")

@router.put("/configuration", response_model=Dict[str, Any])
async def update_alert_configuration(config_data: Dict[str, Any]):
    """Update alert system configuration"""
    try:
        # Validate configuration data
        valid_fields = {
            'email_threshold', 'sms_threshold', 'recipients', 
            'email_template', 'sms_template', 'escalation_rules'
        }
        
        # Filter to only valid fields
        validated_config = {k: v for k, v in config_data.items() if k in valid_fields}
        
        # Save configuration to database
        config_record = {
            'type': 'alert_configuration',
            'configuration': validated_config,
            'updated_at': datetime.utcnow(),
            'updated_by': config_data.get('updated_by', 'system')
        }
        
        config_id = db.save_configuration(config_record)
        
        return {
            'status': 'configuration_updated',
            'config_id': config_id,
            'updated_fields': list(validated_config.keys()),
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Configuration error: {str(e)}")

@router.get("/configuration", response_model=Dict[str, Any])
async def get_alert_configuration():
    """Get current alert system configuration"""
    try:
        # Get latest configuration from database
        config = db.get_latest_configuration('alert_configuration')
        
        if not config:
            # Return default configuration
            return {
                'email_threshold': 0.7,
                'sms_threshold': 0.8,
                'recipients': [],
                'email_template': {
                    'subject': 'ROCKFALL ALERT - {risk_class} Risk Detected',
                    'enabled': True
                },
                'sms_template': {
                    'message': '🚨 ROCKFALL ALERT: {risk_class} risk detected ({risk_probability}% probability).',
                    'enabled': True
                },
                'escalation_rules': {
                    'enabled': False,
                    'levels': []
                }
            }
        
        # Convert ObjectId to string
        config['_id'] = str(config['_id'])
        if isinstance(config.get('updated_at'), datetime):
            config['updated_at'] = config['updated_at'].isoformat()
        
        return config.get('configuration', {})
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Configuration retrieval error: {str(e)}")