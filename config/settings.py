"""
Configuration management
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration"""
    
    # Project paths
    PROJECT_ROOT = Path(__file__).parent.parent
    DATA_DIR = PROJECT_ROOT / 'data'
    
    # API Configuration
    SKYSCANNER_API_KEY: Optional[str] = os.getenv('SKYSCANNER_API_KEY')
    RAPIDAPI_KEY: Optional[str] = os.getenv('RAPIDAPI_KEY')
    
    # Rate limiting
    API_CALLS_PER_MINUTE: int = int(os.getenv('API_CALLS_PER_MINUTE', '10'))
    API_CALLS_PER_HOUR: int = int(os.getenv('API_CALLS_PER_HOUR', '100'))
    
    # Database
    DATABASE_PATH: Path = PROJECT_ROOT / os.getenv('DATABASE_PATH', 'data/flights.db')
    
    # Tracking settings
    CHECK_INTERVAL_HOURS: int = int(os.getenv('CHECK_INTERVAL_HOURS', '6'))
    PRICE_DROP_ALERT_PERCENTAGE: float = float(os.getenv('PRICE_DROP_ALERT_PERCENTAGE', '10'))
    
    # Notifications
    ENABLE_EMAIL_NOTIFICATIONS: bool = os.getenv('ENABLE_EMAIL_NOTIFICATIONS', 'false').lower() == 'true'
    EMAIL_FROM: Optional[str] = os.getenv('EMAIL_FROM')
    EMAIL_TO: Optional[str] = os.getenv('EMAIL_TO')
    SMTP_SERVER: Optional[str] = os.getenv('SMTP_SERVER')
    SMTP_PORT: int = int(os.getenv('SMTP_PORT', '587'))
    SMTP_USERNAME: Optional[str] = os.getenv('SMTP_USERNAME')
    SMTP_PASSWORD: Optional[str] = os.getenv('SMTP_PASSWORD')
    
    @classmethod
    def ensure_directories(cls):
        """Create necessary directories if they don't exist"""
        cls.DATA_DIR.mkdir(parents=True, exist_ok=True)
        cls.DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)


# Create directories on import
Config.ensure_directories()
