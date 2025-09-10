from fastapi import APIRouter, HTTPException
from datetime import datetime
import psutil
import os
from ..schemas import HealthCheck
from ..db import check_db_health
from ..services.predict import health_check as model_health_check
from ..services.alerts import health_check as alerts_health_check
from ..services.mapmyindia import health_check as map_health_check

router = APIRouter(prefix='/api/health', tags=['health'])

@router.get('', response_model=HealthCheck)
async def health():
    """Comprehensive health check endpoint."""
    
    try:
        # Database health
        db_health = check_db_health()
        
        # Model health
        model_health = model_health_check()
        
        # Alert services health
        alerts_health = alerts_health_check()
        
        # MapMyIndia service health
        map_health = map_health_check()
        
        # System metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Determine overall status
        overall_status = "healthy"
        
        if (db_health['status'] == 'unhealthy' or 
            model_health['status'] == 'unhealthy' or
            cpu_percent > 90 or 
            memory.percent > 90 or 
            disk.percent > 95):
            overall_status = "unhealthy"
        elif (alerts_health['status'] in ['warning', 'error'] or
              map_health['status'] in ['warning', 'error'] or
              cpu_percent > 70 or 
              memory.percent > 80 or 
              disk.percent > 85):
            overall_status = "warning"
        
        return HealthCheck(
            status=overall_status,
            timestamp=datetime.utcnow(),
            database=db_health,
            model=model_health,
            services={
                'alerts': alerts_health,
                'map': map_health,
                'system': {
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory.percent,
                    'disk_percent': disk.percent,
                    'process_id': os.getpid()
                }
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Health check failed: {str(e)}"
        )

@router.get('/database')
async def database_health():
    """Database-specific health check."""
    return check_db_health()

@router.get('/model')
async def model_health():
    """Model-specific health check."""
    return model_health_check()

@router.get('/services')
async def services_health():
    """External services health check."""
    return {
        'alerts': alerts_health_check(),
        'map': map_health_check()
    }

@router.get('/system')
async def system_metrics():
    """System performance metrics."""
    try:
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory': {
                'percent': psutil.virtual_memory().percent,
                'available': psutil.virtual_memory().available,
                'total': psutil.virtual_memory().total
            },
            'disk': {
                'percent': psutil.disk_usage('/').percent,
                'free': psutil.disk_usage('/').free,
                'total': psutil.disk_usage('/').total
            },
            'process_id': os.getpid(),
            'timestamp': datetime.utcnow()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Could not get system metrics: {str(e)}"
        )