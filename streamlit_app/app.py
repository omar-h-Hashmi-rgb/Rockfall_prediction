import os
import requests
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
from typing import Dict, List, Optional

# Page configuration
st.set_page_config(
    page_title='🪨 Rockfall Monitor', 
    page_icon='🪨', 
    layout='wide',
    initial_sidebar_state='expanded'
)

# Configuration
API_BASE = os.getenv('API_BASE', 'http://localhost:8000')

# Session state initialization
if 'auth' not in st.session_state:
    st.session_state.auth = False
if 'username' not in st.session_state:
    st.session_state.username = ''

# Enhanced Custom CSS with better contrast and visibility
st.markdown("""
<style>
    /* Main app background */
    .main .block-container {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
    }
    
    /* Main header styling */
    .main-header {
        background: linear-gradient(90deg, #1e3a8a 0%, #0891b2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 5px 20px rgba(0, 0, 0, 0.15);
        font-size: 2.5rem;
        font-weight: bold;
    }
    
    /* Enhanced metric cards */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        border: none;
    }
    
    /* Quick actions card with better contrast */
    .quick-actions-card {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        border: none;
    }
    
    /* Login card styling */
    .login-card {
        background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
        padding: 2rem;
        border-radius: 20px;
        color: white;
        margin: 2rem 0;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        border: none;
    }
    
    /* Risk level cards */
    .risk-high {
        background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 5px 15px rgba(231, 76, 60, 0.3);
    }
    
    .risk-medium {
        background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 5px 15px rgba(243, 156, 18, 0.3);
    }
    
    .risk-low {
        background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 5px 15px rgba(39, 174, 96, 0.3);
    }
    
    /* Sidebar enhancements */
    .sidebar-info {
        background: linear-gradient(135deg, #6c5ce7 0%, #a29bfe 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 5px 15px rgba(108, 92, 231, 0.3);
    }
    
    /* Status indicators */
    .status-online {
        background: linear-gradient(135deg, #00b894 0%, #00cec9 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
        text-align: center;
    }
    
    .status-offline {
        background: linear-gradient(135deg, #e17055 0%, #d63031 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
        text-align: center;
    }
    
    /* Form styling */
    .stTextInput > div > div > input {
        background-color: rgba(255, 255, 255, 0.9);
        border: 2px solid #ddd;
        border-radius: 10px;
        padding: 0.75rem;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 1.5rem;
        font-weight: bold;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
    }
    
    /* Welcome section styling */
    .welcome-section {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        padding: 2rem;
        border-radius: 15px;
        color: #2d3436;
        margin: 1rem 0;
        box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
    }
    
    /* Chart containers */
    .chart-container {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def check_api_health() -> Dict:
    """Check if API is accessible."""
    try:
        response = requests.get(f"{API_BASE}/api/health", timeout=5)
        if response.status_code == 200:
            return {"status": "healthy", "data": response.json()}
        else:
            return {"status": "unhealthy", "error": f"HTTP {response.status_code}"}
    except requests.exceptions.RequestException as e:
        return {"status": "error", "error": str(e)}

def login_ui():
    """Enhanced login interface with better visibility."""
    st.markdown('<div class="main-header">🪨 Rockfall Monitoring System</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div class="login-card">
            <h3>🔐 Secure Access Required</h3>
            <p>Please log in to access the rockfall monitoring dashboard with advanced AI-powered risk assessment capabilities.</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input('👤 Username', placeholder="Enter your username")
            password = st.text_input('🔑 Password', type='password', placeholder="Enter your password")
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                login_btn = st.form_submit_button('🚀 Login', use_container_width=True)
            with col_btn2:
                demo_btn = st.form_submit_button('🧪 Demo Mode', use_container_width=True)
            
            if login_btn:
                if username and password:
                    st.session_state.auth = True
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.error('❌ Please enter both username and password')
            
            if demo_btn:
                st.session_state.auth = True
                st.session_state.username = "demo_user"
                st.rerun()
        
        # Enhanced API Status
        st.markdown('<div class="metric-card"><h3>🔧 System Status</h3></div>', unsafe_allow_html=True)
        api_health = check_api_health()
        
        if api_health["status"] == "healthy":
            st.markdown('<div class="status-online">✅ API Connection: Healthy</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="status-offline">❌ API Connection: {api_health.get("error", "Unknown error")}</div>', unsafe_allow_html=True)

def main_app():
    """Enhanced main application interface."""
    # Enhanced Sidebar
    with st.sidebar:
        st.markdown(f"""
        <div class="sidebar-info">
            <h3>👋 Welcome!</h3>
            <p><strong>{st.session_state.username}</strong></p>
            <p>Logged in at {datetime.now().strftime('%H:%M:%S')}</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button('🚪 Logout', use_container_width=True):
            st.session_state.auth = False
            st.session_state.username = ''
            st.rerun()
        
        st.markdown("---")
        
        st.markdown('<div class="metric-card"><h3>📊 Navigation</h3></div>', unsafe_allow_html=True)
        st.page_link("pages/1_Dashboard.py", label="🗺️ Dashboard", icon="🗺️")
        st.page_link("pages/2_Imagery.py", label="🛰️ Imagery", icon="🛰️")
        st.page_link("pages/3_Sensors.py", label="📡 Sensors", icon="📡")
        st.page_link("pages/4_Alerts.py", label="🚨 Alerts", icon="🚨")
        st.page_link("pages/5_Settings.py", label="⚙️ Settings", icon="⚙️")
        
        st.markdown("---")
        
        # Enhanced system status
        st.markdown('<div class="metric-card"><h3>🔧 System Status</h3></div>', unsafe_allow_html=True)
        api_health = check_api_health()
        
        if api_health["status"] == "healthy":
            st.markdown('<div class="status-online">API: Online</div>', unsafe_allow_html=True)
            
            if "data" in api_health:
                health_data = api_health["data"]
                if health_data.get("status") == "healthy":
                    st.markdown('<div class="status-online">Database: Connected</div>', unsafe_allow_html=True)
                    st.markdown('<div class="status-online">Model: Loaded</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-offline">API: Offline</div>', unsafe_allow_html=True)
    
    # Enhanced main content
    st.markdown('<div class="main-header">🪨 AI-Based Rockfall Prediction System</div>', unsafe_allow_html=True)
    
    # Enhanced welcome section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        <div class="welcome-section">
            <h3>🎯 Welcome to the Rockfall Monitoring Dashboard</h3>
            <p>This advanced AI-powered system provides real-time rockfall risk assessment using:</p>
            <ul>
                <li>🌦️ <strong>Environmental data</strong> (rainfall, temperature, weather conditions)</li>
                <li>📡 <strong>Geotechnical sensors</strong> (displacement, strain, pore pressure, vibrations)</li>
                <li>🛰️ <strong>Drone imagery</strong> analysis and segmentation</li>
                <li>🧠 <strong>Machine learning</strong> algorithms for risk prediction</li>
                <li>🚨 <strong>Automated alerts</strong> via email and SMS</li>
            </ul>
            <p>Navigate using the sidebar to access different system components.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="quick-actions-card">
            <h4>🔥 Quick Actions</h4>
            <p>• View risk dashboard<br>
            • Check sensor readings<br>
            • Review alert history<br>
            • Analyze imagery data</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Enhanced Quick Prediction Widget
    st.markdown('<div class="metric-card"><h3>🚀 Quick Risk Assessment</h3></div>', unsafe_allow_html=True)
    
    with st.form("quick_prediction"):
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            rainfall = st.number_input('🌧️ Rainfall (mm)', 0.0, 500.0, 0.0, help="Current rainfall amount")
        with col2:
            vibrations = st.number_input('📳 Vibrations', 0.0, 5.0, 0.2, help="Ambient vibration level")
        with col3:
            displacement = st.number_input('📏 Displacement (mm)', 0.0, 100.0, 0.0, help="Ground displacement")
        with col4:
            temperature = st.number_input('🌡️ Temperature (°C)', -20.0, 60.0, 25.0, help="Current temperature")
        
        submitted = st.form_submit_button('🔮 Predict Risk Now', use_container_width=True)
        
        if submitted:
            payload = {
                'timestamp': datetime.utcnow().isoformat(),
                'rainfall_mm': rainfall,
                'ambient_vibration': vibrations,
                'displacement': displacement,
                'temperature_c': temperature,
                'strain': 0.5,
                'pore_pressure': 1.0,
                'vibrations': vibrations
            }
            
            try:
                response = requests.post(f"{API_BASE}/api/predict", json=payload, timeout=20)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    col_result1, col_result2, col_result3 = st.columns(3)
                    
                    with col_result1:
                        st.markdown(f"""
                        <div class="metric-card">
                            <h4>🎯 Risk Probability</h4>
                            <h2>{result['probability']:.2%}</h2>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col_result2:
                        risk_class = result['risk_class']
                        if risk_class == 'HIGH':
                            card_class = "risk-high"
                        elif risk_class == 'MEDIUM':
                            card_class = "risk-medium"
                        else:
                            card_class = "risk-low"
                        
                        risk_color = {'LOW': '🟢', 'MEDIUM': '🟡', 'HIGH': '🔴'}.get(risk_class, '⚪')
                        
                        st.markdown(f"""
                        <div class="{card_class}">
                            <h4>⚠️ Risk Level</h4>
                            <h2>{risk_color} {risk_class}</h2>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col_result3:
                        confidence = min(abs(result['probability'] - 0.5) * 2, 1.0)
                        st.markdown(f"""
                        <div class="metric-card">
                            <h4>🎲 Confidence</h4>
                            <h2>{confidence:.2%}</h2>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Enhanced risk interpretation
                    if result['probability'] > 0.7:
                        st.markdown("""
                        <div class="risk-high">
                            <h4>🚨 HIGH RISK DETECTED</h4>
                            <p>Immediate action recommended!</p>
                        </div>
                        """, unsafe_allow_html=True)
                    elif result['probability'] > 0.4:
                        st.markdown("""
                        <div class="risk-medium">
                            <h4>⚠️ MODERATE RISK</h4>
                            <p>Monitor closely and prepare contingencies.</p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown("""
                        <div class="risk-low">
                            <h4>✅ LOW RISK</h4>
                            <p>Current conditions are stable.</p>
                        </div>
                        """, unsafe_allow_html=True)
                
                else:
                    st.error(f"❌ Prediction failed: HTTP {response.status_code}")
                    
            except Exception as e:
                st.error(f"❌ Prediction failed: {str(e)}")
    
    st.markdown("---")
    
    # Enhanced Recent Activity Summary
    st.markdown('<div class="metric-card"><h3>📈 Recent System Activity</h3></div>', unsafe_allow_html=True)
    
    try:
        pred_response = requests.get(f"{API_BASE}/api/predict/recent?limit=10", timeout=10)
        
        if pred_response.status_code == 200:
            pred_data = pred_response.json()
            
            if pred_data.get('predictions'):
                df_predictions = pd.DataFrame(pred_data['predictions'])
                
                if len(df_predictions) > 0:
                    df_predictions['timestamp'] = pd.to_datetime(df_predictions['timestamp'])
                    
                    fig = px.line(
                        df_predictions.head(10), 
                        x='timestamp', 
                        y='probability',
                        title="<b>Recent Risk Predictions</b>",
                        labels={'probability': 'Risk Probability (%)', 'timestamp': 'Date & Time'}
                    )
                    
                    # Enhanced styling with professional colors
                    fig.update_traces(
                        line_color='#00d4ff',
                        line_width=4,
                        mode='lines+markers',
                        marker=dict(size=8, color='#ff6b6b', line=dict(width=2, color='white'))
                    )
                    
                    fig.update_layout(
                        paper_bgcolor='#1e1e1e',
                        plot_bgcolor='#2d2d2d',
                        font=dict(color='white', size=14, family='Arial'),
                        title=dict(
                            font=dict(size=20, color='white', family='Arial'),
                            x=0.5,
                            xanchor='center'
                        ),
                        xaxis=dict(
                            title=dict(text='<b>Date & Time</b>', font=dict(size=16, color='white')),
                            showgrid=True,
                            gridcolor='rgba(128, 128, 128, 0.2)',
                            showline=True,
                            linecolor='white',
                            linewidth=2,
                            tickfont=dict(size=12, color='white')
                        ),
                        yaxis=dict(
                            title=dict(text='<b>Risk Probability (%)</b>', font=dict(size=16, color='white')),
                            showgrid=True,
                            gridcolor='rgba(128, 128, 128, 0.2)',
                            showline=True,
                            linecolor='white',
                            linewidth=2,
                            tickfont=dict(size=12, color='white'),
                            tickformat='.0%'
                        ),
                        hovermode='x unified',
                        hoverlabel=dict(
                            bgcolor='#ff6b6b',
                            font_size=14,
                            font_family='Arial',
                            font_color='white'
                        ),
                        margin=dict(l=80, r=40, t=80, b=80)
                    )
                    
                    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                    st.plotly_chart(fig, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="metric-card"><p>📊 No recent predictions available</p></div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="metric-card"><p>📊 No recent predictions available</p></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-offline">⚠️ Could not load recent activity</div>', unsafe_allow_html=True)
            
    except Exception as e:
        st.markdown(f'<div class="status-offline">⚠️ Could not load recent activity: {str(e)}</div>', unsafe_allow_html=True)

# Main application logic
if not st.session_state.auth:
    login_ui()
else:
    main_app()
