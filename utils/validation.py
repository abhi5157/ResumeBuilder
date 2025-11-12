"""
Real-time field validation utilities for Streamlit forms.
Uses Pydantic for validation with visual feedback.
"""

import re
from typing import Tuple, Optional, Any
from datetime import datetime, date
from pydantic import EmailStr, ValidationError, field_validator
from pydantic_core import PydanticCustomError


class FieldValidator:
    """Real-time field validators with error messages."""
    
    @staticmethod
    def validate_email(value: str) -> Tuple[bool, Optional[str]]:
        """
        Validate email address.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not value or not value.strip():
            return True, None  # Optional field
        
        try:
            # Use Pydantic's EmailStr for validation
            from pydantic import BaseModel, EmailStr
            
            class EmailModel(BaseModel):
                email: EmailStr
            
            EmailModel(email=value)
            return True, None
        except ValidationError:
            return False, "Please enter a valid email address (e.g., name@example.com)"
    
    @staticmethod
    def validate_phone(value: str) -> Tuple[bool, Optional[str]]:
        """
        Validate US phone number - requires exactly 10 digits.
        Accepts optional +1 or 1 country code prefix, automatically strips out formatting characters.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not value or not value.strip():
            return False, "Phone number is required"
        
        # Extract digits only - ignore all formatting characters
        digits = re.sub(r'\D', '', value.strip())
        
        # Check if it's empty after removing non-digits
        if not digits:
            return False, "Phone number must contain at least one digit"
        
        # Validate that all characters are digits
        if not digits.isdigit():
            return False, "Phone number can only contain digits"
        
        # Check length: must be exactly 10 digits (US format)
        if len(digits) == 10:
            return True, None  # Valid 10-digit US number
        else:
            return False, f"Phone number must be exactly 10 digits. You entered {len(digits)} digits"
    
    @staticmethod
    def validate_full_name(value: str) -> Tuple[bool, Optional[str]]:
        """
        Validate full name.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not value or not value.strip():
            return False, "Full Name is required"
        
        if len(value.strip()) < 2:
            return False, "Full Name must be at least 2 characters"
        
        if len(value.strip()) > 100:
            return False, "Full Name must not exceed 100 characters"
        
        return True, None
    
    @staticmethod
    def validate_city_state(value: str) -> Tuple[bool, Optional[str]]:
        """
        Validate city, state format.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not value or not value.strip():
            return True, None  # Optional in some contexts
        
        # More lenient validation for city, state format
        parts = [p.strip() for p in value.replace(',', ' ').split() if p.strip()]
        
        if len(parts) < 1:
            return False, "Please enter at least a city name"
        
        if len(parts[0]) < 2:
            return False, "City name must be at least 2 characters"
        
        return True, None
    
    @staticmethod
    def validate_linkedin(value: str) -> Tuple[bool, Optional[str]]:
        """
        Validate LinkedIn URL.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not value or not value.strip():
            return True, None  # Optional field
        
        # Check if it contains linkedin.com
        if 'linkedin.com' not in value.lower():
            return False, "LinkedIn URL must contain 'linkedin.com'"
        
        return True, None
    
    @staticmethod
    def validate_url(value: str) -> Tuple[bool, Optional[str]]:
        """
        Validate URL format.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not value or not value.strip():
            return True, None  # Optional field
        
        # Basic URL pattern
        url_pattern = r'^(https?://)?(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b'
        
        if not re.match(url_pattern, value):
            return False, "Please enter a valid URL"
        
        return True, None
    
    @staticmethod
    def validate_years_service(value: str) -> Tuple[bool, Optional[str]]:
        """
        Validate years of service.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not value or not value.strip():
            return False, "Years of Service is required"
        
        return True, None
    
    @staticmethod
    def validate_required_text(value: str, field_name: str = "This field", min_length: int = 1) -> Tuple[bool, Optional[str]]:
        """
        Validate required text field.
        
        Args:
            value: Field value
            field_name: Name of the field for error message
            min_length: Minimum length required
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not value or not value.strip():
            return False, f"{field_name} is required"
        
        if len(value.strip()) < min_length:
            return False, f"{field_name} must be at least {min_length} character{'s' if min_length > 1 else ''}"
        
        return True, None
    
    @staticmethod
    def validate_date(value: Any, field_name: str = "Date") -> Tuple[bool, Optional[str]]:
        """
        Validate date field.
        
        Args:
            value: Date value (can be date object, datetime, or string)
            field_name: Name of the field for error message
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if value is None:
            return True, None  # Allow None for optional dates
        
        # If it's already a date object, it's valid
        if isinstance(value, (date, datetime)):
            return True, None
        
        # Try to parse string dates
        if isinstance(value, str):
            value = value.strip().lower()
            
            # Allow "present" or "current" for end dates
            if value in ["present", "current", ""]:
                return True, None
            
            # Try common date formats
            date_formats = [
                "%Y-%m-%d",
                "%m/%d/%Y",
                "%d/%m/%Y",
                "%m/%Y",
                "%B %Y",
                "%b %Y",
            ]
            
            for fmt in date_formats:
                try:
                    datetime.strptime(value, fmt)
                    return True, None
                except ValueError:
                    continue
            
            return False, f"Please enter a valid date for {field_name}"
        
        return False, f"Invalid date format for {field_name}"
    
    @staticmethod
    def validate_date_range(start_date: Any, end_date: Any) -> Tuple[bool, Optional[str]]:
        """
        Validate that end_date is after start_date and not in the future (unless marked as "Present").
        
        Args:
            start_date: Start date
            end_date: End date
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        from datetime import date as date_type
        
        # Convert to date objects if needed
        def to_date(d):
            if d is None:
                return None
            if isinstance(d, datetime):
                return d.date()
            if isinstance(d, date_type):
                return d
            if isinstance(d, str):
                d = d.strip().lower()
                if d in ["present", "current", ""]:
                    return None
                try:
                    return datetime.strptime(d, "%Y-%m-%d").date()
                except:
                    try:
                        return datetime.strptime(d, "%m/%d/%Y").date()
                    except:
                        return None
            return None
        
        start = to_date(start_date)
        end = to_date(end_date)
        
        # If either is None or end is "Present", skip validation
        if start is None or end is None:
            return True, None
        
        # Check if end date is before start date
        if end < start:
            return False, "End date cannot be before start date"
        
        # Check if end date is in the future (beyond today)
        today = date_type.today()
        if end > today:
            return False, "End date cannot be in the future (use 'Present' for current positions)"
        
        return True, None
    
    @staticmethod
    def validate_gpa(value: Any) -> Tuple[bool, Optional[str]]:
        """
        Validate GPA value.
        
        Args:
            value: GPA value
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if value is None or value == "" or str(value).strip() == "":
            return True, None  # Optional field
        
        try:
            gpa = float(str(value).strip())
            
            if gpa < 0:
                return False, "GPA cannot be negative"
            
            if gpa > 100:
                return False, "GPA value is too high"
            
            return True, None
        except (ValueError, TypeError):
            return False, "Please enter a valid GPA (e.g., 3.5)"
    
    @staticmethod
    def validate_year(value: Any) -> Tuple[bool, Optional[str]]:
        """
        Validate year value.
        
        Args:
            value: Year value
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if value is None or value == "" or str(value).strip() == "":
            return True, None  # Optional field
        
        try:
            year = int(str(value).strip())
            
            if year < 1950:
                return False, "Year must be 1950 or later"
            
            if year > 2050:
                return False, "Year must be 2050 or earlier"
            
            return True, None
        except (ValueError, TypeError):
            return False, "Please enter a valid year (e.g., 2020)"


class ValidationState:
    """Manages validation state across the app."""
    
    def __init__(self):
        self.errors = {}
    
    def set_error(self, field_name: str, error_message: Optional[str]):
        """Set or clear error for a field."""
        if error_message:
            self.errors[field_name] = error_message
        elif field_name in self.errors:
            del self.errors[field_name]
    
    def get_error(self, field_name: str) -> Optional[str]:
        """Get error message for a field."""
        return self.errors.get(field_name)
    
    def has_errors(self) -> bool:
        """Check if there are any validation errors."""
        return len(self.errors) > 0
    
    def clear(self):
        """Clear all validation errors."""
        self.errors.clear()


# Create global validator instance
validator = FieldValidator()
