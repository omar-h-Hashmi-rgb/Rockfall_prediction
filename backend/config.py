from pydantic import BaseModel
from dotenv import load_dotenv
import os
from typing import Optional

load_dotenv()

class Settings(BaseModel):
    # Database settings
    mongodb_uri: str = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
    mongodb_db: str = os.getenv('MONGODB_DB', 'rockfall_db')
    
    # MapMyIndia settings
    mapmyindia_access_token: str = os.getenv('MAPMYINDIA_ACCESS_TOKEN', '')
    mapmyindia_base_url: str = os.getenv('MAPMYINDIA_API_BASE_URL', 'https://apis.mapmyindia.com/advancedmaps/v1')
    
    # SendGrid settings
    sendgrid_api_key: str = os.getenv('SENDGRID_API_KEY', '')
    alert_email_from: str = os.getenv('ALERT_EMAIL_FROM', 'alerts@example.com')
    alert_email_to: str = os.getenv('ALERT_EMAIL_TO', 'ops@example.com')
    
    # SMS77 settings
    sms77_key: str = os.getenv('SMS77IO_RAPIDAPI_KEY', '')
    sms77_host: str = os.getenv('SMS77IO_HOST', 'sms77io.p.rapidapi.com')
    alert_sms_to: str = os.getenv('ALERT_SMS_TO', '')
    
    # App settings
    secret_key: str = os.getenv('SECRET_KEY', 'change_this_in_production')
    debug: bool = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # Model settings
    model_path: str = os.getenv('MODEL_PATH', 'ml/artifacts/model.pkl')
    feature_names_path: str = os.getenv('FEATURE_NAMES_PATH', 'ml/artifacts/feature_names.pkl')
    
    class Config:
        env_file = ".env"

# Global settings instance
settings = Settings()