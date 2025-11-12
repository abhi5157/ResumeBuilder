"""
Resume generation service using python-docx for DOCX output.
Handles document generation with precise layout control.
"""

import re
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

from models import ResumeProfile
from utils.config import settings
from utils.logging_utils import get_logger
from services.resume_generator import DocxResumeGenerator

logger = get_logger(__name__)


class ResumeService:
    """Service for generating resume documents."""
    
    def __init__(self, template_dir: Optional[Path] = None, output_dir: Optional[Path] = None):
        """
        Initialize resume service.
        
        Args:
            template_dir: Directory containing resume templates (optional, not used with new generator)
            output_dir: Directory for output files
        """
        self.template_dir = template_dir or settings.template_dir
        self.output_dir = output_dir or settings.output_dir
        
        # Initialize the DOCX generator
        self.generator = DocxResumeGenerator()
        
        # Ensure directories exist
        self.output_dir.mkdir(exist_ok=True, parents=True)
    
    def generate_resume(
        self,
        profile: ResumeProfile,
        template_name: str = "classic",
        output_filename: Optional[str] = None
    ) -> Path:
        """
        Generate a resume DOCX file from profile.
        
        Args:
            profile: Resume profile data
            template_name: Name of template to use (ignored, kept for compatibility)
            output_filename: Custom output filename (optional)
        
        Returns:
            Path to generated DOCX file
        """
        # Determine output filename
        if not output_filename:
            output_filename = self._generate_filename(profile)
        
        output_path = self.output_dir / output_filename
        
        # Generate document using the new generator
        try:
            self.generator.generate(profile, output_path)
            logger.info(f"Generated resume: {output_path}")
        except Exception as e:
            logger.error(f"Resume generation failed: {e}")
            raise Exception(f"Failed to generate resume: {e}")
        
        return output_path
    
    def _normalize_whitespace(self, text: str) -> str:
        """
        Normalize whitespace in text.
        
        Args:
            text: Input text
        
        Returns:
            Text with normalized whitespace
        """
        # Replace multiple spaces with single space
        text = re.sub(r'\s+', ' ', text)
        # Strip leading/trailing whitespace
        text = text.strip()
        return text
    
    def _format_location(self, city: Optional[str], state: Optional[str]) -> str:
        """Format city and state for display."""
        if city and state:
            return f"{city}, {state}"
        elif city:
            return city
        elif state:
            return state
        return ''
    
    def _generate_filename(self, profile: ResumeProfile) -> str:
        """
        Generate deterministic filename from profile.
        
        Args:
            profile: Resume profile
        
        Returns:
            Filename for the resume
        """
        # Sanitize name for filename
        name = profile.contact.full_name.lower()
        name = re.sub(r'[^a-z0-9]+', '_', name)
        name = name.strip('_')
        
        # Add timestamp for uniqueness
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        return f"resume_{name}_{timestamp}.docx"
    
    def get_available_templates(self) -> list[str]:
        """Get list of available template names (deprecated with new generator)."""
        # This method is kept for backward compatibility but is no longer used
        return ["default"]


# Global service instance
_resume_service: Optional[ResumeService] = None


def get_resume_service() -> ResumeService:
    """Get or create the global resume service instance."""
    global _resume_service
    if _resume_service is None:
        _resume_service = ResumeService()
    return _resume_service
