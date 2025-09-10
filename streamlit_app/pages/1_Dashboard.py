import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
from PIL import Image
import io
import folium
from streamlit_folium import folium_static
import numpy as np

st.set_page_config(page_title='Dashboard', page_icon='📊', layout='wide')

# Enhanced CSS for better visibility and contrast
st.markdown("""
<style>
    /* Main background improvements */
    .main .block-container {
        padding-top: 2rem;
        background-color: #f8f9fa;
        border-radius: 10px;
    }
    
    /* Custom cards with better contrast */
    .custom-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }
    
    .metric-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1.2rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.15);
    }
    
    .risk-card-high {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    
    .risk-card-medium {
        background: linear-gradient(135deg, #feca57 0%, #ff9ff3 100%);
        padding: 1rem;
        border-radius: 10px;
        color: #2c2c2c;
        margin: 0.5rem 0;
    }
    
    .risk-card-low {
        background: linear-gradient(135deg, #48dbfb 0%, #0abde3 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    
    .weather-card {
        background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .assessment-card {
        background: linear-gradient(135deg, #a29bfe 0%, #6c5ce7 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    
    /* Section headers */
    .section-header {
        background: linear-gradient(90deg, #2E86AB, #A23B72);
        padding: 0.8rem 1.5rem;
        border-radius: 8px;
        color: white;
        font-weight: bold;
        margin: 1rem 0;
        text-align: center;
    }
    
    /* Chart containers */
    .chart-container {
        background-color: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

API_BASE = os.getenv('API_BASE', 'http://localhost:8000')

# Check authentication
if not st.session_state.get('auth', False):
    st.error("🔒 Please log in to access the dashboard")
    st.stop()

st.markdown('<div class="section-header"><h1>📊 Rockfall Risk Dashboard</h1></div>', unsafe_allow_html=True)

# API Health Check
try:
    health_response = requests.get(f"{API_BASE}/api/health", timeout=5)
    api_healthy = health_response.status_code == 200
except:
    api_healthy = False

if not api_healthy:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #ffeaa7 0%, #fab1a0 100%); 
                padding: 1rem; border-radius: 10px; color: #2d3436; margin: 1rem 0;">
        ⚠️ <strong>API not accessible.</strong> Running in demo mode with simulated data.
    </div>
    """, unsafe_allow_html=True)

# Enhanced sample risk markers
sample_risks = [
    {'lat': 28.6139 + 0.005, 'lng': 77.2090 + 0.005, 'risk': 'HIGH', 'prob': 0.85, 'location': 'Mining Sector A'},
    {'lat': 28.6139 - 0.003, 'lng': 77.2090 + 0.008, 'risk': 'MEDIUM', 'prob': 0.55, 'location': 'Quarry Site B'},
    {'lat': 28.6139 + 0.008, 'lng': 77.2090 - 0.004, 'risk': 'LOW', 'prob': 0.25, 'location': 'Monitoring Point C'},
    {'lat': 28.6139 - 0.006, 'lng': 77.2090 - 0.006, 'risk': 'MEDIUM', 'prob': 0.45, 'location': 'Slope Zone D'},
    {'lat': 28.6139 + 0.002, 'lng': 77.2090 + 0.012, 'risk': 'HIGH', 'prob': 0.78, 'location': 'Critical Area E'},
    {'lat': 28.6139 - 0.008, 'lng': 77.2090 + 0.002, 'risk': 'LOW', 'prob': 0.18, 'location': 'Safe Zone F'},
]

# FIRST ROW - Risk Map Overview
st.markdown('<div class="section-header"><h3>🗺️ Risk Map Overview</h3></div>', unsafe_allow_html=True)

# Map configuration controls with better styling
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    center_lat = st.number_input('📍 Latitude', value=28.6139, format="%.4f")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    center_lng = st.number_input('📍 Longitude', value=77.2090, format="%.4f")
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    zoom_level = st.slider('🔍 Zoom Level', 5, 18, 12)
    st.markdown('</div>', unsafe_allow_html=True)

# Create map with enhanced styling
m = folium.Map(
    location=[center_lat, center_lng],
    zoom_start=zoom_level,
    tiles='CartoDB Positron'  # Better contrast than OpenStreetMap
)

# Update coordinates and add enhanced markers
for i, risk in enumerate(sample_risks):
    if i == 0:
        sample_risks[i]['lat'] = center_lat + 0.005
        sample_risks[i]['lng'] = center_lng + 0.005
    elif i == 1:
        sample_risks[i]['lat'] = center_lat - 0.003
        sample_risks[i]['lng'] = center_lng + 0.008

for risk in sample_risks:
    color = {'HIGH': '#e74c3c', 'MEDIUM': '#f39c12', 'LOW': '#27ae60'}[risk['risk']]
    
    folium.CircleMarker(
        location=[risk['lat'], risk['lng']],
        radius=12,
        popup=folium.Popup(f"""
        <div style="font-family: Arial; padding: 10px;">
            <h4 style="color: {color};">{risk['location']}</h4>
            <p><strong>Risk Level:</strong> {risk['risk']}</p>
            <p><strong>Probability:</strong> {risk['prob']:.1%}</p>
        </div>
        """, max_width=200),
        color='white',
        weight=3,
        fillColor=color,
        fillOpacity=0.9
    ).add_to(m)

# Enhanced legend
legend_html = '''
<div style="position: fixed; 
            top: 15px; right: 15px; width: 160px; height: 120px; 
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%); 
            border: none; z-index: 9999; 
            font-size: 14px; padding: 15px; border-radius: 10px;
            color: white; box-shadow: 0 4px 15px rgba(0,0,0,0.3);">
<h4 style="margin: 0 0 10px 0; color: #ecf0f1;">🏗️ Risk Levels</h4>
<p style="margin: 5px 0;"><span style="color: #e74c3c;">●</span> High Risk (>70%)</p>
<p style="margin: 5px 0;"><span style="color: #f39c12;">●</span> Medium Risk (30-70%)</p>
<p style="margin: 5px 0;"><span style="color: #27ae60;">●</span> Low Risk (<30%)</p>
</div>
'''
m.get_root().html.add_child(folium.Element(legend_html))

# Display map in a container
st.markdown('<div class="chart-container">', unsafe_allow_html=True)
folium_static(m, width=None, height=500)
st.markdown('</div>', unsafe_allow_html=True)

# SECOND ROW - Enhanced Key Metrics and Risk Distribution
st.markdown("---")

col_metrics, col_pie = st.columns([2, 1])

with col_metrics:
    st.markdown('<div class="section-header"><h3>📈 Key Metrics</h3></div>', unsafe_allow_html=True)
    
    # Enhanced metrics with gradient cards
    col_m1, col_m2 = st.columns(2)
    
    with col_m1:
        high_risk_count = len([r for r in sample_risks if r['risk'] == 'HIGH'])
        st.markdown(f"""
        <div class="metric-card">
            <h3>🔴 High-Risk Zones</h3>
            <h1>{high_risk_count}</h1>
            <p>+1 from yesterday</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="metric-card">
            <h3>📡 Active Sensors</h3>
            <h1>28</h1>
            <p>+3 new sensors</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_m2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>🚨 Alerts (24h)</h3>
            <h1>12</h1>
            <p>+5 from yesterday</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="metric-card">
            <h3>⚡ System Uptime</h3>
            <h1>99.9%</h1>
            <p>+0.1% improvement</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Additional system overview
    st.markdown('<div class="section-header"><h4>🏗️ System Overview</h4></div>', unsafe_allow_html=True)
    
    col_sys1, col_sys2, col_sys3 = st.columns(3)
    
    with col_sys1:
        st.markdown("""
        <div class="weather-card">
            <h4>🌡️ Avg Temperature</h4>
            <h2>24.5°C</h2>
            <p>+1.2°C</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_sys2:
        st.markdown("""
        <div class="weather-card">
            <h4>🌧️ Rainfall Today</h4>
            <h2>8.3mm</h2>
            <p>+2.1mm</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_sys3:
        st.markdown("""
        <div class="weather-card">
            <h4>📊 Data Points</h4>
            <h2>2.4K</h2>
            <p>+156 new</p>
        </div>
        """, unsafe_allow_html=True)

with col_pie:
    st.markdown('<div class="section-header"><h3>🎯 Risk Distribution</h3></div>', unsafe_allow_html=True)
    
    # Calculate risk distribution
    risk_counts = {}
    for risk in sample_risks:
        risk_level = risk['risk'].title()
        risk_counts[risk_level] = risk_counts.get(risk_level, 0) + 1
    
    risk_data = pd.DataFrame({
        'Risk Level': list(risk_counts.keys()),
        'Count': list(risk_counts.values())
    })
    
    # Enhanced pie chart
    fig_pie = px.pie(
        risk_data, 
        values='Count', 
        names='Risk Level',
        color='Risk Level',
        color_discrete_map={'Low': '#27ae60', 'Medium': '#f39c12', 'High': '#e74c3c'},
        title="Current Zone Distribution"
    )
    fig_pie.update_traces(
        textposition='inside', 
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>',
        textfont_size=13,
        textfont_color='white'
    )
    fig_pie.update_layout(
        showlegend=True, 
        height=400,
        title_x=0.5,
        font=dict(size=12),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.plotly_chart(fig_pie, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Enhanced risk summary
    total_zones = len(sample_risks)
    high_risk_pct = (risk_counts.get('High', 0) / total_zones) * 100
    
    if high_risk_pct > 40:
        st.markdown(f"""
        <div class="risk-card-high">
            <h4>⚠️ Risk Alert</h4>
            <p>{high_risk_pct:.0f}% zones are high-risk</p>
        </div>
        """, unsafe_allow_html=True)
    elif high_risk_pct > 20:
        st.markdown(f"""
        <div class="risk-card-medium">
            <h4>📊 Risk Status</h4>
            <p>{high_risk_pct:.0f}% zones are high-risk</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="risk-card-low">
            <h4>✅ System Stable</h4>
            <p>Only {high_risk_pct:.0f}% zones are high-risk</p>
        </div>
        """, unsafe_allow_html=True)

# Continue with rest of the dashboard code with similar styling enhancements...
# [Rest of the code would follow the same pattern with enhanced styling]

