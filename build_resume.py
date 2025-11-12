"""
Command-line tool for building resumes from JSON profiles.
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

from models import (
    Contact, Experience, Education, Skill, Certification,
    MOS, ResumeProfile, AdditionalInfo
)
from services.resume_service import get_resume_service
from services.ai_service import get_ai_service
from utils.logging_utils import get_logger

logger = get_logger(__name__)


def load_profile_from_json(json_path: Path) -> ResumeProfile:
    """
    Load resume profile from JSON file.
    
    Args:
        json_path: Path to JSON file
    
    Returns:
        ResumeProfile instance
    """
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    # Parse contact
    contact_data = data['contact']
    if 'security_clearance' not in contact_data:
        contact_data['security_clearance'] = 'None'
    contact = Contact(**contact_data)
    
    # Parse MOS codes - handle both single MOS and list
    mos_data = None
    if data.get('mos_codes') and len(data['mos_codes']) > 0:
        mos_dict = data['mos_codes'][0]
        mos_data = MOS(
            code=mos_dict['code'],
            branch=mos_dict['branch'],
            title=mos_dict.get('title'),
            civilian_skills=mos_dict.get('civilian_skills', [])
        )
    
    # Parse experience/work_history
    work_history = []
    for exp_data in data.get('experience', []):
        # Convert date strings to date objects
        start_date = datetime.fromisoformat(exp_data['start_date']).date()
        end_date = None
        if exp_data.get('end_date'):
            end_date = datetime.fromisoformat(exp_data['end_date']).date()
        
        # Map bullets to achievements
        achievements = exp_data.get('bullets', [])
        
        work_entry = Experience(
            title=exp_data.get('title', exp_data.get('job_title', 'Position')),
            organization=exp_data.get('organization', exp_data.get('employer', 'Unknown')),
            location=exp_data.get('location', ''),
            start_date=start_date,
            end_date=end_date,
            current=exp_data.get('current', False),
            bullets=achievements
        )
        work_history.append(work_entry)
    
    # Parse education
    education = []
    for edu_data in data.get('education', []):
        grad_year = None
        if edu_data.get('graduation_date'):
            grad_date = datetime.fromisoformat(edu_data['graduation_date']).date()
            grad_year = grad_date.year
        elif edu_data.get('graduation_year'):
            grad_year = edu_data['graduation_year']
        
        education.append(Education(
            institution=edu_data['institution'],
            degree=edu_data['degree'],
            field_of_study=edu_data.get('field_of_study'),
            overview=edu_data.get('overview'),
            courses=edu_data.get('courses', []),
            courses_overview=edu_data.get('courses_overview'),
            graduation_year=grad_year,
            gpa=edu_data.get('gpa'),
            honors=edu_data.get('honors', [])
        ))
    
    # Parse skills - convert to core_skills list
    core_skills = []
    for skill_data in data.get('skills', []):
        if isinstance(skill_data, dict):
            core_skills.append(skill_data['name'])
        else:
            core_skills.append(str(skill_data))
    
    # Parse certifications
    certifications = []
    for cert_data in data.get('certifications', []):
        year = None
        if cert_data.get('issue_date'):
            issue_date = datetime.fromisoformat(cert_data['issue_date']).date()
            year = issue_date.year
        
        certifications.append(Certification(
            name=cert_data['name'],
            issuer=cert_data['issuer'],
            year=year,
            credential_id=cert_data.get('credential_id')
        ))
    
    # Build profile
    target_role = data.get('target_role', 'Professional')
    additional_info = None
    if 'additional_info' in data:
        ai = data['additional_info']
        additional_info = AdditionalInfo(
            awards=ai.get('awards', []),
            volunteer=ai.get('volunteer', []),
            veteran_experience=ai.get('veteran_experience', []),
            languages=ai.get('languages', []),
            clearance_note=ai.get('clearance_note'),
            references_available=ai.get('references_available', True)
        )

    profile = ResumeProfile(
        contact=contact,
        target_roles=[target_role] if isinstance(target_role, str) else target_role,
        summary=data.get('summary'),
        mos=mos_data,
        core_skills=core_skills,
        work_history=work_history,
        education=education,
        certifications=certifications,
        additional_info=additional_info
    )
    
    return profile


def generate_ai_content(profile: ResumeProfile) -> ResumeProfile:
    """
    Generate AI content for profile if not already present.
    
    Args:
        profile: Resume profile
    
    Returns:
        Updated profile with AI-generated content
    """
    ai_service = get_ai_service()
    
    # Generate summary if missing
    if not profile.summary:
        logger.info("Generating AI summary...")
        profile.summary = ai_service.generate_summary(profile)
    
    # Generate bullets for work history with empty achievements
    for work in profile.work_history:
        if not work.achievements or len(work.achievements) == 0:
            logger.info(f"Generating bullets for {work.job_title}...")
            # Convert work history to dict format for AI service
            work_dict = {
                'job_title': work.job_title,
                'employer': work.employer,
                'responsibilities': f"Worked as {work.job_title} at {work.employer}",
                'impact': work.scope_metrics or '',
                'target_role': profile.target_roles[0] if profile.target_roles else 'Professional',
                'core_skills': profile.core_skills
            }
            bullets = ai_service.generate_star_bullets(work_dict)
            work.achievements = bullets
    
    return profile


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Build a resume from a JSON profile",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --in profile.json --docx
  %(prog)s --in profile.json --template classic --outdir ~/resumes
  %(prog)s --in profile.json --docx --generate-ai
        """
    )
    
    parser.add_argument(
        '--in', '--input',
        dest='input',
        type=Path,
        required=True,
        help='Input JSON profile file'
    )
    
    parser.add_argument(
        '--template',
        type=str,
        default='classic',
        help='Template name (default: classic)'
    )
    
    parser.add_argument(
        '--docx',
        action='store_true',
        help='Generate DOCX output'
    )
    
    parser.add_argument(
        '--outdir',
        type=Path,
        default=None,
        help='Output directory (default: ./output)'
    )
    
    parser.add_argument(
        '--generate-ai',
        action='store_true',
        help='Generate AI content for missing summary/bullets'
    )
    
    parser.add_argument(
        '--output-filename',
        type=str,
        default=None,
        help='Custom output filename (without extension)'
    )
    
    args = parser.parse_args()
    
    # Validate input file
    if not args.input.exists():
        logger.error(f"Input file not found: {args.input}")
        sys.exit(1)
    
    try:
        # Load profile
        logger.info(f"Loading profile from {args.input}")
        profile = load_profile_from_json(args.input)
        
        # Generate AI content if requested
        if args.generate_ai:
            profile = generate_ai_content(profile)
        
        # Initialize resume service
        resume_service = get_resume_service()
        if args.outdir:
            resume_service.output_dir = args.outdir
            resume_service.output_dir.mkdir(exist_ok=True, parents=True)
        
        # Generate DOCX
        if args.docx:
            logger.info(f"Generating resume with template '{args.template}'")
            
            output_filename = args.output_filename
            if output_filename and not output_filename.endswith('.docx'):
                output_filename += '.docx'
            
            output_path = resume_service.generate_resume(
                profile,
                template_name=args.template,
                output_filename=output_filename
            )
            
            print(f"\n✓ Resume generated successfully!")
            print(f"  Output: {output_path}")
            print(f"  Template: {args.template}")
        
        else:
            logger.error("No output format specified. Use --docx")
            sys.exit(1)
    
    except Exception as e:
        logger.error(f"Error building resume: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
