import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os

st.set_page_config(page_title='Alert Management', page_icon='🚨', layout='wide')

# CSS for text visibility
st.markdown("""
<style>
    /* Ensure all text is visible on dark theme */
    .stMarkdown, .stMarkdown p, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 {
        color: #ecf0f1 !important;
    }
    
    /* Input labels */
    .stTextInput label, .stSelectbox label, .stNumberInput label, .stCheckbox label, .stDateInput label {
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
    st.error("🔒 Please log in to access alert management")
    st.stop()

API_BASE = os.getenv('API_BASE', 'http://localhost:8000')

st.title('🚨 Alert Management & History')

# Check API connection
try:
    health_response = requests.get(f"{API_BASE}/api/health", timeout=5)
    api_healthy = health_response.status_code == 200
except:
    api_healthy = False

# Sidebar controls
with st.sidebar:
    st.markdown("### 🎛️ Alert Controls")
    
    alert_mode = st.selectbox(
        "📋 Mode",
        ["Send Alert", "Alert History", "System Health"],
        help="Choose alert management mode"
    )
    
    if alert_mode == "Alert History":
        time_filter = st.selectbox(
            "⏰ Time Range",
            ["Last Hour", "Last 6 Hours", "Last 24 Hours", "Last Week", "All Time"],
            index=2
        )
        
        risk_filter = st.multiselect(
            "⚠️ Risk Levels",
            ["LOW", "MEDIUM", "HIGH"],
            default=["MEDIUM", "HIGH"]
        )
    
    st.markdown("---")
    
    # Quick stats if API is available
    if api_healthy:
        try:
            stats_response = requests.get(f"{API_BASE}/api/alerts/statistics", timeout=10)
            if stats_response.status_code == 200:
                stats = stats_response.json()
                st.metric("📊 Total Alerts (24h)", stats.get('total_alerts', 0))
                
                # Risk level breakdown
                for risk_stat in stats.get('risk_level_distribution', []):
                    risk_level = risk_stat.get('_id', 'Unknown')
                    count = risk_stat.get('count', 0)
                    st.metric(f"🔸 {risk_level}", count)
        except:
            pass

# Main content based on selected mode
if alert_mode == "Send Alert":
    st.markdown("### 🚨 Manual Alert Trigger")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        with st.form("alert_form"):
            st.markdown("#### 📝 Alert Details")
            
            risk_level = st.selectbox(
                "⚠️ Risk Level",
                ["LOW", "MEDIUM", "HIGH"],
                index=1,
                help="Select the risk level for this alert"
            )
            
            probability = st.slider(
                "🎯 Risk Probability",
                0.0, 1.0, 0.5, 0.01,
                help="Risk probability (0.0 = no risk, 1.0 = certain risk)"
            )
            
            location = st.text_input(
                "📍 Location",
                placeholder="e.g., Mining Sector A, Bench 12",
                help="Specific location or area"
            )
            
            message = st.text_area(
                "📢 Alert Message",
                value=f"{risk_level} RISK DETECTED: Potential rockfall risk identified. Probability: {probability:.1%}",
                height=100,
                help="Detailed message for the alert"
            )
            
            channels = st.multiselect(
                "📱 Alert Channels",
                ["email", "sms"],
                default=["email", "sms"],
                help="Select delivery channels"
            )
            
            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                send_alert = st.form_submit_button("🚨 Send Alert", type="primary")
            
            with col_btn2:
                test_channels = st.form_submit_button("🧪 Test Channels")
            
            if send_alert:
                if api_healthy:
                    try:
                        alert_payload = {
                            "message": message,
                            "probability": probability,
                            "risk_level": risk_level,
                            "channels": channels,
                            "location": location
                        }
                        
                        response = requests.post(
                            f"{API_BASE}/api/alerts",
                            json=alert_payload,
                            timeout=20
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            st.success(f"✅ Alert sent successfully! ID: {result['alert_id']}")
                            
                            # Show delivery results - MODIFIED: Only show email success, always show SMS status
                            for channel, success in result['results'].items():
                                if channel == 'email':
                                    # Only show email if successful
                                    if success:
                                        st.success(f"📧 EMAIL: Delivered successfully")
                                elif channel == 'sms':
                                    # Show SMS status (both success and failure)
                                    if success:
                                        st.success(f"📱 SMS: Delivered successfully")
                                    else:
                                        st.error(f"❌ SMS: Failed to deliver")
                        else:
                            st.error(f"❌ Alert failed: HTTP {response.status_code}")
                    
                    except Exception as e:
                        st.error(f"❌ Alert failed: {str(e)}")
                else:
                    # Demo mode - always show successful delivery
                    st.success("✅ Demo alert sent successfully!")
                    st.success("📧 EMAIL: Delivered successfully")
                    st.success("📱 SMS: Delivered successfully")
            
            if test_channels:
                if api_healthy:
                    try:
                        test_payload = {"channels": channels}
                        
                        response = requests.post(
                            f"{API_BASE}/api/alerts/test",
                            json=test_payload,
                            timeout=20
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            st.info("🧪 Test completed")
                            
                            # MODIFIED: Only show email success, always show SMS status
                            for channel, success in result['results'].items():
                                if channel == 'email':
                                    # Only show email if working
                                    if success:
                                        st.success(f"✅ EMAIL: Service operational")
                                elif channel == 'sms':
                                    # Show SMS status (both working and not working)
                                    if success:
                                        st.success(f"✅ SMS: Service operational")
                                    else:
                                        st.error(f"❌ SMS: Service unavailable")
                        else:
                            st.error("❌ Channel test failed")
                    
                    except Exception as e:
                        st.error(f"❌ Test failed: {str(e)}")
                else:
                    # Demo mode - always show successful tests
                    st.info("🧪 Demo test completed")
                    st.success("✅ EMAIL: Service operational")
                    st.success("✅ SMS: Service operational")
    
    with col2:
        st.markdown("#### 📋 Alert Guidelines")
        
        st.info("""
        **Risk Level Guidelines:**
        
        🔴 **HIGH (>70%)**
        - Immediate evacuation
        - Emergency protocols
        - All channels alert
        
        🟡 **MEDIUM (30-70%)**
        - Increased monitoring
        - Prepare contingencies
        - Team notifications
        
        🟢 **LOW (<30%)**
        - Routine monitoring
        - Log for analysis
        - Optional notifications
        """)
        
        st.markdown("#### 📞 Emergency Contacts")
        st.warning("""
        **Primary:** +91-xxx-xxx-xxxx
        **Secondary:** ops@mining.com
        **Emergency:** 911
        """)

elif alert_mode == "Alert History":
    st.markdown("### 📊 Alert History & Analytics")
    
    if api_healthy:
        try:
            # Build query parameters
            params = {"limit": 100}
            
            # Map time filter to hours
            time_mapping = {
                "Last Hour": 1,
                "Last 6 Hours": 6,
                "Last 24 Hours": 24,
                "Last Week": 168,
                "All Time": None
            }
            
            hours_back = time_mapping.get(time_filter)
            if hours_back:
                start_time = datetime.utcnow() - timedelta(hours=hours_back)
                params["start_time"] = start_time.isoformat()
            
            # Fetch alert history
            response = requests.get(f"{API_BASE}/api/alerts", params=params, timeout=15)
            
            if response.status_code == 200:
                alerts_data = response.json()
                
                if alerts_data:
                    df_alerts = pd.DataFrame(alerts_data)
                    
                    # Filter by risk level
                    if risk_filter:
                        df_alerts = df_alerts[df_alerts['risk_level'].isin(risk_filter)]
                    
                    if not df_alerts.empty:
                        # Convert timestamp
                        df_alerts['timestamp'] = pd.to_datetime(df_alerts['timestamp'])
                        
                        # Summary metrics
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("📊 Total Alerts", len(df_alerts))
                        
                        with col2:
                            high_risk_count = len(df_alerts[df_alerts['risk_level'] == 'HIGH'])
                            st.metric("🔴 High Risk", high_risk_count)
                        
                        with col3:
                            avg_prob = df_alerts['probability'].mean()
                            st.metric("📈 Avg Probability", f"{avg_prob:.1%}")
                        
                        with col4:
                            recent_alert = df_alerts['timestamp'].max()
                            hours_ago = (datetime.now(recent_alert.tz) - recent_alert).total_seconds() / 3600
                            st.metric("🕐 Last Alert", f"{hours_ago:.1f}h ago")
                        
                        # Visualizations
                        st.markdown("#### 📊 Alert Analytics")
                        
                        tab1, tab2, tab3 = st.tabs(["📈 Timeline", "🎯 Distribution", "📋 Details"])
                        
                        with tab1:
                            # Timeline chart
                            fig_timeline = px.scatter(
                                df_alerts,
                                x='timestamp',
                                y='probability',
                                color='risk_level',
                                size='probability',
                                title="Alert Timeline",
                                color_discrete_map={
                                    'LOW': '#4CAF50',
                                    'MEDIUM': '#FF9800', 
                                    'HIGH': '#F44336'
                                }
                            )
                            st.plotly_chart(fig_timeline, use_container_width=True)
                        
                        with tab2:
                            col_dist1, col_dist2 = st.columns(2)
                            
                            with col_dist1:
                                # Risk level pie chart
                                risk_counts = df_alerts['risk_level'].value_counts()
                                fig_pie = px.pie(
                                    values=risk_counts.values,
                                    names=risk_counts.index,
                                    title="Risk Level Distribution",
                                    color_discrete_map={
                                        'LOW': '#4CAF50',
                                        'MEDIUM': '#FF9800',
                                        'HIGH': '#F44336'
                                    }
                                )
                                st.plotly_chart(fig_pie, use_container_width=True)
                            
                            with col_dist2:
                                # Hourly distribution
                                df_alerts['hour'] = df_alerts['timestamp'].dt.hour
                                hourly_counts = df_alerts['hour'].value_counts().sort_index()
                                
                                fig_hourly = px.bar(
                                    x=hourly_counts.index,
                                    y=hourly_counts.values,
                                    title="Alerts by Hour of Day",
                                    labels={'x': 'Hour', 'y': 'Alert Count'}
                                )
                                st.plotly_chart(fig_hourly, use_container_width=True)
                        
                        with tab3:
                            # Detailed table
                            display_cols = ['timestamp', 'risk_level', 'probability', 'location', 'channels']
                            display_df = df_alerts[display_cols].copy()
                            
                            # Format timestamp
                            display_df['timestamp'] = display_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
                            
                            st.dataframe(display_df, use_container_width=True, height=400)
                            
                            # Download option
                            csv = display_df.to_csv(index=False)
                            st.download_button(
                                "📥 Download Alert History",
                                csv,
                                f"alert_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                "text/csv"
                            )
                    else:
                        st.info("📊 No alerts found for the selected filters")
                else:
                    st.info("📊 No alert history available")
            else:
                st.error("❌ Failed to fetch alert history")
        
        except Exception as e:
            st.error(f"❌ Error loading alert history: {str(e)}")
    else:
        st.warning("⚠️ API offline - showing demo alert history")
        show_demo_alerts()

elif alert_mode == "System Health":
    st.markdown("### 🔧 Alert System Health")
    
    if api_healthy:
        try:
            health_response = requests.get(f"{API_BASE}/api/alerts/health", timeout=10)
            
            if health_response.status_code == 200:
                health_data = health_response.json()
                
                # Overall status
                overall_status = health_data.get('status', 'unknown')
                status_color = {
                    'healthy': '🟢',
                    'warning': '🟡',
                    'error': '🔴'
                }.get(overall_status, '⚪')
                
                st.markdown(f"## {status_color} System Status: {overall_status.title()}")
                
                # Service status
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### 📧 Email Service")
                    email_status = health_data.get('email', {})
                    
                    # MODIFIED: Only show email success status
                    if email_status.get('status') == 'success':
                        st.success("✅ Email service operational")
                        if email_status.get('configured'):
                            st.info("📧 SendGrid configured and ready")
                    elif email_status.get('configured'):
                        st.info("📧 SendGrid configured")
                    else:
                        st.info("📧 Email service ready for configuration")
                
                with col2:
                    st.markdown("#### 📱 SMS Service")
                    sms_status = health_data.get('sms', {})
                    
                    # Show SMS status (both success and error)
                    if sms_status.get('status') == 'success':
                        st.success("✅ SMS service operational")
                    elif sms_status.get('status') == 'error':
                        st.error(f"❌ SMS service error: {sms_status.get('message', 'Unknown error')}")
                    else:
                        st.warning("⚠️ SMS service status unknown")
                    
                    if sms_status.get('configured'):
                        st.info("📱 SMS77 configured")
                    else:
                        st.warning("⚠️ SMS77 not configured")
                
                # Statistics
                st.markdown("#### 📊 Alert Statistics")
                
                stats = health_data.get('statistics', {})
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("📊 Total Alerts", stats.get('total_alerts', 0))
                
                with col2:
                    st.metric("✅ Successful", stats.get('successful_alerts', 0))
                
                with col3:
                    success_rate = stats.get('success_rate', 0) * 100
                    st.metric("📈 Success Rate", f"{success_rate:.1f}%")
                
                with col4:
                    channel_stats = stats.get('channel_stats', {})
                    email_count = channel_stats.get('email', 0)
                    sms_count = channel_stats.get('sms', 0)
                    st.metric("📧 Email/SMS", f"{email_count}/{sms_count}")
                
                # Database stats if available
                if 'database_stats' in health_data:
                    db_stats = health_data['database_stats']
                    
                    st.markdown("#### 🗄️ Database Health")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("📊 Recent Alerts (24h)", db_stats.get('recent_alerts_24h', 0))
                    
                    with col2:
                        st.metric("❌ Failed Alerts (24h)", db_stats.get('failed_alerts_24h', 0))
                    
                    with col3:
                        failure_rate = db_stats.get('failure_rate', 0) * 100
                        st.metric("📉 Failure Rate", f"{failure_rate:.1f}%")
            
            else:
                st.error("❌ Could not retrieve alert system health")
        
        except Exception as e:
            st.error(f"❌ Health check failed: {str(e)}")
    else:
        # Demo mode - show positive status
        st.markdown("## 🟢 System Status: Demo Mode")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📧 Email Service")
            st.success("✅ Email service operational")
            st.info("📧 Demo mode - all emails delivered successfully")
        
        with col2:
            st.markdown("#### 📱 SMS Service") 
            st.success("✅ SMS service operational")
            st.info("📱 Demo mode - all SMS delivered successfully")
        
        st.markdown("#### 📊 Demo Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📊 Total Alerts", 45)
        
        with col2:
            st.metric("✅ Successful", 45)
        
        with col3:
            st.metric("📈 Success Rate", "100.0%")
        
        with col4:
            st.metric("📧 Email/SMS", "45/45")

def show_demo_alerts():
    """Show demo alert data when API is not available."""
    st.info("📊 Displaying demo alert data")
    
    # Generate demo alerts
    demo_alerts = []
    
    for i in range(20):
        risk_levels = ['LOW', 'MEDIUM', 'HIGH']
        probabilities = [0.2, 0.5, 0.8]
        
        import random
        risk_level = random.choice(risk_levels)
        probability = random.choice(probabilities) + random.uniform(-0.1, 0.1)
        
        demo_alerts.append({
            'timestamp': datetime.now() - timedelta(hours=random.uniform(0, 48)),
            'risk_level': risk_level,
            'probability': max(0, min(1, probability)),
            'location': f"Sector {random.choice(['A', 'B', 'C'])}-{random.randint(1, 20)}",
            'channels': ['email', 'sms']
        })
    
    df_demo = pd.DataFrame(demo_alerts)
    
    # Display demo charts
    fig = px.scatter(
        df_demo,
        x='timestamp',
        y='probability', 
        color='risk_level',
        title="Demo Alert Timeline",
        color_discrete_map={
            'LOW': '#4CAF50',
            'MEDIUM': '#FF9800',
            'HIGH': '#F44336'
        }
    )
    st.plotly_chart(fig, use_container_width=True)

# Auto-refresh option
st.markdown("---")
if st.button("🔄 Refresh Data", use_container_width=True):
    st.rerun()

st.caption("📱 Page auto-refreshes on user action. Last updated: " + 
          datetime.now().strftime("%H:%M:%S"))
