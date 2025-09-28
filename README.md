# 🪨 AI-Based Rockfall Prediction & Alert System

A comprehensive, end-to-end system that combines environmental data, geotechnical sensors, and drone imagery to predict rockfall probability and trigger automated alerts for mining safety operations.

## 🌟 Features

- **Multi-Modal Data Integration**: Environmental JSON, sensor time-series, and drone imagery
- **Real-time Risk Assessment**: ML-powered probability scoring with LOW/MEDIUM/HIGH classification
- **Interactive Dashboard**: Streamlit web interface with MapMyIndia integration
- **Automated Alerts**: Email (Vonage) and SMS (SMS77) notifications
- **RESTful API**: FastAPI backend with MongoDB storage
- **Scalable Architecture**: Modular design for easy expansion

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit     │    │    FastAPI      │    │    MongoDB      │
│   Frontend      │◄──►│    Backend      │◄──►│    Database     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       
         │                       ▼                       
         │              ┌─────────────────┐              
         │              │  ML Pipeline    │              
         │              │  (RandomForest) │              
         │              └─────────────────┘              
         │                       │                       
         ▼                       ▼                       
┌─────────────────┐    ┌─────────────────┐              
│  External APIs  │    │  Alert Services │              
│  (MapMyIndia)   │    │ (Email + SMS)   │              
└─────────────────┘    └─────────────────┘              
```

## 🚀 Quick Start

### 1. Clone and Setup
```bash
git clone <repository-url>
cd ai-rockfall-system
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment Configuration
```bash
cp .env.example .env
# Edit .env with your API keys and MongoDB URI
```

### 3. Generate Sample Data
```bash
python scripts/seed_sensors.py
```

### 4. Train the Model
```bash
cd ml
python train.py
cd ..
```

### 5. Start Backend API
```bash
uvicorn backend.main:app --reload --port 8000
```

### 6. Launch Frontend
```bash
streamlit run streamlit_app/app.py
```

## 📊 Data Sources

### Environmental Data (`data/Sub_Division_IMD.json`)
- Rainfall measurements
- Temperature readings
- Atmospheric conditions
- Timestamp-indexed records

### Geotechnical Sensors (`data/sensors/*.csv`)
- **Displacement**: Ground movement measurements
- **Strain**: Rock stress indicators
- **Pore Pressure**: Groundwater pressure
- **Vibrations**: Seismic activity

### Drone Imagery (`data/DroneImages/FilteredData/`)
- **Images**: Raw drone photographs
- **Masks**: Segmentation masks
- **BinaryMasks**: Binary classification masks

## 🧠 Machine Learning Pipeline

### Feature Engineering
- Time-based aggregations (rolling windows, lags)
- Cross-sensor correlations
- Weather-geology interactions
- Image summary statistics

### Model Architecture
- **Algorithm**: Random Forest Classifier
- **Features**: 20+ engineered variables
- **Output**: Risk probability (0-1) + classification (LOW/MEDIUM/HIGH)
- **Performance**: Target AUC > 0.75

### Risk Classification
- **LOW**: 0.0 - 0.33
- **MEDIUM**: 0.33 - 0.66  
- **HIGH**: 0.66 - 1.0

## 🌐 API Endpoints

### Health Check
```
GET /api/health
```

### Predictions
```
POST /api/predict
Body: {
  "timestamp": "2025-01-01T12:00:00",
  "rainfall_mm": 25.5,
  "temperature_c": 22.0,
  "displacement": 3.2,
  "strain": 0.8,
  "pore_pressure": 1.5,
  "vibrations": 0.4
}
```

### Sensor Data
```
POST /api/sensors          # Ingest new readings
GET /api/sensors?limit=200 # Retrieve recent data
```

### Alerts
```
POST /api/alerts           # Trigger notifications
GET /api/alerts?limit=50   # View history
```

## 🖥️ User Interface

### Dashboard
- Live risk map with MapMyIndia integration
- Key performance indicators
- Recent activity feed

### Imagery Viewer
- Drone image galleries
- Mask visualizations
- Batch processing controls

### Sensor Management
- Real-time data streams
- Historical trends
- CSV upload interface

### Alert Center
- Manual alert triggers
- Notification history
- Channel preferences

## 🔧 Configuration

### Required Environment Variables
```bash
# Database
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB=rockfall_db

# MapMyIndia
MAPMYINDIA_ACCESS_TOKEN=your_token

# Email Alerts
Vonage_API_KEY=your_key
ALERT_EMAIL_FROM=alerts@domain.com
ALERT_EMAIL_TO=team@domain.com

# SMS Alerts  
SMS77IO_RAPIDAPI_KEY=your_key
ALERT_SMS_TO=+1234567890
```

## 🔄 Development Workflow

### Adding New Features
1. Update ML pipeline in `ml/` directory
2. Modify API endpoints in `backend/routers/`
3. Enhance UI in `streamlit_app/pages/`
4. Test integration end-to-end

### Data Pipeline
1. Place new data in `data/` directories
2. Run feature engineering: `python ml/features.py`
3. Retrain model: `python ml/train.py`
4. Restart backend to load new model

## 📈 Monitoring & Maintenance

### Model Performance
- Monitor prediction accuracy
- Track alert effectiveness
- Analyze false positive/negative rates

### System Health
- API response times
- Database performance
- External service availability

## 🚨 Alert System

### Email Notifications (Vonage)
- Rich HTML formatting
- Attachment support
- Delivery tracking

### SMS Alerts (SMS77/RapidAPI)
- Global coverage
- Delivery confirmation
- Rate limiting

### Trigger Conditions
- High risk probability (>0.66)
- Rapid sensor value changes
- Manual operator triggers

## 📦 Production Deployment

### Docker Support (Optional)
```dockerfile
FROM python:3.9-slim
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Scaling Considerations
- Load balancer for API
- MongoDB replica sets
- Redis for caching
- CDN for image assets

## 🔍 Troubleshooting

### Common Issues
1. **Model not found**: Run `python ml/train.py` first
2. **API connection errors**: Check backend is running on port 8000
3. **Map not loading**: Verify MapMyIndia token in `.env`
4. **Alerts not sending**: Validate Vonage/SMS77 credentials

### Debug Mode
```bash
# Backend with debug logging
uvicorn backend.main:app --reload --log-level debug

# Streamlit with error details
streamlit run streamlit_app/app.py --logger.level=debug
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-feature`
3. Commit changes: `git commit -am 'Add new feature'`
4. Push to branch: `git push origin feature/new-feature`
5. Submit pull request



## 👥 Team

- **ML Engineering**: Predictive modeling and feature engineering
- **Backend Development**: API design and database management  
- **Frontend Development**: User interface and visualization
- **DevOps**: Deployment and infrastructure management

## 🙏 Acknowledgments

- MapMyIndia for mapping services
- Vonage for SMS capabilities
- Open-source ML and web frameworks

## Output

🪨 Alert System
- Vonage for email infrastructure
- SMS77 for SMS capabilities

## Output

1) Using Leaflet and Openstreet API red zones show which are prone, green zones show which are safe and yellow which are medium risk
![WhatsApp Image 2025-09-28 at 17 49 08_25d1e012](https://github.com/user-attachments/assets/07175b45-8323-4f11-ad21-f399b3aaea35)

<img width="887" height="827" alt="image" src="https://github.com/user-attachments/assets/52000dd8-807c-45a6-87c9-0f065974d5f9" />

2) Alert Triggering System working Using Vonage
![WhatsApp Image 2025-09-28 at 17 56 19_8ee269ff](https://github.com/user-attachments/assets/e871e0c7-3017-47c7-9d8a-15e4d4b2102e)

![WhatsApp Image 2025-09-28 at 17 57 41_0cb78c21](https://github.com/user-attachments/assets/e520d5f8-9659-401e-875b-1539baaa5c86)

3) Risk Predictions using graphs
![WhatsApp Image 2025-09-28 at 17 55 32_8a7b97c5](https://github.com/user-attachments/assets/1fb4dcd4-7b06-4201-95b4-d4ba644baed1)

![WhatsApp Image 2025-09-28 at 17 54 36_6bedff71](https://github.com/user-attachments/assets/4d968590-1e6f-4017-8148-34853f3244fc)

4) Sensors
![WhatsApp Image 2025-09-28 at 17 47 10_1ae893a8](https://github.com/user-attachments/assets/2d6a7ac6-b5e7-435a-a255-77b30de5b405)

![WhatsApp Image 2025-09-28 at 17 47 32_bb9352f6](https://github.com/user-attachments/assets/bbdc55e0-7d76-4277-ad54-bbdf51da9207)








