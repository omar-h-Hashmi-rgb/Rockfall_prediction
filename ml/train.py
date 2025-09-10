from __future__ import annotations
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    roc_auc_score, 
    classification_report, 
    confusion_matrix,
    precision_recall_curve,
    roc_curve
)
import warnings
warnings.filterwarnings('ignore')

from .dataset import RockfallDataset
from .utils_image import extract_image_features_for_ml

# Set up paths
SCRIPT_DIR = Path(__file__).resolve().parent
ARTIFACTS_DIR = SCRIPT_DIR / 'artifacts'
DATA_DIR = SCRIPT_DIR.parent / 'data'

ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

def load_and_prepare_data():
    """Load and prepare data for training."""
    print("Initializing dataset...")
    dataset = RockfallDataset(DATA_DIR)
    
    try:
        # Try to load real data
        df = dataset.load(create_labels=True)
        
        if df.empty:
            print("No real data found. Creating synthetic dataset...")
            df = dataset.create_synthetic_data(n_samples=2000)
        else:
            print(f"Loaded real data: {len(df)} samples")
            
    except Exception as e:
        print(f"Error loading data: {e}")
        print("Falling back to synthetic data...")
        df = dataset.create_synthetic_data(n_samples=2000)
    
    # Add image features if available
    images_dir = DATA_DIR / 'DroneImages/FilteredData/Images'
    masks_dir = DATA_DIR / 'DroneImages/FilteredData/Masks'
    
    if images_dir.exists():
        print("Extracting image features...")
        try:
            img_features = extract_image_features_for_ml(images_dir, masks_dir)
            
            # Add image features as constant columns (since they're aggregate statistics)
            for feat_name, feat_value in img_features.items():
                df[f'img_{feat_name}'] = feat_value
                
            print(f"Added {len(img_features)} image features")
        except Exception as e:
            print(f"Warning: Could not extract image features: {e}")
    
    return df, dataset

def prepare_features_and_target(df):
    """Prepare features and target variables."""
    # Define columns to exclude from features
    exclude_cols = ['risk', 'risk_probability', 'timestamp']
    
    # Get feature columns
    feature_cols = [col for col in df.columns if col not in exclude_cols]
    
    X = df[feature_cols].copy()
    y = df['risk'].copy()
    
    # Handle any remaining missing values
    X = X.fillna(0)
    
    # Remove constant features (no variance)
    constant_features = []
    for col in X.columns:
        if X[col].nunique() <= 1:
            constant_features.append(col)
    
    if constant_features:
        print(f"Removing {len(constant_features)} constant features")
        X = X.drop(columns=constant_features)
    
    # Remove highly correlated features
    correlation_matrix = X.corr().abs()
    upper_tri = correlation_matrix.where(
        np.triu(np.ones(correlation_matrix.shape), k=1).astype(bool)
    )
    
    high_corr_features = [
        column for column in upper_tri.columns 
        if any(upper_tri[column] > 0.95)
    ]
    
    if high_corr_features:
        print(f"Removing {len(high_corr_features)} highly correlated features")
        X = X.drop(columns=high_corr_features)
    
    print(f"Final feature set: {X.shape[1]} features")
    print(f"Target distribution: {y.value_counts().to_dict()}")
    
    return X, y

def create_model_pipeline():
    """Create the ML pipeline."""
    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('classifier', RandomForestClassifier(
            n_estimators=300,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            class_weight='balanced',
            random_state=42,
            n_jobs=-1
        ))
    ])
    
    return pipeline

def hyperparameter_tuning(X_train, y_train):
    """Perform hyperparameter tuning with grid search."""
    print("Performing hyperparameter tuning...")
    
    # Define parameter grid
    param_grid = {
        'classifier__n_estimators': [200, 300, 400],
        'classifier__max_depth': [10, 15, 20],
        'classifier__min_samples_split': [2, 5, 10],
        'classifier__min_samples_leaf': [1, 2, 4]
    }
    
    # Create base pipeline
    pipeline = create_model_pipeline()
    
    # Grid search with cross-validation
    grid_search = GridSearchCV(
        pipeline,
        param_grid,
        cv=5,
        scoring='roc_auc',
        n_jobs=-1,
        verbose=1
    )
    
    grid_search.fit(X_train, y_train)
    
    print(f"Best parameters: {grid_search.best_params_}")
    print(f"Best cross-validation score: {grid_search.best_score_:.4f}")
    
    return grid_search.best_estimator_

def evaluate_model(model, X_train, X_test, y_train, y_test):
    """Comprehensive model evaluation."""
    print("\n" + "="*50)
    print("MODEL EVALUATION")
    print("="*50)
    
    # Predictions
    y_train_pred = model.predict(X_train)
    y_test_pred = model.predict(X_test)
    
    y_train_proba = model.predict_proba(X_train)[:, 1]
    y_test_proba = model.predict_proba(X_test)[:, 1]
    
    # AUC Scores
    train_auc = roc_auc_score(y_train, y_train_proba)
    test_auc = roc_auc_score(y_test, y_test_proba)
    
    print(f"Training AUC: {train_auc:.4f}")
    print(f"Validation AUC: {test_auc:.4f}")
    print(f"Overfitting Check: {train_auc - test_auc:.4f}")
    
    # Classification Reports
    print(f"\nTraining Set Classification Report:")
    print(classification_report(y_train, y_train_pred))
    
    print(f"\nValidation Set Classification Report:")
    print(classification_report(y_test, y_test_pred))
    
    # Confusion Matrices
    print(f"\nTraining Confusion Matrix:")
    print(confusion_matrix(y_train, y_train_pred))
    
    print(f"\nValidation Confusion Matrix:")
    print(confusion_matrix(y_test, y_test_pred))
    
    # Cross-validation
    cv_scores = []
    if len(X_train) > 100:  # Only if we have enough data
        cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='roc_auc')
        print(f"\nCross-validation AUC: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
    
    return {
        'train_auc': train_auc,
        'test_auc': test_auc,
        'cv_scores': cv_scores.tolist(),
        'test_predictions': y_test_pred.tolist(),
        'test_probabilities': y_test_proba.tolist()
    }

def analyze_feature_importance(model, feature_names):
    """Analyze and display feature importance."""
    print("\n" + "="*50)
    print("FEATURE IMPORTANCE ANALYSIS")
    print("="*50)
    
    # Get feature importance from the Random Forest
    rf_classifier = model.named_steps['classifier']
    importances = rf_classifier.feature_importances_
    
    # Create feature importance dataframe
    feature_importance_df = pd.DataFrame({
        'feature': feature_names,
        'importance': importances
    }).sort_values('importance', ascending=False)
    
    # Display top features
    print("Top 20 Most Important Features:")
    print("-" * 40)
    for idx, row in feature_importance_df.head(20).iterrows():
        print(f"{row['feature']:<30} {row['importance']:.4f}")
    
    # Categorize features
    categories = {
        'Environmental': ['rainfall', 'temperature', 'humidity', 'wind', 'pressure'],
        'Sensor': ['displacement', 'strain', 'pore_pressure', 'vibrations'],
        'Image': ['img_'],
        'Temporal': ['hour', 'day', 'month', 'weekend', 'night'],
        'Engineered': ['roll', 'diff', 'pct_change', 'interaction', 'ratio', 'product']
    }
    
    category_importance = {}
    for category, keywords in categories.items():
        category_features = []
        for feature in feature_names:
            if any(keyword in feature.lower() for keyword in keywords):
                idx = feature_names.index(feature)
                category_features.append(importances[idx])
        
        if category_features:
            category_importance[category] = {
                'total_importance': sum(category_features),
                'avg_importance': np.mean(category_features),
                'feature_count': len(category_features)
            }
    
    print("\nFeature Category Importance:")
    print("-" * 40)
    for category, stats in sorted(category_importance.items(), 
                                 key=lambda x: x[1]['total_importance'], 
                                 reverse=True):
        print(f"{category:<15} Total: {stats['total_importance']:.4f} "
              f"Avg: {stats['avg_importance']:.4f} "
              f"Count: {stats['feature_count']}")
    
    return feature_importance_df

def save_model_artifacts(model, feature_names, evaluation_results, feature_importance_df):
    """Save model and related artifacts."""
    print("\n" + "="*50)
    print("SAVING MODEL ARTIFACTS")
    print("="*50)
    
    # Save the trained model
    model_path = ARTIFACTS_DIR / 'model.pkl'
    joblib.dump(model, model_path)
    print(f"Saved model to: {model_path}")
    
    # Save feature names (for prediction service)
    features_path = ARTIFACTS_DIR / 'feature_names.pkl'
    joblib.dump(feature_names, features_path)
    print(f"Saved feature names to: {features_path}")
    
    # Save evaluation results
    eval_path = ARTIFACTS_DIR / 'evaluation_results.pkl'
    joblib.dump(evaluation_results, eval_path)
    print(f"Saved evaluation results to: {eval_path}")
    
    # Save feature importance
    importance_path = ARTIFACTS_DIR / 'feature_importance.csv'
    feature_importance_df.to_csv(importance_path, index=False)
    print(f"Saved feature importance to: {importance_path}")
    
    # Create model metadata
    metadata = {
        'model_type': 'RandomForestClassifier',
        'n_features': len(feature_names),
        'training_date': pd.Timestamp.now().isoformat(),
        'performance': {
            'validation_auc': evaluation_results['test_auc'],
            'training_auc': evaluation_results['train_auc']
        },
        'feature_names': feature_names,
        'artifacts_location': str(ARTIFACTS_DIR)
    }
    
    metadata_path = ARTIFACTS_DIR / 'model_metadata.json'
    import json
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"Saved model metadata to: {metadata_path}")

def main():
    """Main training pipeline."""
    print("🪨 ROCKFALL PREDICTION MODEL TRAINING")
    print("=" * 60)
    
    # Load and prepare data
    df, dataset = load_and_prepare_data()
    
    if df.empty or len(df) < 50:
        raise RuntimeError("Insufficient training data. Need at least 50 samples.")
    
    # Prepare features and target
    X, y = prepare_features_and_target(df)
    
    # Check if we have both classes
    if len(y.unique()) < 2:
        print("Warning: Only one class present in target. Creating balanced synthetic data...")
        dataset_new = RockfallDataset(DATA_DIR)
        df = dataset_new.create_synthetic_data(n_samples=2000)
        X, y = prepare_features_and_target(df)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"\nData split:")
    print(f"Training set: {len(X_train)} samples")
    print(f"Test set: {len(X_test)} samples")
    
    # Create and train model
    print("\nTraining model...")
    
    # Option 1: Quick training (default)
    model = create_model_pipeline()
    model.fit(X_train, y_train)
    
    # Option 2: Hyperparameter tuning (uncomment for better performance)
    # if len(X_train) > 500:  # Only tune if we have enough data
    #     model = hyperparameter_tuning(X_train, y_train)
    # else:
    #     model = create_model_pipeline()
    #     model.fit(X_train, y_train)
    
    # Evaluate model
    evaluation_results = evaluate_model(model, X_train, X_test, y_train, y_test)
    
    # Analyze features
    feature_importance_df = analyze_feature_importance(model, list(X.columns))
    
    # Check if model meets minimum requirements
    min_auc_threshold = 0.7
    if evaluation_results['test_auc'] < min_auc_threshold:
        print(f"\nWarning: Model AUC ({evaluation_results['test_auc']:.3f}) "
              f"below threshold ({min_auc_threshold})")
        print("Consider:")
        print("- Collecting more data")
        print("- Feature engineering")
        print("- Hyperparameter tuning")
        print("- Trying different algorithms")
    else:
        print(f"\n✅ Model meets performance requirements (AUC: {evaluation_results['test_auc']:.3f})")
    
    # Save artifacts
    save_model_artifacts(model, list(X.columns), evaluation_results, feature_importance_df)
    
    print("\n🎉 Training completed successfully!")
    print(f"Model artifacts saved to: {ARTIFACTS_DIR}")
    
    return model, evaluation_results

if __name__ == '__main__':
    try:
        model, results = main()
    except Exception as e:
        print(f"Training failed: {e}")
        import traceback
        traceback.print_exc()
