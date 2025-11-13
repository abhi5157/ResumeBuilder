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
        # Allow explicit overrides from OS environment or Streamlit secrets
        # This helps on Streamlit Community Cloud where secrets are available via `st.secrets`.
        import os
        try:
            import streamlit as _st
            _secrets = _st.secrets
        except Exception:
            _secrets = {}

        # Prefer explicit environment variables first (AI_MODEL, LOG_LEVEL, REDACT_PII)
        env_ai_model = os.getenv("AI_MODEL") or os.getenv("ai_model")
        env_log_level = os.getenv("LOG_LEVEL") or os.getenv("log_level")
        env_redact = os.getenv("REDACT_PII")
        env_openai_key = os.getenv("OPENAI_API_KEY") or os.getenv("openai_api_key")

        # Fall back to Streamlit secrets if env vars are not set
        if not env_ai_model:
            env_ai_model = _secrets.get("AI_MODEL") or _secrets.get("ai_model")
        if not env_log_level:
            env_log_level = _secrets.get("LOG_LEVEL") or _secrets.get("log_level")
        if env_redact is None:
            env_redact = _secrets.get("REDACT_PII") or _secrets.get("redact_pii")
        if not env_openai_key:
            env_openai_key = _secrets.get("OPENAI_API_KEY") or _secrets.get("openai_api_key")

        # Apply overrides where present
        if env_ai_model:
            self.ai_model = str(env_ai_model)
        if env_log_level:
            self.log_level = str(env_log_level)
        if env_redact is not None:
            # Allow boolean-like strings
            try:
                self.redact_pii = str(env_redact).lower() == "true"
            except Exception:
                self.redact_pii = False
        if env_openai_key:
            self.openai_api_key = str(env_openai_key)

        # Debug: Show loaded configuration for startup logs (Streamlit captures stdout/stderr)
        print(f"\n[Config] Loaded settings (env/st.secrets aware):")
        print(f"  - AI_PROVIDER: {self.ai_provider}")
        print(f"  - AI_MODEL: {self.ai_model}")
        print(f"  - LOG_LEVEL: {self.log_level}")
        print(f"  - REDACT_PII: {self.redact_pii}")
        print(f"  - OPENAI_API_KEY: {'***' + self.openai_api_key[-8:] if self.openai_api_key else 'NOT SET'}")

        # Validate OpenAI configuration
        if self.ai_provider == "openai" and not self.openai_api_key:
            print("⚠️  WARNING: OpenAI provider selected but no API key found. Falling back to mock provider.")
            self.ai_provider = "mock"
        elif self.ai_provider == "openai" and self.openai_api_key:
            print(f"✓ OpenAI configuration validated")


# Global settings instance
settings = Settings()
