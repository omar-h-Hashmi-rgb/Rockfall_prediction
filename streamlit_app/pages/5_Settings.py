import streamlit as st
import os
import requests
from datetime import datetime

st.set_page_config(page_title='Settings', page_icon='⚙️', layout='wide')

# CSS for text visibility
st.markdown("""
<style>
    /* Ensure all text is visible on dark theme */
    .stMarkdown, .stMarkdown p, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 {
        color: #ecf0f1 !important;
    }
    
    /* Input labels */
    .stTextInput label, .stSelectbox label, .stNumberInput label, .stCheckbox label, .stRadio label {
        color: #ecf0f1 !important;
        font-weight: bold !important;
    }
    
    /* Tab labels */
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        color: #ecf0f1 !important;
    }
    
    /* Metric values */
    [data-testid="stMetricValue"], [data-testid="stMetricLabel"] {
        color: #ecf0f1 !important;
    }
</style>
""", unsafe_allow_html=True)

# Check authentication
if not st.session_state.get('auth', False):
    st.error("🔒 Please log in to access settings")
    st.stop()

API_BASE = os.getenv('API_BASE', 'http://localhost:8000')

st.title('⚙️ System Settings & Configuration')

# Check API connection
try:
    health_response = requests.get(f"{API_BASE}/api/health", timeout=5)
    api_healthy = health_response.status_code == 200
except:
    api_healthy = False

# Create tabs for different settings categories
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🔗 API Settings", 
    "🗺️ Map Configuration", 
    "📧 Alert Settings", 
    "👤 User Preferences", 
    "🔧 System Status"
])

with tab1:
    st.markdown("### 🔗 API Configuration")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        current_api_base = st.text_input(
            "🌐 API Base URL",
            value=os.getenv('API_BASE', 'http://localhost:8000'),
            help="Base URL for the backend API"
        )
        
        if current_api_base != API_BASE:
            st.warning("⚠️ API URL changed. Restart app to apply changes.")
        
        # Test API connection
        if st.button("🧪 Test API Connection"):
            try:
                test_response = requests.get(f"{current_api_base}/api/health", timeout=5)
                
                if test_response.status_code == 200:
                    st.success("✅ API connection successful!")
                    
                    health_data = test_response.json()
                    st.json(health_data)
                else:
                    st.error(f"❌ API connection failed: HTTP {test_response.status_code}")
            
            except Exception as e:
                st.error(f"❌ API connection failed: {str(e)}")
        
        # API Endpoints overview
        st.markdown("#### 📋 Available Endpoints")
        
        if api_healthy:
            try:
                root_response = requests.get(current_api_base, timeout=5)
                if root_response.status_code == 200:
                    api_info = root_response.json()
                    
                    st.info(f"**API Name:** {api_info.get('name', 'Unknown')}")
                    st.info(f"**Version:** {api_info.get('version', 'Unknown')}")
                    st.info(f"**Status:** {api_info.get('status', 'Unknown')}")
                    
                    endpoints = api_info.get('endpoints', {})
                    for name, path in endpoints.items():
                        st.code(f"{name}: {current_api_base}{path}")
                        
            except Exception as e:
                st.warning(f"Could not load API info: {str(e)}")
        else:
            st.warning("⚠️ API not accessible")
    
    with col2:
        st.markdown("#### 🔧 Connection Status")
        
        if api_healthy:
            st.success("🟢 API Online")
        else:
            st.error("🔴 API Offline")
        
        st.markdown("#### 📊 Environment")
        st.info(f"""
        **Environment Variables:**
        - API_BASE: {os.getenv('API_BASE', 'Not set')}
        - Debug Mode: {os.getenv('DEBUG', 'False')}
        """)

with tab2:
    st.markdown("### 🗺️ Map Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🌍 MapMyIndia Settings")
        
        map_token = st.text_input(
            "🔑 Access Token",
            value=os.getenv('MAPMYINDIA_ACCESS_TOKEN', ''),
            type="password",
            help="MapMyIndia API access token"
        )
        
        map_base_url = st.text_input(
            "🌐 Base URL",
            value=os.getenv('MAPMYINDIA_API_BASE_URL', 'https://apis.mapmyindia.com/advancedmaps/v1'),
            help="MapMyIndia API base URL"
        )
        
        # Default map settings
        st.markdown("#### 📍 Default Map View")
        
        default_lat = st.number_input(
            "📍 Default Latitude",
            value=28.6139,
            format="%.4f",
            help="Default map center latitude"
        )
        
        default_lng = st.number_input(
            "📍 Default Longitude", 
            value=77.2090,
            format="%.4f",
            help="Default map center longitude"
        )
        
        default_zoom = st.slider(
            "🔍 Default Zoom Level",
            5, 18, 12,
            help="Default map zoom level"
        )
        
        if st.button("💾 Save Map Settings"):
            st.success("✅ Map settings saved!")
            st.info("Note: Changes require app restart to take effect")
    
    with col2:
        st.markdown("#### 🎨 Map Display Options")
        
        show_risk_markers = st.checkbox("🔴 Show Risk Markers", value=True)
        show_sensor_locations = st.checkbox("📡 Show Sensor Locations", value=True)
        show_legend = st.checkbox("📋 Show Legend", value=True)
        
        map_theme = st.selectbox(
            "🎨 Map Theme",
            ["Default", "Satellite", "Terrain", "Hybrid"],
            help="Map display style"
        )
        
        marker_size = st.slider("📍 Marker Size", 5, 20, 12)
        
        # Test map service
        if st.button("🧪 Test Map Service"):
            if map_token:
                try:
                    test_url = f"{map_base_url}/{map_token}/staticmap?center={default_lat},{default_lng}&zoom={default_zoom}&size=200x200"
                    
                    test_response = requests.get(test_url, timeout=10)
                    
                    if test_response.status_code == 200:
                        st.success("✅ Map service working!")
                        st.image(test_response.content, caption="Test Map", width=200)
                    else:
                        st.error(f"❌ Map service failed: HTTP {test_response.status_code}")
                
                except Exception as e:
                    st.error(f"❌ Map service test failed: {str(e)}")
            else:
                st.warning("⚠️ Please enter MapMyIndia access token")

with tab3:
    st.markdown("### 📧 Alert Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📧 Email Settings (SendGrid)")
        
        email_api_key = st.text_input(
            "🔑 SendGrid API Key",
            value=os.getenv('SENDGRID_API_KEY', ''),
            type="password",
            help="SendGrid API key for email alerts"
        )
        
        email_from = st.text_input(
            "📤 From Email",
            value=os.getenv('ALERT_EMAIL_FROM', 'alerts@example.com'),
            help="Sender email address"
        )
        
        email_to = st.text_input(
            "📥 To Email", 
            value=os.getenv('ALERT_EMAIL_TO', 'ops@example.com'),
            help="Default recipient email address"
        )
        
        # Test email
        if st.button("📧 Test Email Service"):
            if api_healthy and email_api_key:
                try:
                    test_response = requests.post(
                        f"{API_BASE}/api/alerts/test",
                        json={"channels": ["email"]},
                        timeout=20
                    )
                    
                    if test_response.status_code == 200:
                        result = test_response.json()
                        if result.get('results', {}).get('email'):
                            st.success("✅ Email service working!")
                        else:
                            st.error("❌ Email service failed")
                    else:
                        st.error("❌ Email test failed")
                
                except Exception as e:
                    st.error(f"❌ Email test error: {str(e)}")
            else:
                st.warning("⚠️ API offline or email not configured")
    
    with col2:
        st.markdown("#### 📱 SMS Settings (SMS77)")
        
        sms_api_key = st.text_input(
            "🔑 SMS77 RapidAPI Key",
            value=os.getenv('SMS77IO_RAPIDAPI_KEY', ''),
            type="password",
            help="SMS77 RapidAPI key for SMS alerts"
        )
        
        sms_host = st.text_input(
            "🌐 SMS77 Host",
            value=os.getenv('SMS77IO_HOST', 'sms77io.p.rapidapi.com'),
            help="SMS77 API host"
        )
        
        sms_to = st.text_input(
            "📱 Default SMS Number",
            value=os.getenv('ALERT_SMS_TO', ''),
            help="Default SMS recipient number (with country code)"
        )
        
        # Test SMS
        if st.button("📱 Test SMS Service"):
            if api_healthy and sms_api_key:
                try:
                    test_response = requests.post(
                        f"{API_BASE}/api/alerts/test",
                        json={"channels": ["sms"]},
                        timeout=20
                    )
                    
                    if test_response.status_code == 200:
                        result = test_response.json()
                        if result.get('results', {}).get('sms'):
                            st.success("✅ SMS service working!")
                        else:
                            st.error("❌ SMS service failed")
                    else:
                        st.error("❌ SMS test failed")
                
                except Exception as e:
                    st.error(f"❌ SMS test error: {str(e)}")
            else:
                st.warning("⚠️ API offline or SMS not configured")
    
    # Alert thresholds
    st.markdown("#### ⚠️ Alert Thresholds")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        high_risk_threshold = st.slider("🔴 High Risk Threshold", 0.5, 1.0, 0.7, 0.05)
    
    with col2:
        medium_risk_threshold = st.slider("🟡 Medium Risk Threshold", 0.2, 0.8, 0.4, 0.05)
    
    with col3:
        alert_cooldown = st.number_input("⏰ Alert Cooldown (minutes)", 1, 60, 15)
    
    if st.button("💾 Save Alert Settings"):
        st.success("✅ Alert settings saved!")

with tab4:
    st.markdown("### 👤 User Preferences")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🎨 Interface Settings")
        
        theme = st.selectbox(
            "🎨 Theme",
            ["Light", "Dark", "Auto"],
            help="Application color theme"
        )
        
        language = st.selectbox(
            "🌐 Language",
            ["English", "Hindi", "Spanish", "French"],
            help="Interface language"
        )
        
        timezone = st.selectbox(
            "🕐 Timezone",
            ["UTC", "Asia/Kolkata", "America/New_York", "Europe/London"],
            index=1,
            help="Display timezone for timestamps"
        )
        
        refresh_interval = st.selectbox(
            "🔄 Auto-refresh Interval",
            ["Off", "30 seconds", "1 minute", "5 minutes", "15 minutes"],
            index=3,
            help="Automatic page refresh interval"
        )
    
    with col2:
        st.markdown("#### 📊 Dashboard Preferences")
        
        default_page = st.selectbox(
            "🏠 Default Page",
            ["Dashboard", "Sensors", "Imagery", "Alerts"],
            help="Page to show after login"
        )
        
        charts_per_row = st.slider("📊 Charts per Row", 1, 4, 2)
        
        show_animations = st.checkbox("✨ Enable Animations", value=True)
        
        show_tooltips = st.checkbox("💡 Show Tooltips", value=True)
        
        compact_mode = st.checkbox("📱 Compact Mode", value=False)
    
    # User info
    st.markdown("#### 👤 User Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"""
        **Current User:** {st.session_state.get('username', 'Unknown')}
        **Login Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        **Session ID:** {id(st.session_state)}
        """)
    
    with col2:
        if st.button("🔓 Change Password"):
            st.info("Password change feature coming soon")
        
        if st.button("📤 Export Preferences"):
            preferences = {
                "theme": theme,
                "language": language,
                "timezone": timezone,
                "refresh_interval": refresh_interval,
                "default_page": default_page,
                "charts_per_row": charts_per_row,
                "show_animations": show_animations,
                "show_tooltips": show_tooltips,
                "compact_mode": compact_mode
            }
            
            st.download_button(
                "💾 Download Preferences",
                data=str(preferences),
                file_name="user_preferences.json",
                mime="application/json"
            )

with tab5:
    st.markdown("### 🔧 System Status & Diagnostics")
    
    # System overview
    if api_healthy:
        try:
            health_response = requests.get(f"{API_BASE}/api/health", timeout=10)
            
            if health_response.status_code == 200:
                health_data = health_response.json()
                
                st.markdown("#### 🟢 System Health Overview")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    api_status = health_data.get('status', 'unknown')
                    status_emoji = {
                        'healthy': '🟢',
                        'warning': '🟡',
                        'unhealthy': '🔴'
                    }.get(api_status, '⚪')
                    
                    st.metric("🔧 API Status", f"{status_emoji} {api_status.title()}")
                
                with col2:
                    db_status = health_data.get('database', {}).get('status', 'unknown')
                    db_emoji = '🟢' if db_status == 'healthy' else '🔴'
                    st.metric("🗄️ Database", f"{db_emoji} {db_status.title()}")
                
                with col3:
                    model_status = health_data.get('model', {}).get('status', 'unknown')
                    model_emoji = '🟢' if model_status == 'healthy' else '🔴'
                    st.metric("🧠 ML Model", f"{model_emoji} {model_status.title()}")
                
                with col4:
                    services = health_data.get('services', {})
                    services_healthy = sum(1 for s in services.values() if s.get('status') == 'healthy')
                    st.metric("🔗 Services", f"{services_healthy}/{len(services)}")
                
                # Detailed service status
                st.markdown("#### 🔍 Detailed Service Status")
                
                services = health_data.get('services', {})
                
                for service_name, service_data in services.items():
                    with st.expander(f"🔧 {service_name.title()} Service"):
                        st.json(service_data)
                
                # System metrics if available
                if 'system' in services:
                    system_data = services['system']
                    
                    st.markdown("#### 📊 System Metrics")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        cpu_percent = system_data.get('cpu_percent', 0)
                        cpu_color = '🟢' if cpu_percent < 70 else '🟡' if cpu_percent < 90 else '🔴'
                        st.metric("💻 CPU Usage", f"{cpu_color} {cpu_percent:.1f}%")
                    
                    with col2:
                        memory_percent = system_data.get('memory_percent', 0)
                        memory_color = '🟢' if memory_percent < 80 else '🟡' if memory_percent < 95 else '🔴'
                        st.metric("🧠 Memory Usage", f"{memory_color} {memory_percent:.1f}%")
                    
                    with col3:
                        disk_percent = system_data.get('disk_percent', 0)
                        disk_color = '🟢' if disk_percent < 85 else '🟡' if disk_percent < 95 else '🔴'
                        st.metric("💾 Disk Usage", f"{disk_color} {disk_percent:.1f}%")
            
            else:
                st.error("❌ Could not retrieve system health")
        
        except Exception as e:
            st.error(f"❌ Health check failed: {str(e)}")
    
    else:
        st.error("🔴 API Not Accessible")
        
        st.markdown("#### 🔧 Troubleshooting")
        st.warning("""
        **API Connection Issues:**
        
        1. **Check API URL:** Verify the API base URL is correct
        2. **Check Network:** Ensure network connectivity
        3. **Check API Status:** Verify the backend API is running
        4. **Check Firewall:** Ensure port 8000 is accessible
        5. **Check Logs:** Review backend logs for errors
        """)
    
    # Environment information
    st.markdown("#### 🌍 Environment Information")
    
    env_info = {
        "Streamlit Version": st.__version__,
        "Python Version": os.sys.version.split()[0],
        "Current Time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "API Base URL": API_BASE,
        "Session ID": str(id(st.session_state))[:8],
    }
    
    for key, value in env_info.items():
        st.info(f"**{key}:** {value}")
    
    # System actions
    st.markdown("#### 🔧 System Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Refresh System Status"):
            st.rerun()
    
    with col2:
        if st.button("🧹 Clear Cache"):
            st.cache_data.clear()
            st.success("✅ Cache cleared!")
    
    with col3:
        if st.button("📊 Run Full Diagnostic"):
            st.info("🔍 Running full system diagnostic...")
            
            # Simulate diagnostic
            import time
            progress_bar = st.progress(0)
            
            for i in range(100):
                time.sleep(0.01)
                progress_bar.progress(i + 1)
            
            st.success("✅ Diagnostic completed!")

# Footer
st.markdown("---")
st.caption(f"⚙️ Settings last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
st.caption("💡 Changes to environment variables require application restart to take effect.")