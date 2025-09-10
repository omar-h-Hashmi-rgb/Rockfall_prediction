from __future__ import annotations
import io
import requests
from PIL import Image, ImageDraw, ImageFont
from typing import List, Tuple, Dict, Optional
import logging
from ..config import settings

logger = logging.getLogger(__name__)

BASE_URL = settings.mapmyindia_base_url
ACCESS_TOKEN = settings.mapmyindia_access_token

class MapMyIndiaError(Exception):
    """Custom exception for MapMyIndia API errors."""
    pass

def check_api_availability() -> bool:
    """Check if MapMyIndia API is available and configured."""
    if not ACCESS_TOKEN:
        logger.warning("MapMyIndia access token not configured")
        return False
    
    try:
        # Simple API test
        test_url = f"{BASE_URL}/{ACCESS_TOKEN}/staticmap?center=28.6139,77.2090&zoom=10&size=100x100"
        response = requests.get(test_url, timeout=10)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"MapMyIndia API not available: {e}")
        return False

def get_static_map(
    center_lat: float, 
    center_lng: float, 
    zoom: int = 12, 
    size: str = '800x600',
    map_type: str = 'roadmap'
) -> Image.Image:
    """Get static map from MapMyIndia API."""
    
    if not ACCESS_TOKEN:
        raise MapMyIndiaError("MapMyIndia access token not configured")
    
    # Validate inputs
    if not (-90 <= center_lat <= 90):
        raise ValueError("Latitude must be between -90 and 90")
    if not (-180 <= center_lng <= 180):
        raise ValueError("Longitude must be between -180 and 180")
    if not (1 <= zoom <= 18):
        raise ValueError("Zoom must be between 1 and 18")
    
    # Construct API URL
    url = (
        f"{BASE_URL}/{ACCESS_TOKEN}/staticmap"
        f"?center={center_lat},{center_lng}"
        f"&zoom={zoom}"
        f"&size={size}"
        f"&maptype={map_type}"
    )
    
    try:
        logger.debug(f"Requesting map: {url}")
        response = requests.get(url, timeout=20)
        response.raise_for_status()
        
        # Convert response to PIL Image
        image = Image.open(io.BytesIO(response.content)).convert('RGBA')
        logger.info(f"Retrieved map: {image.size[0]}x{image.size[1]}")
        
        return image
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to get map from MapMyIndia: {e}")
        raise MapMyIndiaError(f"Map request failed: {e}")
    except Exception as e:
        logger.error(f"Error processing map image: {e}")
        raise MapMyIndiaError(f"Image processing failed: {e}")

def add_risk_markers(
    image: Image.Image, 
    risk_points: List[Dict],
    legend: bool = True
) -> Image.Image:
    """Add risk markers to map image."""
    
    # Create a copy to avoid modifying original
    img_with_markers = image.copy()
    draw = ImageDraw.Draw(img_with_markers)
    
    # Risk level colors
    risk_colors = {
        'LOW': (0, 200, 0, 180),      # Green
        'MEDIUM': (255, 165, 0, 200),  # Orange  
        'HIGH': (255, 0, 0, 220),      # Red
        'CRITICAL': (139, 0, 0, 240)   # Dark Red
    }
    
    # Default marker style
    marker_size = 12
    
    for point in risk_points:
        try:
            x = int(point.get('x', 0))
            y = int(point.get('y', 0))
            risk_level = point.get('risk_level', 'LOW').upper()
            size = point.get('size', marker_size)
            
            # Get color for risk level
            color = risk_colors.get(risk_level, risk_colors['LOW'])
            
            # Draw circular marker
            bbox = [x - size//2, y - size//2, x + size//2, y + size//2]
            draw.ellipse(bbox, fill=color, outline=(0, 0, 0, 255), width=2)
            
            # Add label if provided
            label = point.get('label')
            if label:
                try:
                    # Try to load a font, fallback to default
                    font = ImageFont.load_default()
                    
                    # Calculate text size and position
                    text_bbox = draw.textbbox((0, 0), label, font=font)
                    text_width = text_bbox[2] - text_bbox[0]
                    text_height = text_bbox[3] - text_bbox[1]
                    
                    text_x = x - text_width // 2
                    text_y = y + size // 2 + 2
                    
                    # Draw text background
                    bg_bbox = [
                        text_x - 2, text_y - 2,
                        text_x + text_width + 2, text_y + text_height + 2
                    ]
                    draw.rectangle(bg_bbox, fill=(255, 255, 255, 200))
                    
                    # Draw text
                    draw.text((text_x, text_y), label, fill=(0, 0, 0, 255), font=font)
                    
                except Exception as e:
                    logger.warning(f"Could not add label '{label}': {e}")
                    
        except Exception as e:
            logger.warning(f"Could not draw marker {point}: {e}")
            continue
    
    # Add legend if requested
    if legend and risk_points:
        try:
            add_legend(img_with_markers, risk_colors)
        except Exception as e:
            logger.warning(f"Could not add legend: {e}")
    
    return img_with_markers

def add_legend(image: Image.Image, risk_colors: Dict[str, Tuple]) -> None:
    """Add a legend to the map image."""
    draw = ImageDraw.Draw(image)
    
    # Legend configuration
    legend_x = 10
    legend_y = 10
    legend_width = 120
    legend_height = len(risk_colors) * 25 + 10
    
    # Draw legend background
    legend_bbox = [
        legend_x, legend_y,
        legend_x + legend_width, legend_y + legend_height
    ]
    draw.rectangle(legend_bbox, fill=(255, 255, 255, 220), outline=(0, 0, 0, 255))
    
    # Add legend title
    try:
        font = ImageFont.load_default()
        draw.text((legend_x + 5, legend_y + 5), "Risk Levels", fill=(0, 0, 0, 255), font=font)
        
        # Add each risk level
        y_offset = 25
        for risk_level, color in risk_colors.items():
            marker_y = legend_y + y_offset
            
            # Draw marker
            marker_bbox = [
                legend_x + 10, marker_y,
                legend_x + 20, marker_y + 10
            ]
            draw.ellipse(marker_bbox, fill=color)
            
            # Draw label
            draw.text(
                (legend_x + 25, marker_y - 2), 
                risk_level.title(), 
                fill=(0, 0, 0, 255), 
                font=font
            )
            
            y_offset += 20
            
    except Exception as e:
        logger.warning(f"Error creating legend text: {e}")

def lat_lng_to_pixel(
    lat: float, 
    lng: float, 
    center_lat: float, 
    center_lng: float, 
    zoom: int, 
    image_width: int, 
    image_height: int
) -> Tuple[int, int]:
    """Convert latitude/longitude to pixel coordinates on the map."""
    
    # Simplified conversion - for production use proper projection
    # This is a basic approximation for demonstration
    
    import math
    
    # Web Mercator projection approximation
    def lat_to_y(lat):
        return math.log(math.tan(math.pi/4 + math.radians(lat)/2))
    
    # Calculate scale based on zoom level
    scale = 2 ** zoom
    
    # Convert coordinates
    center_y = lat_to_y(center_lat)
    point_y = lat_to_y(lat)
    
    # Calculate pixel offsets from center
    x_offset = (lng - center_lng) * scale * (image_width / 360)
    y_offset = (center_y - point_y) * scale * (image_height / (2 * math.pi))
    
    # Calculate final pixel coordinates
    pixel_x = int(image_width / 2 + x_offset)
    pixel_y = int(image_height / 2 + y_offset)
    
    return pixel_x, pixel_y

def create_risk_overlay_map(
    center_lat: float,
    center_lng: float,
    risk_locations: List[Dict],
    zoom: int = 12,
    size: str = '800x600'
) -> Image.Image:
    """Create a map with risk overlay markers."""
    
    try:
        # Get base map
        base_map = get_static_map(center_lat, center_lng, zoom, size)
        
        # Convert risk locations to pixel coordinates
        width, height = base_map.size
        pixel_points = []
        
        for location in risk_locations:
            lat = location.get('lat')
            lng = location.get('lng')
            
            if lat is not None and lng is not None:
                x, y = lat_lng_to_pixel(
                    lat, lng, center_lat, center_lng, zoom, width, height
                )
                
                # Only add if within image bounds
                if 0 <= x <= width and 0 <= y <= height:
                    pixel_points.append({
                        'x': x,
                        'y': y,
                        'risk_level': location.get('risk_level', 'LOW'),
                        'label': location.get('label'),
                        'size': location.get('size', 12)
                    })
        
        # Add markers to map
        if pixel_points:
            map_with_markers = add_risk_markers(base_map, pixel_points)
            logger.info(f"Added {len(pixel_points)} risk markers to map")
            return map_with_markers
        else:
            logger.warning("No valid risk locations to display")
            return base_map
            
    except Exception as e:
        logger.error(f"Error creating risk overlay map: {e}")
        raise MapMyIndiaError(f"Could not create risk overlay: {e}")

def get_map_url(
    center_lat: float,
    center_lng: float,
    zoom: int = 12,
    size: str = '800x600',
    markers: Optional[List[Dict]] = None
) -> str:
    """Get URL for static map (for embedding in web pages)."""
    
    if not ACCESS_TOKEN:
        raise MapMyIndiaError("MapMyIndia access token not configured")
    
    url = (
        f"{BASE_URL}/{ACCESS_TOKEN}/staticmap"
        f"?center={center_lat},{center_lng}"
        f"&zoom={zoom}"
        f"&size={size}"
    )
    
    # Add markers if provided
    if markers:
        marker_params = []
        for marker in markers:
            lat = marker.get('lat')
            lng = marker.get('lng')
            color = marker.get('color', 'red')
            label = marker.get('label', '')
            
            if lat is not None and lng is not None:
                marker_param = f"{lat},{lng}"
                if color:
                    marker_param += f":color={color}"
                if label:
                    marker_param += f":label={label}"
                marker_params.append(marker_param)
        
        if marker_params:
            url += "&markers=" + "|".join(marker_params)
    
    return url

def health_check() -> Dict:
    """Check MapMyIndia service health."""
    try:
        is_available = check_api_availability()
        
        if is_available:
            return {
                'status': 'healthy',
                'service': 'MapMyIndia',
                'api_configured': bool(ACCESS_TOKEN),
                'base_url': BASE_URL
            }
        else:
            return {
                'status': 'unhealthy',
                'service': 'MapMyIndia',
                'api_configured': bool(ACCESS_TOKEN),
                'error': 'API not accessible'
            }
    except Exception as e:
        return {
            'status': 'error',
            'service': 'MapMyIndia',
            'error': str(e)
        }

# Demo function to create sample risk data
def create_sample_risk_locations(center_lat: float, center_lng: float) -> List[Dict]:
    """Create sample risk locations for demonstration."""
    import random
    
    sample_locations = []
    risk_levels = ['LOW', 'MEDIUM', 'HIGH']
    
    for i in range(5):
        # Generate random points around center
        lat_offset = random.uniform(-0.01, 0.01)
        lng_offset = random.uniform(-0.01, 0.01)
        
        sample_locations.append({
            'lat': center_lat + lat_offset,
            'lng': center_lng + lng_offset,
            'risk_level': random.choice(risk_levels),
            'label': f'Zone {i+1}',
            'probability': random.uniform(0, 1)
        })
    
    return sample_locations

if __name__ == "__main__":
    # Test the service
    try:
        print("Testing MapMyIndia service...")
        health = health_check()
        print(f"Health check: {health}")
        
        if health['status'] == 'healthy':
            # Test map generation
            test_lat, test_lng = 28.6139, 77.2090  # New Delhi
            sample_risks = create_sample_risk_locations(test_lat, test_lng)
            
            map_image = create_risk_overlay_map(
                test_lat, test_lng, sample_risks
            )
            
            print(f"Generated test map: {map_image.size}")
            
    except Exception as e:
        print(f"Test failed: {e}")