from pathlib import Path
from PIL import Image
import numpy as np
from typing import Dict, List, Tuple, Optional
import json

def image_dir_stats(img_dir: Path) -> Dict[str, any]:
    """Calculate basic statistics from image directory."""
    img_dir = Path(img_dir)
    
    if not img_dir.exists():
        return {
            'img_count': 0,
            'avg_brightness': 0.0,
            'avg_contrast': 0.0,
            'error': f'Directory not found: {img_dir}'
        }
    
    # Supported image extensions
    supported_exts = {'.png', '.jpg', '.jpeg', '.tif', '.tiff', '.bmp'}
    
    # Find all image files
    image_files = []
    for ext in supported_exts:
        image_files.extend(img_dir.glob(f'*{ext}'))
        image_files.extend(img_dir.glob(f'*{ext.upper()}'))
    
    if not image_files:
        return {
            'img_count': 0,
            'avg_brightness': 0.0,
            'avg_contrast': 0.0,
            'error': 'No image files found'
        }
    
    # Limit processing for performance (sample if too many)
    max_process = 200
    if len(image_files) > max_process:
        # Sample evenly across the dataset
        step = len(image_files) // max_process
        image_files = image_files[::step][:max_process]
    
    brightness_values = []
    contrast_values = []
    size_values = []
    processed_count = 0
    
    for img_path in image_files:
        try:
            with Image.open(img_path) as img:
                # Convert to grayscale for analysis
                gray_img = img.convert('L')
                
                # Resize for faster processing
                gray_img = gray_img.resize((64, 64), Image.Resampling.LANCZOS)
                
                # Convert to numpy array
                img_array = np.array(gray_img)
                
                # Calculate brightness (mean pixel value)
                brightness = np.mean(img_array)
                brightness_values.append(brightness)
                
                # Calculate contrast (standard deviation)
                contrast = np.std(img_array)
                contrast_values.append(contrast)
                
                # Get original image size
                original_size = img.size
                size_values.append(original_size[0] * original_size[1])
                
                processed_count += 1
                
        except Exception as e:
            # Skip corrupted or unreadable images
            continue
    
    if not brightness_values:
        return {
            'img_count': len(image_files),
            'processed_count': 0,
            'avg_brightness': 0.0,
            'avg_contrast': 0.0,
            'error': 'No images could be processed'
        }
    
    return {
        'img_count': len(image_files),
        'processed_count': processed_count,
        'avg_brightness': float(np.mean(brightness_values)),
        'brightness_std': float(np.std(brightness_values)),
        'avg_contrast': float(np.mean(contrast_values)),
        'contrast_std': float(np.std(contrast_values)),
        'avg_size_pixels': float(np.mean(size_values)),
        'min_brightness': float(np.min(brightness_values)),
        'max_brightness': float(np.max(brightness_values)),
        'min_contrast': float(np.min(contrast_values)),
        'max_contrast': float(np.max(contrast_values))
    }


def analyze_mask_coverage(mask_dir: Path, binary_mask_dir: Optional[Path] = None) -> Dict[str, any]:
    """Analyze segmentation mask coverage and quality."""
    mask_dir = Path(mask_dir)
    
    if not mask_dir.exists():
        return {'error': f'Mask directory not found: {mask_dir}'}
    
    # Get mask files
    supported_exts = {'.png', '.jpg', '.jpeg', '.tif', '.tiff'}
    mask_files = []
    for ext in supported_exts:
        mask_files.extend(mask_dir.glob(f'*{ext}'))
        mask_files.extend(mask_dir.glob(f'*{ext.upper()}'))
    
    if not mask_files:
        return {'error': 'No mask files found'}
    
    # Limit processing
    max_process = 100
    if len(mask_files) > max_process:
        step = len(mask_files) // max_process
        mask_files = mask_files[::step][:max_process]
    
    coverage_ratios = []
    unique_classes = set()
    
    for mask_path in mask_files:
        try:
            with Image.open(mask_path) as mask_img:
                # Convert to numpy array
                mask_array = np.array(mask_img)
                
                # Handle different mask formats
                if len(mask_array.shape) == 3:
                    # If RGB mask, convert to single channel
                    mask_array = mask_array[:, :, 0]
                
                # Calculate coverage (non-zero pixels)
                total_pixels = mask_array.size
                non_zero_pixels = np.count_nonzero(mask_array)
                coverage_ratio = non_zero_pixels / total_pixels
                coverage_ratios.append(coverage_ratio)
                
                # Track unique classes/values
                unique_values = np.unique(mask_array)
                unique_classes.update(unique_values.tolist())
                
        except Exception:
            continue
    
    results = {
        'mask_count': len(mask_files),
        'processed_count': len(coverage_ratios),
        'avg_coverage_ratio': float(np.mean(coverage_ratios)) if coverage_ratios else 0.0,
        'coverage_std': float(np.std(coverage_ratios)) if coverage_ratios else 0.0,
        'min_coverage': float(np.min(coverage_ratios)) if coverage_ratios else 0.0,
        'max_coverage': float(np.max(coverage_ratios)) if coverage_ratios else 0.0,
        'unique_classes': sorted(list(unique_classes)),
        'num_classes': len(unique_classes)
    }
    
    # Analyze binary masks if provided
    if binary_mask_dir and Path(binary_mask_dir).exists():
        binary_stats = image_dir_stats(binary_mask_dir)
        results['binary_mask_stats'] = binary_stats
    
    return results


def extract_image_features_for_ml(
    images_dir: Path, 
    masks_dir: Optional[Path] = None,
    sample_size: int = 50
) -> Dict[str, float]:
    """Extract aggregate image features for ML model."""
    
    features = {}
    
    # Basic image statistics
    img_stats = image_dir_stats(images_dir)
    features.update({
        'img_count': img_stats.get('img_count', 0),
        'avg_brightness': img_stats.get('avg_brightness', 0.0),
        'brightness_std': img_stats.get('brightness_std', 0.0),
        'avg_contrast': img_stats.get('avg_contrast', 0.0),
        'contrast_std': img_stats.get('contrast_std', 0.0)
    })
    
    # Mask analysis if available
    if masks_dir and Path(masks_dir).exists():
        mask_stats = analyze_mask_coverage(masks_dir)
        features.update({
            'mask_coverage_avg': mask_stats.get('avg_coverage_ratio', 0.0),
            'mask_coverage_std': mask_stats.get('coverage_std', 0.0),
            'mask_num_classes': mask_stats.get('num_classes', 0)
        })
    
    # Derived features
    if features['avg_brightness'] > 0:
        features['brightness_contrast_ratio'] = features['avg_contrast'] / features['avg_brightness']
    else:
        features['brightness_contrast_ratio'] = 0.0
    
    # Risk indicators based on image analysis
    features['low_light_risk'] = 1.0 if features['avg_brightness'] < 100 else 0.0
    features['high_contrast_risk'] = 1.0 if features['avg_contrast'] > 50 else 0.0
    
    return features


def validate_image_data(data_dir: Path) -> Dict[str, any]:
    """Validate image data structure and quality."""
    data_dir = Path(data_dir)
    
    validation_results = {
        'status': 'unknown',
        'images_valid': False,
        'masks_valid': False,
        'binary_masks_valid': False,
        'errors': [],
        'warnings': []
    }
    
    # Check directory structure
    expected_dirs = [
        'DroneImages/FilteredData/Images',
        'DroneImages/FilteredData/Masks', 
        'DroneImages/FilteredData/BinaryMasks'
    ]
    
    for dir_path in expected_dirs:
        full_path = data_dir / dir_path
        if not full_path.exists():
            validation_results['errors'].append(f'Missing directory: {dir_path}')
    
    # Validate images
    images_dir = data_dir / 'DroneImages/FilteredData/Images'
    if images_dir.exists():
        img_stats = image_dir_stats(images_dir)
        if img_stats.get('img_count', 0) > 0:
            validation_results['images_valid'] = True
            validation_results['image_count'] = img_stats['img_count']
            
            if img_stats['img_count'] < 100:
                validation_results['warnings'].append(
                    f"Low image count: {img_stats['img_count']}"
                )
        else:
            validation_results['errors'].append('No valid images found')
    
    # Validate masks
    masks_dir = data_dir / 'DroneImages/FilteredData/Masks'
    if masks_dir.exists():
        mask_stats = analyze_mask_coverage(masks_dir)
        if not mask_stats.get('error'):
            validation_results['masks_valid'] = True
            validation_results['mask_count'] = mask_stats['mask_count']
            
            if mask_stats['avg_coverage_ratio'] < 0.1:
                validation_results['warnings'].append(
                    f"Low mask coverage: {mask_stats['avg_coverage_ratio']:.2%}"
                )
    
    # Validate binary masks
    binary_dir = data_dir / 'DroneImages/FilteredData/BinaryMasks'
    if binary_dir.exists():
        binary_stats = image_dir_stats(binary_dir)
        if binary_stats.get('img_count', 0) > 0:
            validation_results['binary_masks_valid'] = True
            validation_results['binary_mask_count'] = binary_stats['img_count']
    
    # Overall status
    if validation_results['errors']:
        validation_results['status'] = 'error'
    elif validation_results['warnings']:
        validation_results['status'] = 'warning'
    else:
        validation_results['status'] = 'success'
    
    return validation_results


def create_image_summary_report(data_dir: Path, output_path: Optional[Path] = None) -> Dict[str, any]:
    """Create comprehensive image analysis report."""
    data_dir = Path(data_dir)
    
    report = {
        'analysis_timestamp': np.datetime64('now').astype(str),
        'data_directory': str(data_dir),
        'validation': validate_image_data(data_dir),
        'image_stats': {},
        'mask_stats': {},
        'binary_mask_stats': {},
        'ml_features': {}
    }
    
    # Analyze each image directory
    dirs_to_analyze = {
        'images': 'DroneImages/FilteredData/Images',
        'masks': 'DroneImages/FilteredData/Masks',
        'binary_masks': 'DroneImages/FilteredData/BinaryMasks'
    }
    
    for key, dir_path in dirs_to_analyze.items():
        full_path = data_dir / dir_path
        if full_path.exists():
            if key == 'masks':
                stats = analyze_mask_coverage(full_path)
            else:
                stats = image_dir_stats(full_path)
            report[f'{key}_stats'] = stats
    
    # Extract ML features
    images_dir = data_dir / 'DroneImages/FilteredData/Images'
    masks_dir = data_dir / 'DroneImages/FilteredData/Masks'
    
    if images_dir.exists():
        ml_features = extract_image_features_for_ml(images_dir, masks_dir)
        report['ml_features'] = ml_features
    
    # Save report if output path provided
    if output_path:
        try:
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2, default=str)
        except Exception as e:
            report['save_error'] = str(e)
    
    return report


if __name__ == "__main__":
    # Example usage
    from pathlib import Path
    
    data_dir = Path(__file__).parent.parent / 'data'
    
    # Create comprehensive image analysis report
    report = create_image_summary_report(data_dir)
    
    print("Image Analysis Report")
    print("=" * 50)
    print(f"Status: {report['validation']['status']}")
    
    if report['validation']['errors']:
        print("Errors:")
        for error in report['validation']['errors']:
            print(f"  - {error}")
    
    if report['validation']['warnings']:
        print("Warnings:")
        for warning in report['validation']['warnings']:
            print(f"  - {warning}")
    
    # Print summary statistics
    for key in ['image_stats', 'mask_stats', 'binary_mask_stats']:
        if report[key]:
            print(f"\n{key.replace('_', ' ').title()}:")
            stats = report[key]
            if 'img_count' in stats:
                print(f"  Count: {stats['img_count']}")
            if 'processed_count' in stats:
                print(f"  Processed: {stats['processed_count']}")
            if 'avg_brightness' in stats:
                print(f"  Avg Brightness: {stats['avg_brightness']:.1f}")
            if 'avg_contrast' in stats:
                print(f"  Avg Contrast: {stats['avg_contrast']:.1f}")
            if 'avg_coverage_ratio' in stats:
                print(f"  Avg Coverage: {stats['avg_coverage_ratio']:.2%}")
    
    # Print ML features
    if report['ml_features']:
        print("\nML Features:")
        for key, value in report['ml_features'].items():
            print(f"  {key}: {value}")