from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import numpy as np

from ..utils.database import Database
from ..models.rockfall_predictor import RockfallPredictor
from ..models.data_preprocessor import DataPreprocessor

router = APIRouter(prefix="/predictions", tags=["predictions"])

# Global instances
predictor = RockfallPredictor()
preprocessor = DataPreprocessor()
db = Database()

@router.post("/", response_model=Dict[str, Any])
async def create_prediction(prediction_data: Dict[str, Any]):
    """Create a new rockfall prediction"""
    try:
        # Extract and preprocess features
        dem_features = preprocessor.preprocess_dem_data(
            elevation=prediction_data.get('elevation', 1500),
            slope=prediction_data.get('slope', 30),
            aspect=prediction_data.get('aspect', 180),
            roughness=prediction_data.get('roughness', 1.0)
        )
        
        sensor_features = preprocessor.preprocess_sensor_data({
            'displacement': prediction_data.get('displacement', 1.0),
            'strain': prediction_data.get('strain', 100),
            'pore_pressure': prediction_data.get('pore_pressure', 200),
            'vibrations': prediction_data.get('vibrations', 0.05)
        })
        
        # Use default image features if not provided
        image_features = np.array([
            prediction_data.get('mean_intensity', 128),
            prediction_data.get('std_intensity', 50),
            prediction_data.get('edge_density', 0.1),
            prediction_data.get('b_mean', 100),
            prediction_data.get('g_mean', 120),
            prediction_data.get('r_mean', 110),
            prediction_data.get('laplacian_var', 50),
            prediction_data.get('saturation', 100),
            prediction_data.get('value', 150)
        ])
        
        # Use default environmental features if not provided
        env_features = np.array([
            prediction_data.get('temperature', 25),
            prediction_data.get('humidity', 60),
            prediction_data.get('rainfall', 0),
            prediction_data.get('wind_speed', 10),
            prediction_data.get('atmospheric_pressure', 1013)
        ])
        
        # Combine features
        combined_features = preprocessor.combine_features(
            dem_features, sensor_features, image_features, env_features
        )
        
        # Make prediction
        if not predictor.is_trained:
            # Load model if not already loaded
            try:
                predictor.load_models()
            except:
                raise HTTPException(status_code=503, detail="Model not trained. Please train the model first.")
        
        prediction = predictor.predict(combined_features)
        
        # Add metadata
        prediction.update({
            'coordinates': prediction_data.get('coordinates', {}),
            'sector': prediction_data.get('sector', 'Unknown'),
            'timestamp': datetime.utcnow(),
            'model_version': '1.0.0'
        })
        
        # Save to database
        prediction_id = db.save_prediction(prediction)
        prediction['id'] = prediction_id
        
        return prediction
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@router.get("/recent", response_model=List[Dict[str, Any]])
async def get_recent_predictions(limit: int = 100, sector: Optional[str] = None):
    """Get recent predictions with optional sector filtering"""
    try:
        predictions = db.get_recent_predictions(limit)
        
        # Filter by sector if specified
        if sector:
            predictions = [p for p in predictions if p.get('sector') == sector]
        
        # Convert ObjectId to string for JSON serialization
        for pred in predictions:
            pred['_id'] = str(pred['_id'])
            # Ensure timestamp is properly formatted
            if isinstance(pred.get('timestamp'), datetime):
                pred['timestamp'] = pred['timestamp'].isoformat()
        
        return predictions
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/statistics", response_model=Dict[str, Any])
async def get_prediction_statistics(days: int = 7):
    """Get prediction statistics for the specified number of days"""
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get predictions in date range
        predictions = db.get_predictions_by_date_range(start_date, end_date)
        
        if not predictions:
            return {
                'total_predictions': 0,
                'risk_distribution': {'Low': 0, 'Medium': 0, 'High': 0},
                'average_probability': 0,
                'alerts_triggered': 0
            }
        
        # Calculate statistics
        total = len(predictions)
        risk_distribution = {'Low': 0, 'Medium': 0, 'High': 0}
        total_probability = 0
        alerts_triggered = 0
        
        for pred in predictions:
            risk_class = pred.get('risk_class', 'Low')
            if risk_class in risk_distribution:
                risk_distribution[risk_class] += 1
            
            total_probability += pred.get('risk_probability', 0)
            
            if pred.get('alert_required', False):
                alerts_triggered += 1
        
        return {
            'total_predictions': total,
            'risk_distribution': risk_distribution,
            'average_probability': total_probability / total if total > 0 else 0,
            'alerts_triggered': alerts_triggered,
            'period_days': days
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Statistics error: {str(e)}")

@router.get("/forecast", response_model=List[Dict[str, Any]])
async def get_risk_forecast(hours: int = 24):
    """Generate risk forecast for the next specified hours"""
    try:
        # Get recent predictions to establish baseline
        recent_predictions = db.get_recent_predictions(10)
        
        if not recent_predictions:
            # Return default forecast if no recent data
            forecast = []
            for i in range(hours):
                forecast_time = datetime.utcnow() + timedelta(hours=i)
                forecast.append({
                    'timestamp': forecast_time.isoformat(),
                    'predicted_risk_probability': 0.2 + 0.1 * np.sin(i * 0.3),
                    'confidence': 0.7,
                    'risk_class': 'Low'
                })
            return forecast
        
        # Calculate baseline risk from recent predictions
        baseline_risk = np.mean([p.get('risk_probability', 0.2) for p in recent_predictions])
        
        forecast = []
        for i in range(hours):
            forecast_time = datetime.utcnow() + timedelta(hours=i)
            
            # Simple forecast model (in production, use more sophisticated methods)
            trend = 0.01 * i  # Slight increasing trend
            noise = np.random.normal(0, 0.05)  # Random variation
            seasonal = 0.05 * np.sin(2 * np.pi * i / 24)  # Daily cycle
            
            predicted_prob = np.clip(baseline_risk + trend + noise + seasonal, 0, 1)
            
            # Determine risk class
            if predicted_prob < 0.3:
                risk_class = 'Low'
            elif predicted_prob < 0.7:
                risk_class = 'Medium'
            else:
                risk_class = 'High'
            
            forecast.append({
                'timestamp': forecast_time.isoformat(),
                'predicted_risk_probability': float(predicted_prob),
                'confidence': 0.8 - (i * 0.01),  # Confidence decreases with time
                'risk_class': risk_class
            })
        
        return forecast
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Forecast error: {str(e)}")

@router.delete("/{prediction_id}")
async def delete_prediction(prediction_id: str):
    """Delete a specific prediction"""
    try:
        result = db.delete_prediction(prediction_id)
        if result:
            return {"message": "Prediction deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Prediction not found")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete error: {str(e)}")