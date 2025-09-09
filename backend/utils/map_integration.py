import requests
import os
from typing import Dict, List, Any

class MapMyIndiaIntegration:
    def __init__(self):
        self.access_token = os.getenv('MAPMYINDIA_ACCESS_TOKEN')
        self.base_url = os.getenv('MAPMYINDIA_API_BASE_URL')
        
    def get_static_map(self, center_lat: float, center_lon: float, zoom: int = 10, 
                      size: str = "400x400", markers: List[Dict] = None) -> str:
        """Generate static map URL with risk overlays"""
        url = f"{self.base_url}/{self.access_token}/staticmap"
        
        params = {
            'center': f"{center_lat},{center_lon}",
            'zoom': zoom,
            'size': size
        }
        
        if markers:
            marker_string = ""
            for marker in markers:
                risk_color = {
                    'Low': 'green',
                    'Medium': 'yellow',
                    'High': 'red'
                }.get(marker.get('risk', 'Low'), 'blue')
                
                marker_string += f"|{risk_color}:{marker['lat']},{marker['lon']}"
            
            params['markers'] = marker_string
        
        return f"{url}?" + "&".join([f"{k}={v}" for k, v in params.items()])
    
    def get_risk_overlay_data(self, predictions: List[Dict]) -> List[Dict]:
        """Convert predictions to map overlay data"""
        overlays = []
        
        for pred in predictions:
            if 'coordinates' in pred:
                overlay = {
                    'lat': pred['coordinates']['lat'],
                    'lon': pred['coordinates']['lon'],
                    'risk': pred['risk_class'],
                    'probability': pred['risk_probability'],
                    'timestamp': pred.get('timestamp'),
                    'color': {
                        'Low': '#28a745',
                        'Medium': '#ffc107',
                        'High': '#dc3545'
                    }.get(pred['risk_class'], '#6c757d')
                }
                overlays.append(overlay)
        
        return overlays