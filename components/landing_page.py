"""
Landing page component for Operation MOS.
"""

import streamlit as st
from pathlib import Path
import base64
import json
from datetime import datetime


def load_profile_from_json_data(data: dict) -> dict:
    """
    Parse JSON data and convert to session state format.
    
    Args:
        data: JSON data dictionary
    
    Returns:
        Dictionary with session state data
    """
    session_data = {
        "profile_data": {},
        "work_history": [],
        "education": [],
        "certifications": [],
        "volunteer_experience": [],
        "ai_summary": None,
        "mapped_skills": []
    }
    
    # Parse contact information
    contact = data.get("contact", {})
    session_data["profile_data"]["full_name"] = contact.get("full_name", "")
    session_data["profile_data"]["email"] = contact.get("email", "")
    session_data["profile_data"]["phone"] = contact.get("phone", "")
    session_data["profile_data"]["city"] = contact.get("city", "")
    session_data["profile_data"]["state"] = contact.get("state", "")
    session_data["profile_data"]["linkedin"] = contact.get("linkedin", "")
    session_data["profile_data"]["portfolio"] = contact.get("portfolio", "")
    session_data["profile_data"]["security_clearance"] = contact.get("security_clearance", "None")
    
    # Parse MOS codes
    if data.get("mos_codes") and len(data["mos_codes"]) > 0:
        mos = data["mos_codes"][0]
        session_data["profile_data"]["mos_code"] = mos.get("code", "")
        session_data["profile_data"]["mos_title"] = mos.get("title", "")
        session_data["mapped_skills"] = mos.get("civilian_skills", [])
        session_data["profile_data"]["branch"] = mos.get("branch", "Army")
    
    # Parse target role
    session_data["profile_data"]["target_role"] = data.get("target_role", "")
    
    # Parse summary
    session_data["ai_summary"] = data.get("summary", "")
    
    # Parse work history/experience
    for exp in data.get("experience", []):
        # Parse dates
        start_date = None
        end_date = None
        
        if exp.get("start_date"):
            try:
                start_date = datetime.fromisoformat(exp["start_date"]).date()
            except:
                start_date = exp.get("start_date")
        
        if exp.get("end_date"):
            try:
                end_date = datetime.fromisoformat(exp["end_date"]).date()
            except:
                end_date = exp.get("end_date")
        
        work_entry = {
            "job_title": exp.get("title", ""),
            "employer": exp.get("organization", ""),
            "location": exp.get("location", ""),
            "start_date": start_date,
            "end_date": end_date,
            "current": exp.get("current", False),
            "responsibilities": "",
            "impact": "",
            "ai_bullets": exp.get("bullets", [])
        }
        session_data["work_history"].append(work_entry)
    
    # Parse education
    for edu in data.get("education", []):
        grad_year = None
        if edu.get("graduation_year"):
            grad_year = edu["graduation_year"]
        elif edu.get("graduation_date"):
            try:
                grad_date = datetime.fromisoformat(edu["graduation_date"]).date()
                grad_year = grad_date.year
            except:
                pass
        
        edu_entry = {
            "institution": edu.get("institution", ""),
            "degree": edu.get("degree", ""),
            "year": grad_year,
            "gpa": edu.get("gpa"),
            "field_of_study": edu.get("field_of_study"),
            "overview": edu.get("overview"),
            "honors": edu.get("honors", [])
        }
        session_data["education"].append(edu_entry)
    
    # Parse skills
    skills = []
    for skill in data.get("skills", []):
        if isinstance(skill, dict):
            skills.append(skill.get("name", ""))
        else:
            skills.append(str(skill))
    
    # Merge with MOS skills
    all_skills = session_data["mapped_skills"] + [s for s in skills if s not in session_data["mapped_skills"]]
    session_data["mapped_skills"] = all_skills
    session_data["profile_data"]["core_skills"] = all_skills
    
    # Parse certifications
    for cert in data.get("certifications", []):
        cert_entry = {
            "name": cert.get("name", ""),
            "issuer": cert.get("issuer", ""),
            "year": None
        }
        if cert.get("issue_date"):
            try:
                issue_date = datetime.fromisoformat(cert["issue_date"]).date()
                cert_entry["year"] = issue_date.year
            except:
                pass
        session_data["certifications"].append(cert_entry)
    
    # Parse additional info (volunteer experience, awards, etc.)
    additional_info = data.get("additional_info", {})
    
    # Parse volunteer experience
    volunteer = additional_info.get("volunteer", [])
    for vol in volunteer:
        if isinstance(vol, str):
            # Simple string format
            session_data["volunteer_experience"].append({"description": vol})
        elif isinstance(vol, dict):
            # Structured format
            vol_entry = {
                "organization": vol.get("organization", ""),
                "role": vol.get("role", ""),
                "description": vol.get("description", ""),
                "date_range": vol.get("date_range", ""),
                "location": vol.get("location", "")
            }
            session_data["volunteer_experience"].append(vol_entry)
    
    # Parse veteran experience if present
    if additional_info.get("veteran_experience"):
        session_data["profile_data"]["veteran_experience"] = additional_info.get("veteran_experience", [])
    
    # Parse awards if present
    if additional_info.get("awards"):
        session_data["profile_data"]["awards"] = additional_info.get("awards", [])
    
    # Parse languages if present
    if additional_info.get("languages"):
        session_data["profile_data"]["languages"] = additional_info.get("languages", [])
    
    return session_data


def render_landing_page():
    """Render the branch selection landing page with JSON import option."""
    
    # Add branch card styles
    st.markdown("""
    <style>
        /* Branch card styles */
        .branch-card {{
            text-align: center;
            background: linear-gradient(135deg, rgba(26, 35, 50, 0.9) 0%, rgba(45, 62, 80, 0.8) 100%);
            border-radius: 14px;
            margin: 0.5rem;
            border: 1px solid rgba(45, 62, 80, 0.6);
            transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
            cursor: pointer;
            min-height: 250px;
            height: 100%;
            backdrop-filter: blur(10px);
            box-shadow: 0 3px 12px rgba(0,0,0,0.25);
        }}
        
        .branch-card:hover {{
            transform: translateY(-8px) scale(1.02);
            box-shadow: 0 12px 32px rgba(34, 211, 238, 0.5), 0 0 40px rgba(34, 211, 238, 0.2);
            border-color: #22d3ee;
            background: linear-gradient(135deg, rgba(34, 211, 238, 0.25) 0%, rgba(59, 130, 246, 0.2) 100%);
        }}
        
        .branch-card img {{
            width: 75%;
            height: 75%;
            object-fit: contain;
            margin: 0 auto 0.5rem auto;
            display: block;
            filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.4));
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        
        .branch-card:hover img {{
            filter: drop-shadow(0 8px 16px rgba(34, 211, 238, 0.6));
            transform: scale(1.1);
        }}
        
        .branch-name {{
            color: #ffffff;
            font-weight: 600;
            font-size: 1.1rem;
            margin-top: 0.5rem;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
        }}
        
        /* Custom Start Mission button styling */
        .start-mission-btn button {{
            background: linear-gradient(135deg, rgba(26, 35, 50, 0.9) 0%, rgba(45, 62, 80, 0.8) 100%) !important;
            border: 2px solid rgba(45, 62, 80, 0.6) !important;
            color: #ffffff !important;
            font-weight: 700 !important;
            font-size: 1.2rem !important;
            padding: 1rem 2rem !important;
            border-radius: 12px !important;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4) !important;
            transition: all 0.3s ease !important;
        }}
        
        .start-mission-btn button:hover {{
            background: linear-gradient(135deg, rgba(34, 211, 238, 0.25) 0%, rgba(59, 130, 246, 0.2) 100%) !important;
            border-color: #22d3ee !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 24px rgba(34, 211, 238, 0.6) !important;
        }}
    </style>
    """, unsafe_allow_html=True)
    
    # Main centered container for all landing page elements
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        # Hero Section - centered with minimal top spacing
        st.markdown("""
        <div style="text-align: center; margin-top: 3rem; margin-bottom: 2rem;">
            <h1 style="font-size: 3.5rem; font-weight: 800; margin-bottom: 1rem; color: #ffffff; 
                       text-shadow: 0 2px 10px rgba(34, 211, 238, 0.5); letter-spacing: -1px;">
                Turn Your Service Into Opportunity
            </h1>
            <p style="font-size: 1.3rem; color: #ffffff; margin-bottom: 2rem; font-weight: 400; line-height: 1.6;">
                Build an ATS-ready resume—fast, private, and free
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Badge tags
        st.markdown("""
        <div style="display: flex; justify-content: center; gap: 1rem; margin: 2rem 0 3rem 0;">
            <span style="background: rgba(34, 211, 238, 0.3); padding: 0.6rem 1.2rem; border-radius: 25px; 
                         color: #ffffff; font-weight: 700; font-size: 1rem; border: 2px solid rgba(34, 211, 238, 0.6);
                         box-shadow: 0 4px 12px rgba(34, 211, 238, 0.3);">✓ ATS-Ready</span>
            <span style="background: rgba(34, 211, 238, 0.3); padding: 0.6rem 1.2rem; border-radius: 25px; 
                         color: #ffffff; font-weight: 700; font-size: 1rem; border: 2px solid rgba(34, 211, 238, 0.6);
                         box-shadow: 0 4px 12px rgba(34, 211, 238, 0.3);">✓ Private</span>
            <span style="background: rgba(34, 211, 238, 0.3); padding: 0.6rem 1.2rem; border-radius: 25px; 
                         color: #ffffff; font-weight: 700; font-size: 1rem; border: 2px solid rgba(34, 211, 238, 0.6);
                         box-shadow: 0 4px 12px rgba(34, 211, 238, 0.3);">✓ No Account</span>
        </div>
        """, unsafe_allow_html=True)
    
        # Branch selection header
        st.markdown("""
        <div style="text-align: center; margin: 3rem 0 2rem 0;">
            <h2 style="color: #ffffff; font-weight: 700; font-size: 1.8rem; letter-spacing: 2px; 
                       text-transform: uppercase; text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);">
                SELECT YOUR BRANCH TO BEGIN
            </h2>
            <div style="width: 100px; height: 4px; background: linear-gradient(90deg, #22d3ee, #3b82f6); 
                        margin: 1rem auto; border-radius: 2px;"></div>
        </div>
        """, unsafe_allow_html=True)
        
        # Branch selection with actual logo images
        branches = [
            {"name": "U.S. Army", "img": "army.jpeg", "key": "Army"},
            {"name": "U.S. Navy", "img": "navy.jpeg", "key": "Navy"},
            {"name": "U.S. Marine Corps", "img": "marine-corp.jpeg", "key": "Marines"},
            {"name": "U.S. Air Force", "img": "air-force.jpeg", "key": "Air Force"},
            {"name": "U.S. Space Force", "img": "Space-force.jpeg", "key": "Space Force"},
            {"name": "U.S. Coast Guard", "img": "coast-guard.jpeg", "key": "Coast Guard"},
        ]
        
        # Render branch cards in 3 columns (display only, not clickable)
        cols = st.columns(3, gap="large")
        for idx, branch in enumerate(branches):
            with cols[idx % 3]:
                # Try to load logo image
                logo_img = ""
                try:
                    logo_path = Path(__file__).parent.parent / "Images" / branch['img']
                    if logo_path.exists():
                        with open(logo_path, "rb") as img_file:
                            encoded = base64.b64encode(img_file.read()).decode()
                            logo_img = f'<img src="data:image/jpeg;base64,{encoded}" alt="{branch["name"]}">'
                except Exception:
                    pass  # Silently skip if image not found
                
                # Display card (visual representation only)
                st.markdown(f"""
                <div class="branch-card" style="padding: 2rem 1rem;">
                    {logo_img}
                    <div class="branch-name" style="margin-top: 1rem; font-size: 1.2rem;">{branch['name']}</div>
                </div>
                """, unsafe_allow_html=True)
        
        # Start Mission button centered below the middle card
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # Create columns to center the button below the middle card
        btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 1])
        with btn_col2:
            st.markdown('<div class="start-mission-btn">', unsafe_allow_html=True)
            if st.button(
                "START MISSION", 
                use_container_width=True, 
                key="start_mission"
            ):
                st.session_state.current_step = 1
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Divider
        st.markdown("""
        <div style="text-align: center; margin: 3rem 0 2rem 0;">
            <div style="display: flex; align-items: center; justify-content: center; gap: 1rem;">
                <div style="flex: 1; height: 2px; background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);"></div>
                <span style="color: #94a3b8; font-size: 1rem; font-weight: 600;">OR</span>
                <div style="flex: 1; height: 2px; background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # JSON Import Section
        st.markdown("""
        <div style="text-align: center; margin: 2rem 0 1rem 0;">
            <h3 style="color: #ffffff; font-weight: 600; font-size: 1.3rem;">
                Import Existing Profile
            </h3>
            <p style="color: #94a3b8; font-size: 0.9rem; margin-top: 0.5rem;">
                Have a JSON profile? Upload it to generate your resume instantly
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Template download section
        col_help1, col_download, col_help2 = st.columns([1, 2, 1])
        with col_download:
            # Load the template file
            template_path = Path(__file__).parent.parent / "template.sample.json"
            if template_path.exists():
                with open(template_path, 'r') as f:
                    template_content = f.read()
                
                st.download_button(
                    label="Download JSON Template",
                    data=template_content,
                    file_name="resume_template.json",
                    mime="application/json",
                    use_container_width=True,
                    help="Download a sample JSON template to fill out with your information"
                )
            
            # Help expander
            with st.expander("ℹ️ How to use JSON template", expanded=False):
                st.markdown("""
                **Quick Guide:**
                
                1. **Download** the template above
                2. **Edit** the JSON file with your information:
                   - Replace placeholder text with your actual data
                   - Keep the field names unchanged
                   - Use quotes for text values
                3. **Upload** your completed JSON file below
                
                **Key Fields:**
                - `contact`: Your personal information
                - `target_role`: Desired job title
                - `experience`: Work history with bullet points
                - `education`: Degrees and certifications
                - `certifications`: Professional credentials
                
                **Date Format:** Use `YYYY-MM-DD` (e.g., `2020-01-15`)
                
                **Phone Format:** `(555) 123-4567` or `5551234567`
                
                **Tips:**
                - Include quantifiable achievements (numbers, percentages)
                - Use action verbs in bullet points
                - Set `current: true` for your current position
                - Set `end_date: null` if still employed
                """)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # File uploader
        uploaded_file = st.file_uploader(
            "Upload JSON Profile",
            type=['json'],
            help="Upload a JSON file with your profile data",
            label_visibility="collapsed"
        )
        
        if uploaded_file is not None:
            try:
                # Read and parse JSON
                json_data = json.load(uploaded_file)
                
                # Parse and populate session state
                session_data = load_profile_from_json_data(json_data)
                
                # Update session state
                st.session_state.profile_data = session_data["profile_data"]
                st.session_state.work_history = session_data["work_history"]
                st.session_state.education = session_data["education"]
                st.session_state.certifications = session_data["certifications"]
                st.session_state.volunteer_experience = session_data["volunteer_experience"]
                st.session_state.ai_summary = session_data["ai_summary"]
                st.session_state.mapped_skills = session_data["mapped_skills"]
                
                # Set flags
                st.session_state.json_imported = True
                st.session_state.ai_summary_generated = True if session_data["ai_summary"] else False
                
                st.success("✓ Profile loaded successfully!")
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Generate resume button
                if st.button("Generate Resume", use_container_width=True, type="primary", key="gen_resume_btn"):
                    # Skip to review step
                    st.session_state.current_step = 4
                    st.rerun()
                    
            except json.JSONDecodeError as e:
                st.error(f"Invalid JSON file: {str(e)}")
            except Exception as e:
                st.error(f"Error loading profile: {str(e)}")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Footer info
        st.markdown("""
            <p style="color: #94a3b8; font-size: 0.9rem; margin-top: 1rem; text-align: center;">
                No signup required • 100% free • Your data stays on your device
            </p>
        """, unsafe_allow_html=True)

