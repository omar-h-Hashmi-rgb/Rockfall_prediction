from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class AlertChannel(str, Enum):
    EMAIL = "email"
    SMS = "sms"

class SensorType(str, Enum):
    DISPLACEMENT = "displacement"
    STRAIN = "strain"
    PORE_PRESSURE = "pore_pressure"
    VIBRATIONS = "vibrations"

# Sensor Data Schemas
class SensorRecord(BaseModel):
    model_config = {"protected_namespaces": ()}
    timestamp: datetime
    sensor_type: Optional[SensorType] = None
    displacement: Optional[float] = None
    strain: Optional[float] = None
    pore_pressure: Optional[float] = None
    vibrations: Optional[float] = None
    location: Optional[str] = None
    sensor_id: Optional[str] = None
    
    @validator('displacement', 'strain', 'pore_pressure', 'vibrations')
    def validate_sensor_values(cls, v):
        if v is not None and v < 0:
            raise ValueError('Sensor values must be non-negative')
        return v

class SensorBatch(BaseModel):
    model_config = {"protected_namespaces": ()}
    records: List[SensorRecord]
    
    @validator('records')
    def validate_records_not_empty(cls, v):
        if not v:
            raise ValueError('Records list cannot be empty')
        return v

# Prediction Schemas
class PredictRequest(BaseModel):
    model_config = {"protected_namespaces": ()}
    timestamp: Optional[datetime] = None
    
    # Environmental features
    rainfall_mm: Optional[float] = 0.0
    temperature_c: Optional[float] = 20.0
    humidity: Optional[float] = 50.0
    wind_speed: Optional[float] = 0.0
    pressure: Optional[float] = 1013.25
    ambient_vibration: Optional[float] = 0.0
    
    # Sensor features
    displacement: Optional[float] = 0.0
    strain: Optional[float] = 0.0
    pore_pressure: Optional[float] = 0.0
    vibrations: Optional[float] = 0.0
    
    # Additional features
    location: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = {}
    
    @validator('rainfall_mm', 'displacement', 'strain', 'pore_pressure', 'vibrations')
    def validate_non_negative(cls, v):
        if v is not None and v < 0:
            raise ValueError('Values must be non-negative')
        return v
    
    @validator('temperature_c')
    def validate_temperature(cls, v):
        if v is not None and (v < -50 or v > 60):
            raise ValueError('Temperature must be between -50 and 60 degrees Celsius')
        return v
    
    @validator('humidity')
    def validate_humidity(cls, v):
        if v is not None and (v < 0 or v > 100):
            raise ValueError('Humidity must be between 0 and 100 percent')
        return v

class PredictResponse(BaseModel):
    model_config = {"protected_namespaces": ()}
    probability: float = Field(..., ge=0.0, le=1.0, description="Risk probability between 0 and 1")
    risk_class: RiskLevel = Field(..., description="Risk classification: LOW/MEDIUM/HIGH")
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="Model confidence")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    ml_model_version: Optional[str] = None
    features_used: Optional[List[str]] = None

class BatchPredictRequest(BaseModel):
    model_config = {"protected_namespaces": ()}
    requests: List[PredictRequest]
    
    @validator('requests')
    def validate_requests_not_empty(cls, v):
        if not v:
            raise ValueError('Requests list cannot be empty')
        if len(v) > 100:
            raise ValueError('Maximum 100 requests per batch')
        return v

class BatchPredictResponse(BaseModel):
    model_config = {"protected_namespaces": ()}
    predictions: List[PredictResponse]
    batch_id: str
    processed_count: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# Alert Schemas
class AlertRequest(BaseModel):
    model_config = {"protected_namespaces": ()}
    message: str = Field(..., min_length=1, max_length=500)
    probability: float = Field(..., ge=0.0, le=1.0)
    risk_level: Optional[RiskLevel] = None
    channels: List[AlertChannel] = Field(default=[AlertChannel.EMAIL])
    location: Optional[str] = None
    priority: Optional[str] = "medium"
    metadata: Optional[Dict[str, Any]] = {}
    
    @validator('channels')
    def validate_channels_not_empty(cls, v):
        if not v:
            raise ValueError('At least one alert channel must be specified')
        return v

class AlertResponse(BaseModel):
    model_config = {"protected_namespaces": ()}
    alert_id: str
    status: str
    results: Dict[str, bool]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    message: str

class AlertHistory(BaseModel):
    model_config = {"protected_namespaces": ()}
    alert_id: str
    message: str
    probability: float
    risk_level: RiskLevel
    channels: List[AlertChannel]
    results: Dict[str, bool]
    timestamp: datetime
    location: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = {}

# User Schemas
class UserCreate(BaseModel):
    model_config = {"protected_namespaces": ()}
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$')
    full_name: Optional[str] = None
    role: str = "user"
    is_active: bool = True

class User(BaseModel):
    model_config = {"protected_namespaces": ()}
    id: str
    username: str
    email: str
    full_name: Optional[str] = None
    role: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None

class UserLogin(BaseModel):
    model_config = {"protected_namespaces": ()}
    username: str
    password: str

# Health Check Schema
class HealthCheck(BaseModel):
    model_config = {"protected_namespaces": ()}
    status: str
    timestamp: datetime
    version: str = "1.0.0"
    database: Dict[str, Any]
    model: Dict[str, Any]
    services: Dict[str, Any] = {}

# Map Schemas
class MapRequest(BaseModel):
    model_config = {"protected_namespaces": ()}
    center_lat: float = Field(..., ge=-90, le=90)
    center_lng: float = Field(..., ge=-180, le=180)
    zoom: int = Field(default=12, ge=1, le=18)
    size: str = Field(default="800x600", pattern=r'^\d+x\d+$')
    markers: Optional[List[Dict[str, Any]]] = []

class MapResponse(BaseModel):
    model_config = {"protected_namespaces": ()}
    map_url: str
    center_lat: float
    center_lng: float
    zoom: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# Statistics Schemas
class SensorStats(BaseModel):
    model_config = {"protected_namespaces": ()}
    sensor_type: SensorType
    count: int
    avg_value: float
    min_value: float
    max_value: float
    last_reading: datetime

class SystemStats(BaseModel):
    model_config = {"protected_namespaces": ()}
    total_sensors: int
    total_predictions: int
    total_alerts: int
    high_risk_zones: int
    last_24h_alerts: int
    ml_model_accuracy: Optional[float] = None
    uptime: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# Error Schemas
class ErrorResponse(BaseModel):
    model_config = {"protected_namespaces": ()}
    error: str
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: Optional[str] = None

