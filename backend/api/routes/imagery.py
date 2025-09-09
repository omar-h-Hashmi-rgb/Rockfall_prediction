from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List, Dict, Any, Optional
import os
import cv2
import numpy as np
from datetime import datetime

from ..models.data_preprocessor import DataPreprocessor

router = APIRouter(prefix="/imagery", tags=["imagery"])

# Global instances
preprocessor = DataPreprocessor()

@router.get("/list", response_model=List[Dict[str, Any]])
async def list_drone_images(
    sector: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
):
    """List available drone images with metadata"""
    try:
        images_dir = "data/DroneImages/FilteredData/Images"
        masks_dir = "data/DroneImages/FilteredData/Masks"
        
        if not os.path.exists(images_dir):
            return []
        
        image_files = [f for f in os.listdir(images_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        image_files.sort()
        
        # Apply pagination
        paginated_files = image_files[offset:offset + limit]
        
        images_list = []
        for idx, filename in enumerate(paginated_files, start=offset):
            image_path = os.path.join(images_dir, filename)
            mask_path = os.path.join(masks_dir, filename)
            
            # Check if corresponding mask exists
            has_mask = os.path.exists(mask_path)
            
            # Get file stats
            try:
                stat = os.stat(image_path)
                file_size = stat.st_size
                modified_time = datetime.fromtimestamp(stat.st_mtime)
            except:
                file_size = 0
                modified_time = datetime.utcnow()
            
            # Extract basic image info
            try:
                img = cv2.imread(image_path)
                if img is not None:
                    height, width, channels = img.shape
                else:
                    height = width = channels = 0
            except:
                height = width = channels = 0
            
            # Generate metadata
            image_metadata = {
                'id': idx,
                'filename': filename,
                'path': image_path,
                'has_mask': has_mask,
                'mask_path': mask_path if has_mask else None,
                'file_size': file_size,
                'modified_time': modified_time.isoformat(),
                'dimensions': {
                    'width': width,
                    'height': height,
                    'channels': channels
                },
                'sector': f"Sector {(idx % 4) + 1}",  # Simulated sector assignment
                'risk_level': ['Low', 'Medium', 'High'][idx % 3],  # Simulated risk level
                'analysis_status': 'completed' if has_mask else 'pending'
            }
            
            # Filter by sector if specified
            if sector and image_metadata['sector'] != sector:
                continue
            
            images_list.append(image_metadata)
        
        return images_list
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image listing error: {str(e)}")

@router.get("/analyze/{image_id}", response_model=Dict[str, Any])
async def analyze_image(image_id: int):
    """Analyze a specific drone image and return risk assessment"""
    try:
        images_dir = "data/DroneImages/FilteredData/Images"
        masks_dir = "data/DroneImages/FilteredData/Masks"
        
        # Get list of images
        image_files = [f for f in os.listdir(images_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        image_files.sort()
        
        if image_id >= len(image_files):
            raise HTTPException(status_code=404, detail="Image not found")
        
        filename = image_files[image_id]
        image_path = os.path.join(images_dir, filename)
        mask_path = os.path.join(masks_dir, filename)
        
        # Extract image features using preprocessor
        image_features = preprocessor.preprocess_image_features(image_path, mask_path if os.path.exists(mask_path) else None)
        
        # Perform analysis
        analysis_result = {
            'image_id': image_id,
            'filename': filename,
            'analysis_timestamp': datetime.utcnow().isoformat(),
            'features': {
                'mean_intensity': float(image_features[0]),
                'std_intensity': float(image_features[1]),
                'edge_density': float(image_features[2]),
                'color_analysis': {
                    'blue_mean': float(image_features[3]),
                    'green_mean': float(image_features[4]),
                    'red_mean': float(image_features[5])
                }
            },
            'risk_indicators': generate_risk_indicators(image_features),
            'has_mask': os.path.exists(mask_path),
            'recommendations': generate_recommendations(image_features)
        }
        
        return analysis_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image analysis error: {str(e)}")

@router.get("/mask/{image_id}", response_model=Dict[str, Any])
async def get_mask_analysis(image_id: int):
    """Get detailed mask analysis for a specific image"""
    try:
        masks_dir = "data/DroneImages/FilteredData/Masks"
        
        # Get list of mask files
        mask_files = [f for f in os.listdir(masks_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        mask_files.sort()
        
        if image_id >= len(mask_files):
            raise HTTPException(status_code=404, detail="Mask not found")
        
        filename = mask_files[image_id]
        mask_path = os.path.join(masks_dir, filename)
        
        # Load and analyze mask
        mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
        if mask is None:
            raise HTTPException(status_code=500, detail="Could not load mask image")
        
        # Analyze mask regions
        mask_analysis = analyze_risk_mask(mask)
        
        return {
            'image_id': image_id,
            'mask_filename': filename,
            'analysis_timestamp': datetime.utcnow().isoformat(),
            'risk_regions': mask_analysis['risk_regions'],
            'coverage_stats': mask_analysis['coverage_stats'],
            'risk_distribution': mask_analysis['risk_distribution'],
            'severity_score': mask_analysis['severity_score']
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Mask analysis error: {str(e)}")

@router.post("/upload", response_model=Dict[str, Any])
async def upload_drone_image(
    file: UploadFile = File(...),
    sector: Optional[str] = None,
    metadata: Optional[str] = None
):
    """Upload a new drone image for analysis"""
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Create upload directory if it doesn't exist
        upload_dir = "data/DroneImages/FilteredData/Images"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate unique filename
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        file_extension = os.path.splitext(file.filename)[1]
        new_filename = f"uploaded_{timestamp}{file_extension}"
        file_path = os.path.join(upload_dir, new_filename)
        
        # Save file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Analyze uploaded image
        image_features = preprocessor.preprocess_image_features(file_path)
        risk_indicators = generate_risk_indicators(image_features)
        
        return {
            'status': 'uploaded',
            'filename': new_filename,
            'file_path': file_path,
            'file_size': len(content),
            'upload_timestamp': datetime.utcnow().isoformat(),
            'sector': sector,
            'initial_analysis': {
                'risk_indicators': risk_indicators,
                'features_extracted': len(image_features),
                'analysis_ready': True
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload error: {str(e)}")

@router.delete("/{image_id}")
async def delete_image(image_id: int):
    """Delete a drone image and its associated mask"""
    try:
        images_dir = "data/DroneImages/FilteredData/Images"
        masks_dir = "data/DroneImages/FilteredData/Masks"
        
        # Get image files
        image_files = [f for f in os.listdir(images_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        image_files.sort()
        
        if image_id >= len(image_files):
            raise HTTPException(status_code=404, detail="Image not found")
        
        filename = image_files[image_id]
        image_path = os.path.join(images_dir, filename)
        mask_path = os.path.join(masks_dir, filename)
        
        # Delete files
        deleted_files = []
        
        if os.path.exists(image_path):
            os.remove(image_path)
            deleted_files.append(image_path)
        
        if os.path.exists(mask_path):
            os.remove(mask_path)
            deleted_files.append(mask_path)
        
        return {
            'status': 'deleted',
            'image_id': image_id,
            'filename': filename,
            'deleted_files': deleted_files,
            'deletion_timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Deletion error: {str(e)}")

def generate_risk_indicators(image_features: np.ndarray) -> Dict[str, Any]:
    """Generate risk indicators from image features"""
    try:
        mean_intensity = image_features[0]
        std_intensity = image_features[1]
        edge_density = image_features[2]
        
        # Determine risk factors
        risk_factors = []
        
        if mean_intensity < 80:
            risk_factors.append("Low visibility conditions detected")
        elif mean_intensity > 200:
            risk_factors.append("High glare or overexposure detected")
        
        if std_intensity < 20:
            risk_factors.append("Low texture variation - potential landslide area")
        elif std_intensity > 80:
            risk_factors.append("High texture variation - fractured rock surface")
        
        if edge_density > 0.15:
            risk_factors.append("High edge density - multiple crack patterns")
        elif edge_density < 0.05:
            risk_factors.append("Smooth surface - potential instability")
        
        # Calculate overall risk score
        risk_score = 0.0
        risk_score += max(0, (80 - mean_intensity) / 80 * 0.3)  # Low visibility risk
        risk_score += max(0, (mean_intensity - 200) / 55 * 0.3)  # Overexposure risk
        risk_score += max(0, (20 - std_intensity) / 20 * 0.2)    # Low texture risk
        risk_score += max(0, (edge_density - 0.15) / 0.15 * 0.2) # High edge density risk
        
        risk_level = 'Low'
        if risk_score > 0.7:
            risk_level = 'High'
        elif risk_score > 0.4:
            risk_level = 'Medium'
        
        return {
            'risk_score': min(1.0, risk_score),
            'risk_level': risk_level,
            'risk_factors': risk_factors,
            'confidence': 0.8 - min(0.3, len(risk_factors) * 0.1)
        }
        
    except Exception:
        return {
            'risk_score': 0.5,
            'risk_level': 'Medium',
            'risk_factors': ['Analysis incomplete'],
            'confidence': 0.5
        }

def analyze_risk_mask(mask: np.ndarray) -> Dict[str, Any]:
    """Analyze risk mask to extract detailed risk information"""
    try:
        total_pixels = mask.shape[0] * mask.shape[1]
        
        # Define risk levels based on pixel intensity
        high_risk_pixels = np.sum(mask > 200)
        medium_risk_pixels = np.sum((mask > 100) & (mask <= 200))
        low_risk_pixels = np.sum(mask <= 100)
        
        # Calculate percentages
        high_risk_percent = (high_risk_pixels / total_pixels) * 100
        medium_risk_percent = (medium_risk_pixels / total_pixels) * 100
        low_risk_percent = (low_risk_pixels / total_pixels) * 100
        
        # Find connected components for risk regions
        _, labels = cv2.connectedComponents((mask > 150).astype(np.uint8))
        num_risk_regions = labels.max()
        
        # Calculate severity score
        severity_score = (high_risk_percent * 0.8 + medium_risk_percent * 0.4) / 100
        
        return {
            'risk_regions': {
                'total_regions': int(num_risk_regions),
                'high_risk_regions': int(np.sum(mask > 200) > 100),  # Regions with significant high-risk areas
                'analysis_method': 'connected_components'
            },
            'coverage_stats': {
                'total_area_pixels': int(total_pixels),
                'analyzed_area_percent': 100.0
            },
            'risk_distribution': {
                'high_risk_percent': round(high_risk_percent, 2),
                'medium_risk_percent': round(medium_risk_percent, 2),
                'low_risk_percent': round(low_risk_percent, 2)
            },
            'severity_score': round(severity_score, 3)
        }
        
    except Exception as e:
        return {
            'risk_regions': {'total_regions': 0, 'high_risk_regions': 0, 'analysis_method': 'failed'},
            'coverage_stats': {'total_area_pixels': 0, 'analyzed_area_percent': 0},
            'risk_distribution': {'high_risk_percent': 0, 'medium_risk_percent': 0, 'low_risk_percent': 0},
            'severity_score': 0.0
        }

def generate_recommendations(image_features: np.ndarray) -> List[str]:
    """Generate recommendations based on image analysis"""
    recommendations = []
    
    try:
        mean_intensity = image_features[0]
        std_intensity = image_features[1]
        edge_density = image_features[2]
        
        if mean_intensity < 80:
            recommendations.append("Consider improving lighting conditions for better image quality")
        
        if edge_density > 0.15:
            recommendations.append("High crack density detected - schedule detailed geological survey")
            recommendations.append("Implement enhanced monitoring in this area")
        
        if std_intensity < 20:
            recommendations.append("Uniform surface texture may indicate loose material - verify stability")
        
        if len(recommendations) == 0:
            recommendations.append("Continue regular monitoring schedule")
        
    except Exception:
        recommendations.append("Image analysis incomplete - manual review recommended")
    
    return recommendations