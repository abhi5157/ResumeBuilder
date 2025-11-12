"""
Step 4 - Resume Review & Download
Clean, professional preview with DOCX and JSON downloads using mammoth library
"""

import streamlit as st
import json
from utils.resume_preview import render_docx_preview
import datetime


def render_step_4(resume_service):
    """Render Step 4: Resume Review & Download"""
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(34, 211, 238, 0.15) 0%, rgba(59, 130, 246, 0.15) 100%); 
                border-left: 4px solid #22d3ee; 
                border-radius: 10px; 
                padding: 1rem; 
                margin: 1rem 0 2rem 0;">
        <h2 style="color: #22d3ee; margin: 0; font-size: 1.5rem;"> Step 4: Review & Download Resume</h2>
        <p style="color: #cbd5e1; margin: 0.5rem 0 0 0; font-size: 0.95rem;">
            Review your professional resume and download in your preferred format.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Download Buttons - side by side
    col1, col2, col3, col4 = st.columns([1, 2, 2, 1], gap="large")
    
    with col2:
        if st.button(" Review & Download Resume", use_container_width=False, key="download_word", type="primary"):
            try:
                if resume_service and st.session_state.profile_data:
                    with st.spinner(" Generating your professional resume..."):
                        from app import create_resume_profile_from_session
                        profile = create_resume_profile_from_session()
                        output_path = resume_service.generate_resume(profile, template_name="classic")
                        
                        st.session_state.generated_resume_path = output_path
                        st.success(" Resume generated successfully!")
                        st.rerun()
                else:
                    st.error("Resume service not available or profile data missing")
            except Exception as e:
                st.error(f" Error generating resume: {str(e)}")
                import traceback
                with st.expander(" Show error details"):
                    st.code(traceback.format_exc())
    
    with col3:
        # Custom JSON encoder to handle date objects
        class DateTimeEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, (datetime.date, datetime.datetime)):
                    return obj.isoformat()
                return super().default(obj)
        
        # Prepare JSON data
        json_data = {
            "profile_data": st.session_state.profile_data,
            "work_history": st.session_state.work_history,
            "education": st.session_state.education,
            "certifications": st.session_state.certifications,
            "volunteer_experience": st.session_state.volunteer_experience,
            "ai_summary": st.session_state.ai_summary,
            "ats_keywords": st.session_state.get('ats_keywords', []),
        }
        
        try:
            json_str = json.dumps(json_data, indent=2, cls=DateTimeEncoder)
            st.download_button(
                label="Download Profile JSON",
                data=json_str,
                file_name=f"profile_{st.session_state.profile_data.get('full_name', 'veteran').replace(' ', '_').lower()}.json",
                mime="application/json",
                use_container_width=False,
                key="download_profile_json",
            )
        except Exception as e:
            st.error(f"❌ Error generating JSON: {e}")
    
    # Show white preview if resume is generated
    if st.session_state.get('generated_resume_path'):
        try:
            # Use mammoth to render clean HTML preview
            st.markdown("---")
            st.markdown("<h3 style='text-align: center;'>Resume Preview</h3>", unsafe_allow_html=True)
            render_docx_preview(st.session_state.generated_resume_path)
            
            # Download button below preview - centered and smaller
            col_left, col_center, col_right = st.columns([1, 1, 1])
            with col_center:
                with open(st.session_state.generated_resume_path, "rb") as file:
                    st.download_button(
                        label="Download",
                        data=file,
                        file_name=f"Resume_{st.session_state.profile_data.get('full_name', 'Veteran').replace(' ', '_')}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True,
                        type="primary",
                        key="download_resume_docx_main"
                    )
            
        except Exception as e:
            st.error(f"Error previewing document: {e}")
            import traceback
            with st.expander(" Show error details"):
                st.code(traceback.format_exc())
    
    st.markdown("<div style='margin: 3rem 0;'></div>", unsafe_allow_html=True)
    
    # Navigation
    col_left, col_center, col_right = st.columns([1, 1, 1])
    with col_left:
        if st.button("← Previous Step", use_container_width=True, key="back_btn_4"):
            st.session_state.current_step = 3
            st.rerun()
    with col_center:
        if st.button(" Start Over", use_container_width=True, key="restart_btn"):
            if 'confirm_restart' not in st.session_state:
                st.session_state.confirm_restart = False
            
            if not st.session_state.confirm_restart:
                st.session_state.confirm_restart = True
                st.warning("Click again to confirm restart. All data will be reset.")
            else:
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
    with col_right:
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.2) 0%, rgba(5, 150, 105, 0.2) 100%); 
                    border: 2px solid #10b981;
                    border-radius: 8px; 
                    padding: 0.75rem; 
                    text-align: center;">
            <p style="color: #10b981; margin: 0; font-weight: 600; font-size: 0.95rem;">
                 Resume Ready
            </p>
        </div>
        """, unsafe_allow_html=True)
