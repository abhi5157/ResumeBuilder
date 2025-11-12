"""
Enhanced resume preview rendering for Step 4.
Professional format matching Resume.docx template.
Uses mammoth library to convert DOCX to clean HTML for accurate preview.
"""

import streamlit as st
from typing import Dict, List
import mammoth
from pathlib import Path


def convert_docx_to_html(docx_path: str) -> str:
    """
    Convert a DOCX file to clean HTML using mammoth library.
    
    Args:
        docx_path: Path to the DOCX file
        
    Returns:
        HTML string representation of the document
    """
    try:
        with open(docx_path, "rb") as docx_file:
            result = mammoth.convert_to_html(docx_file)
            html = result.value  # The generated HTML
            messages = result.messages  # Any messages such as warnings
            
            
            return html
    except Exception as e:
        st.error(f"Error converting DOCX to HTML: {e}")
        return ""


def render_docx_preview(docx_path: str):
    """
    Render a professional preview of a DOCX resume using mammoth.
    
    Args:
        docx_path: Path to the generated DOCX file
    """
    # Convert DOCX to HTML
    html_content = convert_docx_to_html(docx_path)
    
    if not html_content:
        st.error("Unable to generate preview")
        return
    
    # Custom CSS for professional resume styling matching DOCX format exactly
    custom_css = """
    <style>
        .resume-preview {
            background: white !important;
            padding: 0.5in 0.7in;
            font-family: 'Calibri Light', 'Calibri', 'Arial', sans-serif;
            max-width: 8.5in;
            margin: 1rem auto;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            border: 1px solid #d1d5db;
            color: #000000 !important;
            line-height: 1.0;
            font-size: 10pt;
        }
        
        .resume-preview * {
            color: #000000 !important;
            background: transparent !important;
            box-sizing: border-box;
        }
        
        /* All paragraphs default to 10pt, Calibri Light */
        .resume-preview p {
            margin: 0 !important;
            padding: 0 !important;
            font-size: 10pt !important;
            font-family: 'Calibri Light', 'Calibri', 'Arial', sans-serif !important;
            line-height: 1.0 !important;
        }
        
        /* Name header - first paragraph with strong tag, centered, bold, 16pt */
        .resume-preview > p:first-of-type {
            text-align: center !important;
            margin-bottom: 2pt !important;
        }
        
        .resume-preview > p:first-of-type strong {
            font-size: 16pt !important;
            font-weight: 700 !important;
        }
        
        /* Contact line - second paragraph, centered, 10pt */
        .resume-preview > p:nth-of-type(2) {
            text-align: center !important;
            font-size: 10pt !important;
            margin-bottom: 2pt !important;
        }
        
        /* Branch title - third paragraph with strong, centered, bold, 11pt */
        .resume-preview > p:nth-of-type(3) {
            text-align: center !important;
            margin-bottom: 2pt !important;
        }
        
        .resume-preview > p:nth-of-type(3) strong {
            font-size: 11pt !important;
            font-weight: 700 !important;
        }
        
        /* Section headings - standalone paragraph with text like "SUMMARY", "PROFESSIONAL EXPERIENCE", etc. */
        .resume-preview > p:not(:first-of-type):not(:nth-of-type(2)):not(:nth-of-type(3)):not(:has(strong)):not(:has(em)):not(:has(table)) {
            text-align: center !important;
            font-size: 11pt !important;
            font-weight: 400 !important;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            border-top: 1px solid #000000 !important;
            padding-top: 0 !important;
            margin: 0 0 2pt 0 !important;
        }
        
        /* Detect section headings by content */
        .resume-preview > p {
            position: relative;
        }
        
        .resume-preview > p:not(:first-of-type):not(:nth-of-type(2)):not(:nth-of-type(3)):not(:has(*)) {
            text-align: center !important;
            font-size: 11pt !important;
            border-top: 1px solid #000000 !important;
            padding-top: 0 !important;
            margin-top: 0 !important;
            margin-bottom: 2pt !important;
        }
        
        /* Summary paragraph - text-justified, after section heading */
        .resume-preview > p:nth-of-type(5) {
            text-align: justify !important;
            margin-bottom: 2pt !important;
        }
        
        /* Tables - match DOCX table styling with borders */
        .resume-preview table {
            width: 100% !important;
            border-collapse: collapse !important;
            margin: 0 0 4pt 0 !important;
            border: 1px solid #000000 !important;
        }
        
        .resume-preview td {
            border: 1px solid #000000 !important;
            padding: 2pt 4pt !important;
            vertical-align: top !important;
        }
        
        .resume-preview td p {
            margin: 0 !important;
            padding: 0 !important;
            font-size: 10pt !important;
            line-height: 1.0 !important;
        }
        
        /* Left column: 75% width */
        .resume-preview tr td:first-child {
            width: 75% !important;
        }
        
        /* Right column: 25% width, right-aligned */
        .resume-preview tr td:last-child {
            width: 25% !important;
        }
        
        .resume-preview tr td:last-child p {
            text-align: right !important;
            font-style: normal !important;
        }
        
        /* Job titles / degrees inside table cells - bold, 11pt, first <strong> in <p> */
        .resume-preview td p:first-child strong {
            font-size: 11pt !important;
            font-weight: 700 !important;
        }
        
        /* Company names / institutions - italic, 10pt */
        .resume-preview td em {
            font-style: italic !important;
            font-size: 10pt !important;
            font-weight: 400 !important;
        }
        
        /* Bullet points within table cells */
        .resume-preview td p:not(:first-child) {
            margin-top: 0 !important;
            padding-left: 0 !important;
        }
        
        /* Strong text */
        .resume-preview strong {
            font-weight: 700 !important;
        }
        
        /* Links */
        .resume-preview a {
            text-decoration: none !important;
            color: #000000 !important;
        }
        
        /* Skills section paragraph - the last standalone paragraph before any volunteer table, justified */
        .resume-preview > p:last-of-type,
        .resume-preview > table:last-of-type ~ p {
            text-align: justify !important;
        }
    </style>
    """
    
    # Render the preview
    st.markdown(custom_css, unsafe_allow_html=True)
    st.markdown(f'<div class="resume-preview">{html_content}</div>', unsafe_allow_html=True)


def render_enhanced_resume_preview(profile_data: Dict, work_history: List, education: List, certifications: List, volunteer: List = None):
    """
    Render a professional resume preview matching the Resume.docx template format.
    
    Args:
        profile_data: Dictionary containing profile information
        work_history: List of work history entries
        education: List of education entries
        certifications: List of certification entries
        volunteer: Optional list of volunteer experience entries
    """
    

    
    # ===== HEADER SECTION =====
    full_name = profile_data.get('full_name', 'YOUR NAME').upper()
    st.markdown(f"""
    <div style="text-align: center; border-bottom: 2px solid #000000; padding-bottom: 0.5rem; margin-bottom: 1rem;">
        <h1 style="color: #000000; margin: 0; font-size: 1.4rem; font-weight: 700; letter-spacing: 0.3px;">
            {full_name}
        </h1>
    """, unsafe_allow_html=True)
    
    # Contact Information
    contact_parts = []
    if profile_data.get('city') and profile_data.get('state'):
        contact_parts.append(f"{profile_data['city']}, {profile_data['state']}")
    if profile_data.get('phone'):
        contact_parts.append(profile_data['phone'])
    if profile_data.get('email'):
        contact_parts.append(profile_data['email'])
    if profile_data.get('linkedin'):
        linkedin_clean = profile_data['linkedin'].replace('https://', '').replace('http://', '').replace('www.', '')
        contact_parts.append(linkedin_clean)
    
    if contact_parts:
        st.markdown(f"""
        <p style="color: #000000; text-align: center; margin: 0.75rem 0 0 0; font-size: 0.85rem; line-height: 1.4;">
            {' | '.join(contact_parts)}
        </p>
        """, unsafe_allow_html=True)
    
    # Security Clearance Badge
    if profile_data.get('security_clearance') and profile_data['security_clearance'] != 'None':
        st.markdown(f"""
        <p style="text-align: center; margin: 0.5rem 0 0 0;">
            <span style="background: #1e40af; padding: 0.25rem 0.75rem; border-radius: 4px; font-size: 0.85rem; font-weight: 600;">
                🔒 {profile_data['security_clearance']} Clearance
            </span>
        </p>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # ===== PROFESSIONAL SUMMARY =====
    ai_summary = st.session_state.get('ai_summary')
    if ai_summary:
        st.markdown(f"""
        <div style="margin: 1.5rem 0;">
            <h2 style="color: #000000; font-size: 1.1rem; font-weight: 700; text-transform: uppercase; 
                       letter-spacing: 1px; border-bottom: 2px solid #000000; padding-bottom: 0.25rem; margin: 0 0 0.75rem 0;">
                SUMMARY
            </h2>
            <p style="color: #000000 !important; margin: 0; line-height: 1.7; text-align: justify; font-size: 0.85rem;">
                {ai_summary}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # ===== CORE COMPETENCIES =====
    core_skills = profile_data.get('core_skills', [])
    if core_skills:
        skills_display = core_skills[:12]  # Show top 12 skills
        skills_html = '<div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.5rem; margin: 0;">'
        for skill in skills_display:
            skills_html += f'<div style="color: #000000; font-size: 0.85rem;">• {skill}</div>'
        skills_html += '</div>'
        
        st.markdown(f"""
        <div style="margin: 1.5rem 0;">
            <h2 style="color: #000000; font-size: 1.1rem; font-weight: 700; text-transform: uppercase; 
                       letter-spacing: 1px; border-bottom: 2px solid #000000; padding-bottom: 0.25rem; margin: 0 0 0.75rem 0;">
                CORE COMPETENCIES
            </h2>
            {skills_html}
        </div>
        """, unsafe_allow_html=True)
    
    # ===== PROFESSIONAL EXPERIENCE =====
    if work_history:
        st.markdown("""
        <div style="margin: 1.5rem 0;">
            <h2 style="color: #000000; font-size: 1.1rem; font-weight: 700; text-transform: uppercase; 
                       letter-spacing: 1px; border-bottom: 2px solid #000000; padding-bottom: 0.25rem; margin: 0 0 0.75rem 0;">
                PROFESSIONAL EXPERIENCE
            </h2>
        """, unsafe_allow_html=True)
        
        for idx, role in enumerate(work_history):
            job_title = role.get('job_title', 'Position')
            employer = role.get('employer', 'Organization')
            location = role.get('location', '')
            start_date = role.get('start_date', 'Start')
            end_date = role.get('end_date', 'Present')
            
            st.markdown(f"""
            <div style="margin: {'1rem 0 1.5rem 0' if idx > 0 else '0 0 1.5rem 0'};">
                <div style="display: flex; justify-content: space-between; align-items: baseline;">
                    <h3 style="color: #000000; margin: 0; font-size: 0.95rem; font-weight: 700;">
                        {job_title}
                    </h3>
                    <span style="color: #000000; font-size: 0.85rem; font-style: italic;">
                        {start_date} – {end_date}
                    </span>
                </div>
                <p style="color: #000000; margin: 0.25rem 0 0.5rem 0; font-size: 0.85rem; font-weight: 600;">
                    {employer}{f" | {location}" if location else ''}
                </p>
            """, unsafe_allow_html=True)
            
            # Mission/Responsibilities
            if role.get('responsibilities'):
                st.markdown(f"""
                <p style="color: #000000; margin: 0.5rem 0; line-height: 1.6; font-size: 0.85rem; text-align: justify;">
                    {role['responsibilities']}
                </p>
                """, unsafe_allow_html=True)
            
            # Achievement Bullets
            bullets = role.get('ai_bullets', [])
            if bullets:
                bullets_html = '<ul style="margin: 0.25rem 0; padding-left: 1.2rem; color: #000000;">'
                for bullet in bullets[:4]:
                    bullets_html += f'<li style="margin: 0.15rem 0; line-height: 1.4; font-size: 0.83rem; color: #000000;">{bullet}</li>'
                bullets_html += '</ul>'
                st.markdown(bullets_html, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # ===== EDUCATION =====
    if education:
        st.markdown("""
        <div style="margin: 1.5rem 0;">
            <h2 style="color: #000000; font-size: 1.1rem; font-weight: 700; text-transform: uppercase; 
                       letter-spacing: 1px; border-bottom: 2px solid #000000; padding-bottom: 0.25rem; margin: 0 0 0.75rem 0;">
                EDUCATION
            </h2>
        """, unsafe_allow_html=True)
        
        for edu in education:
            degree = edu.get('degree', 'Degree')
            field = edu.get('field_of_study', '')
            institution = edu.get('institution', 'Institution')
            year = edu.get('year', 'Year')
            gpa = edu.get('gpa', '')
            
            gpa_display = f" | GPA: {gpa}" if gpa else ''
            
            st.markdown(f"""
            <div style="margin: 0.4rem 0;">
                <p style="color: #000000; margin: 0; font-size: 0.83rem; line-height: 1.3;">
                    <strong>{degree}</strong>{f" in {field}" if field else ''}
                </p>
                <p style="color: #000000; margin: 0.15rem 0 0 0; font-size: 0.83rem; line-height: 1.3;">
                    {institution}{f" | {year}" if year else ''}{gpa_display}
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # ===== CERTIFICATIONS =====
    if certifications:
        st.markdown("""
        <div style="margin: 1.5rem 0;">
            <h2 style="color: #000000; font-size: 1.1rem; font-weight: 700; text-transform: uppercase; 
                       letter-spacing: 1px; border-bottom: 2px solid #000000; padding-bottom: 0.25rem; margin: 0 0 0.75rem 0;">
                CERTIFICATIONS
            </h2>
        """, unsafe_allow_html=True)
        # Single column compact list
        certs_html = '<ul style="margin: 0.3rem 0; padding-left: 1.2rem;">'
        for cert in certifications:
            cert_name = cert.get('name', 'Certification')
            issuer = cert.get('issuer', '')
            certs_html += f'<li style="margin: 0.15rem 0; font-size: 0.83rem; line-height: 1.3;">{cert_name}{f" – {issuer}" if issuer else ""}</li>'
        certs_html += '</ul>'
        st.markdown(certs_html, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # ===== VOLUNTEER EXPERIENCE =====
    if volunteer:
        st.markdown("""
        <div style="margin: 1.5rem 0;">
            <h2 style="color: #000000; font-size: 1.1rem; font-weight: 700; text-transform: uppercase; 
                       letter-spacing: 1px; border-bottom: 2px solid #000000; padding-bottom: 0.25rem; margin: 0 0 0.75rem 0;">
                VOLUNTEER EXPERIENCE
            </h2>
        """, unsafe_allow_html=True)
        # Support both list of strings and list of dict entries
        if volunteer and isinstance(volunteer, list):
            # Detect dict style
            if all(isinstance(v, dict) for v in volunteer):
                for idx, vol in enumerate(volunteer):
                    role = vol.get('role') or vol.get('title') or 'Role'
                    org = vol.get('organization') or vol.get('org') or 'Organization'
                    date_range = vol.get('date_range') or vol.get('duration') or ''
                    description = vol.get('description') or ''
                    
                    st.markdown(f"""
                    <div style="margin: {'1rem 0 1.5rem 0' if idx > 0 else '0 0 1.5rem 0'}; 
                                padding: 0.75rem; border: 1px solid #cbd5e1; border-radius: 4px; 
                                background: #f8fafc;">
                        <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 0.5rem;">
                            <p style="color: #000000; margin: 0; font-size: 0.9rem; font-weight: 700;">
                                {org}
                            </p>
                            <span style="color: #000000; font-size: 0.8rem; font-style: italic;">
                                {date_range}
                            </span>
                        </div>
                        <p style="color: #000000; margin: 0 0 0.5rem 0; font-size: 0.85rem; font-style: italic;">
                            {role}
                        </p>
                        <p style="color: #000000; margin: 0; font-size: 0.83rem; line-height: 1.6; text-align: justify;">
                            {description}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                # Treat as bullet list of strings
                vol_html = '<ul style="margin: 0.3rem 0; padding-left: 1.2rem;">'
                for v in volunteer:
                    vol_html += f'<li style="margin: 0.15rem 0; font-size: 0.83rem; line-height: 1.3;">{v}</li>'
                vol_html += '</ul>'
                st.markdown(vol_html, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

