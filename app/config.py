from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    database_url: str
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # Weekly Email Report Configuration (Gmail API)
    weekly_report_sender_email: Optional[str] = None
    
    # Branding Configuration
    company_name: str = "SpennX"
    company_logo_url: Optional[str] = None  # Set in .env if you have a logo URL
    
    class Config:
        env_file = ".env"

settings = Settings()
