"""
Core data models for the Resume Builder application.
Uses Pydantic v2 for validation.
"""

from datetime import date
from typing import List, Optional, Union
from pydantic import BaseModel, Field, EmailStr, field_validator


class Contact(BaseModel):
    """Contact information for the resume."""
    
    model_config = {"from_attributes": True, "validate_assignment": True}
    
    full_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone: str = Field(..., pattern=r'^[\+]?[\d\s\(\)\-\.]{10,14}$')
    city: str = Field(..., max_length=100, description="City or base location")
    state: str = Field(..., max_length=50, description="State abbreviation")
    linkedin: Optional[str] = Field(default=None)
    portfolio: Optional[str] = Field(default=None)
    security_clearance: str = Field(
        default="None",
        pattern=r'^(None|Public Trust|Secret|TS|TS/SCI)$'
    )
    branch: Optional[str] = Field(
        default=None,
        description="Military branch (Army, Navy, Marines, Air Force, Space Force, Coast Guard)"
    )
    
    @field_validator('linkedin', 'portfolio')
    @classmethod
    def validate_urls(cls, v: Optional[str]) -> Optional[str]:
        """Validate URLs - accept None or empty string, or valid URL."""
        if not v or v.strip() == '':
            return None
        # Basic URL validation
        if not v.startswith(('http://', 'https://')):
            v = 'https://' + v
        if 'linkedin' in v and 'linkedin.com' not in v:
            raise ValueError("LinkedIn URL must contain 'linkedin.com'")
        return v
    
    @field_validator('phone')
    @classmethod
    def format_phone(cls, v: str) -> str:
        """
        Normalize phone number format.
        Accepts various US phone number formats, extracts digits, validates exactly 10 digits, and formats consistently.
        Only supports US phone numbers (10 digits) with optional +1 or 1 country code prefix.
        """
        import re
        
        if not v or not v.strip():
            raise ValueError("Phone number is required")
        
        # Extract digits only
        digits = re.sub(r'\D', '', v.strip())
        
        # Check if it's empty after removing non-digits
        if not digits:
            raise ValueError("Phone number must contain at least one digit")
        
        # Validate that all characters are digits
        if not digits.isdigit():
            raise ValueError("Phone number can only contain digits")
        
        # Check length: must be 10 digits, or 11 digits starting with 1 (US country code)
        if len(digits) == 10:
            pass  # Valid 10-digit US number, proceed to formatting
        elif len(digits) == 11 and digits.startswith('1'):
            digits = digits[1:]  # Remove leading 1 for US country code
        else:
            raise ValueError(f'Phone number must be exactly 10 digits (US format). You provided {len(digits)} digits')
        
        # At this point, digits should be exactly 10 digits
        if len(digits) != 10:
            raise ValueError(f'Unexpected error: phone number should be 10 digits after processing, got {len(digits)}')
        
        # Format as (XXX) XXX-XXXX
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"


class MOS(BaseModel):
    """Military Occupational Specialty."""
    
    model_config = {"from_attributes": True, "validate_assignment": True}
    
    code: str = Field(..., description="MOS code (e.g., 11B)")
    branch: str = Field(
        ...,
        pattern=r'^(Army|Navy|Marines|Air Force|Space Force|Coast Guard)$'
    )
    branch_code: Optional[str] = Field(None, max_length=5, description="Branch code (V, N, etc.)")
    personnel_category: Optional[str] = Field(None, max_length=5, description="O, E, W, etc.")
    title: Optional[str] = None
    title_military: Optional[str] = Field(None, description="Official military title")
    civilian_skills: List[str] = Field(default_factory=list)
    soc_code: Optional[str] = Field(None, description="Standard Occupational Classification code")
    soc_code_title: Optional[str] = Field(None, description="SOC code title")
    soc_title: Optional[str] = Field(None, description="SOC title")
    onet_code: Optional[str] = Field(None, description="O*NET code")
    onet_occupation: Optional[str] = Field(None, description="O*NET occupation")
    csv_lookup_key: Optional[str] = Field(None, description="CSV lookup key (branch|code)")
    years_of_service: Optional[float] = Field(None, ge=0, le=50)
    years_served: Optional[str] = Field(None, max_length=50, description="Years served (text)")
    last_duty_title: Optional[str] = Field(None, max_length=200)
    deployments: Optional[str] = Field(None, max_length=500, description="Deployments/locations")
    
    @field_validator('code')
    @classmethod
    def uppercase_code(cls, v: str) -> str:
        """Normalize MOS code to uppercase."""
        return v.upper()


class WorkHistory(BaseModel):
    """Work history entry with STAR achievements."""
    
    model_config = {"from_attributes": True, "validate_assignment": True}
    
    title: str = Field(..., min_length=2, max_length=200, description="Job title")
    organization: str = Field(..., min_length=2, max_length=200, description="Organization/Employer")
    location: Optional[str] = Field(None, max_length=100, description="City, State")
    start_date: date
    end_date: Optional[date] = None
    current: bool = False
    bullets: List[str] = Field(
        default_factory=list,
        max_length=10,
        description="Achievement bullets (AI can rewrite to STAR)"
    )
    mos_codes: List[str] = Field(default_factory=list, description="Associated MOS codes")
    scope_metrics: Optional[str] = Field(
        None,
        max_length=1000,
        description="Team size, budget, assets managed"
    )
    ai_generated_bullets: List[str] = Field(default_factory=list)
    
    # Legacy fields for backward compatibility
    @property
    def employer(self) -> str:
        """Alias for organization."""
        return self.organization
    
    @property
    def job_title(self) -> str:
        """Alias for title."""
        return self.title
    
    @property
    def achievements(self) -> List[str]:
        """Alias for bullets."""
        return self.bullets
    
    @field_validator('end_date')
    @classmethod
    def validate_end_date(cls, v: Optional[date], info) -> Optional[date]:
        """Ensure end_date is after start_date if provided."""
        if v and 'start_date' in info.data:
            start = info.data['start_date']
            if v < start:
                raise ValueError("end_date must be after start_date")
        return v
    
    @property
    def date_range(self) -> str:
        """Format date range for display."""
        start = self.start_date.strftime("%B %Y")
        end = "Present" if self.current else (
            self.end_date.strftime("%B %Y") if self.end_date else ""
        )
        return f"{start} - {end}"


class Education(BaseModel):
    """Education entry."""
    
    model_config = {"from_attributes": True, "validate_assignment": True}
    
    institution: str = Field(..., min_length=2, max_length=200)
    degree: str = Field(..., min_length=2, max_length=200, description="Degree / Program")
    field_of_study: Optional[str] = Field(None, max_length=200)
    overview: Optional[str] = Field(
        None,
        max_length=400,
        description="Optional concise program overview or focus area (1 line, ATS-friendly)"
    )
    courses: List[str] = Field(
        default_factory=list,
        description="Optional list of notable courses (3-6 concise items)"
    )
    courses_overview: Optional[str] = Field(
        None,
        max_length=300,
        description="Optional one-line summary grouping the courses (appears before list)"
    )
    graduation_date: Optional[date] = Field(None, description="Graduation date")
    graduation_year: Optional[int] = Field(None, ge=1950, le=2050)
    in_progress: bool = False
    gpa: Optional[float] = Field(None, ge=0.0, le=4.0)
    honors: List[str] = Field(default_factory=list)
    
    @property
    def degree_display(self) -> str:
        """Format degree for display."""
        parts = [self.degree]
        if self.field_of_study:
            parts.append(f"in {self.field_of_study}")
        if self.in_progress:
            parts.append("(In progress)")
        elif self.graduation_year:
            parts.append(f"({self.graduation_year})")
        return " ".join(parts)


class Certification(BaseModel):
    """Professional certification."""
    
    model_config = {"from_attributes": True, "validate_assignment": True}
    
    name: str = Field(..., min_length=2, max_length=200)
    issuer: str = Field(..., min_length=2, max_length=200)
    issue_date: Optional[date] = Field(None, description="Issue date")
    expiration_date: Optional[date] = Field(None, description="Expiration date")
    year: Optional[int] = Field(None, ge=1950, le=2050)
    credential_id: Optional[str] = Field(None, max_length=100)
    dod_mapping: Optional[str] = Field(
        None,
        max_length=100,
        description="DoD 8140/8570 role mapping"
    )


class VolunteerExperience(BaseModel):
    """Volunteer experience entry."""
    
    organization: str = Field(..., min_length=2, max_length=200, description="Organization name")
    role: str = Field(..., min_length=2, max_length=200, description="Volunteer role")
    description: str = Field(..., min_length=10, max_length=500, description="Description of volunteer work")
    date_range: str = Field(..., min_length=4, max_length=50, description="Date range (e.g., '2020 - Present')")


class AdditionalInfo(BaseModel):
    """Additional resume information."""
    
    awards: List[str] = Field(default_factory=list, description="Awards & honors")
    volunteer: Union[List[str], List[VolunteerExperience]] = Field(
        default_factory=list, 
        description="Volunteer/service (can be simple strings or detailed entries)"
    )
    veteran_experience: List[str] = Field(
        default_factory=list,
        description="Veteran-specific experiences (transition assistance, mentorship, organizations)"
    )
    languages: List[str] = Field(default_factory=list)
    clearance_note: Optional[str] = Field(None, max_length=200)
    references_available: bool = True


class DocumentPreferences(BaseModel):
    """Document generation preferences."""
    
    model_config = {"from_attributes": True, "validate_assignment": True}
    
    template: str = Field(
        default="classic",
        description="Template name (classic, modern, etc.)"
    )


class ResumeProfile(BaseModel):
    """Complete resume profile."""
    
    model_config = {
        "arbitrary_types_allowed": True, 
        "validate_assignment": True,
        "from_attributes": True,
        "extra": "forbid"
    }
    
    contact: Contact
    target_roles: List[str] = Field(
        default_factory=list,
        min_length=1,
        description="Target job title(s)"
    )
    summary: Optional[str] = Field(None, max_length=1000, description="AI-generated, editable")
    
    # Service details
    mos: Optional[MOS] = None
    
    # Skills & Keywords
    core_skills: List[str] = Field(default_factory=list, description="Core skills (chips/tags)")
    tools_technologies: List[str] = Field(default_factory=list, description="Tools/technologies")
    target_keywords: List[str] = Field(default_factory=list, description="Target keywords")
    mos_translated_skills: List[str] = Field(
        default_factory=list,
        description="Auto-suggested from MOS"
    )
    
    # Work & Education
    work_history: List[WorkHistory] = Field(default_factory=list)
    education: List[Education] = Field(default_factory=list)
    certifications: List[Certification] = Field(default_factory=list)
    
    # Additional
    additional_info: Optional[AdditionalInfo] = None
    
    # Preferences
    preferences: DocumentPreferences = Field(default_factory=DocumentPreferences)
    
    @field_validator('summary')
    @classmethod
    def validate_summary_length(cls, v: Optional[str]) -> Optional[str]:
        """Ensure summary is 2-3 sentences."""
        if v:
            sentences = v.count('.') + v.count('!') + v.count('?')
            if sentences > 5:
                raise ValueError("Summary should be 2-3 concise sentences")
        return v
    
    def model_dump_json_safe(self) -> dict:
        """Return a JSON-safe dict with dates as strings."""
        return self.model_dump(mode='json')


class AIGenerationRequest(BaseModel):
    """Request for AI-generated content."""
    
    profile: ResumeProfile
    content_type: str = Field(..., pattern=r'^(summary|bullets)$')
    context: Optional[str] = None


class AIGenerationResponse(BaseModel):
    """Response from AI generation."""
    
    content: str | List[str]
    content_type: str
    metadata: Optional[dict] = None


class Skill(BaseModel):
    """Skill entry for structured skills tracking."""
    
    name: str = Field(..., min_length=1, max_length=100)
    category: Optional[str] = Field(None, max_length=50, description="e.g., Leadership, Technical")
    proficiency: Optional[str] = Field(None, pattern=r'^(Beginner|Intermediate|Advanced|Expert)$')


# ========== Enhanced Models for v0.2 Schema ==========

class ServiceDates(BaseModel):
    """Service start and end dates."""
    start: str = Field(..., description="Start date in YYYY-MM format")
    end: str = Field(..., description="End date in YYYY-MM format or 'Present'")


class ServiceDetails(BaseModel):
    """Enhanced military service details for v0.2 schema."""
    
    branch: str = Field(..., pattern=r'^(Army|Navy|Marines|Air Force|Space Force|Coast Guard)$')
    mos_code: str = Field(..., min_length=2, max_length=10)
    mos_title: str = Field(..., min_length=2, max_length=200)
    paygrade_at_separation: Optional[str] = Field(None, max_length=50, description="e.g., E-6 (TSgt)")
    years_of_service: int = Field(..., ge=0, le=50)
    service_dates: ServiceDates
    clearance: str = Field(
        default="None",
        description="Security clearance with status, e.g., 'TS/SCI (Active)'"
    )
    deployments: List[str] = Field(default_factory=list, description="Deployment details")
    awards: List[str] = Field(default_factory=list, description="Military awards and decorations")


class TargetProfile(BaseModel):
    """Target job profile for v0.2 schema."""
    
    titles: List[str] = Field(..., min_length=1, description="Target job titles")
    industries: List[str] = Field(default_factory=list, description="Target industries")
    locations: List[str] = Field(default_factory=list, description="Target locations")


class STARAchievement(BaseModel):
    """STAR-formatted achievement entry."""
    
    s: str = Field(..., description="Situation - The context or challenge")
    t: str = Field(..., description="Task - The objective or goal")
    a: str = Field(..., description="Action - What you did")
    r: str = Field(..., description="Result - The measurable outcome")
    bullet: str = Field(..., description="Final polished bullet point")


class ExperienceEntry(BaseModel):
    """Experience entry with STAR achievements for v0.2 schema."""
    
    role_military: str = Field(..., min_length=2, max_length=200, description="Military role title")
    unit: Optional[str] = Field(None, max_length=200, description="Military unit")
    dates: ServiceDates
    achievements_star: List[STARAchievement] = Field(
        default_factory=list,
        description="STAR-formatted achievements"
    )


class ResumePreferences(BaseModel):
    """Resume generation preferences for v0.2 schema."""
    
    template: str = Field(default="modern", pattern=r'^(classic|modern|federal)$')
    tone: str = Field(default="impactful", pattern=r'^(professional|impactful|technical)$')
    include_clearance: bool = Field(default=True)
    bullet_density: int = Field(default=4, ge=2, le=6)


class ContactV2(BaseModel):
    """Contact information for v0.2 schema."""
    
    full_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone: str = Field(..., pattern=r'^\+?1?\(?\d{3}\)?[\s.-]?\d{4}[\s.-]?\d{4}$')
    city_state: str = Field(..., max_length=150, description="City, State format")
    linkedin: Optional[str] = Field(default=None)


class ResumeProfileV2(BaseModel):
    """Complete resume profile for v0.2 schema - Enhanced structure."""
    
    schema_version: str = Field(default="v0.2")
    profile_id: str = Field(..., description="Unique profile identifier")
    csv_lookup_key: str = Field(..., description="MOS lookup key (Branch|Code)")
    
    contact: ContactV2
    service: ServiceDetails
    target: TargetProfile
    
    skills_core: List[str] = Field(default_factory=list, description="Core competencies")
    tools_tech: List[str] = Field(default_factory=list, description="Tools and technologies")
    
    experience: List[ExperienceEntry] = Field(default_factory=list)
    education: List[Education] = Field(default_factory=list)
    certifications: List[Certification] = Field(default_factory=list)
    
    keywords: List[str] = Field(default_factory=list, description="ATS keywords")
    resume_preferences: ResumePreferences = Field(default_factory=ResumePreferences)
    
    def to_legacy_profile(self) -> 'ResumeProfile':
        """Convert v0.2 profile to legacy ResumeProfile format for compatibility."""
        # Parse city and state from city_state
        city_state_parts = self.contact.city_state.split(', ')
        city = city_state_parts[0] if len(city_state_parts) > 0 else ''
        state = city_state_parts[1] if len(city_state_parts) > 1 else ''
        
        # Create legacy Contact
        legacy_contact = Contact(
            full_name=self.contact.full_name,
            email=self.contact.email,
            phone=self.contact.phone,
            city=city,
            state=state,
            linkedin=self.contact.linkedin,
            security_clearance=self.service.clearance
        )
        
        # Create legacy MOS
        legacy_mos = MOS(
            code=self.service.mos_code,
            branch=self.service.branch,
            title=self.service.mos_title,
            years_of_service=float(self.service.years_of_service)
        )
        
        # Convert experience entries
        legacy_work_history = []
        for exp in self.experience:
            # Parse dates
            start_parts = exp.dates.start.split('-')
            start_date = date(int(start_parts[0]), int(start_parts[1]), 1)
            
            end_date = None
            is_current = exp.dates.end == 'Present'
            if not is_current:
                end_parts = exp.dates.end.split('-')
                end_date = date(int(end_parts[0]), int(end_parts[1]), 1)
            
            # Extract bullets from STAR achievements
            bullets = [star.bullet for star in exp.achievements_star]
            
            legacy_work = WorkHistory(
                title=exp.role_military,
                organization=exp.unit or "United States Military",
                location="",
                start_date=start_date,
                end_date=end_date,
                current=is_current,
                bullets=bullets
            )
            legacy_work_history.append(legacy_work)
        
        # Create legacy profile
        return ResumeProfile(
            contact=legacy_contact,
            target_roles=self.target.titles,
            mos=legacy_mos,
            core_skills=self.skills_core,
            tools_technologies=self.tools_tech,
            target_keywords=self.keywords,
            work_history=legacy_work_history,
            education=self.education,
            certifications=self.certifications,
            preferences=DocumentPreferences(
                template=self.resume_preferences.template,
                bullet_density=self.resume_preferences.bullet_density
            )
        )


# Backward compatibility alias for CLI
Experience = WorkHistory

