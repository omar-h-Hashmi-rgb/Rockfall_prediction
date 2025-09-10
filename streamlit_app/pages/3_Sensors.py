
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import numpy as np

st.set_page_config(page_title='Sensor Data', page_icon='📡', layout='wide')

# Check authentication
if not st.session_state.get('auth', False):
    st.error("🔒 Please log in to access sensor data")
    st.stop()

API_BASE = os.getenv('API_BASE', 'http://localhost:8000')

def show_demo_data():
    '''Show demo sensor data when API is not available.'''
    st.info("📊 Displaying demo sensor data")
    
    # Generate demo data
    timestamps = pd.date_range(
        start=datetime.now() - timedelta(hours=24),
        end=datetime.now(),
        freq='1H'
    )
    
    np.random.seed(42)
    demo_data = pd.DataFrame({
        'timestamp': timestamps,
        'displacement': 2 + np.random.normal(0, 0.3, len(timestamps)),
        'strain': 0.5 + np.random.normal(0, 0.1, len(timestamps)),
        'pore_pressure': 1.2 + np.random.normal(0, 0.2, len(timestamps)),
        'vibrations': 0.3 + np.random.gamma(2, 0.1, len(timestamps))
    })
    
    # Ensure non-negative values
    for col in ['displacement', 'strain', 'pore_pressure', 'vibrations']:
        demo_data[col] = np.maximum(demo_data[col], 0)
    
    display_sensor_data(demo_data)

def display_sensor_data(df):
    '''Display sensor data with charts and statistics.'''
    
    if df.empty:
        st.warning("📊 No data to display")
        return
    
    # Convert timestamp if it's a string
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Sensor overview metrics
    st.markdown("#### 📊 Sensor Overview")
    
    cols = st.columns(4)
    sensor_types = ['displacement', 'strain', 'pore_pressure', 'vibrations']
    
    for i, sensor_type in enumerate(sensor_types):
        if sensor_type in df.columns:
            values = df[sensor_type].dropna()
            if len(values) > 0:
                with cols[i]:
                    current_val = values.iloc[-1] if len(values) > 0 else 0
                    delta_val = (values.iloc[-1] - values.iloc[-2]) if len(values) > 1 else None
                    
                    st.metric(
                        label=f"📏 {sensor_type.title()}",
                        value=f"{current_val:.2f}",
                        delta=f"{delta_val:.2f}" if delta_val is not None else None
                    )
    
    # Time series charts
    st.markdown("#### 📈 Time Series Analysis")
    
    available_sensors = [col for col in sensor_types if col in df.columns and not df[col].isna().all()]
    
    if available_sensors and 'timestamp' in df.columns:
        # Create tabs for different views
        tab1, tab2, tab3 = st.tabs(["📊 Individual Sensors", "🔍 Combined View", "📋 Data Table"])
        
        with tab1:
            for sensor_type in available_sensors:
                st.markdown(f"##### {sensor_type.replace('_', ' ').title()}")
                
                sensor_data = df[['timestamp', sensor_type]].dropna()
                
                if len(sensor_data) > 0:
                    fig = px.line(
                        sensor_data,
                        x='timestamp',
                        y=sensor_type,
                        title=f"{sensor_type.title()} Over Time",
                        labels={sensor_type: f"{sensor_type.title()} Value", 'timestamp': 'Time'}
                    )
                    fig.update_traces(line_color='#2E86AB')
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Show statistics
                    col1, col2, col3, col4 = st.columns(4)
                    values = sensor_data[sensor_type]
                    
                    with col1:
                        st.metric("📊 Average", f"{values.mean():.2f}")
                    with col2:
                        st.metric("📈 Maximum", f"{values.max():.2f}")
                    with col3:
                        st.metric("📉 Minimum", f"{values.min():.2f}")
                    with col4:
                        st.metric("📏 Std Dev", f"{values.std():.2f}")
        
        with tab2:
            if len(available_sensors) > 1:
                # Create combined plot
                fig = go.Figure()
                colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D']
                
                for i, sensor in enumerate(available_sensors):
                    sensor_data = df[['timestamp', sensor]].dropna()
                    if len(sensor_data) > 0:
                        fig.add_trace(go.Scatter(
                            x=sensor_data['timestamp'],
                            y=sensor_data[sensor],
                            mode='lines',
                            name=sensor.title(),
                            line=dict(color=colors[i % len(colors)])
                        ))
                
                fig.update_layout(
                    title="Sensor Data Comparison",
                    xaxis_title="Time",
                    yaxis_title="Sensor Values",
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("🔍 Need multiple sensor types for combined view")
        
        with tab3:
            st.markdown("##### 📋 Raw Data")
            st.dataframe(df, use_container_width=True, height=400)
            
            # Download button
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"sensor_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

# Main application logic
def main():
    st.title('📡 Geotechnical & Environmental Sensors')
    
    # Check API connection
    try:
        health_response = requests.get(f"{API_BASE}/api/health", timeout=5)
        api_healthy = health_response.status_code == 200
    except:
        api_healthy = False
    
    # Sidebar controls
    with st.sidebar:
        st.markdown("### 🎛️ Data Controls")
        
        data_source = st.selectbox(
            "📊 Data Source",
            ["🧪 Demo Data", "📁 Upload CSV", "🔗 Live API Data"],
            help="Choose your data source"
        )
        
        refresh_data = st.button("🔄 Refresh Data", use_container_width=True)
    
    # Main content based on data source
    if data_source == "🧪 Demo Data":
        st.markdown("### 🧪 Demo Sensor Data")
        show_demo_data()
        
    elif data_source == "📁 Upload CSV":
        st.markdown("### 📤 Upload Sensor Data")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            uploaded_file = st.file_uploader(
                "📄 Choose CSV file",
                type=['csv'],
                help="Upload a CSV file with sensor data"
            )
            
            if uploaded_file:
                try:
                    df = pd.read_csv(uploaded_file)
                    st.success(f"✅ Loaded {len(df)} records")
                    
                    # Show preview
                    st.markdown("#### 👀 Data Preview")
                    st.dataframe(df.head(10), use_container_width=True)
                    
                    # Display the data
                    display_sensor_data(df)
                    
                except Exception as e:
                    st.error(f"❌ Error reading file: {str(e)}")
        
        with col2:
            st.markdown("#### 📋 CSV Format Guide")
            st.info("""
            **Expected columns:**
            - `timestamp`: Date/time
            - `displacement`: Displacement values
            - `strain`: Strain measurements
            - `pore_pressure`: Pressure readings
            - `vibrations`: Vibration data
            """)
    
    elif data_source == "🔗 Live API Data":
        st.markdown("### 📊 Live Sensor Data")
        
        if api_healthy:
            try:
                # Try to fetch some sample data from API
                response = requests.get(f"{API_BASE}/api/sensors", timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('records'):
                        df_api = pd.DataFrame(data['records'])
                        st.success(f"✅ Loaded {len(df_api)} API records")
                        display_sensor_data(df_api)
                    else:
                        st.info("📊 No recent sensor data available from API")
                        show_demo_data()
                else:
                    st.warning("⚠️ API returned no data. Showing demo data.")
                    show_demo_data()
                    
            except Exception as e:
                st.error(f"❌ Error fetching API data: {str(e)}")
                st.info("📊 Falling back to demo data")
                show_demo_data()
        else:
            st.warning("⚠️ API not available. Showing demo data.")
            show_demo_data()
    
    # System health section
    st.markdown("---")
    st.markdown("### 🔧 System Health")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        api_status = "🟢 Healthy" if api_healthy else "🔴 Offline"
        st.metric("🔧 API Status", api_status)
    
    with col2:
        st.metric("📊 Data Source", data_source)
    
    with col3:
        current_time = datetime.now().strftime("%H:%M:%S")
        st.metric("⏰ Last Update", current_time)
    
    # Auto-refresh option
    if st.button("🔄 Auto-refresh", use_container_width=True):
        st.rerun()

# Run the main application
if __name__ == "__main__":
    main()

