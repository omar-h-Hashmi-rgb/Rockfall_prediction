import numpy as np
import pandas as pd
import cv2
from sklearn.preprocessing import StandardScaler, LabelEncoder
from typing import Dict, List, Tuple, Any, Optional
import json
import os

class DataPreprocessor:
    """
    Data preprocessing utilities for rockfall prediction system
    """
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.feature_names = []
        
    def preprocess_environmental_data(self, json_data: Dict) -> np.ndarray:
        """Preprocess environmental data from JSON"""
        if isinstance(json_data, list):
            df = pd.DataFrame(json_data)
        else:
            df = pd.DataFrame([json_data])
        
        # Select numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        # Handle missing values
        df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
        
        # Extract features
        features = []
        if 'temperature' in df.columns:
            features.append(df['temperature'].mean())
        if 'humidity' in df.columns:
            features.append(df['humidity'].mean())
        if 'rainfall' in df.columns:
            features.append(df['rainfall'].sum())
        if 'wind_speed' in df.columns:
            features.append(df['wind_speed'].mean())
        if 'atmospheric_pressure' in df.columns:
            features.append(df['atmospheric_pressure'].mean())
        
        return np.array(features)
    
    def preprocess_sensor_data(self, sensor_readings: Dict) -> np.ndarray:
        """Preprocess geotechnical sensor data"""
        features = []
        
        # Extract key sensor metrics
        features.append(sensor_readings.get('displacement', 0.0))
        features.append(sensor_readings.get('strain', 0.0))
        features.append(sensor_readings.get('pore_pressure', 0.0))
        features.append(sensor_readings.get('vibrations', 0.0))
        
        # Add derived features
        if all(k in sensor_readings for k in ['displacement', 'strain']):
            # Displacement-strain ratio
            strain_val = sensor_readings['strain']
            if strain_val != 0:
                features.append(sensor_readings['displacement'] / strain_val)
            else:
                features.append(0.0)
        
        return np.array(features)
    
    def preprocess_image_features(self, image_path: str, mask_path: Optional[str] = None) -> np.ndarray:
        """Extract features from drone imagery"""
        if not os.path.exists(image_path):
            # Return default features if image doesn't exist
            return np.array([128.0, 50.0, 0.1, 100.0, 120.0, 110.0])
        
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                return np.array([128.0, 50.0, 0.1, 100.0, 120.0, 110.0])
            
            # Convert to different color spaces
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            features = []
            
            # Basic intensity features
            features.append(np.mean(gray))  # Mean intensity
            features.append(np.std(gray))   # Standard deviation
            
            # Texture features using edge detection
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges) / (edges.shape[0] * edges.shape[1])
            features.append(edge_density)
            
            # Color features
            b_mean, g_mean, r_mean = np.mean(image, axis=(0, 1))
            features.extend([b_mean, g_mean, r_mean])
            
            # Terrain roughness (using Laplacian variance)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            features.append(laplacian_var)
            
            # Saturation and value from HSV
            features.append(np.mean(hsv[:, :, 1]))  # Saturation
            features.append(np.mean(hsv[:, :, 2]))  # Value
            
            return np.array(features)
            
        except Exception as e:
            print(f"Error processing image {image_path}: {e}")
            return np.array([128.0, 50.0, 0.1, 100.0, 120.0, 110.0, 50.0, 100.0, 150.0])
    
    def preprocess_dem_data(self, elevation: float, slope: float, aspect: float, roughness: float) -> np.ndarray:
        """Preprocess Digital Elevation Model data"""
        features = []
        
        # Basic topographic features
        features.append(elevation)
        features.append(slope)
        features.append(aspect)
        features.append(roughness)
        
        # Derived features
        # Slope category (0: flat, 1: gentle, 2: moderate, 3: steep)
        if slope < 5:
            slope_category = 0
        elif slope < 15:
            slope_category = 1
        elif slope < 30:
            slope_category = 2
        else:
            slope_category = 3
        features.append(slope_category)
        
        # Aspect category (0: N, 1: E, 2: S, 3: W)
        aspect_category = int((aspect + 45) / 90) % 4
        features.append(aspect_category)
        
        return np.array(features)
    
    def combine_features(self, 
                        dem_features: np.ndarray,
                        sensor_features: np.ndarray,
                        image_features: np.ndarray,
                        env_features: np.ndarray) -> np.ndarray:
        """Combine all feature types into a single feature vector"""
        
        # Ensure all feature arrays are 1D
        dem_features = np.atleast_1d(dem_features)
        sensor_features = np.atleast_1d(sensor_features)
        image_features = np.atleast_1d(image_features)
        env_features = np.atleast_1d(env_features)
        
        # Combine all features
        combined = np.concatenate([
            dem_features,
            sensor_features,
            image_features,
            env_features
        ])
        
        return combined
    
    def normalize_features(self, features: np.ndarray, fit: bool = False) -> np.ndarray:
        """Normalize features using StandardScaler"""
        features_2d = features.reshape(-1, 1) if features.ndim == 1 else features
        
        if fit:
            return self.scaler.fit_transform(features_2d)
        else:
            return self.scaler.transform(features_2d)
    
    def create_feature_names(self) -> List[str]:
        """Create descriptive names for all features"""
        names = [
            # DEM features
            'elevation', 'slope', 'aspect', 'roughness', 'slope_category', 'aspect_category',
            # Sensor features
            'displacement', 'strain', 'pore_pressure', 'vibrations', 'displacement_strain_ratio',
            # Image features
            'mean_intensity', 'std_intensity', 'edge_density', 'b_mean', 'g_mean', 'r_mean',
            'laplacian_var', 'saturation', 'value',
            # Environmental features
            'temperature', 'humidity', 'rainfall', 'wind_speed', 'atmospheric_pressure'
        ]
        
        self.feature_names = names
        return names