"""
Logging utilities with PII redaction support.
"""

import logging
import re
from typing import Any


class PIIRedactingFormatter(logging.Formatter):
    """Custom formatter that redacts PII from log messages."""
    
    # Patterns for PII detection
    EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    PHONE_PATTERN = re.compile(r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b')
    NAME_PATTERN = re.compile(r'(full_name|name)[\"\']?\s*[:=]\s*["\']([^"\']+)["\']')
    
    def format(self, record: logging.LogRecord) -> str:
        """Format the log record with PII redaction."""
        message = super().format(record)
        
        # Redact email addresses
        message = self.EMAIL_PATTERN.sub('[EMAIL_REDACTED]', message)
        
        # Redact phone numbers
        message = self.PHONE_PATTERN.sub('[PHONE_REDACTED]', message)
        
        # Redact names in key-value pairs
        message = self.NAME_PATTERN.sub(r'\1: "[NAME_REDACTED]"', message)
        
        return message


def get_logger(name: str, redact_pii: bool = True) -> logging.Logger:
    """
    Get a configured logger instance.
    
    Args:
        name: Logger name (typically __name__)
        redact_pii: Whether to redact PII from logs
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        
        if redact_pii:
            formatter = PIIRedactingFormatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        else:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    
    return logger
