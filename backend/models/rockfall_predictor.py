import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, mean_squared_error
import joblib
import json
import cv2
import os
from typing import Dict, List, Tuple, Any

class RockfallPredictor:
    def __init__(self):
        self.classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        self.regressor = GradientBoostingRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
        
    def load_environmental_data(self, json_path: str) -> pd.DataFrame:
        """Load environmental data from JSON file"""
        with open(json_path, 'r') as f:
            data = json.load(f)
        return pd.DataFrame(data)
    
    def generate_synthetic_dem_data(self, num_samples: int = 1000) -> np.ndarray:
        """Generate synthetic Digital Elevation Model data"""
        # Simulate terrain elevation with realistic patterns
        elevation_data = []
        for i in range(num_samples):
            # Base elevation with some randomness
            base_elevation = np.random.normal(1500, 300)  # meters
            # Slope gradient (important for rockfall risk)
            slope = np.random.uniform(15, 75)  # degrees
            # Aspect (direction of slope)
            aspect = np.random.uniform(0, 360)  # degrees
            # Roughness index
            roughness = np.random.uniform(0.1, 2.5)
            
            elevation_data.append([base_elevation, slope, aspect, roughness])
        
        return np.array(elevation_data)
    
    def generate_synthetic_sensor_data(self, num_samples: int = 1000) -> np.ndarray:
        """Generate synthetic geotechnical sensor data"""
        sensor_data = []
        for i in range(num_samples):
            # Displacement (mm)
            displacement = np.random.exponential(2.0)
            # Strain (micro-strain)
            strain = np.random.normal(100, 50)
            # Pore pressure (kPa)
            pore_pressure = np.random.normal(200, 75)
            # Vibrations (acceleration in g)
            vibrations = np.random.exponential(0.1)
            
            sensor_data.append([displacement, strain, pore_pressure, vibrations])
        
        return np.array(sensor_data)
    
    def process_drone_images(self, image_dir: str, mask_dir: str) -> np.ndarray:
        """Process drone images and extract features"""
        features = []
        
        # Get list of images (assuming you have 1000+ images)
        image_files = [f for f in os.listdir(image_dir) if f.endswith(('.jpg', '.png', '.jpeg'))][:100]  # Sample first 100
        
        for img_file in image_files:
            try:
                # Load image
                img_path = os.path.join(image_dir, img_file)
                img = cv2.imread(img_path)
                
                if img is None:
                    continue
                
                # Convert to grayscale
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                
                # Extract features
                mean_intensity = np.mean(gray)
                std_intensity = np.std(gray)
                
                # Edge detection for texture analysis
                edges = cv2.Canny(gray, 50, 150)
                edge_density = np.sum(edges) / (gray.shape[0] * gray.shape[1])
                
                # Color analysis
                b_mean, g_mean, r_mean = np.mean(img, axis=(0, 1))
                
                features.append([mean_intensity, std_intensity, edge_density, b_mean, g_mean, r_mean])
                
            except Exception as e:
                print(f"Error processing image {img_file}: {e}")
                continue
        
        return np.array(features) if features else np.random.rand(100, 6)
    
    def create_risk_labels(self, num_samples: int) -> Tuple[np.ndarray, np.ndarray]:
        """Create synthetic risk labels for training"""
        # Risk classification (0: Low, 1: Medium, 2: High)
        risk_classes = np.random.choice([0, 1, 2], size=num_samples, p=[0.6, 0.3, 0.1])
        
        # Risk probability (0-1)
        risk_probabilities = []
        for risk_class in risk_classes:
            if risk_class == 0:  # Low risk
                prob = np.random.uniform(0.0, 0.3)
            elif risk_class == 1:  # Medium risk
                prob = np.random.uniform(0.3, 0.7)
            else:  # High risk
                prob = np.random.uniform(0.7, 1.0)
            risk_probabilities.append(prob)
        
        return risk_classes, np.array(risk_probabilities)
    
    def prepare_training_data(self, json_path: str, drone_images_dir: str, drone_masks_dir: str) -> Dict[str, Any]:
        """Prepare all training data"""
        print("Loading environmental data...")
        env_data = self.load_environmental_data(json_path)
        
        print("Generating synthetic DEM data...")
        dem_data = self.generate_synthetic_dem_data(1000)
        
        print("Generating synthetic sensor data...")
        sensor_data = self.generate_synthetic_sensor_data(1000)
        
        print("Processing drone images...")
        if os.path.exists(drone_images_dir):
            image_features = self.process_drone_images(drone_images_dir, drone_masks_dir)
        else:
            print("Drone images directory not found, using synthetic data")
            image_features = np.random.rand(1000, 6)
        
        # Ensure all arrays have the same number of samples
        min_samples = min(len(env_data), len(dem_data), len(sensor_data), len(image_features))
        
        # Combine all features
        combined_features = np.hstack([
            dem_data[:min_samples],  # DEM features (4)
            sensor_data[:min_samples],  # Sensor features (4)
            image_features[:min_samples],  # Image features (6)
            env_data.iloc[:min_samples].select_dtypes(include=[np.number]).values  # Environmental (varies)
        ])
        
        # Create labels
        risk_classes, risk_probabilities = self.create_risk_labels(min_samples)
        
        return {
            'features': combined_features,
            'risk_classes': risk_classes,
            'risk_probabilities': risk_probabilities,
            'feature_names': ['elevation', 'slope', 'aspect', 'roughness',
                            'displacement', 'strain', 'pore_pressure', 'vibrations',
                            'mean_intensity', 'std_intensity', 'edge_density', 'b_mean', 'g_mean', 'r_mean']
        }
    
    def train(self, json_path: str, drone_images_dir: str, drone_masks_dir: str):
        """Train the rockfall prediction model"""
        print("Preparing training data...")
        data = self.prepare_training_data(json_path, drone_images_dir, drone_masks_dir)
        
        X = data['features']
        y_class = data['risk_classes']
        y_prob = data['risk_probabilities']
        
        # Split data
        X_train, X_test, y_class_train, y_class_test, y_prob_train, y_prob_test = train_test_split(
            X, y_class, y_prob, test_size=0.2, random_state=42
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train classifier
        print("Training risk classifier...")
        self.classifier.fit(X_train_scaled, y_class_train)
        
        # Train regressor
        print("Training probability regressor...")
        self.regressor.fit(X_train_scaled, y_prob_train)
        
        # Evaluate models
        class_pred = self.classifier.predict(X_test_scaled)
        prob_pred = self.regressor.predict(X_test_scaled)
        
        class_accuracy = accuracy_score(y_class_test, class_pred)
        prob_rmse = np.sqrt(mean_squared_error(y_prob_test, prob_pred))
        
        print(f"Classification Accuracy: {class_accuracy:.3f}")
        print(f"Probability RMSE: {prob_rmse:.3f}")
        
        self.is_trained = True
        
        # Save models
        self.save_models()
        
        return {
            'classification_accuracy': class_accuracy,
            'probability_rmse': prob_rmse
        }
    
    def predict(self, features: np.ndarray) -> Dict[str, Any]:
        """Make rockfall predictions"""
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        # Scale features
        features_scaled = self.scaler.transform(features.reshape(1, -1))
        
        # Get predictions
        risk_class = self.classifier.predict(features_scaled)[0]
        risk_probability = self.regressor.predict(features_scaled)[0]
        
        # Get class probabilities
        class_probabilities = self.classifier.predict_proba(features_scaled)[0]
        
        risk_levels = ['Low', 'Medium', 'High']
        
        return {
            'risk_class': risk_levels[risk_class],
            'risk_probability': float(risk_probability),
            'class_probabilities': {
                'Low': float(class_probabilities[0]),
                'Medium': float(class_probabilities[1]),
                'High': float(class_probabilities[2])
            },
            'alert_required': risk_probability > 0.7
        }
    
    def save_models(self, path: str = 'models/'):
        """Save trained models"""
        os.makedirs(path, exist_ok=True)
        joblib.dump(self.classifier, f'{path}/classifier.pkl')
        joblib.dump(self.regressor, f'{path}/regressor.pkl')
        joblib.dump(self.scaler, f'{path}/scaler.pkl')
        
    def load_models(self, path: str = 'models/'):
        """Load trained models"""
        self.classifier = joblib.load(f'{path}/classifier.pkl')
        self.regressor = joblib.load(f'{path}/regressor.pkl')
        self.scaler = joblib.load(f'{path}/scaler.pkl')
        self.is_trained = True