from __future__ import annotations
import json
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, Tuple, Optional

def load_env_features(env_json_path: Path) -> pd.DataFrame:
    """Load and process environmental data from JSON file."""
    try:
        with open(env_json_path, 'r') as f:
            env = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Warning: Could not load environmental data: {e}")
        return pd.DataFrame()
    
    # Handle different JSON structures
    records = []
    
    # If data is in 'records' key
    if 'records' in env:
        for rec in env['records']:
            records.append({
                'timestamp': rec.get('timestamp'),
                'rainfall_mm': rec.get('rainfall_mm', rec.get('rainfall', 0.0)),
                'temperature_c': rec.get('temperature_c', rec.get('temperature', 20.0)),
                'ambient_vibration': rec.get('vibrations', rec.get('ambient_vibration', 0.0)),
                'humidity': rec.get('humidity', 50.0),
                'wind_speed': rec.get('wind_speed', 0.0),
                'pressure': rec.get('pressure', 1013.25)
            })
    
    # If data is direct array
    elif isinstance(env, list):
        for rec in env:
            records.append({
                'timestamp': rec.get('timestamp'),
                'rainfall_mm': rec.get('rainfall_mm', rec.get('rainfall', 0.0)),
                'temperature_c': rec.get('temperature_c', rec.get('temperature', 20.0)),
                'ambient_vibration': rec.get('vibrations', rec.get('ambient_vibration', 0.0)),
                'humidity': rec.get('humidity', 50.0),
                'wind_speed': rec.get('wind_speed', 0.0),
                'pressure': rec.get('pressure', 1013.25)
            })
    
    # If data is flat structure
    else:
        records.append({
            'timestamp': env.get('timestamp'),
            'rainfall_mm': env.get('rainfall_mm', env.get('rainfall', 0.0)),
            'temperature_c': env.get('temperature_c', env.get('temperature', 20.0)),
            'ambient_vibration': env.get('vibrations', env.get('ambient_vibration', 0.0)),
            'humidity': env.get('humidity', 50.0),
            'wind_speed': env.get('wind_speed', 0.0),
            'pressure': env.get('pressure', 1013.25)
        })
    
    if not records:
        return pd.DataFrame()
    
    df = pd.DataFrame(records)
    
    # Convert timestamp
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        df = df.dropna(subset=['timestamp'])
        df = df.sort_values('timestamp')
    
    # Fill missing values with reasonable defaults
    numeric_cols = ['rainfall_mm', 'temperature_c', 'ambient_vibration', 'humidity', 'wind_speed', 'pressure']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)
    
    return df


def load_sensor_csvs(sensor_dir: Path) -> pd.DataFrame:
    """Load and merge sensor CSV files."""
    sensor_dir = Path(sensor_dir)
    frames = []
    
    sensor_types = ['displacement', 'strain', 'pore_pressure', 'vibrations']
    
    for name in sensor_types:
        csv_path = sensor_dir / f"{name}.csv"
        if csv_path.exists():
            try:
                df = pd.read_csv(csv_path)
                
                # Ensure required columns exist
                if 'timestamp' not in df.columns or 'value' not in df.columns:
                    print(f"Warning: {csv_path} missing required columns (timestamp, value)")
                    continue
                
                # Convert timestamp
                df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
                df = df.dropna(subset=['timestamp'])
                
                # Convert value to numeric
                df['value'] = pd.to_numeric(df['value'], errors='coerce')
                df = df.dropna(subset=['value'])
                
                # Aggregate by hour if multiple readings
                if len(df) > 0:
                    df_agg = df.groupby(pd.Grouper(key='timestamp', freq='1H'))['value'].agg(['mean', 'std', 'count']).reset_index()
                    df_agg = df_agg.rename(columns={
                        'mean': name,
                        'std': f'{name}_std',
                        'count': f'{name}_count'
                    })
                    # Fill std with 0 where count is 1
                    df_agg[f'{name}_std'] = df_agg[f'{name}_std'].fillna(0.0)
                    frames.append(df_agg)
                    
            except Exception as e:
                print(f"Error loading {csv_path}: {e}")
                continue
    
    if not frames:
        return pd.DataFrame()
    
    # Merge all sensor dataframes
    result = frames[0]
    for frame in frames[1:]:
        result = pd.merge_asof(
            result.sort_values('timestamp'), 
            frame.sort_values('timestamp'), 
            on='timestamp',
            direction='nearest',
            tolerance=pd.Timedelta('2H')
        )
    
    return result


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create advanced features from raw data."""
    if df.empty:
        return df
    
    df = df.copy()
    
    # Time-based features
    if 'timestamp' in df.columns:
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['month'] = df['timestamp'].dt.month
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        df['is_night'] = ((df['hour'] >= 22) | (df['hour'] <= 6)).astype(int)
    
    # Rolling window features
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    for col in numeric_cols:
        if col in df.columns:
            # Rolling statistics
            df[f'{col}_roll3h'] = df[col].rolling(window=3, min_periods=1).mean()
            df[f'{col}_roll6h'] = df[col].rolling(window=6, min_periods=1).mean()
            df[f'{col}_roll12h'] = df[col].rolling(window=12, min_periods=1).mean()
            
            # Rolling standard deviation
            df[f'{col}_roll3h_std'] = df[col].rolling(window=3, min_periods=1).std().fillna(0)
            
            # Differences and changes
            df[f'{col}_diff1'] = df[col].diff().fillna(0)
            df[f'{col}_diff3'] = df[col].diff(3).fillna(0)
            
            # Rate of change
            df[f'{col}_pct_change'] = df[col].pct_change().fillna(0).replace([np.inf, -np.inf], 0)
    
    # Interaction features
    if 'rainfall_mm' in df.columns and 'temperature_c' in df.columns:
        df['rain_temp_interaction'] = df['rainfall_mm'] * df['temperature_c']
    
    if 'displacement' in df.columns and 'vibrations' in df.columns:
        df['displacement_vibration_ratio'] = df['displacement'] / (df['vibrations'] + 1e-6)
    
    if 'strain' in df.columns and 'pore_pressure' in df.columns:
        df['strain_pressure_product'] = df['strain'] * df['pore_pressure']
    
    # Threshold-based features
    if 'rainfall_mm' in df.columns:
        df['heavy_rain'] = (df['rainfall_mm'] > 20).astype(int)
        df['extreme_rain'] = (df['rainfall_mm'] > 50).astype(int)
    
    if 'displacement' in df.columns:
        df['high_displacement'] = (df['displacement'] > 5).astype(int)
        df['critical_displacement'] = (df['displacement'] > 10).astype(int)
    
    if 'vibrations' in df.columns:
        df['high_vibration'] = (df['vibrations'] > 0.6).astype(int)
    
    # Cumulative features
    if 'rainfall_mm' in df.columns:
        df['rainfall_cumsum_24h'] = df['rainfall_mm'].rolling(window=24, min_periods=1).sum()
        df['rainfall_cumsum_72h'] = df['rainfall_mm'].rolling(window=72, min_periods=1).sum()
    
    return df


def build_tabular_features(env_df: pd.DataFrame, sensor_df: pd.DataFrame) -> pd.DataFrame:
    """Combine environmental and sensor data with feature engineering."""
    
    # If both dataframes are empty, return empty
    if env_df.empty and sensor_df.empty:
        return pd.DataFrame()
    
    # If one is empty, use the other
    if env_df.empty:
        df = sensor_df.copy()
    elif sensor_df.empty:
        df = env_df.copy()
    else:
        # Merge environmental and sensor data
        df = pd.merge_asof(
            env_df.sort_values('timestamp'),
            sensor_df.sort_values('timestamp'),
            on='timestamp',
            direction='nearest',
            tolerance=pd.Timedelta('30min')
        )
    
    # Apply feature engineering
    df = engineer_features(df)
    
    # Remove rows with too many missing values (keep if at least 60% of columns have data)
    min_non_null = int(0.6 * len(df.columns))
    df = df.dropna(thresh=min_non_null)
    
    # Fill remaining missing values
    # Forward fill first, then backward fill
    df = df.fillna(method='ffill').fillna(method='bfill')
    
    # If still have NaN values, fill with 0
    df = df.fillna(0)
    
    return df


def create_risk_labels(df: pd.DataFrame) -> pd.DataFrame:
    """Create synthetic risk labels based on domain knowledge."""
    if df.empty:
        return df
    
    df = df.copy()
    
    # Initialize risk score
    risk_score = np.zeros(len(df))
    
    # Rain-based risk
    if 'rainfall_mm' in df.columns:
        rain_risk = np.where(df['rainfall_mm'] > 20, 0.3, 0.0)
        rain_risk += np.where(df['rainfall_mm'] > 50, 0.2, 0.0)
        risk_score += rain_risk
    
    # Cumulative rain risk
    if 'rainfall_cumsum_24h' in df.columns:
        cum_rain_risk = np.where(df['rainfall_cumsum_24h'] > 100, 0.2, 0.0)
        risk_score += cum_rain_risk
    
    # Vibration-based risk
    if 'vibrations' in df.columns:
        vib_risk = np.where(df['vibrations'] > 0.6, 0.25, 0.0)
        vib_risk += np.where(df['vibrations'] > 1.0, 0.15, 0.0)
        risk_score += vib_risk
    
    # Displacement-based risk
    if 'displacement' in df.columns:
        disp_risk = np.where(df['displacement'] > 5, 0.3, 0.0)
        disp_risk += np.where(df['displacement'] > 10, 0.2, 0.0)
        risk_score += disp_risk
    
    # Strain-based risk
    if 'strain' in df.columns:
        strain_risk = np.where(df['strain'] > 1.0, 0.15, 0.0)
        risk_score += strain_risk
    
    # Pore pressure risk
    if 'pore_pressure' in df.columns:
        pressure_risk = np.where(df['pore_pressure'] > 2.0, 0.1, 0.0)
        risk_score += pressure_risk
    
    # Combined conditions (higher risk)
    if all(col in df.columns for col in ['rainfall_mm', 'vibrations']):
        combined_risk = np.where((df['rainfall_mm'] > 20) & (df['vibrations'] > 0.6), 0.2, 0.0)
        risk_score += combined_risk
    
    if all(col in df.columns for col in ['displacement', 'strain']):
        geo_risk = np.where((df['displacement'] > 5) & (df['strain'] > 1.0), 0.15, 0.0)
        risk_score += geo_risk
    
    # Temperature extremes
    if 'temperature_c' in df.columns:
        temp_risk = np.where(df['temperature_c'] < 0, 0.05, 0.0)  # Freeze-thaw
        temp_risk += np.where(df['temperature_c'] > 40, 0.05, 0.0)  # Thermal expansion
        risk_score += temp_risk
    
    # Normalize risk score to [0, 1] and create binary labels
    risk_score = np.clip(risk_score, 0, 1)
    
    # Create binary risk label (threshold at 0.5)
    df['risk'] = (risk_score > 0.5).astype(int)
    df['risk_probability'] = risk_score
    
    return df


def validate_features(df: pd.DataFrame) -> Dict[str, any]:
    """Validate feature quality and return metrics."""
    if df.empty:
        return {"status": "empty", "message": "No data available"}
    
    validation_results = {
        "status": "success",
        "n_samples": len(df),
        "n_features": len(df.columns),
        "missing_percentage": (df.isnull().sum().sum() / (df.shape[0] * df.shape[1])) * 100,
        "numeric_features": len(df.select_dtypes(include=[np.number]).columns),
        "datetime_features": len(df.select_dtypes(include=['datetime64']).columns),
        "feature_names": list(df.columns)
    }
    
    # Check for potential issues
    warnings = []
    
    if validation_results["missing_percentage"] > 10:
        warnings.append(f"High missing data: {validation_results['missing_percentage']:.1f}%")
    
    if validation_results["n_samples"] < 100:
        warnings.append(f"Low sample count: {validation_results['n_samples']}")
    
    if 'risk' in df.columns:
        risk_distribution = df['risk'].value_counts()
        if len(risk_distribution) < 2:
            warnings.append("Risk labels are not balanced")
        else:
            minority_class_pct = min(risk_distribution) / len(df) * 100
            if minority_class_pct < 5:
                warnings.append(f"Severe class imbalance: {minority_class_pct:.1f}% minority class")
    
    validation_results["warnings"] = warnings
    
    return validation_results