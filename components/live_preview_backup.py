"""
Live Preview Component
Displays real-time preview of resume as user fills out the form.
"""

import streamlit as st
from typing import Dict


def render_live_preview_panel(profile_data: Dict):
    """
    Render live preview panel with sticky header and scrollable content.
    
    Args:
        profile_data: Dictionary containing profile information
    """
    
    # Custom CSS for live preview panel
    st.markdown("""
    <style>
        /* Override global styles for live preview */
        .live-preview-panel .stMarkdown,
        .live-preview-panel .stMarkdown p,
        .live-preview-panel .stMarkdown span,
        .live-preview-panel .stMarkdown div {
            color: inherit !important;
            # background: transparent !important;
            background-color: #0B1220 !important;
        }
        
        /* Live Preview Container */
        .live-preview-panel {
            position: sticky;
            top: 80px;
            background: #ffffff !important;
            border-radius: 16px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2), 0 4px 12px rgba(0, 0, 0, 0.15);
            border: 1px solid rgba(148, 163, 184, 0.3);
            overflow: hidden;
            max-height: calc(100vh - 100px);
            display: flex;
            flex-direction: column;
        }
        
        /* Sticky Header */
        .preview-header {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%) !important;
            color: white !important;
            padding: 1.25rem 1.75rem !important;
            border-bottom: 3px solid #22d3ee !important;
            position: sticky;
            top: 0;
            z-index: 10;
        }
        
        .preview-title {
            font-size: 1rem !important;
            font-weight: 700 !important;
            letter-spacing: 1px !important;
            text-transform: uppercase !important;
            margin: 0 !important;
            color: #ffffff !important;
        }
        
        .preview-subtitle {
            font-size: 0.8rem !important;
            color: #ffffff !important;
            margin: 0.35rem 0 0 0 !important;
            font-weight: 400 !important;
        }
        
        /* Sticky Contact Header inside preview */
        .preview-contact-sticky {
           background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%) !important;
           color: white !important;
            padding: 1.5rem 1.75rem !important;
            border-bottom: 2px solid #cbd5e1 !important;
            position: sticky;
            top: 0;
            z-index: 9;
            box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08) !important;
        }
        
        /* Scrollable Content */
        .preview-content {
            flex: 1;
            overflow-y: auto;
            padding: 1.75rem !important;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%) !important;
            min-height: 200px;
        }
        
        .preview-content::-webkit-scrollbar {
            width: 6px;
        }
        
        .preview-content::-webkit-scrollbar-track {
            background: #f1f5f9;
            border-radius: 3px;
        }
        
        .preview-content::-webkit-scrollbar-thumb {
            background: #cbd5e1;
            border-radius: 3px;
        }
        
        .preview-content::-webkit-scrollbar-thumb:hover {
            background: #94a3b8;
        }
        
        /* Name */
        .preview-name {
            font-size: 1.75rem !important;
            font-weight: 700 !important;
            color: #0f172a !important;
            margin: 0 0 0.5rem 0 !important;
            line-height: 1.2 !important;
        }
        
        /* Contact Info */
        .preview-contact {
            font-size: 0.9rem !important;
            color: #475569 !important;
            line-height: 1.7 !important;
            margin: 0 !important;
        }
        
        .preview-contact-item {
            display: inline-block !important;
            margin-right: 0.85rem !important;
            color: #475569 !important;
        }
        
        .preview-contact-item:not(:last-child)::after {
            content: "•" !important;
            margin-left: 0.85rem !important;
            color: #94a3b8 !important;
        }
        
        /* Badges */
        .preview-badges {
            margin: 0.85rem 0 0 0 !important;
        }
        
        .preview-badge {
            display: inline-block !important;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%) !important;
            color: #22d3ee !important;
            padding: 0.425rem 1rem !important;
            border-radius: 8px !important;
            font-size: 0.8rem !important;
            font-weight: 700 !important;
            margin-right: 0.6rem !important;
            margin-bottom: 0.6rem !important;
            letter-spacing: 0.75px !important;
            box-shadow: 0 2px 8px rgba(15, 23, 42, 0.3) !important;
            border: 1px solid #334155 !important;
        }
        
        /* Section Divider */
        .preview-divider {
            height: 2px !important;
            background: linear-gradient(to right, transparent, #cbd5e1, transparent) !important;
            margin: 1.5rem 0 !important;
        }
        
        /* Section Headers */
        .preview-section-title {
            font-size: 0.95rem !important;
            font-weight: 700 !important;
            color: #0f172a !important;
            text-transform: uppercase !important;
            letter-spacing: 0.75px !important;
            margin: 0 0 1rem 0 !important;
            padding-bottom: 0.5rem !important;
            border-bottom: 3px solid #22d3ee !important;
        }
        
        /* Content Text */
        .preview-text {
            font-size: 0.9rem !important;
            color: #334155 !important;
            line-height: 1.7 !important;
            margin: 0.6rem 0 !important;
        }
        
        /* Skills */
        .preview-skill {
            display: inline-block !important;
            background: linear-gradient(135deg, #ecfeff 0%, #cffafe 100%) !important;
            color: #0e7490 !important;
            padding: 0.45rem 0.9rem !important;
            border-radius: 8px !important;
            font-size: 0.85rem !important;
            font-weight: 600 !important;
            margin: 0.3rem 0.3rem 0.3rem 0 !important;
            border: 1px solid #67e8f9 !important;
            box-shadow: 0 1px 3px rgba(14, 116, 144, 0.1) !important;
        }
        
        /* Work History / Education Cards */
        .preview-card {
            background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%) !important;
            border-left: 4px solid #22d3ee !important;
            border-radius: 8px !important;
            padding: 1rem 1.25rem !important;
            margin: 0.85rem 0 !important;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08) !important;
            animation: fadeInUp 0.3s ease-out;
            border: 1px solid #e2e8f0 !important;
            border-left: 4px solid #22d3ee !important;
        }
        
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .preview-card-title {
            font-size: 0.95rem !important;
            font-weight: 700 !important;
            color: #0f172a !important;
            margin: 0 0 0.35rem 0 !important;
        }
        
        .preview-card-subtitle {
            font-size: 0.85rem !important;
            color: #64748b !important;
            margin: 0 !important;
        }
        
        /* Empty State */
        .preview-empty {
            font-size: 0.875rem !important;
            color: #0B1220 !important;
            font-style: italic !important;
            text-align: center !important;
            padding: 1.75rem 1.25rem !important;
            border-radius: 8px !important;
            margin: 0.6rem 0 !important;
            border: 2px dashed #cbd5e1 !important;
        }
        
        /* Fade in animation for new content */
        .fade-in {
            animation: fadeIn 0.4s ease-in !important;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Main preview container
    st.markdown('<div class="live-preview-panel">', unsafe_allow_html=True)
    
    # Header
    st.markdown("""
        <div class="preview-header">
            <p class="preview-title">Live Preview</p>
            <p class="preview-subtitle">Updated in Real Time</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Sticky Contact Header
    name = profile_data.get("full_name", "Your Name")
    
    contact_parts = []
    if profile_data.get("email"):
        contact_parts.append(profile_data["email"])
    if profile_data.get("phone"):
        contact_parts.append(profile_data["phone"])
    if profile_data.get("city") or profile_data.get("state"):
        location = f"{profile_data.get('city', '')}, {profile_data.get('state', '')}".strip(", ")
        if location:
            contact_parts.append(location)
    if profile_data.get("linkedin"):
        linkedin_display = profile_data["linkedin"].replace("https://", "").replace("http://", "")
        contact_parts.append(linkedin_display)
    
    contact_html = " ".join([f'<span class="preview-contact-item">{part}</span>' for part in contact_parts])
    
    st.markdown(f"""
        <div class="preview-contact-sticky fade-in">
            <h2 class="preview-name">{name}</h2>
            <div class="preview-contact">{contact_html if contact_html else '<span class="preview-empty">Contact info will appear here</span>'}</div>
    """, unsafe_allow_html=True)
    
    # Badges
    badges = []
    if st.session_state.get("selected_branch"):
        badges.append(st.session_state.selected_branch.upper())
    if profile_data.get("security_clearance") and profile_data["security_clearance"] != "None":
        badges.append(profile_data["security_clearance"].upper())
    
    if badges:
        badges_html = "".join([f'<span class="preview-badge">{badge}</span>' for badge in badges])
        st.markdown(f'<div class="preview-badges">{badges_html}</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)  # Close sticky contact
    
    # Scrollable Content
    st.markdown('<div class="preview-content">', unsafe_allow_html=True)
    
    # Target Role
    if profile_data.get("target_role"):
        st.markdown('<p class="preview-section-title">Target Role</p>', unsafe_allow_html=True)
        st.markdown(f'<p class="preview-text">{profile_data["target_role"]}</p>', unsafe_allow_html=True)
        st.markdown('<div class="preview-divider"></div>', unsafe_allow_html=True)
    
    # Professional Summary
    if st.session_state.get("ai_summary"):
        st.markdown('<p class="preview-section-title">Professional Summary</p>', unsafe_allow_html=True)
        summary_text = st.session_state.ai_summary
        st.markdown(f'<p class="preview-text">{summary_text}</p>', unsafe_allow_html=True)
        st.markdown('<div class="preview-divider"></div>', unsafe_allow_html=True)
    
    # Core Skills
    st.markdown('<p class="preview-section-title">Core Skills</p>', unsafe_allow_html=True)
    all_skills = st.session_state.get("mos_skills", []) + profile_data.get("core_skills", [])
    
    if all_skills:
        skills_html = "".join([f'<span class="preview-skill">{skill}</span>' for skill in all_skills[:12]])
        st.markdown(f'<div class="fade-in">{skills_html}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="preview-empty">Skills will appear here as you add them</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="preview-divider"></div>', unsafe_allow_html=True)
    
    # Work History
    st.markdown('<p class="preview-section-title">Work History</p>', unsafe_allow_html=True)
    work_history = st.session_state.get("work_history", [])
    
    if work_history:
        for idx, role in enumerate(work_history[:3]):  # Show first 3 roles
            job_title = role.get("job_title", "Position")
            employer = role.get("employer", "Company")
            start_date = role.get("start_date", "Start")
            end_date = role.get("end_date", "Present")
            
            # Format dates
            if hasattr(start_date, 'strftime'):
                start_date = start_date.strftime("%b %Y")
            if hasattr(end_date, 'strftime'):
                end_date = end_date.strftime("%b %Y")
            
            dates = f"{start_date} - {end_date}"
            
            st.markdown(f"""
                <div class="preview-card">
                    <p class="preview-card-title">{job_title}</p>
                    <p class="preview-card-subtitle">{employer} • {dates}</p>
                </div>
            """, unsafe_allow_html=True)
        
        if len(work_history) > 3:
            st.markdown(f'<p class="preview-text" style="text-align: center; font-style: italic; color: #64748b;">+ {len(work_history) - 3} more role(s)</p>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="preview-empty">Work history will appear here</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="preview-divider"></div>', unsafe_allow_html=True)
    
    # Education
    st.markdown('<p class="preview-section-title">Education</p>', unsafe_allow_html=True)
    education = st.session_state.get("education", [])
    
    if education:
        for edu in education:
            institution = edu.get("institution", "Institution")
            degree = edu.get("degree", "Degree")
            year = edu.get("year", "")
            gpa = edu.get("gpa", "")
            
            details = []
            if year:
                details.append(year)
            if gpa:
                details.append(f"GPA: {gpa}")
            
            details_str = " • ".join(details)
            
            st.markdown(f"""
                <div class="preview-card">
                    <p class="preview-card-title">{degree}</p>
                    <p class="preview-card-subtitle">{institution}{' • ' + details_str if details_str else ''}</p>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown('<div class="preview-empty">Education will appear here</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="preview-divider"></div>', unsafe_allow_html=True)
    
    # Certifications
    st.markdown('<p class="preview-section-title">Certifications</p>', unsafe_allow_html=True)
    certifications = st.session_state.get("certifications", [])
    
    if certifications:
        for cert in certifications:
            cert_name = cert.get("name", "Certification")
            issuer = cert.get("issuer", "")
            
            st.markdown(f"""
                <div class="preview-card">
                    <p class="preview-card-title">{cert_name}</p>
                    {f'<p class="preview-card-subtitle">{issuer}</p>' if issuer else ''}
                </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown('<div class="preview-empty">Certifications will appear here</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)  # Close preview-content
    st.markdown('</div>', unsafe_allow_html=True)  # Close live-preview-panel
