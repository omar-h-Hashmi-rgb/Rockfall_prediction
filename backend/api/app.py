from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
from datetime import datetime, timedelta
import numpy as np

from models.rockfall_predictor import RockfallPredictor
from utils.database import Database
from utils.alert_system import AlertSystem
from utils.map_integration import MapMyIndiaIntegration

app = FastAPI(title="Rockfall Prediction API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
predictor = RockfallPredictor()
db = Database()
alert_system = AlertSystem()
map_integration = MapMyIndiaIntegration()

# Load trained model if exists
try:
    predictor.load_models()
    print("Loaded existing trained model")
except:
    print("No trained model found, will need to train first")

@app.on_event("startup")
async def startup_event():
    print("Rockfall Prediction API starting up...")
    
    # Train model if not already trained
    if not predictor.is_trained:
        print("Training model with available data...")
        try:
            json_path = "data/Sub_Division_IMD.json"
            drone_images_dir = "data/DroneImages/FilteredData/Images"
            drone_masks_dir = "data/DroneImages/FilteredData/Masks"
            
            # Check if data files exist
            if os.path.exists(json_path):
                results = predictor.train(json_path, drone_images_dir, drone_masks_dir)
                print(f"Model training completed: {results}")
            else:
                print("Training data not found, using pre-trained model or synthetic data")
        except Exception as e:
            print(f"Error during model training: {e}")

@app.get("/")
async def root():
    return {"message": "Rockfall Prediction API", "status": "active"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "model_trained": predictor.is_trained
    }

@app.post("/predict")
async def predict_rockfall(data: dict):
    """Make rockfall prediction"""
    try:
        # Extract features from input data
        features = np.array([
            data.get('elevation', 1500),
            data.get('slope', 30),
            data.get('aspect', 180),
            data.get('roughness', 1.0),
            data.get('displacement', 1.0),
            data.get('strain', 100),
            data.get('pore_pressure', 200),
            data.get('vibrations', 0.05),
            data.get('mean_intensity', 128),
            data.get('std_intensity', 50),
            data.get('edge_density', 0.1),
            data.get('b_mean', 100),
            data.get('g_mean', 120),
            data.get('r_mean', 110)
        ])
        
        # Make prediction
        prediction = predictor.predict(features)
        
        # Add coordinates if provided
        if 'coordinates' in data:
            prediction['coordinates'] = data['coordinates']
        
        # Save prediction to database
        prediction_id = db.save_prediction(prediction)
        prediction['id'] = prediction_id
        
        # Send alert if high risk
        if prediction['alert_required']:
            alert_data = {
                'prediction_id': prediction_id,
                'risk_class': prediction['risk_class'],
                'risk_probability': prediction['risk_probability'],
                'coordinates': data.get('coordinates', {}),
                'sector': data.get('sector', 'Unknown')
            }
            
            # Example recipients (in real implementation, get from database)
            recipients = [
                {'email': 'safety@minesite.com', 'phone': '+1234567890'}
            ]
            
            alert_results = alert_system.send_bulk_alerts(recipients, alert_data)
            
            # Save alert to database
            alert_data['results'] = alert_results
            db.save_alert(alert_data)
        
        return prediction
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@app.get("/predictions/recent")
async def get_recent_predictions(limit: int = 100):
    """Get recent predictions"""
    try:
        predictions = db.get_recent_predictions(limit)
        # Convert ObjectId to string
        for pred in predictions:
            pred['_id'] = str(pred['_id'])
        return predictions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/alerts/recent")
async def get_recent_alerts(limit: int = 50):
    """Get recent alerts"""
    try:
        alerts = db.get_recent_alerts(limit)
        # Convert ObjectId to string
        for alert in alerts:
            alert['_id'] = str(alert['_id'])
        return alerts
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/dashboard/stats")
async def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        risk_stats = db.get_risk_statistics()
        
        # Get recent sensor data (last 24 hours)
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=1)
        recent_sensor_data = db.get_sensor_data_range(start_date, end_date)
        
        return {
            'risk_statistics': risk_stats,
            'recent_sensor_count': len(recent_sensor_data),
            'total_predictions': db.predictions.count_documents({}),
            'total_alerts': db.alerts.count_documents({}),
            'last_updated': datetime.utcnow()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stats error: {str(e)}")

@app.get("/map/risk-overlay")
async def get_risk_overlay():
    """Get risk overlay data for maps"""
    try:
        recent_predictions = db.get_recent_predictions(50)
        overlay_data = map_integration.get_risk_overlay_data(recent_predictions)
        return overlay_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Map error: {str(e)}")

@app.post("/sensors/data")
async def save_sensor_data(data: dict):
    """Save sensor data"""
    try:
        sensor_id = db.save_sensor_data(data)
        return {"id": sensor_id, "status": "saved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sensor data error: {str(e)}")

@app.get("/sensors/data")
async def get_sensor_data(hours: int = 24):
    """Get sensor data for specified hours"""
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(hours=hours)
        sensor_data = db.get_sensor_data_range(start_date, end_date)
        
        # Convert ObjectId to string
        for data in sensor_data:
            data['_id'] = str(data['_id'])
        
        return sensor_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sensor data error: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", 8000)),
        reload=True
    )