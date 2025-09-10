from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List
import uuid
from datetime import datetime
import logging

from ..schemas import (
    PredictRequest, 
    PredictResponse, 
    BatchPredictRequest, 
    BatchPredictResponse,
    ErrorResponse
)
from ..services.predict import (
    predict_proba, 
    classify_risk, 
    validate_input,
    get_model_info,
    predict_batch
)
from ..db import predictions_col, alerts_col

router = APIRouter(prefix='/api/predict', tags=['predictions'])
logger = logging.getLogger(__name__)

@router.post('', response_model=PredictResponse)
async def predict(request: PredictRequest, background_tasks: BackgroundTasks):
    """Make a single prediction."""
    
    try:
        # Convert request to dict
        payload = request.model_dump()
        
        # Validate input
        is_valid, validation_message = validate_input(payload)
        if not is_valid:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid input: {validation_message}"
            )
        
        # Make prediction
        probability = predict_proba(payload)
        risk_class = classify_risk(probability)
        
        # Create response
        response = PredictResponse(
            probability=probability,
            risk_class=risk_class,
            timestamp=datetime.utcnow(),
            model_version="1.0"
        )
        
        # Log prediction in background
        background_tasks.add_task(
            log_prediction,
            payload,
            probability,
            risk_class
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )

@router.post('/batch', response_model=BatchPredictResponse)
async def predict_batch_endpoint(
    request: BatchPredictRequest, 
    background_tasks: BackgroundTasks
):
    """Make batch predictions."""
    
    try:
        # Convert requests to list of dicts
        payloads = [req.model_dump() for req in request.requests]
        
        # Validate all inputs
        validation_errors = []
        for i, payload in enumerate(payloads):
            is_valid, validation_message = validate_input(payload)
            if not is_valid:
                validation_errors.append(f"Request {i}: {validation_message}")
        
        if validation_errors:
            raise HTTPException(
                status_code=400,
                detail=f"Validation errors: {'; '.join(validation_errors)}"
            )
        
        # Make batch predictions
        probabilities = predict_batch(payloads)
        
        # Create responses
        predictions = []
        for i, (payload, prob) in enumerate(zip(payloads, probabilities)):
            risk_class = classify_risk(prob)
            
            prediction = PredictResponse(
                probability=prob,
                risk_class=risk_class,
                timestamp=datetime.utcnow(),
                model_version="1.0"
            )
            predictions.append(prediction)
        
        # Create batch response
        batch_id = str(uuid.uuid4())
        response = BatchPredictResponse(
            predictions=predictions,
            batch_id=batch_id,
            processed_count=len(predictions),
            timestamp=datetime.utcnow()
        )
        
        # Log batch prediction in background
        background_tasks.add_task(
            log_batch_prediction,
            batch_id,
            payloads,
            probabilities
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Batch prediction failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Batch prediction failed: {str(e)}"
        )

@router.get('/model-info')
async def model_info():
    """Get information about the loaded model."""
    try:
        info = get_model_info()
        return info
    except Exception as e:
        logger.error(f"Failed to get model info: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Could not get model info: {str(e)}"
        )

@router.get('/recent')
async def get_recent_predictions(limit: int = 50):
    """Get recent predictions from the database."""
    try:
        # Query recent predictions
        cursor = predictions_col.find().sort('timestamp', -1).limit(limit)
        predictions = []
        
        for doc in cursor:
            doc['_id'] = str(doc['_id'])  # Convert ObjectId to string
            predictions.append(doc)
        
        return {
            'predictions': predictions,
            'count': len(predictions),
            'timestamp': datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Failed to get recent predictions: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Could not get recent predictions: {str(e)}"
        )

@router.get('/statistics')
async def get_prediction_statistics():
    """Get prediction statistics."""
    try:
        # Get total predictions count
        total_predictions = predictions_col.count_documents({})
        
        # Get predictions by risk level
        risk_stats = list(predictions_col.aggregate([
            {
                '$group': {
                    '_id': '$risk_class',
                    'count': {'$sum': 1},
                    'avg_probability': {'$avg': '$probability'}
                }
            }
        ]))
        
        # Get recent activity (last 24 hours)
        from datetime import timedelta
        yesterday = datetime.utcnow() - timedelta(days=1)
        recent_count = predictions_col.count_documents({
            'timestamp': {'$gte': yesterday}
        })
        
        # Get hourly distribution for last 24 hours
        hourly_stats = list(predictions_col.aggregate([
            {
                '$match': {'timestamp': {'$gte': yesterday}}
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
        
        return {
            'total_predictions': total_predictions,
            'recent_24h': recent_count,
            'risk_distribution': risk_stats,
            'hourly_distribution': hourly_stats,
            'timestamp': datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Failed to get prediction statistics: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Could not get prediction statistics: {str(e)}"
        )

# Background task functions
async def log_prediction(payload: dict, probability: float, risk_class: str):
    """Log prediction to database."""
    try:
        log_entry = {
            'timestamp': datetime.utcnow(),
            'input': payload,
            'probability': probability,
            'risk_class': risk_class,
            'type': 'single_prediction'
        }
        
        predictions_col.insert_one(log_entry)
        
        # Also log to alerts collection for audit trail
        alerts_col.insert_one({
            'type': 'prediction_log',
            'timestamp': datetime.utcnow(),
            'probability': probability,
            'risk_class': risk_class,
            'payload': payload
        })
        
    except Exception as e:
        logger.error(f"Failed to log prediction: {e}")

async def log_batch_prediction(batch_id: str, payloads: List[dict], probabilities: List[float]):
    """Log batch prediction to database."""
    try:
        # Log individual predictions
        for payload, prob in zip(payloads, probabilities):
            risk_class = classify_risk(prob)
            log_entry = {
                'timestamp': datetime.utcnow(),
                'batch_id': batch_id,
                'input': payload,
                'probability': prob,
                'risk_class': risk_class,
                'type': 'batch_prediction'
            }
            predictions_col.insert_one(log_entry)
        
        # Log batch summary
        alerts_col.insert_one({
            'type': 'batch_prediction_log',
            'timestamp': datetime.utcnow(),
            'batch_id': batch_id,
            'batch_size': len(payloads),
            'avg_probability': sum(probabilities) / len(probabilities),
            'high_risk_count': sum(1 for p in probabilities if classify_risk(p) == 'HIGH')
        })
        
    except Exception as e:
        logger.error(f"Failed to log batch prediction: {e}")