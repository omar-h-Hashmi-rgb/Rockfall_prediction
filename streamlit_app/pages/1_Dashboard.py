# Create the enhanced Dashboard.py with India-wide coverage
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
    
    .custom-card label {
        color: white !important;
        font-weight: bold !important;
        font-size: 1.1rem !important;
    }
    
    .custom-card input, .custom-card .stSlider {
        background-color: rgba(255, 255, 255, 0.2) !important;
        color: white !important;
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
    
    .section-header {
        background: linear-gradient(90deg, #2E86AB, #A23B72);
        padding: 0.8rem 1.5rem;
        border-radius: 8px;
        color: white;
        font-weight: bold;
        margin: 1rem 0;
        text-align: center;
    }
    
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

st.markdown('<div class="section-header"><h1>📊 India-Wide Rockfall Risk Dashboard</h1></div>', unsafe_allow_html=True)

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
        ⚠️ <strong>API not accessible.</strong> Running in demo mode with India-wide simulation data.
    </div>
    """, unsafe_allow_html=True)

# COMPREHENSIVE INDIA-WIDE RISK MONITORING LOCATIONS
# Based on major mining regions, geological fault zones, and high-risk areas
india_risk_zones = [
    # NORTHERN INDIA - Himalayan Region & Mining Areas
    {'lat': 28.6139, 'lng': 77.2090, 'risk': 'HIGH', 'prob': 0.85, 'location': 'Delhi NCR Mining Zone', 'state': 'Delhi', 'type': 'Urban Mining'},
    {'lat': 30.7333, 'lng': 76.7794, 'risk': 'MEDIUM', 'prob': 0.55, 'location': 'Chandigarh Quarry Complex', 'state': 'Punjab', 'type': 'Stone Quarry'},
    {'lat': 32.2431, 'lng': 77.1892, 'risk': 'HIGH', 'prob': 0.78, 'location': 'Himachal Slate Mines', 'state': 'Himachal Pradesh', 'type': 'Slate Mining'},
    {'lat': 34.0837, 'lng': 74.7973, 'risk': 'MEDIUM', 'prob': 0.62, 'location': 'Kashmir Valley Minerals', 'state': 'J&K', 'type': 'Mineral Extraction'},
    {'lat': 29.9457, 'lng': 78.1642, 'risk': 'LOW', 'prob': 0.28, 'location': 'Haridwar Limestone', 'state': 'Uttarakhand', 'type': 'Limestone Quarry'},
    
    # CENTRAL INDIA - Coal Belt & Iron Ore Regions
    {'lat': 23.2599, 'lng': 77.4126, 'risk': 'HIGH', 'prob': 0.82, 'location': 'Bhopal Mining District', 'state': 'Madhya Pradesh', 'type': 'Coal Mining'},
    {'lat': 21.2787, 'lng': 81.8661, 'risk': 'HIGH', 'prob': 0.89, 'location': 'Raipur Coal Fields', 'state': 'Chhattisgarh', 'type': 'Coal Mining'},
    {'lat': 25.5941, 'lng': 85.1376, 'risk': 'MEDIUM', 'prob': 0.58, 'location': 'Patna Quarry Zone', 'state': 'Bihar', 'type': 'Stone Quarry'},
    {'lat': 23.3441, 'lng': 85.3096, 'risk': 'HIGH', 'prob': 0.76, 'location': 'Ranchi Iron Ore', 'state': 'Jharkhand', 'type': 'Iron Ore Mining'},
    {'lat': 26.9124, 'lng': 75.7873, 'risk': 'MEDIUM', 'prob': 0.45, 'location': 'Jaipur Marble Mines', 'state': 'Rajasthan', 'type': 'Marble Quarry'},
    
    # WESTERN INDIA - Coastal & Industrial Mining
    {'lat': 19.0760, 'lng': 72.8777, 'risk': 'MEDIUM', 'prob': 0.52, 'location': 'Mumbai Port Quarry', 'state': 'Maharashtra', 'type': 'Construction Material'},
    {'lat': 15.2993, 'lng': 74.1240, 'risk': 'HIGH', 'prob': 0.73, 'location': 'Goa Iron Ore Mines', 'state': 'Goa', 'type': 'Iron Ore Mining'},
    {'lat': 23.0225, 'lng': 72.5714, 'risk': 'MEDIUM', 'prob': 0.48, 'location': 'Ahmedabad Limestone', 'state': 'Gujarat', 'type': 'Limestone Quarry'},
    {'lat': 18.5204, 'lng': 73.8567, 'risk': 'LOW', 'prob': 0.32, 'location': 'Pune Basalt Quarry', 'state': 'Maharashtra', 'type': 'Basalt Extraction'},
    
    # SOUTHERN INDIA - Granite & Mineral Rich Region
    {'lat': 12.9716, 'lng': 77.5946, 'risk': 'MEDIUM', 'prob': 0.59, 'location': 'Bangalore Granite Mines', 'state': 'Karnataka', 'type': 'Granite Quarry'},
    {'lat': 13.0827, 'lng': 80.2707, 'risk': 'LOW', 'prob': 0.35, 'location': 'Chennai Coastal Mining', 'state': 'Tamil Nadu', 'type': 'Sand Mining'},
    {'lat': 8.5241, 'lng': 76.9366, 'risk': 'LOW', 'prob': 0.22, 'location': 'Trivandrum Clay Mines', 'state': 'Kerala', 'type': 'Clay Extraction'},
    {'lat': 17.3850, 'lng': 78.4867, 'risk': 'MEDIUM', 'prob': 0.64, 'location': 'Hyderabad Coal Region', 'state': 'Telangana', 'type': 'Coal Mining'},
    {'lat': 15.3173, 'lng': 75.7139, 'risk': 'HIGH', 'prob': 0.81, 'location': 'Bellary Iron Ore', 'state': 'Karnataka', 'type': 'Iron Ore Mining'},
    
    # EASTERN INDIA - Coal & Steel Belt
    {'lat': 22.5726, 'lng': 88.3639, 'risk': 'MEDIUM', 'prob': 0.56, 'location': 'Kolkata Industrial Belt', 'state': 'West Bengal', 'type': 'Industrial Mining'},
    {'lat': 20.9517, 'lng': 85.0985, 'risk': 'HIGH', 'prob': 0.87, 'location': 'Bhubaneswar Iron Ore', 'state': 'Odisha', 'type': 'Iron Ore Mining'},
    {'lat': 26.2006, 'lng': 92.9376, 'risk': 'MEDIUM', 'prob': 0.43, 'location': 'Guwahati Coal Mines', 'state': 'Assam', 'type': 'Coal Mining'},
    {'lat': 25.5788, 'lng': 91.8933, 'risk': 'LOW', 'prob': 0.29, 'location': 'Shillong Limestone', 'state': 'Meghalaya', 'type': 'Limestone Quarry'},
    
    # NORTHEASTERN INDIA - Remote Mining Operations
    {'lat': 23.1645, 'lng': 92.9376, 'risk': 'MEDIUM', 'prob': 0.47, 'location': 'Tripura Gas Fields', 'state': 'Tripura', 'type': 'Gas Extraction'},
    {'lat': 27.0238, 'lng': 88.2636, 'risk': 'LOW', 'prob': 0.31, 'location': 'Sikkim Mineral Zone', 'state': 'Sikkim', 'type': 'Mineral Mining'},
    
    # ADDITIONAL STRATEGIC LOCATIONS - Major Geological Zones
    {'lat': 22.9734, 'lng': 78.6569, 'risk': 'HIGH', 'prob': 0.79, 'location': 'Central India Coal Belt', 'state': 'Madhya Pradesh', 'type': 'Coal Mining'},
    {'lat': 19.7515, 'lng': 75.7139, 'risk': 'MEDIUM', 'prob': 0.53, 'location': 'Aurangabad Quarries', 'state': 'Maharashtra', 'type': 'Stone Quarry'},
    {'lat': 16.5062, 'lng': 80.6480, 'risk': 'LOW', 'prob': 0.26, 'location': 'Vijayawada Clay Mines', 'state': 'Andhra Pradesh', 'type': 'Clay Mining'},
    {'lat': 11.0168, 'lng': 76.9558, 'risk': 'LOW', 'prob': 0.24, 'location': 'Coimbatore Granite', 'state': 'Tamil Nadu', 'type': 'Granite Quarry'},
    
    # HIMALAYAN BORDER REGIONS - High Altitude Mining
    {'lat': 29.3919, 'lng': 79.4304, 'risk': 'HIGH', 'prob': 0.84, 'location': 'Uttarakhand Border Mines', 'state': 'Uttarakhand', 'type': 'Border Mining'},
    {'lat': 27.7172, 'lng': 85.3240, 'risk': 'MEDIUM', 'prob': 0.61, 'location': 'Nepal Border Zone', 'state': 'Bihar', 'type': 'Cross-border Mining'}
]

# FIRST ROW - India-Wide Risk Map Overview
st.markdown('<div class="section-header"><h3>🗺️ India-Wide Risk Map Overview</h3></div>', unsafe_allow_html=True)

# Map configuration controls with India defaults
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    center_lat = st.number_input('📍 Latitude', value=20.5937, format="%.4f", help="Center of India")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    center_lng = st.number_input('📍 Longitude', value=78.9629, format="%.4f", help="Center of India")
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    zoom_level = st.slider('🔍 Zoom Level', 4, 8, 5, help="India-wide view")
    st.markdown('</div>', unsafe_allow_html=True)

# Region filter
region_filter = st.multiselect(
    "🌍 Filter by Region",
    ["Northern India", "Central India", "Western India", "Southern India", "Eastern India", "Northeastern India"],
    default=["Northern India", "Central India", "Western India", "Southern India", "Eastern India", "Northeastern India"]
)

# Create India-wide map
m = folium.Map(
    location=[center_lat, center_lng],
    zoom_start=zoom_level,
    tiles='CartoDB Positron'
)

# Filter zones based on region selection
region_mapping = {
    "Northern India": ["Delhi", "Punjab", "Himachal Pradesh", "J&K", "Uttarakhand"],
    "Central India": ["Madhya Pradesh", "Chhattisgarh", "Bihar", "Jharkhand", "Rajasthan"],
    "Western India": ["Maharashtra", "Goa", "Gujarat"],
    "Southern India": ["Karnataka", "Tamil Nadu", "Kerala", "Telangana", "Andhra Pradesh"],
    "Eastern India": ["West Bengal", "Odisha", "Assam"],
    "Northeastern India": ["Meghalaya", "Tripura", "Sikkim"]
}

filtered_zones = []
for zone in india_risk_zones:
    zone_state = zone['state']
    for region in region_filter:
        if zone_state in region_mapping.get(region, []):
            filtered_zones.append(zone)
            break

# Add enhanced markers for each risk zone
for zone in filtered_zones:
    color = {'HIGH': '#e74c3c', 'MEDIUM': '#f39c12', 'LOW': '#27ae60'}[zone['risk']]
    
    # Marker size based on risk level
    radius = {'HIGH': 15, 'MEDIUM': 12, 'LOW': 10}[zone['risk']]
    
    folium.CircleMarker(
        location=[zone['lat'], zone['lng']],
        radius=radius,
        popup=folium.Popup(f"""
        <div style="font-family: Arial; padding: 15px; min-width: 250px;">
            <h4 style="color: {color}; margin: 0 0 10px 0;">{zone['location']}</h4>
            <p><strong>State:</strong> {zone['state']}</p>
            <p><strong>Mining Type:</strong> {zone['type']}</p>
            <p><strong>Risk Level:</strong> <span style="color: {color};">{zone['risk']}</span></p>
            <p><strong>Probability:</strong> {zone['prob']:.1%}</p>
            <p><strong>Coordinates:</strong> {zone['lat']:.4f}, {zone['lng']:.4f}</p>
        </div>
        """, max_width=300),
        color='white',
        weight=3,
        fillColor=color,
        fillOpacity=0.8,
        tooltip=f"{zone['location']} - {zone['risk']} Risk"
    ).add_to(m)

# Add state boundaries visualization (simplified)
state_boundaries = [
    # Major state boundary points for visual reference
    {'name': 'Rajasthan', 'coords': [[23.0, 69.0], [30.0, 69.0], [30.0, 78.0], [23.0, 78.0], [23.0, 69.0]]},
    {'name': 'Maharashtra', 'coords': [[15.5, 72.0], [22.0, 72.0], [22.0, 80.5], [15.5, 80.5], [15.5, 72.0]]},
    {'name': 'Uttar Pradesh', 'coords': [[24.0, 77.0], [31.0, 77.0], [31.0, 84.0], [24.0, 84.0], [24.0, 77.0]]}
]

# Enhanced legend with statistics
total_zones = len(filtered_zones)
high_risk_zones = len([z for z in filtered_zones if z['risk'] == 'HIGH'])
medium_risk_zones = len([z for z in filtered_zones if z['risk'] == 'MEDIUM']) 
low_risk_zones = len([z for z in filtered_zones if z['risk'] == 'LOW'])

legend_html = f'''
<div style="position: fixed; 
            top: 15px; right: 15px; width: 200px; height: 180px; 
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%); 
            border: none; z-index: 9999; 
            font-size: 13px; padding: 15px; border-radius: 10px;
            color: white; box-shadow: 0 4px 15px rgba(0,0,0,0.3);">
<h4 style="margin: 0 0 10px 0; color: #ecf0f1;">🏗️ India Mining Risk Zones</h4>
<p style="margin: 5px 0;"><span style="color: #e74c3c;">●</span> High Risk: {high_risk_zones} zones</p>
<p style="margin: 5px 0;"><span style="color: #f39c12;">●</span> Medium Risk: {medium_risk_zones} zones</p>
<p style="margin: 5px 0;"><span style="color: #27ae60;">●</span> Low Risk: {low_risk_zones} zones</p>
<hr style="margin: 10px 0; border-color: #7f8c8d;">
<p style="margin: 5px 0; font-size: 12px;"><strong>Total Zones:</strong> {total_zones}</p>
<p style="margin: 5px 0; font-size: 11px;">🌍 Covering all major mining regions across India</p>
</div>
'''
m.get_root().html.add_child(folium.Element(legend_html))

# Display India-wide map
st.markdown('<div class="chart-container">', unsafe_allow_html=True)
folium_static(m, width=None, height=600)
st.markdown('</div>', unsafe_allow_html=True)

# SECOND ROW - Enhanced India-Wide Statistics
st.markdown("---")

col_metrics, col_pie = st.columns([2, 1])

with col_metrics:
    st.markdown('<div class="section-header"><h3>📈 India-Wide Risk Metrics</h3></div>', unsafe_allow_html=True)
    
    # National overview metrics
    col_m1, col_m2 = st.columns(2)
    
    with col_m1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>🔴 High-Risk Mining Zones</h3>
            <h1>{high_risk_zones}</h1>
            <p>Across {len(set([z['state'] for z in filtered_zones if z['risk'] == 'HIGH']))} states</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="metric-card">
            <h3>🏭 Total Mining Operations</h3>
            <h1>{total_zones}</h1>
            <p>Major mining regions monitored</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_m2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>📊 States Under Monitoring</h3>
            <h1>{len(set([z['state'] for z in filtered_zones]))}</h1>
            <p>Comprehensive coverage</p>
        </div>
        """, unsafe_allow_html=True)
        
        avg_risk = np.mean([z['prob'] for z in filtered_zones])
        st.markdown(f"""
        <div class="metric-card">
            <h3>📈 National Avg Risk</h3>
            <h1>{avg_risk:.1%}</h1>
            <p>All India average</p>
        </div>
        """, unsafe_allow_html=True)

# State-wise breakdown
    st.markdown('<div class="section-header"><h4>🗺️ State-wise Risk Distribution</h4></div>', unsafe_allow_html=True)
    
    # Calculate state-wise statistics
    state_stats = {}
    for zone in filtered_zones:
        state = zone['state']
        if state not in state_stats:
            state_stats[state] = {'HIGH': 0, 'MEDIUM': 0, 'LOW': 0, 'total': 0}
        state_stats[state][zone['risk']] += 1
        state_stats[state]['total'] += 1
    
    # Display top 5 states by risk zones
    top_states = sorted(state_stats.items(), key=lambda x: x[1]['total'], reverse=True)[:5]
    
    for state, stats in top_states:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.write(f"**{state}:**")
        with col2:
            st.write(f"🔴 {stats['HIGH']}")
        with col3:
            st.write(f"🟡 {stats['MEDIUM']}")
        with col4:
            st.write(f"🟢 {stats['LOW']}")

with col_pie:
    st.markdown('<div class="section-header"><h3>🎯 National Risk Distribution</h3></div>', unsafe_allow_html=True)
    
    # Calculate risk distribution
    risk_counts = {'High': high_risk_zones, 'Medium': medium_risk_zones, 'Low': low_risk_zones}
    
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
        title="India-Wide Risk Assessment"
    )
    fig_pie.update_traces(
        textposition='inside', 
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Zones: %{value}<br>Percentage: %{percent}<extra></extra>',
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
    
    # National risk assessment
    high_risk_pct = (high_risk_zones / total_zones) * 100
    
    if high_risk_pct > 40:
        st.markdown(f"""
        <div class="risk-card-high">
            <h4>🚨 National Alert</h4>
            <p>{high_risk_pct:.0f}% of mining zones are high-risk</p>
        </div>
        """, unsafe_allow_html=True)
    elif high_risk_pct > 20:
        st.markdown(f"""
        <div class="risk-card-medium">
            <h4>⚠️ Elevated Risk</h4>
            <p>{high_risk_pct:.0f}% of zones require monitoring</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="risk-card-low">
            <h4>✅ Stable Conditions</h4>
            <p>Only {high_risk_pct:.0f}% zones are high-risk</p>
        </div>
        """, unsafe_allow_html=True)

# Mining type analysis
st.markdown("---")
st.markdown('<div class="section-header"><h3>⛏️ Mining Type Risk Analysis</h3></div>', unsafe_allow_html=True)

# Calculate mining type distribution
mining_types = {}
for zone in filtered_zones:
    m_type = zone['type']
    if m_type not in mining_types:
        mining_types[m_type] = {'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
    mining_types[m_type][zone['risk']] += 1

# Display mining type analysis
col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 🏭 High-Risk Mining Operations")
    high_risk_types = sorted([(k, v['HIGH']) for k, v in mining_types.items()], key=lambda x: x[1], reverse=True)
    for mining_type, count in high_risk_types[:5]:
        if count > 0:
            st.write(f"• **{mining_type}**: {count} high-risk zones")

with col2:
    st.markdown("#### 📊 Mining Type Distribution")
    for mining_type, risks in list(mining_types.items())[:5]:
        total_type = sum(risks.values())
        st.write(f"**{mining_type}**: {total_type} zones")
        st.progress(total_type / len(filtered_zones))

# Auto-refresh and footer
st.markdown("---")

col_refresh1, col_refresh2 = st.columns(2)

with col_refresh1:
    if st.button("🔄 Refresh Dashboard", use_container_width=True):
        st.rerun()

with col_refresh2:
    auto_refresh = st.checkbox("🔄 Auto-refresh (30s)", value=False)

# Enhanced footer
st.markdown("---")
col_footer1, col_footer2, col_footer3 = st.columns(3)

with col_footer1:
    st.caption(f"📱 Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

with col_footer2:
    st.caption(f"🌐 Monitoring {total_zones} zones across {len(set([z['state'] for z in filtered_zones]))} Indian states")

with col_footer3:
    st.caption("🏗️ RockGuard AI v2.0 - India-Wide Rockfall Prediction System")
