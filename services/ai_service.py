"""
AI service for generating resume content.
Provides abstract interface with multiple provider implementations.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
import random

from models import ResumeProfile, WorkHistory

try:
    from utils.config import settings
    from utils.logging_utils import get_logger
    logger = get_logger(__name__)
except ImportError:
    settings = None
    logger = None
    
    class MockSettings:
        ai_provider = "mock"
        ai_model = "mock"
    
    if not settings:
        settings = MockSettings()


class AIProvider(ABC):
    """Abstract base class for AI providers."""
    
    @abstractmethod
    def generate_summary(self, profile: ResumeProfile) -> str:
        """
        Generate a professional summary for the resume.
        
        Args:
            profile: Complete resume profile
        
        Returns:
            2-3 sentence professional summary
        """
        pass
    
    @abstractmethod
    def generate_bullets(
        self,
        experience: 'WorkHistory',
        profile: ResumeProfile,
        count: int = 4
    ) -> List[str]:
        """
        Generate STAR-style bullet points for an experience entry.
        
        Args:
            experience: The experience entry
            profile: Complete resume profile for context
            count: Number of bullets to generate
        
        Returns:
            List of STAR-formatted bullet points
        """
        pass


class MockAIProvider(AIProvider):
    """Mock AI provider for testing and development."""
    
    SUMMARY_TEMPLATES = [
        "Results-driven {role} with {years}+ years of military experience transitioning to civilian sector. Proven track record in {skill1}, {skill2}, and {skill3}. Seeking to leverage leadership and technical expertise in a dynamic organization.",
        "Accomplished military professional with expertise in {skill1} and {skill2}, seeking {role} position. {years}+ years of experience leading teams and executing complex operations. Strong problem-solver with excellent communication skills.",
        "Highly motivated {role} candidate with {years} years of service in {branch}. Expert in {skill1}, {skill2}, and {skill3}. Committed to excellence and continuous improvement in fast-paced environments."
    ]
    
    BULLET_TEMPLATES = [
        "Led team of {team_size} personnel in {activity}, resulting in {metric}% improvement in operational efficiency",
        "Managed {resource} worth ${value}K, ensuring 100% accountability and zero loss incidents",
        "Coordinated {activity} across {scope}, supporting {beneficiary} and exceeding performance standards",
        "Implemented {initiative} that reduced {problem} by {metric}%, saving {value} hours annually",
        "Trained and mentored {team_size}+ personnel in {skill}, achieving {metric}% proficiency rate",
        "Executed {activity} under high-pressure conditions, maintaining {metric}% accuracy rate",
        "Developed and maintained {system} supporting {scope}, ensuring {metric}% uptime",
        "Analyzed {data} to identify trends and optimize {process}, improving {metric} by {percent}%"
    ]
    
    def __init__(self):
        """Initialize the mock AI provider."""
        self.call_count = 0
    
    def generate_summary(self, profile: ResumeProfile) -> str:
        """Generate a mock professional summary."""
        self.call_count += 1
        
        # Extract data from profile
        role = profile.target_role
        years = self._calculate_years_of_service(profile)
        skills = self._extract_top_skills(profile, 3)
        branch = profile.mos_codes[0].branch if profile.mos_codes else "military"
        
        # Select random template
        template = random.choice(self.SUMMARY_TEMPLATES)
        
        # Fill in template
        summary = template.format(
            role=role,
            years=years,
            skill1=skills[0] if len(skills) > 0 else "leadership",
            skill2=skills[1] if len(skills) > 1 else "operations management",
            skill3=skills[2] if len(skills) > 2 else "team coordination",
            branch=branch
        )
        
        logger.info(f"Generated mock summary for {role}")
        return summary
    
    def generate_bullets(
        self,
        experience: 'WorkHistory',
        profile: ResumeProfile,
        count: int = 4
    ) -> List[str]:
        """Generate mock STAR-style bullets."""
        self.call_count += 1
        
        bullets = []
        templates = random.sample(self.BULLET_TEMPLATES, min(count, len(self.BULLET_TEMPLATES)))
        
        for template in templates:
            bullet = template.format(
                team_size=random.choice([5, 8, 10, 15, 20]),
                activity=self._get_activity(experience),
                metric=random.choice([15, 20, 25, 30, 35, 40, 95, 98, 100]),
                resource="equipment and supplies",
                value=random.choice([50, 100, 250, 500, 1000]),
                scope="multiple departments",
                beneficiary=f"{random.choice([50, 100, 200, 500])}+ personnel",
                initiative="process improvement initiative",
                problem="processing time",
                skill=self._extract_top_skills(profile, 1)[0] if profile.skills else "operations",
                system="tracking system",
                data="performance metrics",
                process="workflow",
                percent=random.choice([15, 20, 25, 30])
            )
            bullets.append(bullet)
        
        logger.info(f"Generated {len(bullets)} mock bullets for {experience.title}")
        return bullets
    
    def _calculate_years_of_service(self, profile: ResumeProfile) -> int:
        """Calculate total years of service from experience."""
        if not profile.experience:
            return 4
        
        total_days = 0
        for exp in profile.experience:
            end = exp.end_date if exp.end_date else exp.start_date
            delta = end - exp.start_date
            total_days += delta.days
        
        return max(1, total_days // 365)
    
    def _extract_top_skills(self, profile: ResumeProfile, count: int) -> List[str]:
        """Extract top skills from profile."""
        # Combine skills from various sources
        all_skills = []
        
        # From skills list
        all_skills.extend([s.name for s in profile.skills[:count]])
        
        # From MOS codes
        for mos in profile.mos_codes:
            all_skills.extend(mos.civilian_skills[:2])
        
        # Default skills if none found
        if not all_skills:
            all_skills = ["leadership", "team coordination", "operations management"]
        
        return all_skills[:count]
    
    def _get_activity(self, experience: 'WorkHistory') -> str:
        """Extract activity description from experience."""
        title_lower = experience.job_title.lower() if hasattr(experience, 'job_title') else experience.title.lower()
        
        if "engineer" in title_lower:
            return "construction and maintenance operations"
        elif "medic" in title_lower or "medical" in title_lower:
            return "emergency medical response"
        elif "intelligence" in title_lower:
            return "intelligence gathering and analysis"
        elif "supply" in title_lower or "logistics" in title_lower:
            return "supply chain operations"
        else:
            return "tactical operations"


class OpenAIProvider(AIProvider):
    """OpenAI GPT-based AI provider."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        """
        Initialize OpenAI provider.
        
        Args:
            api_key: OpenAI API key
            model: Model to use (gpt-4, gpt-3.5-turbo, etc.)
        """
        self.api_key = api_key or settings.openai_api_key
        self.model = model
        
        if not self.api_key:
            raise ValueError("OpenAI API key not provided")
        
        try:
            import openai
            # Remove quotes if they exist in the API key
            clean_api_key = self.api_key.strip("'").strip('"')
            self.client = openai.OpenAI(api_key=clean_api_key)
        except ImportError:
            raise ImportError("openai package not installed. Run: pip install openai")
    
    def generate_summary(self, profile: ResumeProfile) -> str:
        """Generate professional summary using OpenAI."""
        prompt = self._build_summary_prompt(profile)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional resume writer specializing in military-to-civilian transitions. Write concise, impactful professional summaries which would be related to all detail provided as input"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.8  # Increased for more variety
            )
            
            summary = response.choices[0].message.content.strip()
            if logger:
                logger.info(f"Generated AI summary using OpenAI")
            return summary
        
        except Exception as e:
            if logger:
                logger.error(f"Error generating summary: {e}")
            raise
    
    def generate_bullets(
        self,
        experience: 'WorkHistory',
        profile: ResumeProfile,
        count: int = 4
    ) -> List[str]:
        """Generate STAR-style bullets using OpenAI."""
        # Use the new method with empty context for backward compatibility
        return self.generate_bullets_with_context(experience, profile, {}, count)
    
    def generate_bullets_with_context(
        self,
        experience: 'WorkHistory',
        profile: ResumeProfile,
        extra_context: dict,
        count: int = 4
    ) -> List[str]:
        """Generate STAR-style bullets using OpenAI with additional context."""
        prompt = self._build_bullets_prompt_with_context(experience, profile, extra_context, count)
        
        try:
            print(f"[OpenAI] Generating bullets with prompt length: {len(prompt)} chars")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional resume writer. Create compelling STAR-method bullet points (Situation, Task, Action, Result) that highlight achievements with specific metrics. Keep each bullet concise (under 24 words)."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=600,
                temperature=0.8
            )
            
            content = response.choices[0].message.content.strip()
            print(f"[OpenAI] Raw response: {content[:200]}...")
            bullets = [line.strip('- ').strip() for line in content.split('\n') if line.strip() and not line.strip().isdigit()]
            
            print(f"[OpenAI] Generated {len(bullets)} bullets")
            if logger:
                logger.info(f"Generated {len(bullets)} AI bullets using OpenAI")
            return bullets[:count]
        
        except Exception as e:
            print(f"[OpenAI] Error generating bullets: {e}")
            if logger:
                logger.error(f"Error generating bullets: {e}")
            raise
    
    def _build_summary_prompt(self, profile: ResumeProfile) -> str:
        """Build prompt for summary generation."""
        import time
        
        # Extract skills
        skills_list = []
        if hasattr(profile, 'core_skills') and profile.core_skills:
            skills_list.extend(profile.core_skills[:5])
        elif hasattr(profile, 'skills') and profile.skills:
            skills_list.extend([s.name for s in profile.skills[:5]])
        skills = ", ".join(skills_list) if skills_list else "leadership, operations, team management, communication, problem-solving, analyzing"
        
        # Extract MOS info
        mos_info = ""
        if hasattr(profile, 'mos') and profile.mos:
            mos_info = f"{profile.mos.code} ({profile.mos.title})"
        elif hasattr(profile, 'mos_codes') and profile.mos_codes:
            mos_info = ", ".join([f"{m.code} ({m.title_military})" for m in profile.mos_codes[:2]])
        
        # Get target role
        target_role = profile.target_roles[0] if hasattr(profile, 'target_roles') and profile.target_roles else profile.target_role if hasattr(profile, 'target_role') else "professional role"
        
        # Add unique timestamp to ensure fresh generation
        timestamp = int(time.time() * 1000)
        
        return f"""
        Write a professional 3-4 sentence resume summary for a veteran transitioning to civilian work.
        Target Role: {target_role}
        Military Background: {mos_info if mos_info else "Military service professional"}
        Key Skills: {skills}
        Security Clearance: {profile.contact.security_clearance if hasattr(profile.contact, 'security_clearance') else 'N/A'}
        Focus on accomplishments and value proposition. Be concise and impactful.
        DO NOT use phrases like "Here is" or "The summary is". Just provide the summary text directly.     
        Request ID: {timestamp}
        """
    
    def _build_bullets_prompt(
        self,
        experience: 'WorkHistory',
        profile: ResumeProfile,
        count: int
    ) -> str:
        """Build prompt for bullet generation (backward compatibility)."""
        return self._build_bullets_prompt_with_context(experience, profile, {}, count)
    
    def _build_bullets_prompt_with_context(
        self,
        experience: 'WorkHistory',
        profile: ResumeProfile,
        extra_context: dict,
        count: int
    ) -> str:
        """Build prompt for bullet generation with additional context."""
        # Handle both WorkHistory and Experience models
        job_title = getattr(experience, 'job_title', getattr(experience, 'title', 'Position'))
        employer = getattr(experience, 'employer', getattr(experience, 'organization', 'Organization'))
        
        # Get context from extra_context dict (not from experience attributes)
        responsibilities = extra_context.get('responsibilities', '')
        impact = extra_context.get('impact', '')
        impact_metrics = extra_context.get('impact_metrics', '')
        mission = extra_context.get('mission', '')
        
        # Fallback to experience attributes if available (backward compatibility)
        if not responsibilities:
            responsibilities = getattr(experience, 'responsibilities', '')
        if not impact:
            impact = getattr(experience, 'impact', '')
        if not impact_metrics:
            impact_metrics = getattr(experience, 'impact_metrics', '')
        
        # Get achievements from experience
        achievements = getattr(experience, 'achievements', [])
        
        # Get MOS codes if available
        mos_info = ""
        if hasattr(experience, 'mos_codes') and experience.mos_codes:
            mos_info = ", ".join(experience.mos_codes)
        elif hasattr(profile, 'mos') and profile.mos:
            mos_info = f"{profile.mos.code} ({profile.mos.title})"
        
        # Get target role
        target_role = profile.target_roles[0] if hasattr(profile, 'target_roles') and profile.target_roles else profile.target_role if hasattr(profile, 'target_role') else "professional role"
        
        # Get skills
        skills = []
        if hasattr(profile, 'core_skills') and profile.core_skills:
            skills = profile.core_skills
        skills_text = ", ".join(skills) if skills else ""
        
        context_parts = []
        if mission:
            context_parts.append(f"Mission: {mission}")
        if responsibilities:
            context_parts.append(f"Responsibilities: {responsibilities}")
        if impact:
            context_parts.append(f"Impact/Achievements: {impact}")
        if impact_metrics:
            context_parts.append(f"Metrics/Outcomes: {impact_metrics}")
        if achievements:
            context_parts.append(f"Additional Achievements: {', '.join(achievements[:3])}")
        
        context_text = "\n".join(context_parts)
        import time
        timestamp = int(time.time() * 1000)
        
        return f"""
        Create {count} STAR-method bullet points for this military experience, translated for civilian employers.
        
        Position: {job_title}
        Organization: {employer}
        MOS Codes: {mos_info if mos_info else "N/A"}
        Target Civilian Role: {target_role}
        Skills: {skills_text}
        {context_text}
        
        Requirements:
        - Use STAR method (Situation, Task, Action, Result)
        - ONLY include metrics, numbers, or percentages if they are explicitly provided in the context above
        - DO NOT invent or estimate any numbers, percentages, or quantifiable metrics
        - If no specific metrics are provided, focus on qualitative achievements and responsibilities
        - Keep each bullet under 24 words
        - Focus on actions taken, processes improved, and qualitative impact
        
        Return only the bullet points, one per line, without numbers or dashes.
        DO NOT include introductory phrases like "Here are" or "The bullets are".
            Request ID: {timestamp}
        """


class AIService:
    """Main AI service that delegates to the configured provider."""
    
    def __init__(self, provider: Optional[AIProvider] = None):
        """
        Initialize AI service.
        
        Args:
            provider: AI provider instance (defaults to configured provider)
        """
        if provider:
            self.provider = provider
        else:
            self.provider = self._create_provider()
    
    def _create_provider(self) -> AIProvider:
        """Create AI provider based on configuration."""
        if settings.ai_provider == "openai":
            try:
                return OpenAIProvider(model=settings.ai_model)
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI provider: {e}. Falling back to mock.")
                return MockAIProvider()
        else:
            return MockAIProvider()
    
    def generate_summary(self, profile: ResumeProfile) -> str:
        """Generate professional summary."""
        return self.provider.generate_summary(profile)
    
    def generate_bullets(
        self,
        experience: 'WorkHistory',
        profile: ResumeProfile,
        count: int = 4
    ) -> List[str]:
        """Generate STAR-style bullet points."""
        return self.provider.generate_bullets(experience, profile, count)


# Global service instance
_ai_service: Optional[AIService] = None


def get_ai_service() -> AIService:
    """Get or create the global AI service instance."""
    global _ai_service
    if _ai_service is None:
        _ai_service = AIService()
    return _ai_service


# Simplified interface for Streamlit
class SimpleAIService:
    """Simplified AI service for Streamlit UI."""
    
    def __init__(self):
        """Initialize with the configured AI provider."""
        try:
            print(f"[AI Service Init] ai_provider setting: {settings.ai_provider}")
            print(f"[AI Service Init] has openai_api_key: {bool(settings.openai_api_key)}")
            print(f"[AI Service Init] ai_model: {settings.ai_model}")
            
            if settings.ai_provider == "openai" and settings.openai_api_key:
                print(f"[AI Service] Initializing OpenAI provider with model: {settings.ai_model}")
                self._provider = OpenAIProvider(model=settings.ai_model)
                print(f"[AI Service] ✓ OpenAI provider initialized successfully")
                print(f"[AI Service] Provider type: {type(self._provider).__name__}")
            else:
                print(f"[AI Service] Using Mock provider (ai_provider={settings.ai_provider}, has_key={bool(settings.openai_api_key)})")
                self._provider = MockAIProvider()
                print(f"[AI Service] WARNING: Mock provider will generate template-based bullets, not real AI")
        except Exception as e:
            print(f"[AI Service] Error initializing OpenAI, falling back to Mock: {e}")
            import traceback
            traceback.print_exc()
            self._provider = MockAIProvider()
    
    def generate_summary(self, profile_data) -> str:
        """Generate summary from profile data dict or ResumeProfile object."""
        # Build minimal profile
        try:
            from models import Contact, ResumeProfile, MOS
            
            # If already a ResumeProfile, use it directly
            if isinstance(profile_data, ResumeProfile):
                return self._provider.generate_summary(profile_data)
            
            # Otherwise, build from dict
            # Create contact
            contact = Contact(
                full_name=profile_data.get('full_name', 'Veteran'),
                email=profile_data.get('email', 'email@example.com'),
                phone=profile_data.get('phone', '1234567890'),
                city=profile_data.get('city', 'City'),
                state=profile_data.get('state', 'ST'),
                security_clearance=profile_data.get('security_clearance', 'None')
            )
            
            # Create MOS if available
            mos = None
            if profile_data.get('mos_code'):
                mos = MOS(
                    code=profile_data.get('mos_code'),
                    branch=profile_data.get('branch', 'Army'),
                    title=profile_data.get('mos_title', profile_data.get('mos_code', ''))
                )
            
            # Create profile
            profile = ResumeProfile(
                contact=contact,
                target_roles=[profile_data.get('target_role', 'Professional')],
                mos=mos,
                core_skills=profile_data.get('core_skills', [])
            )
            
            return self._provider.generate_summary(profile)
        
        except Exception as e:
            print(f"Error generating summary: {e}")
            import traceback
            traceback.print_exc()
            
            # Fallback simple generation
            if isinstance(profile_data, ResumeProfile):
                branch = profile_data.mos.branch if profile_data.mos else 'military'
                role = profile_data.target_roles[0] if profile_data.target_roles else 'operations professional'
                clearance = profile_data.contact.security_clearance if hasattr(profile_data.contact, 'security_clearance') else 'clearance'
                mos = profile_data.mos.title if profile_data.mos else 'military operations'
            else:
                branch = profile_data.get('branch', 'military')
                role = profile_data.get('target_role', 'operations professional')
                clearance = profile_data.get('security_clearance', 'clearance')
                mos = profile_data.get('mos_title', profile_data.get('mos_code', 'military operations'))
            
            # Generate a more detailed fallback summary
            skills_text = ", ".join(profile_data.get('core_skills', [])[:3]) if not isinstance(profile_data, ResumeProfile) else ""
            if not skills_text:
                skills_text = "leadership, operations management, and team coordination"
            
            years = profile_data.get('years_of_service', '4+') if not isinstance(profile_data, ResumeProfile) else '4+'
            
            clearance_text = f" Holds {clearance} clearance." if clearance and clearance != 'None' else ""
            
            return f"Results-driven {role} with {years} years of {branch} experience. Proven expertise in {skills_text}.{clearance_text} Committed to leveraging military training and discipline to drive operational excellence in civilian sector."
    
    def generate_star_bullets(self, role_data: Dict) -> List[str]:
        """Generate STAR bullets from role data dict."""
        print(f"[SimpleAI] Generating bullets for: {role_data.get('job_title', 'Unknown')}")
        print(f"[SimpleAI] Provider type: {type(self._provider).__name__}")
        
        try:
            from models import Contact, ResumeProfile, WorkHistory
            from datetime import date
            
            # Validate required fields with better defaults
            job_title = role_data.get('job_title', '').strip() or 'Military Professional'
            employer = role_data.get('employer', '').strip() or 'U.S. Military'
            location = role_data.get('location', '').strip() or 'Location'
            
            print(f"[SimpleAI] Job Title: {job_title}")
            print(f"[SimpleAI] Employer: {employer}")
            
            # Create minimal profile for context
            contact = Contact(
                full_name="Veteran",
                email="email@example.com",
                phone="1234567890",
                city="City",
                state="ST"
            )
            profile = ResumeProfile(
                contact=contact,
                target_roles=[role_data.get('target_role', 'Professional')],
                core_skills=role_data.get('core_skills', [])
            )
            
            # Create work history object WITHOUT the extra fields
            # (responsibilities, impact, impact_metrics are not in the WorkHistory model)
            work_history = WorkHistory(
                title=job_title,
                organization=employer,
                location=location,
                start_date=date(2020, 1, 1),
                end_date=date(2024, 1, 1),
                bullets=[],
                scope_metrics=role_data.get('impact_metrics', '')
            )
            
            # Store the extra context in a separate dict for the prompt
            extra_context = {
                'responsibilities': role_data.get('responsibilities', ''),  # Mission
                'impact': role_data.get('impact', ''),  # Responsibilities  
                'impact_metrics': role_data.get('impact_metrics', ''),  # Metrics
                'mission': role_data.get('responsibilities', ''),  # Mission
            }
            
            print(f"[SimpleAI] Mission: {extra_context['responsibilities'][:50]}...")
            print(f"[SimpleAI] Impact: {extra_context['impact'][:50]}...")
            print(f"[SimpleAI] Metrics: {extra_context['impact_metrics'][:50]}...")
            
            # Try to use the AI provider - pass extra_context separately
            if isinstance(self._provider, OpenAIProvider):
                print(f"[SimpleAI] Using OpenAI provider")
                bullets = self._provider.generate_bullets_with_context(work_history, profile, extra_context, count=4)
                print(f"[SimpleAI] Successfully generated {len(bullets)} bullets using OpenAI")
                return bullets
            else:
                print(f"[SimpleAI] Using Mock provider (fallback)")
                bullets = self._provider.generate_bullets(work_history, profile, count=4)
                print(f"[SimpleAI] Generated {len(bullets)} bullets using Mock provider")
                return bullets
        
        except Exception as e:
            print(f"[SimpleAI] ERROR in generate_star_bullets: {e}")
            import traceback
            traceback.print_exc()
            raise  # Re-raise the exception instead of returning demo bullets
    
    def generate_skills_from_mos(self, mos_code: str, mos_title: str, target_role: str) -> List[str]:
        """Generate AI-suggested skills based on MOS and target role."""
        try:
            # Use OpenAI to generate relevant skills
            if isinstance(self._provider, OpenAIProvider):
                prompt = f"""
                Based on military MOS {mos_code} ({mos_title}) transitioning to civilian role: {target_role}
                
                Generate 8-12 relevant civilian skills that would be valuable for this transition.
                Focus on:
                - Technical skills relevant to the target role
                - Transferable military skills in civilian terms
                - Industry-standard competencies
                
                Return ONLY the skills as a comma-separated list, no explanations or numbering.
                Example format: Leadership, Project Management, Risk Assessment, Data Analysis
                """
                
                response = self._provider.client.chat.completions.create(
                    model=self._provider.model,
                    messages=[
                        {"role": "system", "content": "You are a career counselor specializing in military-to-civilian transitions."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=150,
                    temperature=0.7
                )
                
                skills_text = response.choices[0].message.content.strip()
                skills = [s.strip() for s in skills_text.split(',') if s.strip()]
                return skills[:12]
            else:
                # Fallback to template-based skills
                return self._generate_fallback_skills(mos_title, target_role)
        
        except Exception as e:
            print(f"Error generating skills: {e}")
            return self._generate_fallback_skills(mos_title, target_role)
    
    def _generate_fallback_skills(self, mos_title: str, target_role: str) -> List[str]:
        """Generate fallback skills when AI is not available."""
        base_skills = [
            "Leadership & Team Management",
            "Strategic Planning",
            "Operations Management",
            "Problem Solving",
            "Communication",
            "Risk Assessment",
            "Process Improvement",
            "Training & Development"
        ]
        
        # Add role-specific skills
        role_lower = target_role.lower()
        if "manager" in role_lower or "lead" in role_lower:
            base_skills.extend(["Project Management", "Resource Allocation", "Performance Optimization"])
        if "analyst" in role_lower or "intelligence" in role_lower:
            base_skills.extend(["Data Analysis", "Critical Thinking", "Report Writing"])
        if "engineer" in role_lower or "technical" in role_lower:
            base_skills.extend(["Technical Documentation", "System Design", "Quality Assurance"])
        if "logistics" in role_lower or "supply" in role_lower:
            base_skills.extend(["Supply Chain Management", "Inventory Control", "Vendor Relations"])
        
        return base_skills[:12]

