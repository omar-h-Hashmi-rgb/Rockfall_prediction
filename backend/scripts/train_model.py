#!/usr/bin/env python3
"""
Script to train the rockfall prediction model with your data
"""

import os
import sys
import argparse
from datetime import datetime

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.rockfall_predictor import RockfallPredictor
from data.synthetic.dem_data import generate_dem_data
from data.synthetic.sensor_data import generate_sensor_readings

def main():
    parser = argparse.ArgumentParser(description='Train the rockfall prediction model')
    parser.add_argument('--json-path', 
                       default='data/Sub_Division_IMD.json',
                       help='Path to environmental data JSON file')
    parser.add_argument('--images-dir', 
                       default='data/DroneImages/FilteredData/Images',
                       help='Path to drone images directory')
    parser.add_argument('--masks-dir', 
                       default='data/DroneImages/FilteredData/Masks',
                       help='Path to drone masks directory')
    parser.add_argument('--output-dir', 
                       default='models',
                       help='Directory to save trained models')
    
    args = parser.parse_args()
    
    print("🚀 Starting AI model training for rockfall prediction...")
    print(f"📅 Training started at: {datetime.now()}")
    print("-" * 60)
    
    # Initialize predictor
    predictor = RockfallPredictor()
    
    # Check if data files exist
    if not os.path.exists(args.json_path):
        print(f"⚠️  Warning: JSON file not found at {args.json_path}")
        print("📝 Creating synthetic environmental data...")
        # Create a basic JSON structure if file doesn't exist
        import json
        sample_env_data = [
            {
                "timestamp": datetime.now().isoformat(),
                "temperature": 25.5,
                "humidity": 65.2,
                "rainfall": 2.3,
                "wind_speed": 15.8,
                "atmospheric_pressure": 1013.25
            }
        ]
        os.makedirs(os.path.dirname(args.json_path), exist_ok=True)
        with open(args.json_path, 'w') as f:
            json.dump(sample_env_data, f, indent=2)
        print(f"✅ Created sample environmental data at {args.json_path}")
    
    # Create directories if they don't exist
    os.makedirs(args.output_dir, exist_ok=True)
    os.makedirs(os.path.dirname(args.images_dir), exist_ok=True)
    os.makedirs(os.path.dirname(args.masks_dir), exist_ok=True)
    
    try:
        # Train the model
        print("🧠 Training AI model with multi-source data...")
        results = predictor.train(
            json_path=args.json_path,
            drone_images_dir=args.images_dir,
            drone_masks_dir=args.masks_dir
        )
        
        print("\n🎉 Training completed successfully!")
        print(f"📊 Classification Accuracy: {results['classification_accuracy']:.3f}")
        print(f"📈 Probability RMSE: {results['probability_rmse']:.3f}")
        print(f"💾 Models saved to: {args.output_dir}/")
        
        print("\n📋 Model Summary:")
        print(f"   • Random Forest Classifier: 100 estimators")
        print(f"   • Gradient Boosting Regressor: 100 estimators")
        print(f"   • Feature scaling: StandardScaler")
        print(f"   • Data sources: DEM + Sensors + Images + Environment")
        
        print(f"\n✅ Training completed at: {datetime.now()}")
        
    except Exception as e:
        print(f"\n❌ Training failed with error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()