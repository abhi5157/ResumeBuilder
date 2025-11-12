"""
Configuration management for the Resume Builder application.
"""

import os
from pathlib import Path
from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# Load .env file explicitly
load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # AI Service
    openai_api_key: str = ""
    ai_provider: Literal["openai", "mock"] = "mock"
    ai_model: str = "gpt-4"
    
    # Application
    log_level: str = "INFO"
    redact_pii: bool = True
    
    # Backend Server
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    
    # Directories
    output_dir: Path = Path("output")
    template_dir: Path = Path("templates")
    data_dir: Path = Path("data")
    
    # Database (future use)
    database_url: str = ""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create directories if they don't exist
        self.output_dir.mkdir(exist_ok=True)
        self.template_dir.mkdir(exist_ok=True, parents=True)
        self.data_dir.mkdir(exist_ok=True)
        
        # Debug: Show loaded configuration
        print(f"\n[Config] Loaded settings from .env:")
        print(f"  - AI_PROVIDER: {self.ai_provider}")
        print(f"  - AI_MODEL: {self.ai_model}")
        print(f"  - OPENAI_API_KEY: {'***' + self.openai_api_key[-8:] if self.openai_api_key else 'NOT SET'}")
        
        # Validate OpenAI configuration
        if self.ai_provider == "openai" and not self.openai_api_key:
            print("⚠️  WARNING: OpenAI provider selected but no API key found. Falling back to mock provider.")
            self.ai_provider = "mock"
        elif self.ai_provider == "openai" and self.openai_api_key:
            print(f"✓ OpenAI configuration validated")


# Global settings instance
settings = Settings()
