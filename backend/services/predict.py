from __future__ import annotations
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
import logging
from datetime import datetime
import json

logger = logging.getLogger(__name__)

# Model paths
ARTIFACTS_DIR = Path(__file__).resolve().parents[2] / 'ml' / 'artifacts'
MODEL_PATH = ARTIFACTS_DIR / 'model.pkl'
FEATURE_NAMES_PATH = ARTIFACTS_DIR / 'feature_names.pkl'
METADATA_PATH = ARTIFACTS_DIR / 'model_metadata.json'

# Global model cache
_model = None
_feature_names = None
_model_metadata = None

# Risk classification thresholds
RISK_THRESHOLDS = {
    'LOW': (0.0, 0.33),
    'MEDIUM': (0.33, 0.66),
    'HIGH': (0.66, 1.0)
}

class ModelNotFoundError(Exception):
    """Raised when model artifacts are not found."""
    pass

class PredictionError(Exception):
    """Raised when prediction fails."""
    pass

def load_model():
    """Load model and feature names from artifacts."""
    global _model, _feature_names, _model_metadata
    
    if _model is not None:
        return _model, _feature_names, _model_metadata
    
    try:
        # Check if model file exists
        if not MODEL_PATH.exists():
            raise ModelNotFoundError(f"Model file not found: {MODEL_PATH}")
        
        # Load model
        _model = joblib.load(MODEL_PATH)
        logger.info(f"Loaded model from {MODEL_PATH}")
        
        # Load feature names
        if FEATURE_NAMES_PATH.exists():
            _feature_names = joblib.load(FEATURE_NAMES_PATH)
            logger.info(f"Loaded {len(_feature_names)} feature names")
        else:
            logger.warning(f"Feature names file not found: {FEATURE_NAMES_PATH}")
            _feature_names = []
        
        # Load model metadata
        if METADATA_PATH.exists():
            with open(METADATA_PATH, 'r') as f:
                _model_metadata = json.load(f)
            logger.info("Loaded model metadata")
        else:
            _model_metadata = {}
            logger.warning(f"Model metadata file not found: {METADATA_PATH}")
        
        return _model, _feature_names, _model_metadata
        
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        raise ModelNotFoundError(f"Could not load model: {e}")

def prepare_features(payload: Dict) -> pd.DataFrame:
    """Prepare features from input payload."""
    try:
        model, feature_names, metadata = load_model()
        
        # Create DataFrame from payload
        df = pd.DataFrame([payload])
        
        # Add timestamp-based features if timestamp is provided
        if 'timestamp' in payload and payload['timestamp']:
            timestamp = pd.to_datetime(payload['timestamp'])
            df['hour'] = timestamp.hour
            df['day_of_week'] = timestamp.dayofweek
            df['month'] = timestamp.month
            df['is_weekend'] = int(timestamp.dayofweek >= 5)
            df['is_night'] = int(timestamp.hour >= 22 or timestamp.hour <= 6)
        
        # Ensure all expected features exist
        for feature in feature_names:
            if feature not in df.columns:
                # Set default values based on feature type
                if 'roll' in feature or 'diff' in feature or 'pct_change' in feature:
                    df[feature] = 0.0  # Derived features default to 0
                elif 'temp' in feature.lower():
                    df[feature] = 20.0  # Default temperature
                elif 'pressure' in feature.lower():
                    df[feature] = 1013.25  # Default atmospheric pressure
                elif 'humidity' in feature.lower():
                    df[feature] = 50.0  # Default humidity
                else:
                    df[feature] = 0.0  # Default to 0 for other features
        
        # Select only the features used by the model
        df = df[feature_names]
        
        # Fill any remaining NaN values
        df = df.fillna(0)
        
        logger.debug(f"Prepared features: {df.shape[1]} columns, {df.shape[0]} rows")
        return df
        
    except Exception as e:
        logger.error(f"Feature preparation failed: {e}")
        raise PredictionError(f"Could not prepare features: {e}")

def predict_proba(payload: Dict) -> float:
    """Predict probability of rockfall risk."""
    try:
        model, feature_names, metadata = load_model()
        
        # Prepare features
        features_df = prepare_features(payload)
        
        # Make prediction
        probability = model.predict_proba(features_df)[0, 1]
        
        logger.debug(f"Predicted probability: {probability:.4f}")
        return float(probability)
        
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        raise PredictionError(f"Prediction failed: {e}")

def predict_batch(payloads: List[Dict]) -> List[float]:
    """Predict probabilities for multiple inputs."""
    try:
        model, feature_names, metadata = load_model()
        
        # Prepare all features at once
        all_features = []
        for payload in payloads:
            features_df = prepare_features(payload)
            all_features.append(features_df.iloc[0])
        
        # Combine into single DataFrame
        batch_df = pd.DataFrame(all_features)
        batch_df = batch_df[feature_names]  # Ensure correct order
        batch_df = batch_df.fillna(0)
        
        # Batch prediction
        probabilities = model.predict_proba(batch_df)[:, 1]
        
        logger.info(f"Batch prediction completed: {len(probabilities)} predictions")
        return probabilities.tolist()
        
    except Exception as e:
        logger.error(f"Batch prediction failed: {e}")
        raise PredictionError(f"Batch prediction failed: {e}")

def classify_risk(probability: float) -> str:
    """Classify risk level based on probability."""
    for risk_level, (low, high) in RISK_THRESHOLDS.items():
        if low <= probability < high:
            return risk_level
    
    # Handle edge case where probability is exactly 1.0
    if probability >= RISK_THRESHOLDS['HIGH'][0]:
        return 'HIGH'
    
    return 'LOW'

def get_model_info() -> Dict:
    """Get information about the loaded model."""
    try:
        model, feature_names, metadata = load_model()
        
        info = {
            'model_loaded': True,
            'model_type': str(type(model).__name__),
            'n_features': len(feature_names),
            'feature_names': feature_names[:10],  # First 10 features
            'metadata': metadata
        }
        
        return info
        
    except Exception as e:
        return {
            'model_loaded': False,
            'error': str(e),
            'model_path': str(MODEL_PATH),
            'artifacts_dir': str(ARTIFACTS_DIR)
        }

def calculate_confidence(probability: float, features_df: pd.DataFrame) -> float:
    """Calculate confidence score for the prediction."""
    try:
        model, feature_names, metadata = load_model()
        
        # Get prediction probabilities for both classes
        probabilities = model.predict_proba(features_df)[0]
        
        # Confidence is the difference between the two class probabilities
        confidence = abs(probabilities[1] - probabilities[0])
        
        return float(confidence)
        
    except Exception as e:
        logger.warning(f"Could not calculate confidence: {e}")
        return 0.5  # Default confidence

def validate_input(payload: Dict) -> Tuple[bool, str]:
    """Validate input payload for prediction."""
    required_numeric_fields = [
        'rainfall_mm', 'temperature_c', 'displacement', 
        'strain', 'pore_pressure', 'vibrations'
    ]
    
    errors = []
    
    # Check for negative values where they shouldn't be
    non_negative_fields = ['rainfall_mm', 'displacement', 'strain', 'pore_pressure', 'vibrations']
    for field in non_negative_fields:
        if field in payload and payload[field] is not None and payload[field] < 0:
            errors.append(f"{field} cannot be negative")
    
    # Check temperature range
    if 'temperature_c' in payload and payload['temperature_c'] is not None:
        temp = payload['temperature_c']
        if temp < -50 or temp > 60:
            errors.append("temperature_c must be between -50 and 60")
    
    # Check humidity range
    if 'humidity' in payload and payload['humidity'] is not None:
        humidity = payload['humidity']
        if humidity < 0 or humidity > 100:
            errors.append("humidity must be between 0 and 100")
    
    # Check for extremely large values (potential errors)
    max_values = {
        'rainfall_mm': 1000,  # mm
        'displacement': 1000,  # mm
        'strain': 100,  # strain units
        'pore_pressure': 100,  # pressure units
        'vibrations': 50,  # vibration units
        'wind_speed': 200  # km/h
    }
    
    for field, max_val in max_values.items():
        if field in payload and payload[field] is not None and payload[field] > max_val:
            errors.append(f"{field} seems unusually high (>{max_val})")
    
    if errors:
        return False, "; ".join(errors)
    
    return True, "Valid"

# Health check for prediction service
def health_check() -> Dict:
    """Check health of prediction service."""
    try:
        model, feature_names, metadata = load_model()
        
        # Test prediction with dummy data
        test_payload = {
            'rainfall_mm': 10.0,
            'temperature_c': 25.0,
            'displacement': 2.0,
            'strain': 0.5,
            'pore_pressure': 1.0,
            'vibrations': 0.3
        }
        
        test_prob = predict_proba(test_payload)
        
        return {
            'status': 'healthy',
            'model_loaded': True,
            'test_prediction': test_prob,
            'n_features': len(feature_names),
            'model_metadata': metadata
        }
        
    except Exception as e:
        return {
            'status': 'unhealthy',
            'error': str(e),
            'model_loaded': False
        }

# Initialize model on import (optional)
def initialize_model():
    """Initialize model on service startup."""
    try:
        load_model()
        logger.info("Prediction service initialized successfully")
    except Exception as e:
        logger.warning(f"Could not initialize model on startup: {e}")

# Call initialization
if __name__ != "__main__":
    initialize_model()