import numpy as np
import json
from typing import Dict, List

def generate_dem_data(grid_size: int = 100, terrain_type: str = "open_pit") -> Dict:
    """Generate synthetic Digital Elevation Model data for open-pit mine"""
    
    # Create coordinate grid
    x = np.linspace(0, 1000, grid_size)  # 1km x 1km area
    y = np.linspace(0, 1000, grid_size)
    X, Y = np.meshgrid(x, y)
    
    if terrain_type == "open_pit":
        # Create pit-like elevation profile
        center_x, center_y = 500, 500
        pit_depth = 150  # meters
        pit_radius = 300  # meters
        
        # Distance from center
        dist_from_center = np.sqrt((X - center_x)**2 + (Y - center_y)**2)
        
        # Elevation decreases towards center (pit)
        elevation = 1500 - pit_depth * np.exp(-((dist_from_center / pit_radius)**2))
        
        # Add random variations for realistic terrain
        elevation += np.random.normal(0, 10, elevation.shape)
        
        # Calculate slope (gradient)
        slope_x = np.gradient(elevation, axis=1)
        slope_y = np.gradient(elevation, axis=0)
        slope = np.sqrt(slope_x**2 + slope_y**2)
        
        # Calculate aspect (direction of slope)
        aspect = np.arctan2(slope_y, slope_x) * 180 / np.pi
        aspect = (aspect + 360) % 360  # Convert to 0-360 degrees
        
        # Calculate roughness (terrain complexity)
        roughness = np.std([
            elevation[1:, 1:], elevation[:-1, 1:], 
            elevation[1:, :-1], elevation[:-1, :-1]
        ], axis=0)
        roughness = np.pad(roughness, 1, mode='edge')
    
    dem_data = {
        'grid_size': grid_size,
        'coordinates': {
            'x': X.tolist(),
            'y': Y.tolist()
        },
        'elevation': elevation.tolist(),
        'slope': slope.tolist(),
        'aspect': aspect.tolist(),
        'roughness': roughness.tolist(),
        'metadata': {
            'min_elevation': float(np.min(elevation)),
            'max_elevation': float(np.max(elevation)),
            'mean_slope': float(np.mean(slope)),
            'terrain_type': terrain_type,
            'pit_center': [center_x, center_y],
            'pit_depth': pit_depth
        }
    }
    
    return dem_data

def save_dem_data(filename: str = "dem_data.json"):
    """Save DEM data to JSON file"""
    dem_data = generate_dem_data()
    with open(filename, 'w') as f:
        json.dump(dem_data, f, indent=2)
    return dem_data

if __name__ == "__main__":
    data = save_dem_data()
    print(f"Generated DEM data with {data['grid_size']}x{data['grid_size']} grid")
    print(f"Elevation range: {data['metadata']['min_elevation']:.1f}m - {data['metadata']['max_elevation']:.1f}m")