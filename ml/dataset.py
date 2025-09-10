from __future__ import annotations
from pathlib import Path
import pandas as pd
import numpy as np
from typing import Tuple, Optional
from .features import (
    load_env_features, 
    load_sensor_csvs, 
    build_tabular_features, 
    create_risk_labels,
    validate_features
)

class RockfallDataset:
    """Main dataset class for rockfall prediction."""
    
    def __init__(self, data_dir: Path):
        self.data_dir = Path(data_dir)
        self.env_path = self.data_dir / 'Sub_Division_IMD.json'
        self.sensor_dir = self.data_dir / 'sensors'
        self.df = None
        self.validation_results = None
    
    def load(self, create_labels: bool = True) -> pd.DataFrame:
        """Load and process all data sources."""
        print("Loading environmental data...")
        env_df = load_env_features(self.env_path)
        
        print("Loading sensor data...")
        sensor_df = load_sensor_csvs(self.sensor_dir)
        
        print("Building features...")
        df = build_tabular_features(env_df, sensor_df)
        
        if create_labels and not df.empty:
            print("Creating risk labels...")
            df = create_risk_labels(df)
        
        # Validate the dataset
        self.validation_results = validate_features(df)
        print(f"Dataset validation: {self.validation_results['status']}")
        
        if self.validation_results['warnings']:
            print("Warnings:")
            for warning in self.validation_results['warnings']:
                print(f"  - {warning}")
        
        self.df = df
        return df
    
    def get_train_test_split(
        self, 
        test_size: float = 0.2, 
        random_state: int = 42,
        stratify: bool = True
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
        """Split data into training and testing sets."""
        if self.df is None:
            raise ValueError("Dataset not loaded. Call load() first.")
        
        if 'risk' not in self.df.columns:
            raise ValueError("Risk labels not found. Ensure create_labels=True when loading.")
        
        # Prepare features and target
        feature_cols = [col for col in self.df.columns 
                       if col not in ['risk', 'risk_probability', 'timestamp']]
        
        X = self.df[feature_cols]
        y = self.df['risk']
        
        # Handle missing values in features
        X = X.fillna(0)
        
        from sklearn.model_selection import train_test_split
        
        stratify_y = y if stratify and len(y.unique()) > 1 else None
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, 
            test_size=test_size, 
            random_state=random_state,
            stratify=stratify_y
        )
        
        return X_train, X_test, y_train, y_test
    
    def get_feature_names(self) -> list:
        """Get list of feature column names."""
        if self.df is None:
            return []
        
        return [col for col in self.df.columns 
                if col not in ['risk', 'risk_probability', 'timestamp']]
    
    def get_latest_data(self, n_records: int = 1) -> pd.DataFrame:
        """Get the most recent n records for prediction."""
        if self.df is None or self.df.empty:
            return pd.DataFrame()
        
        # Sort by timestamp if available
        if 'timestamp' in self.df.columns:
            sorted_df = self.df.sort_values('timestamp', ascending=False)
        else:
            sorted_df = self.df
        
        return sorted_df.head(n_records)
    
    def summary_stats(self) -> dict:
        """Get summary statistics of the dataset."""
        if self.df is None:
            return {}
        
        stats = {
            'total_records': len(self.df),
            'date_range': None,
            'feature_count': len(self.get_feature_names()),
            'risk_distribution': None,
            'missing_data_percentage': None
        }
        
        # Date range
        if 'timestamp' in self.df.columns:
            stats['date_range'] = {
                'start': self.df['timestamp'].min(),
                'end': self.df['timestamp'].max(),
                'duration_days': (self.df['timestamp'].max() - self.df['timestamp'].min()).days
            }
        
        # Risk distribution
        if 'risk' in self.df.columns:
            risk_counts = self.df['risk'].value_counts()
            stats['risk_distribution'] = {
                'low_risk': risk_counts.get(0, 0),
                'high_risk': risk_counts.get(1, 0),
                'risk_percentage': (risk_counts.get(1, 0) / len(self.df)) * 100
            }
        
        # Missing data
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            missing_pct = (self.df[numeric_cols].isnull().sum().sum() / 
                          (len(self.df) * len(numeric_cols))) * 100
            stats['missing_data_percentage'] = missing_pct
        
        return stats
    
    def export_processed_data(self, output_path: Path) -> bool:
        """Export processed dataset to CSV."""
        if self.df is None:
            return False
        
        try:
            self.df.to_csv(output_path, index=False)
            print(f"Exported processed data to {output_path}")
            return True
        except Exception as e:
            print(f"Error exporting data: {e}")
            return False
    
    def create_synthetic_data(
        self, 
        n_samples: int = 1000, 
        start_date: str = "2025-01-01"
    ) -> pd.DataFrame:
        """Create synthetic dataset for testing when real data is not available."""
        print(f"Creating synthetic dataset with {n_samples} samples...")
        
        # Create time index
        timestamps = pd.date_range(start=start_date, periods=n_samples, freq='1H')
        
        # Generate synthetic features
        np.random.seed(42)
        
        data = {
            'timestamp': timestamps,
            'rainfall_mm': np.random.exponential(5, n_samples),
            'temperature_c': 20 + 10 * np.sin(np.arange(n_samples) * 2 * np.pi / (24 * 7)) + np.random.normal(0, 3, n_samples),
            'ambient_vibration': np.random.gamma(2, 0.2, n_samples),
            'displacement': np.random.gamma(1.5, 2, n_samples),
            'strain': np.random.normal(0.5, 0.3, n_samples),
            'pore_pressure': np.random.normal(1.2, 0.4, n_samples),
            'vibrations': np.random.gamma(1.8, 0.3, n_samples),
            'humidity': np.random.normal(60, 15, n_samples),
            'wind_speed': np.random.weibull(1.5, n_samples) * 10,
            'pressure': np.random.normal(1013.25, 15, n_samples)
        }
        
        # Ensure non-negative values where appropriate
        for col in ['rainfall_mm', 'ambient_vibration', 'displacement', 'vibrations', 'wind_speed']:
            data[col] = np.maximum(data[col], 0)
        
        # Clip values to reasonable ranges
        data['temperature_c'] = np.clip(data['temperature_c'], -10, 45)
        data['humidity'] = np.clip(data['humidity'], 0, 100)
        data['strain'] = np.maximum(data['strain'], 0)
        data['pore_pressure'] = np.maximum(data['pore_pressure'], 0)
        
        df = pd.DataFrame(data)
        
        # Apply feature engineering
        df = build_tabular_features(df, pd.DataFrame())
        
        # Create risk labels
        df = create_risk_labels(df)
        
        self.df = df
        self.validation_results = validate_features(df)
        
        print(f"Generated synthetic dataset: {len(df)} samples, {len(df.columns)} features")
        return df


def load_sample_environmental_data() -> dict:
    """Create sample environmental data structure for testing."""
    return {
        "records": [
            {
                "timestamp": "2025-01-01T00:00:00Z",
                "rainfall_mm": 0.0,
                "temperature_c": 22.5,
                "humidity": 65.0,
                "wind_speed": 5.2,
                "pressure": 1013.25,
                "vibrations": 0.3
            },
            {
                "timestamp": "2025-01-01T01:00:00Z",
                "rainfall_mm": 2.5,
                "temperature_c": 22.0,
                "humidity": 68.0,
                "wind_speed": 6.1,
                "pressure": 1012.8,
                "vibrations": 0.4
            },
            {
                "timestamp": "2025-01-01T02:00:00Z",
                "rainfall_mm": 15.2,
                "temperature_c": 21.5,
                "humidity": 75.0,
                "wind_speed": 8.3,
                "pressure": 1011.5,
                "vibrations": 0.7
            }
        ]
    }


if __name__ == "__main__":
    # Example usage
    from pathlib import Path
    
    # Initialize dataset
    data_dir = Path(__file__).parent.parent / 'data'
    dataset = RockfallDataset(data_dir)
    
    # Try to load real data, fallback to synthetic
    try:
        df = dataset.load()
        if df.empty:
            print("No real data found, creating synthetic dataset...")
            df = dataset.create_synthetic_data(n_samples=2000)
    except Exception as e:
        print(f"Error loading data: {e}")
        print("Creating synthetic dataset...")
        df = dataset.create_synthetic_data(n_samples=2000)
    
    # Print summary
    print("\nDataset Summary:")
    stats = dataset.summary_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Print validation results
    if dataset.validation_results:
        print(f"\nValidation Status: {dataset.validation_results['status']}")
        print(f"Samples: {dataset.validation_results['n_samples']}")
        print(f"Features: {dataset.validation_results['n_features']}")
        print(f"Missing Data: {dataset.validation_results['missing_percentage']:.2f}%")
