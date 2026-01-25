from pydantic_settings import BaseSettings
from pydantic import ConfigDict, Field
from typing import Optional

class Settings(BaseSettings):
    database_url: str
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # Weekly Email Report Configuration (Gmail API)
    weekly_report_sender_email: Optional[str] = None
    gmail_client_id: Optional[str] = Field(default=None, alias="GMAIL_CLIENT_ID")
    gmail_client_secret: Optional[str] = Field(default=None, alias="GMAIL_CLIENT_SECRET")
    gmail_refresh_token: Optional[str] = Field(default=None, alias="GMAIL_REFRESH_TOKEN")
    gmail_sender_email: Optional[str] = Field(default=None, alias="GMAIL_SENDER_EMAIL")
    
    # Transaction Sync Configuration
    global_transaction_api_key: str = Field(..., alias="GLOBAL_TRANSACTION_API_KEY")
    
    # Branding Configuration
    company_name: str = "SpennX"
    company_logo_url: Optional[str] = None  # Set in .env if you have a logo URL
    
    model_config = ConfigDict(env_file=".env", extra="ignore", populate_by_name=True)

settings = Settings()
