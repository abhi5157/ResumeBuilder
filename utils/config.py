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
    # Default to gpt-4o-mini to match preferred default (and your Streamlit env snippet)
    ai_model: str = "gpt-4o-mini"
    
    # Application
    log_level: str = "INFO"
    # Default to False to match typical opt-in behavior; allow env/st.secrets override
    redact_pii: bool = False
    
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

        import os
        try:
            import streamlit as _st
            _secrets = _st.secrets
        except Exception:
            _secrets = {}

        # Track source for each config
        config_sources = {}

        # AI_MODEL
        env_ai_model = os.getenv("AI_MODEL") or os.getenv("ai_model")
        if env_ai_model:
            self.ai_model = str(env_ai_model)
            config_sources['AI_MODEL'] = f"env:AI_MODEL"
        elif "AI_MODEL" in _secrets or "ai_model" in _secrets:
            self.ai_model = str(_secrets["AI_MODEL"] if "AI_MODEL" in _secrets else _secrets["ai_model"])
            config_sources['AI_MODEL'] = f"st.secrets:AI_MODEL"
        else:
            config_sources['AI_MODEL'] = ".env or default"

        # LOG_LEVEL
        env_log_level = os.getenv("LOG_LEVEL") or os.getenv("log_level")
        if env_log_level:
            self.log_level = str(env_log_level)
            config_sources['LOG_LEVEL'] = f"env:LOG_LEVEL"
        elif "LOG_LEVEL" in _secrets or "log_level" in _secrets:
            self.log_level = str(_secrets["LOG_LEVEL"] if "LOG_LEVEL" in _secrets else _secrets["log_level"])
            config_sources['LOG_LEVEL'] = f"st.secrets:LOG_LEVEL"
        else:
            config_sources['LOG_LEVEL'] = ".env or default"

        # REDACT_PII
        env_redact = os.getenv("REDACT_PII")
        if env_redact is not None:
            try:
                self.redact_pii = str(env_redact).lower() == "true"
            except Exception:
                self.redact_pii = False
            config_sources['REDACT_PII'] = f"env:REDACT_PII"
        elif "REDACT_PII" in _secrets or "redact_pii" in _secrets:
            try:
                self.redact_pii = str(_secrets["REDACT_PII"] if "REDACT_PII" in _secrets else _secrets["redact_pii"]).lower() == "true"
            except Exception:
                self.redact_pii = False
            config_sources['REDACT_PII'] = f"st.secrets:REDACT_PII"
        else:
            config_sources['REDACT_PII'] = ".env or default"

        # OPENAI_API_KEY
        env_openai_key = os.getenv("OPENAI_API_KEY") or os.getenv("openai_api_key")
        if env_openai_key:
            self.openai_api_key = str(env_openai_key)
            config_sources['OPENAI_API_KEY'] = f"env:OPENAI_API_KEY"
        elif "OPENAI_API_KEY" in _secrets or "openai_api_key" in _secrets:
            self.openai_api_key = str(_secrets["OPENAI_API_KEY"] if "OPENAI_API_KEY" in _secrets else _secrets["openai_api_key"])
            config_sources['OPENAI_API_KEY'] = f"st.secrets:OPENAI_API_KEY"
        else:
            config_sources['OPENAI_API_KEY'] = ".env or default"

        # Debug: Show loaded configuration for startup logs (Streamlit captures stdout/stderr)
        print(f"\n[Config] Loaded settings (env/st.secrets aware):")
        print(f"  - AI_PROVIDER: {self.ai_provider}")
        print(f"  - AI_MODEL: {self.ai_model}   [source: {config_sources['AI_MODEL']}]")
        print(f"  - LOG_LEVEL: {self.log_level} [source: {config_sources['LOG_LEVEL']}]")
        print(f"  - REDACT_PII: {self.redact_pii} [source: {config_sources['REDACT_PII']}]")
        print(f"  - OPENAI_API_KEY: {'***' + self.openai_api_key[-8:] if self.openai_api_key else 'NOT SET'} [source: {config_sources['OPENAI_API_KEY']}]\n")

        # Validate OpenAI configuration
        if self.ai_provider == "openai" and not self.openai_api_key:
            print("⚠️  WARNING: OpenAI provider selected but no API key found. Falling back to mock provider.")
            self.ai_provider = "mock"
        elif self.ai_provider == "openai" and self.openai_api_key:
            print(f"✓ OpenAI configuration validated")


# Global settings instance
settings = Settings()
