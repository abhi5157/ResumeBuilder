"""
Operation MOS - Military Resume Builder
Streamlit application with military-themed UI for veterans transitioning to civilian careers.
"""

import streamlit as st
from pathlib import Path
from datetime import date, datetime
from typing import List, Optional, Dict
import json
import base64

from models import (
    Contact,
    MOS,
    WorkHistory,
    Education,
    Certification,
    AdditionalInfo,
    DocumentPreferences,
    ResumeProfile,
)

try:
    from services.mapping_service import MappingService
    from services.ai_service import SimpleAIService
    from services.resume_service import ResumeService
    from utils.config import settings
    from utils.resume_preview import render_enhanced_resume_preview
    from components.landing_page import render_landing_page
    # Use the cleaned live preview component (avoids duplicated HTML tags)
    from components.live_preview_clean import render_live_preview_panel
    from utils.validation import FieldValidator, ValidationState

    mapping_service = MappingService()
    ai_service = SimpleAIService()
    resume_service = ResumeService()
    validator = FieldValidator()

    # Silently configure AI provider - no console output

except ImportError as e:
    mapping_service = None
    ai_service = None
    resume_service = None
    settings = None
    validator = None
    # Provide safe fallbacks so the app doesn't crash with NameError when a component
    # import fails on deployment (e.g., packaging/path differences on Streamlit Cloud).
    # These fallbacks show a helpful error message in the UI and avoid AttributeErrors
    # from missing validator methods.

    def _missing_component(name, exc):
        def _f(*args, **kwargs):
            st.error(
                f"Component '{name}' failed to load. The app is partially degraded; check logs for details."
            )
            with st.expander("Debug info"):
                # Only show the exception string to aid debugging (no sensitive data expected in ImportError)
                st.write(str(exc))
            return None

        return _f

    # Fallback UI components
    render_landing_page = _missing_component("components.landing_page.render_landing_page", e)
    render_live_preview_panel = _missing_component(
        "components.live_preview_clean.render_live_preview_panel", e
    )
    render_enhanced_resume_preview = _missing_component(
        "utils.resume_preview.render_enhanced_resume_preview",
        e,
    )

    # Minimal validator stub to avoid AttributeErrors in validation calls.
    class _ValidatorStub:
        def _ok(self, *a, **k):
            return (True, "")

        validate_full_name = _ok
        validate_phone = _ok
        validate_email = _ok
        validate_linkedin = _ok
        validate_city_state = _ok
        validate_years_service = _ok
        validate_url = _ok

        def validate_date(self, value, label=None):
            return (True, "")

    validator = _ValidatorStub()
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}     /* Hides the hamburger menu */
    footer {visibility: hidden;}        /* Hides the footer */
    header {visibility: hidden;}        /* Hides the header */
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Page config
st.set_page_config(
    page_title="Operation MOS - Resume Builder",
    page_icon="🎖️",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# Minimal custom styling - primarily using Streamlit theme
def load_custom_css():
    """Load custom styling to match the UI design."""
    current_step = st.session_state.get("current_step", 0)

    # Load background image for landing page
    background_style = ""
    if current_step == 0:
        try:
            image_path = Path(__file__).parent / "Images" / "background.jpeg"
            if image_path.exists():
                with open(image_path, "rb") as image_file:
                    encoded_image = base64.b64encode(image_file.read()).decode()
                background_style = f"background-image: linear-gradient(rgba(0, 0, 0, 0.6), rgba(0, 0, 0, 0.7)), url('data:image/jpeg;base64,{encoded_image}'); background-size: cover; background-position: center; background-attachment: fixed;"
        except Exception:
            pass  # Silently skip if background image not found

    css = f"""
    <style>
        /* Global App Styling - Dark Blue/Teal Theme */
        .stApp {{
            {background_style if current_step == 0 else 'background: linear-gradient(135deg, #1a2a3a 0%, #243447 50%, #2d4a5a 100%);'}
        }}
       .block-container {{
        padding: 0 !important;
        margin: 0 !important;
    }}

    .stMainBlockContainer {{
        padding: 0 1rem !important;
        margin: 0 !important;
    }}
        
        /* Hide Streamlit branding and menu */
        #MainMenu {{visibility: hidden !important;}}
        footer {{visibility: hidden !important;}}
        header {{visibility: hidden !important;}}
        .stDeployButton {{display: none !important;}}
        
        /* Hide the default top toolbar */
        [data-testid="stToolbar"] {{
            display: none !important;
        }}
        
        /* Typography */
        h1, h2, h3 {{
            color: #ffffff !important;
        }}
        
         label, .stMarkdown, div[class*="stMarkdown"] p {{
            color: #ffffff ;
        }}
        
        /* Ensure all text elements are white on dark background */
        .stMarkdown, .stMarkdown p, .stMarkdown span, .stMarkdown div {{
            color: #ffffff ;
        }}
        
        /* Caption text should be slightly dimmer but still visible */
        .stCaption, [data-testid="stCaptionContainer"] {{
            color: #cbd5e1 ;
        }}
        
        /* Input fields styling - darker theme */
        .stTextInput input, .stTextArea textarea, .stSelectbox select, .stSelectbox [data-testid="stSelectboxDropdown"].stDateInput input {{
            background-color: #1a2332 !important;
            color: #ffffff !important;
            border: 1px solid #2d3e50 !important;
            border-radius: 6px !important;
            padding: 0.4rem 0.6rem !important; /* Reduced padding for more compact inputs */
            font-size: 0.8rem !important; /* Smaller font size */
            line-height: 1.1rem !important;
            transition: all 0.25s ease !important;
            width: 100% !important;
            box-sizing: border-box !important;
        }}
        
        /* Remove extra spacing from input containers */
        .stTextInput, .stTextArea, .stSelectbox, .stDateInput {{
            margin-bottom: 0.5rem !important;
            width: 100% !important;
        }}
        
        .stTextInput > div, .stSelectbox > div, .stTextArea > div, .stDateInput > div {{
            gap: 0 !important;
            width: 100% !important;
        }}
        
        .stTextInput > label, .stTextArea > label, .stSelectbox > label, .stDateInput > label {{
            margin-bottom: 0.25rem !important;
            padding-bottom: 0 !important;
            width: 100% !important;
        }}
        
        .stTextInput input:focus, .stTextArea textarea:focus, .stSelectbox select:focus, .stDateInput input:focus {{
            border-color: #22d3ee !important;
            box-shadow: 0 0 0 2px rgba(34, 211, 238, 0.2) !important;
            background-color: #0f1923 !important;
        }}
        /* Make inputs slightly shorter visually */
        .stTextInput input, .stDateInput input {{ height: 38px !important; }}
        
        /* Error state styling for invalid fields */
        .stTextInput.error input, .stTextArea.error textarea, .stSelectbox.error select, .stDateInput.error input {{
            border-color: #ef4444 !important;
            box-shadow: 0 0 0 2px rgba(239, 68, 68, 0.2) !important;
        }}
        
        .stTextInput.error input:focus, .stTextArea.error textarea:focus, .stSelectbox.error select:focus, .stDateInput.error input:focus {{
            border-color: #dc2626 !important;
            box-shadow: 0 0 0 2px rgba(220, 38, 38, 0.3) !important;
        }}
        
        /* Error message styling */
        .error-message {{
            color: #fca5a5 !important;
            font-size: 0.75rem !important;
            margin-top: 0.25rem !important;
            margin-bottom: 0.5rem !important;
            font-weight: 500 !important;
        }}
        
        
        /* Selectbox specific styling */
        .stSelectbox > div > div {{
            background-color: #1a2332 !important;
            color: #ffffff !important;
            border: 1px solid #2d3e50 !important;
            border-radius: 8px !important;
        }}
        
        .stSelectbox > div > div:hover {{
            border-color: #22d3ee !important;
            background-color: #1a2332 !important;
        }}
        
        .stSelectbox [data-baseweb="select"] {{
            background-color: #1a2332 !important;
        }}
        
        .stSelectbox [data-baseweb="select"] > div {{
            background-color: #1a2332 !important;
            color: #ffffff !important;
            border-color: #2d3e50 !important;
        }}
        
        /* Selectbox dropdown menu */
        .stSelectbox [role="listbox"] {{
            background-color: #1a2332 !important;
            border: 1px solid #2d3e50 !important;
            border-radius: 8px !important;
        }}
        
        .stSelectbox [role="option"] {{
            background-color: #1a2332 !important;
            color: #ffffff !important;
        }}
        
        .stSelectbox [role="option"]:hover {{
            background-color: #2d3e50 !important;
            color: #22d3ee !important;
        }}
        
        .stSelectbox select option {{
            background-color: #1a2332 !important;
            color: #ffffff !important;
        }}
        
        /* Remove white tooltip/popup on hover */
        .stSelectbox [data-baseweb="popover"] {{
            background-color: transparent !important;
        }}
        
        .stSelectbox [data-baseweb="tooltip"] {{
            display: none !important;
        }}
        
        .stTextInput input::placeholder, .stTextArea textarea::placeholder {{
            color: #64748b !important;
        }}
        
        /* Input labels */
        .stTextInput label, .stTextArea label, .stSelectbox label, .stDateInput label {{
            color: #cbd5e1 !important;
            font-weight: 500 !important;
            margin-bottom: 0.5rem !important;
        }}
        
        /* Button styling */
        .stButton button, .stButton > button {{
            background-color: #1a2332 !important;
            background: #1a2332 !important;
            color: #ffffff !important;
            border: 1px solid #2d3e50 !important;
                border-radius: 6px !important;
                font-weight: 500 !important;
                padding: 0.5rem 0.9rem !important;
                font-size: 0.9rem !important;
                transition: all 0.25s ease !important;
                max-width: 300px !important;
        }}
        
        .stButton button:hover, .stButton > button:hover,
        .stButton button:focus, .stButton > button:focus,
        .stButton button:active, .stButton > button:active {{
            background-color: #2d3e50 !important;
            background: #2d3e50 !important;
            border-color: #22d3ee !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 4px 12px rgba(34, 211, 238, 0.3) !important;
            color: #ffffff !important;
            outline: none !important;
        }}
        
        .stButton button[kind="primary"] {{
            background: linear-gradient(135deg, #1E3A8A 0%, #1e40af 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 10px !important;
            font-weight: 600 !important;
            font-size: 1rem !important;
            padding: 0.75rem 1.5rem !important;
            box-shadow: 0 4px 14px rgba(30, 58, 138, 0.4) !important;
            max-width: 300px !important;
        }}
        
        .stButton button[kind="primary"]:hover {{
            background: linear-gradient(135deg, #1e40af 0%, #2563eb 100%) !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 20px rgba(37, 99, 235, 0.5) !important;
        }}
        
        /* Expander styling */
        .streamlit-expanderHeader,
        [data-testid="stExpander"] > div:first-child,
        [data-testid="stExpanderToggleIcon"],
        div[data-testid="stExpander"] summary {{
            background: linear-gradient(135deg, rgba(26, 35, 50, 0.8) 0%, rgba(45, 62, 80, 0.6) 100%) !important;
            color: #ffffff !important;
            border-radius: 8px !important;
            border: 1px solid #2d3e50 !important;
            font-weight: 600 !important;
            padding: 1rem !important;
            transition: all 0.3s ease !important;
        }}
        
        .streamlit-expanderHeader:hover,
        [data-testid="stExpander"] > div:first-child:hover,
        div[data-testid="stExpander"] summary:hover {{
            background: linear-gradient(135deg, rgba(34, 211, 238, 0.2) 0%, rgba(59, 130, 246, 0.2) 100%) !important;
            border-color: #22d3ee !important;
        }}
        
        .streamlit-expanderContent,
        [data-testid="stExpander"] > div:last-child,
        div[data-testid="stExpander"] > div {{
            background-color: rgba(15, 25, 35, 0.8) !important;
            border: 1px solid #2d3e50 !important;
            border-radius: 0 0 8px 8px !important;
            padding: 1.5rem !important;
        }}
        
        /* Override all white backgrounds */
        details[open],
        details summary,
        .st-emotion-cache-uf99v8,
        .st-emotion-cache-16idsys,
        .element-container,
        [data-testid="stExpanderDetails"] {{
            background-color: transparent !important;
            background: transparent !important;
        }}
        
        /* Ensure expander content area has dark background */
        details[open] > div:not(summary),
        [data-testid="stExpanderDetails"] > div {{
            background-color: rgba(15, 25, 35, 0.8) !important;
            border: 1px solid #2d3e50 !important;
            border-radius: 0 0 8px 8px !important;
            padding: 1.5rem !important;
        }}
        
        /* Info/Success/Warning boxes */
        .stAlert {{
            background-color: rgba(26, 35, 50, 0.8) !important;
            border-radius: 8px !important;
            border-left: 4px solid !important;
            animation: slideIn 0.3s ease-out !important;
            color: #ffffff !important;
        }}
        
        .stAlert p {{
            color: #ffffff !important;
        }}
        
        @keyframes slideIn {{
            from {{
                opacity: 0;
                transform: translateX(-20px);
            }}
            to {{
                opacity: 1;
                transform: translateX(0);
            }}
        }}
        
        /* Container animations */
        [data-testid="stContainer"] {{
            background-color: rgba(26, 35, 50, 0.5) !important;
            border-radius: 12px !important;
            padding: 1rem !important;
            animation: fadeIn 0.4s ease-in !important;
        }}
        
        @keyframes fadeIn {{
            from {{
                opacity: 0;
            }}
            to {{
                opacity: 1;
            }}
        }}
        
        /* Divider */
        hr {{
            border-color: #2d3e50 !important;
            margin: 1.5rem 0 !important;
        }}
        
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
            width: 50%;
            height: 50%;
            object-fit: contain;
            margin: 0 auto 1rem auto;
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
        
        /* Skill tags */
        .skill-tag {{
            display: inline-block;
            padding: 0.5rem 1rem;
            background: linear-gradient(135deg, rgba(34, 211, 238, 0.2) 0%, rgba(59, 130, 246, 0.2) 100%);
            border: 1px solid rgba(34, 211, 238, 0.5);
            border-radius: 20px;
            color: #67e8f9;
            font-size: 0.85rem;
            margin: 0.25rem;
            font-weight: 500;
            transition: all 0.3s ease;
            cursor: pointer;
        }}
        
        .skill-tag:hover {{
            background: linear-gradient(135deg, rgba(34, 211, 238, 0.3) 0%, rgba(59, 130, 246, 0.3) 100%);
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(34, 211, 238, 0.3);
        }}
        
        .preview-badge {{
            display: inline-block;
            padding: 0.4rem 1rem;
            background: linear-gradient(135deg, rgba(234, 179, 8, 0.3) 0%, rgba(249, 115, 22, 0.2) 100%);
            border: 1px solid rgba(234, 179, 8, 0.6);
            border-radius: 20px;
            color: #fde047;
            font-size: 0.85rem;
            margin: 0.25rem;
            font-weight: 600;
            box-shadow: 0 2px 8px rgba(234, 179, 8, 0.2);
        }}
        
        /* Live Preview Box */
        .live-preview-container {{
            background: rgba(0, 0, 0, 0.92) !important;
            border: 2px solid rgba(34, 211, 238, 0.35) !important;
            border-radius: 16px !important;
            padding: 2rem 1.75rem 1.75rem 1.75rem !important; /* Added more inner padding so name/contact are visible */
            box-shadow: 0 10px 36px rgba(0, 0, 0, 0.45) !important;
            position: relative;
            z-index: 5;
        }}
        
        .live-preview-container .element-container {{
            background: transparent !important;
        }}
        
        /* Progress bar */
        .stProgress > div > div {{
            background-color: #22d3ee !important;
        }}
        
        .stProgress > div {{
            background-color: rgba(45, 62, 80, 0.5) !important;
            border-radius: 10px !important;
            overflow: hidden !important;
        }}
        
        /* Back button at top */
        .back-button-top {{
            position: absolute;
            top: 1rem;
            left: 1rem;
            z-index: 100;
        }}
        
        .back-button-top button {{
            background: transparent !important;
            border: none !important;
            color: #22d3ee !important;
            font-size: 1.5rem !important;
            padding: 0.5rem !important;
            cursor: pointer;
        }}
        
        .back-button-top button:hover {{
            color: #06b6d4 !important;
        }}
        
        /* Metrics */
        [data-testid="stMetricValue"] {{
            color: #22d3ee !important;
            font-weight: 700 !important;
            font-size: 1.8rem !important;
        }}
        
        [data-testid="stMetricLabel"] {{
            color: #cbd5e1 !important;
            font-weight: 500 !important;
        }}
        
        /* Info/Success/Warning boxes */
        .stAlert {{
            background-color: rgba(26, 35, 50, 0.8) !important;
            border-radius: 6px !important;
            color: #ffffff !important;
        }}
        
        /* Divider */
        hr {{
            border-color: #2d3e50 !important;
        }}
        
        /* Form submit button styling */
        .stForm button,
        .stForm button:hover,
        .stForm button:active,
        .stForm button:focus {{
            background-color: #1a2332 !important;
            background: linear-gradient(135deg, #1a2332 0%, #2d3e50 100%) !important;
            color: #ffffff !important;
            border: 1px solid #2d3e50 !important;
            border-radius: 8px !important;
            font-weight: 500 !important;
            padding: 0.6rem 1.2rem !important;
            transition: all 0.3s ease !important;
        }}

        .stForm button:hover {{
            background: linear-gradient(135deg, #2d3e50 0%, #384860 100%) !important;
            border-color: #22d3ee !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 4px 12px rgba(34, 211, 238, 0.3) !important;
        }}
        
        /* Yellow download button */
        .yellow-button button {{
            background-color: #eab308 !important;
            border-color: #eab308 !important;
            color: #0f172a !important;
            font-weight: 600 !important;
        }}
        
        .yellow-button button:hover {{
            background-color: #ca8a04 !important;
        }}
        
        /* Cyan download button */
        .cyan-button button {{
            background-color: #22d3ee !important;
            border-color: #22d3ee !important;
            color: #0f172a !important;
            font-weight: 600 !important;
        }}
        
        .cyan-button button:hover {{
            background-color: #06b6d4 !important;
        }}
        
        /* Global white background override - catch all */
        div[data-testid="stVerticalBlock"] > div,
        div[data-testid="column"] > div,
        .stMarkdown,
        section[data-testid="stSidebar"],
        [data-baseweb="tab-panel"],
        [role="tabpanel"] {{
            background-color: transparent !important;
        }}
        
        /* Ensure no white backgrounds anywhere */
        * {{
            scrollbar-color: #2d3e50 #1a2332;
        }}
        
        *::-webkit-scrollbar {{
            width: 10px;
            height: 10px;
        }}
        
        *::-webkit-scrollbar-track {{
            background: #1a2332;
        }}
        
        *::-webkit-scrollbar-thumb {{
            background: #2d3e50;
            border-radius: 5px;
        }}
        
        *::-webkit-scrollbar-thumb:hover {{
            background: #22d3ee;
        }}
        
        /* Responsive adjustments */
        @media (max-width: 768px) {{
            .branch-card {{
                # padding: 1rem 0.5rem;
            }}
            .branch-card img {{
                width: 80px;
                height: 80px;
            }}
            .stTextInput input, .stTextArea textarea, .stSelectbox select, .stDateInput input {{
                padding: 0.5rem 0.6rem !important;
                font-size: 0.85rem !important;
            }}
            .stButton button {{
                padding: 0.45rem 0.7rem !important;
                font-size: 0.85rem !important;
            }}
            /* Stack columns on mobile for better readability */
            [data-testid="column"] {{ flex: 1 1 100% !important; max-width: 100% !important; }}
        }}
        
        @media (min-width: 1200px) {{
            /* Narrow primary form column across large screens */
            [data-testid="column"]:first-child {{
                flex: 0 0 640px !important;
                max-width: 640px !important;
            }}
            [data-testid="column"]:nth-child(2) {{
                flex: 1 1 auto !important;
            }}
            .stForm {{
                max-width: 760px !important;
                margin-left: 0 !important;
                margin-right: auto !important;
            }}
        }}
        /* General column tightening for desktop (except when stacked on mobile) */
        @media (min-width: 900px) and (max-width: 1199px) {{
            [data-testid="column"]:first-child {{
                flex: 0 0 58% !important;
                max-width: 58% !important;
            }}
            [data-testid="column"]:nth-child(2) {{
                flex: 0 0 42% !important;
                max-width: 42% !important;
            }}
        }}
        /* Ensure preview content doesn't clip header/name */
        .preview-wrapper, .live-preview-container {{
            overflow: visible !important;
        }}
        .preview-header, .preview-contact-sticky {{
            position: relative;
            z-index: 10;
        }}
        .preview-contact-sticky {{
            padding-top: 1.25rem !important;
        }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


# Add Operation MOS branding at the top
def render_header():
    """Render the Operation MOS header."""
    st.markdown(
        """
    <div style="
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    background-color: rgba(0, 0, 0, 0.7); 
    padding: 0.75rem 1rem;
    text-align: left;
    z-index: 9999;
">
    <h1 style="
        color: #ffffff;
        margin: 0;
        padding: 0;
        font-weight: 700;
        font-size: 2.5rem;
        letter-spacing: 1px;
    ">
        OPERATION MOS
    </h1>
</div>
    """,
        unsafe_allow_html=True,
    )


def initialize_session_state():
    """Initialize session state variables."""
    defaults = {
        "current_step": 0,
        "selected_branch": None,
        "profile_data": {},
        "ai_summary": None,
        "work_history": [],
        "education": [],
        "certifications": [],
        "volunteer_experience": [],
        "mos_skills": [],
        "regenerate_summary": False,
        "summary_version": 0,
        "validation_errors": {},  # Store field-level validation errors
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def validated_text_input(
    label: str,
    field_name: str,
    validator_func,
    value: str = "",
    placeholder: str = "",
    key: str = None,
    required: bool = True,
    **kwargs,
):
    """
    Render a text input with real-time validation and error display.

    Args:
        label: Input label
        field_name: Field name for storage
        validator_func: Validation function that returns (is_valid, error_message)
        value: Current value
        placeholder: Placeholder text
        key: Streamlit key
        required: Whether field is required
        **kwargs: Additional st.text_input parameters

    Returns:
        Input value
    """

    # Auto-save callback
    def on_change():
        new_value = st.session_state[key]
        st.session_state.profile_data[field_name] = new_value

        # Validate and store error
        is_valid, error_msg = validator_func(new_value)
        if not is_valid:
            st.session_state.validation_errors[field_name] = error_msg
        elif field_name in st.session_state.validation_errors:
            del st.session_state.validation_errors[field_name]

    # Get current error
    error_msg = st.session_state.validation_errors.get(field_name)
    has_error = error_msg is not None

    # Render input with error styling
    input_value = st.text_input(
        label,
        value=value,
        placeholder=placeholder,
        key=key,
        on_change=on_change,
        help=error_msg if has_error else kwargs.get("help"),
        **{k: v for k, v in kwargs.items() if k != "help"},
    )

    # Display error message below field
    if has_error:
        st.markdown(f'<p class="error-message">{error_msg}</p>', unsafe_allow_html=True)

    return input_value


def validated_selectbox(
    label: str, field_name: str, options: list, value=None, key: str = None, **kwargs
):
    """
    Render a selectbox with auto-save.

    Args:
        label: Input label
        field_name: Field name for storage
        options: List of options
        value: Current value
        key: Streamlit key
        **kwargs: Additional st.selectbox parameters

    Returns:
        Selected value
    """

    # Auto-save callback
    def on_change():
        new_value = st.session_state[key]
        st.session_state.profile_data[field_name] = new_value

    # Find index of current value
    index = 0
    if value and value in options:
        index = options.index(value)

    # Render selectbox
    selected = st.selectbox(
        label, options=options, index=index, key=key, on_change=on_change, **kwargs
    )

    return selected


def validated_date_input(label: str, field_name: str, value=None, key: str = None, **kwargs):
    """
    Render a date input with auto-save and validation.

    Args:
        label: Input label
        field_name: Field name for storage
        value: Current value
        key: Streamlit key
        **kwargs: Additional st.date_input parameters

    Returns:
        Date value
    """

    # Auto-save callback
    def on_change():
        new_value = st.session_state[key]
        st.session_state.profile_data[field_name] = new_value

        # Validate date
        is_valid, error_msg = validator.validate_date(new_value, label)
        if not is_valid:
            st.session_state.validation_errors[field_name] = error_msg
        elif field_name in st.session_state.validation_errors:
            del st.session_state.validation_errors[field_name]

    # Get current error
    error_msg = st.session_state.validation_errors.get(field_name)
    has_error = error_msg is not None

    # Render date input
    date_value = st.date_input(
        label,
        value=value,
        key=key,
        on_change=on_change,
        help=error_msg if has_error else kwargs.get("help"),
        **{k: v for k, v in kwargs.items() if k != "help"},
    )

    # Display error message below field
    if has_error:
        st.markdown(f'<p class="error-message">{error_msg}</p>', unsafe_allow_html=True)

    return date_value


def render_progress_bar():
    """Render progress bar using Streamlit native progress - 100% width, centered like preview."""
    steps = ["Contact & Profile", "Work History", "Education & Certs", "Review & Export"]
    current = st.session_state.current_step - 1

    # Handle intermediate steps 1.5 and 1.6
    if st.session_state.current_step == 1.5:
        current = 0.33  # MOS Translation
    elif st.session_state.current_step == 1.6:
        current = 0.66  # Professional Summary

    progress_pct = ((current + 1) / len(steps)) if current >= 0 else 0

    # Centered container with 50% width
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        # Container styled like live preview

        # Step indicators with numbers
        st.markdown(
            """
        <div style="margin-bottom: 1.5rem;">
            <div style="display: flex; background: rgba(15, 25, 35, 0.9); padding: 1rem; border-radius: 10px; margin-top: 1rem; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);">
                {}
            </div>
        </div>
        """.format(
                "".join(
                    [
                        f"""<div style="flex: 1; text-align: center;">
                    <div style="background: {'#22d3ee' if i <= current else '#2d3e50'}; 
                                color: {'#0f172a' if i <= current else '#9ca3af'}; 
                                width: 36px; 
                                height: 36px; 
                                border-radius: 50%; 
                                display: inline-flex; 
                                align-items: center; 
                                justify-content: center;
                                font-weight: 700;
                                font-size: 1rem;
                                margin-bottom: 0.5rem;
                                border: 2px solid {'#22d3ee' if i <= current else '#2d3e50'};
                                box-shadow: {'0 0 10px rgba(34, 211, 238, 0.5)' if i == current else 'none'};
                                transition: all 0.3s ease;">
                        {i + 1}
                    </div>
                    <div style="font-size: 0.7rem; color: {'#ffffff' if i <= current else '#64748b'}; font-weight: {'600' if i <= current else '400'}; line-height: 1.2;">
                        {step}
                    </div>
                </div>"""
                        for i, step in enumerate(steps)
                    ]
                )
            ),
            unsafe_allow_html=True,
        )

        # Progress bar with percentage
        progress_text = f"{int(progress_pct * 100)}% MISSION COMPLETE"
        st.markdown(
            f"""
        <div style="text-align: center; margin-bottom: 0.5rem;">
            <p style="color: #cbd5e1; font-size: 0.875rem; font-weight: 600; letter-spacing: 0.5px;">{progress_text}</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

        st.progress(progress_pct)

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)


def validate_contact_form() -> tuple[bool, list[str]]:
    """
    Validate the contact form data using Pydantic models.

    Returns:
        Tuple of (is_valid, list of error messages)
    """
    from models import Contact
    from pydantic import ValidationError

    errors = []

    # Helper function to clean URL
    def clean_url(url_value):
        if not url_value or url_value.strip() == "":
            return None
        return url_value.strip()

    # Try to create a Contact object to validate all fields at once
    try:
        contact = Contact(
            full_name=st.session_state.profile_data.get("full_name", ""),
            email=st.session_state.profile_data.get("email", ""),
            phone=st.session_state.profile_data.get("phone", ""),
            city=st.session_state.profile_data.get("city", ""),
            state=st.session_state.profile_data.get("state", ""),
            linkedin=clean_url(st.session_state.profile_data.get("linkedin")),
            portfolio=clean_url(st.session_state.profile_data.get("portfolio")),
            security_clearance=st.session_state.profile_data.get("security_clearance", "None"),
        )
    except ValidationError as e:
        for error in e.errors():
            field = error["loc"][0] if error["loc"] else "unknown"
            msg = error["msg"]

            # Convert field names to user-friendly names
            field_names = {
                "full_name": "Full Name",
                "email": "Email",
                "phone": "Phone",
                "city": "City",
                "state": "State",
                "linkedin": "LinkedIn",
                "portfolio": "Portfolio",
            }

            friendly_field = field_names.get(field, field)
            errors.append(f"{friendly_field}: {msg}")

    # Additional business logic validation
    years_service = st.session_state.profile_data.get("years_of_service", "") or ""
    if isinstance(years_service, str):
        years_service = years_service.strip()
    else:
        years_service = str(years_service) if years_service else ""

    if not years_service:
        errors.append("Years of Service is required")

    return (len(errors) == 0, errors)


def validate_work_history_entry(role_data: dict) -> tuple[bool, list[str]]:
    """Validate a single work history entry using Pydantic."""
    from models import WorkHistory
    from pydantic import ValidationError
    from datetime import datetime

    errors = []

    # Helper function to parse dates
    def parse_date(date_str):
        if not date_str or date_str.strip().lower() in ["present", "current", ""]:
            return None
        try:
            date_str = date_str.strip()
            if "/" in date_str:
                month, year = date_str.split("/")
            elif "-" in date_str:
                month, year = date_str.split("-")
            else:
                return datetime(int(date_str), 1, 1).date()
            return datetime(int(year), int(month), 1).date()
        except:
            return datetime.now().replace(month=1, day=1).date()

    # Validate required fields first
    if not role_data.get("job_title", "").strip():
        errors.append("Job Title is required")
    if not role_data.get("employer", "").strip():
        errors.append("Employer is required")
    if not role_data.get("start_date"):
        errors.append("Start Date is required")

    if errors:
        return (False, errors)

    # Try to create WorkHistory object
    try:
        # Handle date objects from st.date_input
        start_date = role_data.get("start_date")
        end_date = role_data.get("end_date")

        # For validation purposes, convert date objects to strings if needed
        start_date_str = str(start_date) if start_date else ""
        end_date_str = str(end_date) if end_date else ""

        # Check if end date indicates current position
        is_current = end_date is None or end_date_str.lower() in ["present", "current"]

        work_history = WorkHistory(
            title=role_data.get("job_title", ""),
            organization=role_data.get("employer", ""),
            location=role_data.get("location", ""),
            start_date=start_date or datetime.now().replace(year=2020, month=1, day=1).date(),
            end_date=end_date,
            current=is_current,
            bullets=role_data.get("ai_bullets", []),
            ai_generated_bullets=role_data.get("ai_bullets", []),
            scope_metrics=role_data.get("impact", ""),
        )
    except ValidationError as e:
        for error in e.errors():
            field = error["loc"][0] if error["loc"] else "unknown"
            msg = error["msg"]
            errors.append(f"{field}: {msg}")

    return (len(errors) == 0, errors)


def validate_education_entry(edu_data: dict) -> tuple[bool, list[str]]:
    """Validate a single education entry using Pydantic."""
    from models import Education
    from pydantic import ValidationError

    errors = []

    # Validate required fields
    if not edu_data.get("institution", "").strip():
        errors.append("Institution is required")
    if not edu_data.get("degree", "").strip():
        errors.append("Degree/Program is required")

    if errors:
        return (False, errors)

    # Helper function to convert GPA
    def convert_gpa(gpa_value):
        if gpa_value is None or gpa_value == "" or str(gpa_value).strip() == "":
            return None
        try:
            gpa = float(str(gpa_value).strip())
            if gpa <= 4.0:
                return round(gpa, 2)
            elif gpa <= 10.0:
                return round((gpa / 10.0) * 4.0, 2)
            elif gpa <= 100.0:
                return round((gpa / 100.0) * 4.0, 2)
            else:
                return 4.0
        except (ValueError, TypeError):
            return None

    # Helper function to convert year
    def convert_year(year_value):
        if year_value is None or year_value == "" or str(year_value).strip() == "":
            return None
        try:
            return int(str(year_value).strip())
        except (ValueError, TypeError):
            return None

    # Try to create Education object
    try:
        education = Education(
            institution=edu_data.get("institution", ""),
            degree=edu_data.get("degree", ""),
            graduation_year=convert_year(edu_data.get("year")),
            gpa=convert_gpa(edu_data.get("gpa")),
        )
    except ValidationError as e:
        for error in e.errors():
            field = error["loc"][0] if error["loc"] else "unknown"
            msg = error["msg"]
            errors.append(f"{field}: {msg}")

    return (len(errors) == 0, errors)


def render_step_1_contact():
    """Step 1: Contact & Profile - Comprehensive version with all fields."""
    # Back button at top
    if st.button("← ", key="back_top_1", help="Back"):
        st.session_state.current_step = 0
        st.rerun()

    st.markdown(
        """
    <h1 style="color: #ffffff; font-size: 2rem; margin-bottom: 0.5rem;">Build Your Résumé</h1>
    """,
        unsafe_allow_html=True,
    )


    col_form, col_gap, col_preview = st.columns([1, 0.1, 1])

    with col_form:
        # Add padding container for the form
        st.markdown("""
        <div style="padding: 1.5rem; background: rgba(26, 35, 50, 0.3); border-radius: 12px; margin-bottom: 1rem;">
        """, unsafe_allow_html=True)
        st.markdown(
            """
        <h2 style="color: #ffffff; font-size: 1.5rem; margin-bottom: 1rem;">Step 1 – Contact & Profile</h2>
        """,
            unsafe_allow_html=True,
        )

        # ===== CONTACT INFORMATION =====
        st.markdown("### Contact Information")
        # Row 1: Full Name | Phone
        col1, col2 = st.columns(2)
        with col1:
            current_full_name = st.session_state.profile_data.get("full_name", "")
            validated_text_input(
                "Full Name *",
                "full_name",
                validator.validate_full_name,
                value=current_full_name,
                placeholder="Andrew Shea",
                key="full_name_input",
            )
        with col2:
            current_phone = st.session_state.profile_data.get("phone", "")
            validated_text_input(
                "Phone *",
                "phone",
                validator.validate_phone,
                value=current_phone,
                placeholder="9632587410",
                key="phone_input",
            )
        # Row 2: Email | LinkedIn
        col1, col2 = st.columns(2)
        with col1:
            current_email = st.session_state.profile_data.get("email", "")
            validated_text_input(
                "Email *",
                "email",
                validator.validate_email,
                value=current_email,
                placeholder="andrew.shea@email.com",
                key="email_input",
            )
        with col2:
            current_linkedin = st.session_state.profile_data.get("linkedin", "")
            validated_text_input(
                "LinkedIn (optional)",
                "linkedin",
                validator.validate_linkedin,
                value=current_linkedin,
                placeholder="linkedin.com/in/andrewshea",
                key="linkedin_input",
                required=False,
            )
        # Row 3: City/State | Portfolio
        col1, col2 = st.columns(2)
        with col1:
            current_city = st.session_state.profile_data.get("city", "")
            current_state = st.session_state.profile_data.get("state", "")
            current_city_state = f"{current_city}, {current_state}".strip(", ")
            def on_city_state_change():
                city_state = st.session_state["location_input"]
                if city_state.strip():
                    city_state_clean = city_state.strip()
                    if "," in city_state_clean:
                        parts = [p.strip() for p in city_state_clean.split(",") if p.strip()]
                        if len(parts) >= 2:
                            st.session_state.profile_data["city"] = parts[0]
                            st.session_state.profile_data["state"] = parts[1]
                        elif len(parts) == 1:
                            st.session_state.profile_data["city"] = parts[0]
                            st.session_state.profile_data["state"] = ""
                    elif " " in city_state_clean:
                        parts = city_state_clean.split()
                        if len(parts) >= 2:
                            st.session_state.profile_data["city"] = " ".join(parts[:-1])
                            st.session_state.profile_data["state"] = parts[-1]
                        else:
                            st.session_state.profile_data["city"] = parts[0]
                            st.session_state.profile_data["state"] = ""
                    else:
                        st.session_state.profile_data["city"] = city_state_clean
                        st.session_state.profile_data["state"] = ""
                else:
                    st.session_state.profile_data["city"] = ""
                    st.session_state.profile_data["state"] = ""
                is_valid, error_msg = validator.validate_city_state(city_state)
                if not is_valid:
                    st.session_state.validation_errors["city_state"] = error_msg
                elif "city_state" in st.session_state.validation_errors:
                    del st.session_state.validation_errors["city_state"]
            error_msg = st.session_state.validation_errors.get("city_state")
            st.text_input(
                "City, State (State optional)",
                value=current_city_state,
                placeholder="Norfolk, VA",
                key="location_input",
                on_change=on_city_state_change,
                help=error_msg,
            )
            if error_msg:
                st.markdown(f'<p class="error-message">❌ {error_msg}</p>', unsafe_allow_html=True)
        with col2:
            current_portfolio = st.session_state.profile_data.get("portfolio", "")
            validated_text_input(
                "Portfolio / Website (optional)",
                "portfolio",
                validator.validate_url,
                value=current_portfolio,
                placeholder="www.andrewshea.dev",
                key="portfolio_input",
                required=False,
            )
        # Privacy reassurance note
        st.markdown(
            "<p style='color:#64748b;font-size:0.7rem;margin-top:0.25rem;'>Your contact details stay in this browser session and are never shared externally unless you choose AI generation features.</p>",
            unsafe_allow_html=True,
        )
        st.markdown("<br>", unsafe_allow_html=True)

        # ===== SERVICE DETAILS =====
        st.markdown("### Service Details")

        col1, col2 = st.columns(2)
        with col1:
            branch_options = [
                "Army",
                "Navy",
                "Marine Corps",
                "Air Force",
                "Space Force",
                "Coast Guard",
            ]
            # Map display names to valid model names
            branch_map = {
                "Marine Corps": "Marines",
                "Army": "Army",
                "Navy": "Navy",
                "Air Force": "Air Force",
                "Space Force": "Space Force",
                "Coast Guard": "Coast Guard",
            }

            # Auto-save callback for branch
            def on_branch_change():
                selected_branch = st.session_state["branch_select"]
                st.session_state.selected_branch = branch_map.get(selected_branch, selected_branch)
                st.session_state.profile_data["branch"] = st.session_state.selected_branch

            # Find current value for reverse mapping
            current_branch_display = st.session_state.selected_branch
            for display_name, model_name in branch_map.items():
                if model_name == st.session_state.selected_branch:
                    current_branch_display = display_name
                    break

            st.selectbox(
                "Branch *",
                options=branch_options,
                index=(
                    branch_options.index(current_branch_display)
                    if current_branch_display in branch_options
                    else 0
                ),
                key="branch_select",
                on_change=on_branch_change,
            )

        with col2:
            current_years_service = st.session_state.profile_data.get("years_of_service", "") or ""
            if not isinstance(current_years_service, str):
                current_years_service = str(current_years_service)

            validated_text_input(
                "Years of Service *",
                "years_of_service",
                validator.validate_years_service,
                value=current_years_service,
                placeholder="e.g., 4 years or 2015-2019",
                key="years_service_input",
            )

        # Service Details (continued)
        col1, col2 = st.columns(2)
        with col1:
            current_last_duty = st.session_state.profile_data.get("last_duty_title", "")

            def on_last_duty_change():
                st.session_state.profile_data["last_duty_title"] = st.session_state[
                    "last_duty_input"
                ]

            st.text_input(
                "Last Duty Title (optional)",
                value=current_last_duty,
                placeholder="e.g., Squad Leader, Platoon Sergeant",
                key="last_duty_input",
                on_change=on_last_duty_change,
            )

        with col2:
            current_deployments = st.session_state.profile_data.get("deployments", "")

            def on_deployments_change():
                st.session_state.profile_data["deployments"] = st.session_state["deployments_input"]

            st.text_input(
                "Deployments/Locations (optional)",
                value=current_deployments,
                placeholder="e.g., Iraq 2018, Afghanistan 2019",
                key="deployments_input",
                on_change=on_deployments_change,
            )

        st.markdown("<br>", unsafe_allow_html=True)

        # ===== SECURITY CLEARANCE =====
        st.markdown("### Security Clearance")

        col1, col2 = st.columns(2)
        with col1:
            validated_selectbox(
                "Security Clearance *",
                "security_clearance",
                options=["None", "Public Trust", "Secret", "TS", "TS/SCI"],
                value=st.session_state.profile_data.get("security_clearance", "None"),
                key="clearance_select",
            )

        st.markdown("<br>", unsafe_allow_html=True)

    

        # Navigation
        st.markdown("<br><br>", unsafe_allow_html=True)

        # Show validation status
        has_validation_errors = len(st.session_state.validation_errors) > 0
        if has_validation_errors:
            st.warning(
                f"Please fix {len(st.session_state.validation_errors)} validation error(s) before continuing"
            )

        # Check if all required fields are filled
        is_valid, validation_errors = validate_contact_form()

        col1, col2 = st.columns(2)
        with col1:
            st.info("All changes are saved automatically")
        with col2:
            if st.button(
                "Continue to MOS Translation →",
                use_container_width=True,
                type="primary",
                disabled=not is_valid or has_validation_errors,
            ):
                st.session_state.current_step = 1.5  # Go to MOS Translation step
                st.rerun()

        # Close the padding container div
        st.markdown("</div>", unsafe_allow_html=True)

    with col_preview:
        render_live_preview_panel(st.session_state.profile_data)


def render_step_1_5_mos_translation():
    """Step 1.5: MOS Code Translation with AI-powered suggestions."""
    # Back button at top
    if st.button("← ", key="back_top_1_5", help="Back"):
        st.session_state.current_step = 1
        st.rerun()

    st.markdown(
        """
    <h2 style="color: #ffffff; font-size: 1.5rem; margin-bottom: 1rem;">MOS Code Translation</h2>
    <p style="color: #cbd5e1; font-size: 0.95rem;">Enter your Military Occupational Specialty code to map civilian skills</p>
    """,
        unsafe_allow_html=True,
    )

    col_form, col_gap, col_preview = st.columns([1, 0.1, 1])

    with col_form:
        # Add padding container for the form
        st.markdown("""
        <div style="padding: 1.5rem; background: rgba(26, 35, 50, 0.3); border-radius: 12px; margin-bottom: 1rem;">
        """, unsafe_allow_html=True)
        # MOS Code Input with real-time search
        st.markdown("**MOS Code** *")

        # Real-time MOS lookup (triggers on every keystroke) - MUST be defined before validation
        mos_match = None
        mos_results = []

        # Check validation for mos_code AFTER defining mos_match
        current_mos_code = st.session_state.profile_data.get("mos_code", "")

        mos_code = st.text_input(
            "MOS Code",
            value=current_mos_code,
            placeholder="11B , 1U031W, K070, A22A , V12C",
            label_visibility="collapsed",
            key="mos_translation_input",
            help="Type your MOS code (e.g., 11B, 25B, 42A)",
        )

        # Perform MOS lookup
        if mos_code and mapping_service:
            try:
                mos_results = mapping_service.search_mos(mos_code)
                if mos_results:
                    mos_match = mos_results[0]
                    st.session_state.profile_data["mos_code"] = mos_match.get("code", "")
                    st.session_state.profile_data["mos_title"] = mos_match.get("title", "")
                    st.session_state.profile_data["civilian_equivalent"] = mos_match.get(
                        "civilian_equivalent", ""
                    )
                    st.session_state.mos_skills = mos_match.get("civilian_skills", [])
                    st.session_state.mos_keywords = mos_match.get("keywords", [])
            except Exception as e:
                st.error(f"Error searching MOS: {e}")
        elif not mos_code:
            # Clear MOS data when input is empty
            st.session_state.mos_skills = []
            st.session_state.mos_keywords = []

        st.markdown("<br>", unsafe_allow_html=True)

        # Display MOS match results
        if mos_match:
            st.markdown("<br>", unsafe_allow_html=True)

            # ===== RECOMMENDED JOB TITLES =====
            st.markdown("###  Recommended Job Titles for Your MOS")

            # Parse civilian equivalent for job titles
            suggested_jobs = []
            if mos_match.get("civilian_equivalent"):
                suggested_jobs = [t.strip() for t in mos_match["civilian_equivalent"].split("|")]

            # Add skill-based recommendations
            additional_jobs = []
            mos_skills_list = st.session_state.mos_skills
            if any("Leadership" in s or "Team" in s or "Management" in s for s in mos_skills_list):
                additional_jobs.extend(["Operations Manager", "Team Lead", "Project Manager"])
            if any("IT" in s or "Technology" in s or "Computer" in s for s in mos_skills_list):
                additional_jobs.extend(
                    ["IT Specialist", "Systems Administrator", "Technical Support"]
                )
            if any("Security" in s or "Intelligence" in s for s in mos_skills_list):
                additional_jobs.extend(["Security Analyst", "Intelligence Analyst"])
            if any("Logistics" in s or "Supply" in s for s in mos_skills_list):
                additional_jobs.extend(["Logistics Coordinator", "Supply Chain Analyst"])

            all_jobs = suggested_jobs + [j for j in additional_jobs if j not in suggested_jobs]

            # Display job title buttons
            if all_jobs:
                cols = st.columns(3)
                for idx, job_title in enumerate(all_jobs[:9]):
                    with cols[idx % 3]:
                        if st.button(
                            f"{job_title}",
                            use_container_width=True,
                            key=f"job_select_{idx}",
                        ):
                            st.session_state.profile_data["target_role"] = job_title
                            st.success(f"Selected: {job_title}")
                            st.rerun()

            # Show selected job or allow custom input
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("**Your Target Role** *")

            # Real-time input without form - updates on blur (when user moves to another field)
            current_target_role = st.session_state.profile_data.get("target_role", "") or ""
            if not isinstance(current_target_role, str):
                current_target_role = str(current_target_role)

            target_role_error = ""
            if not current_target_role.strip():
                target_role_error = "Target Job Role is required"

            target_role = st.text_input(
                "Target Job Title",
                value=current_target_role,
                placeholder="e.g., Project Manager, IT Specialist",
                help=(
                    target_role_error
                    if target_role_error
                    else "Select from suggestions above or type your own (auto-saves when you move to another field)"
                ),
                label_visibility="collapsed",
                key="target_role_input",
            )

            # Auto-save when value changes
            if target_role != current_target_role:
                st.session_state.profile_data["target_role"] = target_role

            # Display current selection with MOS reference
            if st.session_state.profile_data.get("target_role"):
                mos_ref = f"Based on MOS {mos_match.get('code', '')} ({mos_match.get('title', '')})"
                st.markdown(
                    f"""
                <div style="background: rgba(234, 179, 8, 0.2); 
                            border: 1px solid rgba(234, 179, 8, 0.4); 
                            border-radius: 8px; 
                            padding: 1rem; 
                            color: #fde047; 
                            margin: 1rem 0;">
                    <p style="font-weight: 600; font-size: 1.1rem; margin: 0 0 0.5rem 0; text-align: center;">
                        Targeting: {st.session_state.profile_data['target_role']}
                    </p>
                    <p style="font-size: 0.8rem; margin: 0; text-align: center; opacity: 0.8;">
                        {mos_ref}
                    </p>
                </div>
                """,
                    unsafe_allow_html=True,
                )

            st.markdown("<br>", unsafe_allow_html=True)

            # ===== MAPPED CIVILIAN SKILLS =====
            st.markdown("###  Skills")

            # Initialize or update mapped skills when MOS changes
            current_mos = st.session_state.profile_data.get("mos_code", "")
            if (
                "last_mos_code" not in st.session_state
                or st.session_state.last_mos_code != current_mos
            ):
                # MOS code changed, reinitialize mapped skills
                st.session_state.mapped_skills = (
                    st.session_state.mos_skills.copy() if st.session_state.mos_skills else []
                )
                st.session_state.last_mos_code = current_mos

            # Display mapped skills as removable tags
            if st.session_state.mapped_skills:
                skills_cols = st.columns(3)
                for idx, skill in enumerate(st.session_state.mapped_skills):
                    with skills_cols[idx % 3]:
                        col1, col2 = st.columns([4, 1])
                        with col1:
                            st.markdown(
                                f"""
                            <div style="background: rgba(34, 211, 238, 0.2); 
                                        border: 1px solid rgba(34, 211, 238, 0.4); 
                                        border-radius: 20px; 
                                        padding: 0.5rem 1rem; 
                                        color: #67e8f9; 
                                        margin: 0.25rem 0;
                                        text-align: center;">
                                {skill}
                            </div>
                            """,
                                unsafe_allow_html=True,
                            )
                        with col2:
                            if st.button("×", key=f"remove_skill_{idx}", help=f"Remove {skill}"):
                                st.session_state.mapped_skills.remove(skill)
                                st.rerun()
            else:
                st.caption("No skills mapped yet")

            st.markdown("<br>", unsafe_allow_html=True)

            # ===== ADD CUSTOM SKILL =====
            st.markdown("### Add Custom Skill")

            # Initialize session state for tracking custom skill input
            if "last_custom_skill" not in st.session_state:
                st.session_state.last_custom_skill = ""

            custom_skill = st.text_input(
                "Add additional skill",
                placeholder="Type a skill (auto-adds when you move to another field)",
                key="custom_skill_input",
                value=st.session_state.last_custom_skill,
            )

            # Auto-add skill when input changes and is not empty
            if custom_skill and custom_skill != st.session_state.last_custom_skill:
                if custom_skill.strip() and custom_skill not in st.session_state.mapped_skills:
                    st.session_state.mapped_skills.append(custom_skill.strip())
                    st.session_state.last_custom_skill = ""
                    st.rerun()
                else:
                    st.session_state.last_custom_skill = custom_skill

            st.markdown("<br>", unsafe_allow_html=True)

            st.markdown("### Suggested Skills from MOS")

            suggested = [
                s for s in st.session_state.mos_skills if s not in st.session_state.mapped_skills
            ]

            if suggested:
                cols = st.columns(min(4, len(suggested)))
                for idx, skill in enumerate(suggested[:8]):
                    with cols[idx % 4]:
                        if st.button(f"+ {skill}", use_container_width=True, key=f"suggest_{idx}"):
                            st.session_state.mapped_skills.append(skill)
                            st.rerun()
            else:
                st.caption("All suggested skills have been added!")

            # Add AI-powered skill suggestions button
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Generate AI-Recommended Skills", use_container_width=True):
                with st.spinner("Generating AI-recommended skills..."):
                    if ai_service:
                        try:
                            ai_skills = ai_service.generate_skills_from_mos(
                                mos_match.get("code", ""),
                                mos_match.get("title", ""),
                                st.session_state.profile_data.get("target_role", ""),
                            )
                            # Add only new skills
                            new_skills_count = 0
                            for skill in ai_skills:
                                if skill not in st.session_state.mapped_skills:
                                    st.session_state.mapped_skills.append(skill)
                                    new_skills_count += 1
                            if new_skills_count > 0:
                                st.success(f"Added {new_skills_count} AI-recommended skills!")
                                st.rerun()
                            else:
                                st.info("All AI-recommended skills are already in your list!")
                        except Exception as e:
                            st.error(f"Error generating AI skills: {e}")

            st.markdown("<br>", unsafe_allow_html=True)

        elif mos_code and not mos_match:
            st.warning(
                f"MOS code '{mos_code}' not found. Please check the code or try searching differently."
            )
        else:
            st.info(
                "Enter your MOS code above to get started with skill mapping and job recommendations"
            )

        # Navigation
        st.markdown("<br><br>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Back to Contact Info", use_container_width=True, key="back_mos"):
                st.session_state.current_step = 1
                st.rerun()
        with col2:
            # Validation: require MOS match
            has_mos = bool(mos_match)
            can_continue = has_mos

            if st.button(
                "Continue to Professional Summary →",
                use_container_width=True,
                type="primary",
                key="next_summary",
                disabled=not can_continue,
            ):
                # Save mapped skills to core skills
                if "core_skills" not in st.session_state.profile_data:
                    st.session_state.profile_data["core_skills"] = []
                st.session_state.profile_data["core_skills"] = st.session_state.mapped_skills.copy()
                st.session_state.current_step = 1.6
                st.rerun()

            if not has_mos:
                st.caption("⚠ Please enter a valid MOS code to continue")

        # Close the padding container div
        st.markdown("</div>", unsafe_allow_html=True)

    with col_preview:
        render_live_preview_panel(st.session_state.profile_data)


def render_step_1_6_professional_summary():
    """Step 1.6: Professional Summary Generation."""
    # Back button at top
    if st.button("← ", key="back_top_1_6", help="Back"):
        st.session_state.current_step = 1.5
        st.rerun()

    st.markdown(
        """
    <h2 style="color: #ffffff; font-size: 1.5rem; margin-bottom: 1rem;">Professional Summary</h2>
    <p style="color: #cbd5e1; font-size: 0.95rem;">Generate an AI-powered professional summary for your resume</p>
    """,
        unsafe_allow_html=True,
    )

    col_form, col_gap, col_preview = st.columns([1, 0.1, 1])

    with col_form:
        # Get MOS match for context
        mos_match = None
        current_mos_code = st.session_state.profile_data.get("mos_code", "")
        if current_mos_code and mapping_service:
            try:
                mos_results = mapping_service.search_mos(current_mos_code)
                if mos_results:
                    mos_match = mos_results[0]
            except Exception as e:
                pass

        # ===== AI-POWERED SUMMARY =====
        st.markdown("### ✨ AI-Powered Professional Summary")

        # Generate AI Summary button - always visible
        generate_clicked = st.button(
            "Generate Professional Summary", use_container_width=True, type="primary", key="gen_summary_btn"
        )
        
        # Check if we should generate (on button click OR if regenerate flag is set)
        regenerate_clicked = st.session_state.get("regenerate_summary", False)
        
        # Clear the regenerate flag immediately to prevent infinite loops
        if regenerate_clicked:
            st.session_state.regenerate_summary = False
        
        should_generate = generate_clicked or regenerate_clicked
        
        if should_generate:
            with st.spinner("Creating your professional summary..."):
                if ai_service and mos_match:
                    try:
                        profile_dict = {
                            "full_name": st.session_state.profile_data.get("full_name", ""),
                            "mos_code": mos_match.get("code", ""),
                            "mos_title": mos_match.get("title", ""),
                            "security_clearance": st.session_state.profile_data.get(
                                "security_clearance", "None"
                            ),
                            "target_role": st.session_state.profile_data.get("target_role", ""),
                            "core_skills": st.session_state.mapped_skills,
                            "years_of_service": st.session_state.profile_data.get(
                                "years_of_service", "4"
                            ),
                        }
                        # Create a minimal ResumeProfile for AI service
                        from models import Contact, MOS, ResumeProfile

                        contact = Contact(
                            full_name=profile_dict["full_name"],
                            email=st.session_state.profile_data.get(
                                "email", "temp@example.com"
                            ),
                            phone=st.session_state.profile_data.get("phone", "0000000000"),
                            city=st.session_state.profile_data.get("city", "City"),
                            state=st.session_state.profile_data.get("state", "ST"),
                            security_clearance=profile_dict["security_clearance"],
                        )
                        mos_obj = MOS(
                            code=profile_dict["mos_code"],
                            branch=st.session_state.selected_branch or "Army",
                            title=profile_dict["mos_title"],
                            civilian_skills=profile_dict["core_skills"],
                        )
                        profile = ResumeProfile(
                            contact=contact,
                            mos=mos_obj,
                            target_roles=[profile_dict["target_role"]],
                            core_skills=profile_dict["core_skills"],
                        )
                        # Generate new summary
                        summary = ai_service.generate_summary(profile)
                        st.session_state.ai_summary = summary
                        st.session_state.ai_summary_generated = True
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error generating summary: {e}")
                        if mos_match:
                            st.session_state.ai_summary = f"Transitioning {st.session_state.selected_branch} veteran with experience as {mos_match.get('title', '')}. Skilled in {', '.join(st.session_state.mapped_skills[:3])}. Seeking roles as {st.session_state.profile_data.get('target_role', 'professional')}."
                        st.session_state.ai_summary_generated = True

        # Display generated summary ONLY AFTER it's been generated
        if st.session_state.get("ai_summary") and st.session_state.get("ai_summary_generated"):
            st.markdown("**Professional Summary**")

            # Use a unique key that changes when regenerating to force textarea refresh
            text_area_key = f"summary_edit_{st.session_state.get('summary_version', 0)}"

            st.session_state.ai_summary = st.text_area(
                "Edit your summary",
                value=st.session_state.ai_summary,
                height=120,
                key=text_area_key,
            )

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Regenerate", use_container_width=True, key="regen_summary_btn"):
                    # Set regenerate flag and increment version
                    st.session_state.regenerate_summary = True
                    st.session_state.summary_version = (
                        st.session_state.get("summary_version", 0) + 1
                    )
                    # Clear summary to force regeneration
                    st.session_state.pop("ai_summary", None)
                    st.rerun()
            with col2:
                if st.button("Looks Good", use_container_width=True):
                    st.success("Summary saved!")

        st.markdown("<br>", unsafe_allow_html=True)

        # Navigation
        st.markdown("<br><br>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Back to MOS Translation", use_container_width=True, key="back_summary"):
                st.session_state.current_step = 1.5
                st.rerun()
        with col2:
            # User can skip summary generation
            if st.button(
                "Continue to Work History →",
                use_container_width=True,
                type="primary",
                key="next_work_from_summary",
            ):
                st.session_state.current_step = 2
                st.rerun()

        # Close the padding container div
        st.markdown("</div>", unsafe_allow_html=True)

    with col_preview:
        render_live_preview_panel(st.session_state.profile_data)


def render_step_2_work_history():
    """Step 2: Work History."""
    # Back button at top
    if st.button("← ", key="back_top_2", help="Back"):
        st.session_state.current_step = 1
        st.rerun()

    st.markdown(
        """
    <h2 style="color: #ffffff; font-size: 1.5rem; margin-bottom: 1rem;">Step 2 – Work History</h2>
    """,
        unsafe_allow_html=True,
    )

    col_form, col_gap, col_preview = st.columns([1.5, 0.5, 1])

    with col_form:
      
        col_title, col_button = st.columns([3, 1])
        with col_title:
            st.markdown("### Work History")
        with col_button:
            if st.button("➕ Add role", type="primary"):
                st.session_state.work_history.append(
                    {
                        "employer": "",
                        "job_title": "",
                        "location": "",
                        "start_date": "",
                        "end_date": "",
                        "responsibilities": "",
                        "impact": "",
                        "ai_bullets": [],
                    }
                )
                st.rerun()

        for idx, role in enumerate(st.session_state.work_history):
            # Role status indicator with Pydantic validation
            # Only validate if user has started filling the form
            has_any_data = any([
                role.get("job_title"),
                role.get("employer"),
                role.get("start_date"),
                role.get("end_date"),
                role.get("responsibilities"),
                role.get("impact")
            ])
            
            is_valid, validation_errors = validate_work_history_entry(role)
            is_complete = role.get("job_title") and role.get("employer") and role.get("start_date")

            if is_valid and is_complete:
                status_badge = "✓ Valid"
                status_color = "#10b981"
            elif is_complete:
                status_badge = "⚠ Has Issues"
                status_color = "#f59e0b"
            elif has_any_data:
                status_badge = "⚠ Incomplete"
                status_color = "#ef4444"
            else:
                status_badge = "Add Details"
                status_color = "#64748b"

            # Expander title with role info
            expander_title = f"Role {idx + 1}: {role.get('job_title', 'Add details')}"
            if role.get("employer"):
                expander_title = f"Role {idx + 1}: {role.get('job_title', 'Add details')}"

            with st.expander(
                expander_title, expanded=(idx == len(st.session_state.work_history) - 1)
            ):
                # Status and dates on same line with delete button
                col_status, col_dates, col_delete = st.columns([1, 1, 0.5])
               
                
                with col_dates:
                    if role.get("start_date") or role.get("end_date"):
                        st.caption(f" Start / End")
                with col_delete:
                    if st.button("🗑️", key=f"delete_role_{idx}", help="Delete this role"):
                        st.session_state.work_history.pop(idx)
                        st.rerun()

                # Job Title with validation
                st.markdown("**Job Title** *")
                role["job_title"] = st.text_input(
                    "Job Title",
                    value=role.get("job_title", ""),
                    key=f"job_{idx}",
                    label_visibility="collapsed",
                    placeholder="e.g., Operations Manager, IT Specialist",
                )

                # Only show error if user has started filling this role
                if has_any_data and role["job_title"] and not role["job_title"].strip():
                    st.markdown(
                        '<p class="error-message">Job Title is required</p>', unsafe_allow_html=True
                    )

                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Start Date** *")
                    # Parse date string to date object for st.date_input
                    start_date_value = None
                    if role.get("start_date"):
                        try:
                            if isinstance(role["start_date"], str):
                                # Parse MM/YYYY or DD/MM/YYYY format
                                date_str = role["start_date"].strip()
                                if "/" in date_str:
                                    parts = date_str.split("/")
                                    if len(parts) == 2:  # MM/YYYY
                                        month, year = parts
                                        start_date_value = datetime(int(year), int(month), 1).date()
                                    elif len(parts) == 3:  # DD/MM/YYYY
                                        day, month, year = parts
                                        start_date_value = datetime(
                                            int(year), int(month), int(day)
                                        ).date()
                                elif "-" in date_str:
                                    parts = date_str.split("-")
                                    if len(parts) == 2:  # MM-YYYY
                                        month, year = parts
                                        start_date_value = datetime(int(year), int(month), 1).date()
                            elif hasattr(role["start_date"], "date"):  # datetime object
                                start_date_value = role["start_date"].date()
                            else:  # date object
                                start_date_value = role["start_date"]
                        except:
                            start_date_value = None

                    role["start_date"] = st.date_input(
                        "Start Date",
                        value=start_date_value,
                        key=f"start_{idx}",
                        format="DD/MM/YYYY",
                        label_visibility="collapsed",
                    )

                    # Only show error if user has started filling this role and date is missing
                    if has_any_data and not role.get("start_date"):
                        st.markdown(
                            '<p class="error-message">❌ Start date is required</p>',
                            unsafe_allow_html=True,
                        )

                with col2:
                    st.markdown("**End Date** (leave blank for current position)")
                    # Parse date string to date object for st.date_input
                    end_date_value = None
                    if role.get("end_date"):
                        try:
                            if isinstance(role["end_date"], str):
                                # Parse MM/YYYY or DD/MM/YYYY format
                                date_str = role["end_date"].strip().lower()
                                if date_str in ["present", "current"]:
                                    end_date_value = None  # Will show as today
                                elif "/" in date_str:
                                    parts = date_str.split("/")
                                    if len(parts) == 2:  # MM/YYYY
                                        month, year = parts
                                        end_date_value = datetime(int(year), int(month), 1).date()
                                    elif len(parts) == 3:  # DD/MM/YYYY
                                        day, month, year = parts
                                        end_date_value = datetime(
                                            int(year), int(month), int(day)
                                        ).date()
                                elif "-" in date_str:
                                    parts = date_str.split("-")
                                    if len(parts) == 2:  # MM-YYYY
                                        month, year = parts
                                        end_date_value = datetime(int(year), int(month), 1).date()
                            elif hasattr(role["end_date"], "date"):  # datetime object
                                end_date_value = role["end_date"].date()
                            else:  # date object
                                end_date_value = role["end_date"]
                        except:
                            end_date_value = None

                    role["end_date"] = st.date_input(
                        "End Date",
                        value=end_date_value,
                        key=f"end_{idx}",
                        format="DD/MM/YYYY",
                        label_visibility="collapsed",
                    )

                    # Validate date range - only if both dates exist
                    if has_any_data and role.get("start_date") and role.get("end_date"):
                        is_valid_range, range_error = validator.validate_date_range(
                            role["start_date"], role["end_date"]
                        )
                        if not is_valid_range:
                            st.markdown(
                                f'<p class="error-message"> {range_error}</p>',
                                unsafe_allow_html=True,
                            )

                # Employer with validation
                st.markdown("**Employer** *")
                role["employer"] = st.text_input(
                    "Employer",
                    value=role.get("employer", ""),
                    key=f"emp_{idx}",
                    label_visibility="collapsed",
                    placeholder="e.g., U.S. Navy, ABC Corporation",
                )

                # Only show error if user has started filling this role
                if has_any_data and role["employer"] and not role["employer"].strip():
                    st.markdown(
                        '<p class="error-message"> Employer is required</p>', unsafe_allow_html=True
                    )

                st.markdown("<br>", unsafe_allow_html=True)

                st.markdown("**Mission (1–3 sentences)**")
                st.caption("Aim for 1–3 sentences")
                role["responsibilities"] = st.text_area(
                    "Mission",
                    value=role.get("responsibilities", ""),
                    height=100,
                    key=f"resp_{idx}",
                    placeholder="What was the mandate for this role?",
                    label_visibility="collapsed",
                )

                st.markdown("**Responsibilities (paste list or paragraph)**")
                role["impact"] = st.text_area(
                    "Responsibilities",
                    value=role.get("impact", ""),
                    height=100,
                    key=f"impact_{idx}",
                    placeholder="List responsibilities or paste bullets; we'll clean them up.",
                    label_visibility="collapsed",
                )

                st.markdown("**Impact (metrics/outcomes)**")
                st.caption("Highlight at least one metric for bullet generation to land better")
                role["impact_metrics"] = st.text_area(
                    "Impact",
                    value=role.get("impact_metrics", ""),
                    height=100,
                    key=f"impact_met_{idx}",
                    placeholder="What changed because of you? Add metrics where possible.",
                    label_visibility="collapsed",
                )

                # Generate/Regenerate AI Bullets Button
                col_gen, col_regen = st.columns(2)
                with col_gen:
                    if st.button(
                        f" Generate AI Bullets", key=f"ai_{idx}", use_container_width=True
                    ):
                        with st.spinner("Generating professional bullet points..."):
                            # Add target_role to role data for context
                            role["target_role"] = st.session_state.profile_data.get(
                                "target_role", ""
                            )
                            role["core_skills"] = st.session_state.profile_data.get(
                                "core_skills", []
                            )

                            if ai_service:
                                # Debug: Show which provider is being used
                                provider_type = type(ai_service._provider).__name__
                                print(f"\n[Generate Bullets] Using provider: {provider_type}")
                                try:
                                    generated_bullets = ai_service.generate_star_bullets(role)
                                    role["generated_bullets"] = generated_bullets
                                    # Select all bullets by default
                                    role["selected_bullet_indices"] = list(
                                        range(len(generated_bullets))
                                    )
                                    st.success("✓ Bullets generated!")
                                except Exception as e:
                                    st.error(f" Error generating bullets: {str(e)}")
                                    import traceback

                                    st.error(f"Details: {traceback.format_exc()}")
                                    # Don't set demo bullets, let user try again
                                    return
                            else:
                                st.error("AI service not available. Please check configuration.")
                                return
                            st.rerun()

                with col_regen:
                    if role.get("generated_bullets"):
                        if st.button(
                            f"↻ Regenerate Bullets", key=f"regen_{idx}", use_container_width=True
                        ):
                            with st.spinner("Regenerating professional bullet points..."):
                                # Clear previous bullets before generating new ones
                                role.pop("generated_bullets", None)
                                role.pop("selected_bullet_indices", None)
                                role.pop("ai_bullets", None)
                                
                                # Increment regeneration counter to force text area refresh
                                role["bullet_regeneration_count"] = role.get("bullet_regeneration_count", 0) + 1
                                
                                # Add target_role to role data for context
                                role["target_role"] = st.session_state.profile_data.get(
                                    "target_role", ""
                                )
                                role["core_skills"] = st.session_state.profile_data.get(
                                    "core_skills", []
                                )

                                if ai_service:
                                    # Debug: Show which provider is being used
                                    provider_type = type(ai_service._provider).__name__
                                    print(f"\n[Regenerate Bullets] Using provider: {provider_type}")
                                    try:
                                        generated_bullets = ai_service.generate_star_bullets(role)
                                        role["generated_bullets"] = generated_bullets
                                        # Select all bullets by default for new generation
                                        role["selected_bullet_indices"] = list(
                                            range(len(generated_bullets))
                                        )
                                        st.success("✓ Bullets regenerated!")
                                    except Exception as e:
                                        st.error(f"❌ Error regenerating bullets: {str(e)}")
                                        import traceback

                                        st.error(f"Details: {traceback.format_exc()}")
                                        return
                                else:
                                    st.warning("AI service not available")
                                    return
                                st.rerun()

                # Display generated bullets with checkboxes for selection
                if role.get("generated_bullets"):
                    st.info(
                        "**AI-Generated Bullets** - Select which bullets to include in your resume:"
                    )

                    # Initialize selected indices if not exists
                    if "selected_bullet_indices" not in role:
                        role["selected_bullet_indices"] = list(
                            range(len(role["generated_bullets"]))
                        )  # Select all by default

                    for b_idx, bullet in enumerate(role["generated_bullets"]):
                        col_check, col_bullet = st.columns([0.5, 9.5])
                        with col_check:
                            is_selected = b_idx in role["selected_bullet_indices"]
                            if st.checkbox(
                                "✓",
                                value=is_selected,
                                key=f"check_{idx}_{b_idx}",
                                label_visibility="collapsed",
                            ):
                                if b_idx not in role["selected_bullet_indices"]:
                                    role["selected_bullet_indices"].append(b_idx)
                            else:
                                if b_idx in role["selected_bullet_indices"]:
                                    role["selected_bullet_indices"].remove(b_idx)

                        with col_bullet:
                            # Allow editing of bullets
                            regen_count = role.get("bullet_regeneration_count", 0)
                            role["generated_bullets"][b_idx] = st.text_area(
                                f"Bullet {b_idx + 1}",
                                value=bullet,
                                height=60,
                                key=f"bullet_{idx}_{b_idx}_{regen_count}",
                                label_visibility="collapsed",
                            )

                    # Update ai_bullets with only selected bullets for resume generation
                    role["ai_bullets"] = [
                        role["generated_bullets"][i]
                        for i in sorted(role["selected_bullet_indices"])
                    ]

                    # Show count of selected bullets
                    st.caption(
                        f"✓ {len(role['selected_bullet_indices'])} bullet(s) selected for resume"
                    )

        if not st.session_state.work_history:
            st.info(" Click 'Add role' to start adding your work experience")

        st.markdown("<br>", unsafe_allow_html=True)

        # Validate all work history entries before allowing continue
        all_valid = True
        validation_messages = []

        for idx, role in enumerate(st.session_state.work_history):
            # Only validate if user has started filling this role
            has_any_data = any([
                role.get("job_title"),
                role.get("employer"),
                role.get("start_date"),
                role.get("end_date"),
                role.get("responsibilities"),
                role.get("impact_metrics")
            ])
            
            if not has_any_data:
                continue  # Skip validation for empty entries
            
            role_errors = []

            # Check required fields
            if not role.get("job_title") or not role.get("job_title").strip():
                role_errors.append(f"Role {idx + 1}: Job Title is required")

            if not role.get("employer") or not role.get("employer").strip():
                role_errors.append(f"Role {idx + 1}: Employer is required")

            if not role.get("start_date"):
                role_errors.append(f"Role {idx + 1}: Start Date is required")

            # Check date range validation
            if role.get("start_date") and role.get("end_date"):
                is_valid_range, range_error = validator.validate_date_range(
                    role["start_date"], role["end_date"]
                )
                if not is_valid_range:
                    role_errors.append(f"Role {idx + 1}: {range_error}")

            # Check impact_metrics field length (maps to scope_metrics in model)
            impact_metrics_text = role.get("impact_metrics", "")
            if impact_metrics_text and len(impact_metrics_text) > 1000:
                role_errors.append(f"Role {idx + 1}: Impact/Metrics text is too long ({len(impact_metrics_text)} characters). Maximum allowed is 1000 characters.")

            if role_errors:
                all_valid = False
                validation_messages.extend(role_errors)

        # Show validation errors if any
        if not all_valid:
            st.error("⚠️ Please complete the following required fields:")
            for msg in validation_messages:
                st.markdown(f"• {msg}")
        
        # Check if at least one work history entry exists with data
        has_work_history = any([
            any([role.get("job_title"), role.get("employer"), role.get("start_date")])
            for role in st.session_state.work_history
        ])

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Save Mission ", use_container_width=True, key="save2"):
                st.success("✓ Saved!")
        with col2:
            if st.button(
                "Continue →",
                use_container_width=True,
                type="primary",
                key="cont2",
                disabled=not all_valid,
            ):
                st.session_state.current_step = 3
                st.rerun()

        # Close the padding container div
        st.markdown("</div>", unsafe_allow_html=True)

    with col_preview:
        render_live_preview_panel(st.session_state.profile_data)


def render_step_3_education():
    """Step 3: Education & Certifications."""
    # Back button at top
    if st.button("← ", key="back_top_3", help="Back"):
        st.session_state.current_step = 2
        st.rerun()

    st.markdown(
        """
    <h2 style="color: #ffffff; font-size: 1.5rem; margin-bottom: 1rem;">Step 3 – Education & Certifications</h2>
    """,
        unsafe_allow_html=True,
    )

    col_form, col_gap, col_preview = st.columns([1, 0.1, 1])

    with col_form:
        # Add padding container for the form
        st.markdown("""
        <div style="padding: 1.5rem; background: rgba(26, 35, 50, 0.3); border-radius: 12px; margin-bottom: 1rem;">
        """, unsafe_allow_html=True)
        # Education Section
        col_title, col_button = st.columns([3, 1])
        with col_title:
            st.markdown("### Education")
        with col_button:
            if st.button("Add Education"):
                st.session_state.education.append({})
                st.rerun()

        for idx, edu in enumerate(st.session_state.education):
            # Check if user has started filling this education entry
            has_any_data = any([
                edu.get("institution"),
                edu.get("degree"),
                edu.get("year"),
                edu.get("gpa")
            ])
            
            with st.expander(
                f"**Education {idx + 1}:** {edu.get('institution', 'Click to add details')}",
                expanded=True,
            ):
                # Add delete button at the top
                col_header, col_delete = st.columns([6, 1])
                with col_delete:
                    if st.button("🗑️", key=f"delete_edu_{idx}", help="Delete this education"):
                        st.session_state.education.pop(idx)
                        st.rerun()
                
                col1, col2 = st.columns(2)
                with col1:
                    # Institution with validation
                    st.markdown("**Institution** *")
                    edu["institution"] = st.text_input(
                        "Institution *",
                        value=edu.get("institution", ""),
                        key=f"edu_inst_{idx}",
                        placeholder="e.g., University of Virginia",
                        label_visibility="collapsed",
                    )

                    # Only show error if user has started filling and field is invalid
                    if has_any_data and edu.get("institution") is not None and not edu.get("institution", "").strip():
                        st.markdown(
                            '<p class="error-message">❌ Institution is required</p>',
                            unsafe_allow_html=True,
                        )

                    # Degree with validation
                    st.markdown("**Degree/Program** *")
                    edu["degree"] = st.text_input(
                        "Degree/Program *",
                        value=edu.get("degree", ""),
                        key=f"edu_deg_{idx}",
                        placeholder="e.g., Bachelor of Science in Computer Science",
                        label_visibility="collapsed",
                    )

                    # Only show error if user has started filling and field is invalid
                    if has_any_data and edu.get("degree") is not None and not edu.get("degree", "").strip():
                        st.markdown(
                            '<p class="error-message">❌ Degree/Program is required</p>',
                            unsafe_allow_html=True,
                        )

                with col2:
                    # Year with validation
                    st.markdown("**Graduation Year**")
                    edu["year"] = st.text_input(
                        "Year",
                        value=edu.get("year", ""),
                        placeholder="e.g., 2020 or In Progress",
                        key=f"edu_yr_{idx}",
                        label_visibility="collapsed",
                    )

                    # Validate year only if provided
                    if has_any_data and edu.get("year"):
                        is_valid_year, year_error = validator.validate_year(edu["year"])
                        if not is_valid_year:
                            st.markdown(
                                f'<p class="error-message">❌ {year_error}</p>',
                                unsafe_allow_html=True,
                            )

                    # GPA with validation
                    st.markdown("**GPA (optional)**")
                    edu["gpa"] = st.text_input(
                        "GPA (optional)",
                        value=edu.get("gpa", ""),
                        key=f"edu_gpa_{idx}",
                        placeholder="e.g., 3.5",
                        label_visibility="collapsed",
                    )

                    # Validate GPA only if provided
                    if has_any_data and edu.get("gpa"):
                        is_valid_gpa, gpa_error = validator.validate_gpa(edu["gpa"])
                        if not is_valid_gpa:
                            st.markdown(
                                f'<p class="error-message">❌ {gpa_error}</p>',
                                unsafe_allow_html=True,
                            )

        if not st.session_state.education:
            st.caption(" 'Add Certification' to showcase your Education")
        

        st.markdown("<br>", unsafe_allow_html=True)

        # Certifications Section
        col_title, col_button = st.columns([3, 1])
        with col_title:
            st.markdown("### Certifications")
        with col_button:
            if st.button("Add Certification"):
                st.session_state.certifications.append({})
                st.rerun()

        for idx, cert in enumerate(st.session_state.certifications):
            with st.expander(
                f"**Certification {idx + 1}:** {cert.get('name', 'Click to add details')}",
                expanded=True,
            ):
                # Add delete button
                col_header, col_delete = st.columns([3, 1])
                with col_delete:
                    if st.button("🗑️", key=f"delete_cert_{idx}", help="Delete this certification"):
                        st.session_state.certifications.pop(idx)
                        st.rerun()
                
                col1, col2 = st.columns(2)
                with col1:
                    cert["name"] = st.text_input(
                        "Name *",
                        value=cert.get("name", ""),
                        key=f"cert_name_{idx}",
                        placeholder="PMP, AWS Certified, etc.",
                    )
                with col2:
                    cert["issuer"] = st.text_input(
                        "Issuer *",
                        value=cert.get("issuer", ""),
                        key=f"cert_iss_{idx}",
                        placeholder="Issuing Organization",
                    )

        if not st.session_state.certifications:
            st.caption(" 'Add Certification' to showcase your credentials")

        st.markdown("<br>", unsafe_allow_html=True)

        # Volunteer Experience Section
        if "volunteer_experience" not in st.session_state:
            st.session_state.volunteer_experience = []

        col_title, col_button = st.columns([3, 1])
        with col_title:
            st.markdown("### Volunteer Experience")
        with col_button:
            if st.button("Add Activity"):
                st.session_state.volunteer_experience.append({})
                st.rerun()

        st.caption("Showcase your community involvement and leadership outside of work")

        for idx, vol in enumerate(st.session_state.volunteer_experience):
            with st.expander(f"**Activity {idx + 1}**", expanded=True):
                # Add delete button
                col_header, col_delete = st.columns([3, 1])
                with col_delete:
                    if st.button("🗑️", key=f"delete_vol_{idx}", help="Delete this activity"):
                        st.session_state.volunteer_experience.pop(idx)
                        st.rerun()
                
                vol["organization"] = st.text_input(
                    "Organization Name",
                    value=vol.get("organization", ""),
                    key=f"vol_org_{idx}",
                    placeholder="e.g., Big Brothers Big Sisters of America",
                )

                vol["role"] = st.text_input(
                    "Your Role",
                    value=vol.get("role", ""),
                    key=f"vol_role_{idx}",
                    placeholder="e.g., Mentor",
                )

                col1, col2 = st.columns(2)
                with col1:
                    vol["location"] = st.text_input(
                        "Location",
                        value=vol.get("location", ""),
                        key=f"vol_loc_{idx}",
                        placeholder="e.g., Norfolk, VA",
                    )
                with col2:
                    vol["duration"] = st.text_input(
                        "Duration",
                        value=vol.get("duration", ""),
                        key=f"vol_dur_{idx}",
                        placeholder="e.g., 2018-2019",
                    )

                vol["description"] = st.text_area(
                    "Description & Achievements",
                    value=vol.get("description", ""),
                    height=100,
                    key=f"vol_desc_{idx}",
                    placeholder="Describe your contributions and impact...",
                )

        if not st.session_state.volunteer_experience:
            st.markdown(
                """
            <div style="background: rgba(234, 179, 8, 0.1); border: 1px solid rgba(234, 179, 8, 0.3); border-radius: 6px; padding: 1rem; margin: 1rem 0;">
                <p style="color: #fde047; font-size: 0.875rem; margin: 0;">
                     <strong>Tip:</strong> Volunteer experience demonstrates leadership, commitment, and community engagement—qualities valued by civilian employers.
                </p>
            </div>
            """,
                unsafe_allow_html=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)

        # Validate all education entries before allowing continue
        all_valid = True
        validation_messages = []

        for idx, edu in enumerate(st.session_state.education):
            # Only validate if user has started filling this education entry
            has_any_data = any([
                edu.get("institution"),
                edu.get("degree"),
                edu.get("year"),
                edu.get("gpa")
            ])
            
            if not has_any_data:
                continue  # Skip validation for empty entries
            
            edu_errors = []

            # Check required fields
            if not edu.get("institution") or not edu.get("institution").strip():
                edu_errors.append(f"Education {idx + 1}: Institution is required")

            if not edu.get("degree") or not edu.get("degree").strip():
                edu_errors.append(f"Education {idx + 1}: Degree/Program is required")

            # Validate year if provided
            if edu.get("year"):
                is_valid_year, year_error = validator.validate_year(edu["year"])
                if not is_valid_year:
                    edu_errors.append(f"Education {idx + 1}: {year_error}")

            # Validate GPA if provided
            if edu.get("gpa"):
                is_valid_gpa, gpa_error = validator.validate_gpa(edu["gpa"])
                if not is_valid_gpa:
                    edu_errors.append(f"Education {idx + 1}: {gpa_error}")

            if edu_errors:
                all_valid = False
                validation_messages.extend(edu_errors)

        # Validate all certification entries
        for idx, cert in enumerate(st.session_state.certifications):
            # Only validate if user has started filling this certification
            has_any_data = cert.get("name") or cert.get("issuer")
            
            if not has_any_data:
                continue  # Skip validation for empty entries
            
            cert_errors = []

            # Check required fields for certifications
            if not cert.get("name") or not cert.get("name").strip():
                cert_errors.append(f"Certification {idx + 1}: Name is required")

            if not cert.get("issuer") or not cert.get("issuer").strip():
                cert_errors.append(f"Certification {idx + 1}: Issuer is required")

            if cert_errors:
                all_valid = False
                validation_messages.extend(cert_errors)

        # Show validation errors if any
        if not all_valid:
            st.error("⚠️ Please complete the following required fields:")
            for msg in validation_messages:
                st.markdown(f"• {msg}")

        # Navigation
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Save Mission", use_container_width=True, key="save3"):
                st.success("✓ Saved!")
        with col2:
            if st.button(
                "Continue →",
                use_container_width=True,
                type="primary",
                key="cont3",
                disabled=not all_valid,
            ):
                st.session_state.current_step = 4
                st.rerun()

        # Close the padding container div
        st.markdown("</div>", unsafe_allow_html=True)

    with col_preview:
        render_live_preview_panel(st.session_state.profile_data)


def render_step_4_review():
    """Step 4: Review & Download Resume"""
    from components.step4_new import render_step_4

    render_step_4(resume_service)


def create_resume_profile_from_session() -> ResumeProfile:
    """Create a ResumeProfile object from session state data."""
    from models import Contact, MOS, WorkHistory, Education, Certification, DocumentPreferences
    from datetime import datetime

    # Helper function to handle optional URLs
    def clean_url(url_value):
        """Convert empty string to None for optional URL fields."""
        if not url_value:
            return None
        if isinstance(url_value, str):
            return url_value.strip() if url_value.strip() else None
        return None

    # Helper function to parse dates
    def parse_date(date_str):
        """Convert date string (MM/YYYY or MM-YYYY) to date object."""
        if not date_str:
            return None
        if not isinstance(date_str, str):
            # If it's already a date object, return it
            if hasattr(date_str, "year"):
                return date_str
            return None

        date_str = date_str.strip()
        if date_str.lower() in ["present", "current", ""]:
            return None

        try:
            # Handle MM/YYYY or MM-YYYY format
            if "/" in date_str:
                month, year = date_str.split("/")
            elif "-" in date_str:
                month, year = date_str.split("-")
            else:
                # Assume year only
                return datetime(int(date_str), 1, 1).date()
            return datetime(int(year), int(month), 1).date()
        except:
            # Default to first day of current year if parsing fails
            return datetime.now().replace(month=1, day=1).date()

    # Contact information
    contact = Contact(
        full_name=st.session_state.profile_data.get("full_name", ""),
        email=st.session_state.profile_data.get("email", ""),
        phone=st.session_state.profile_data.get("phone", ""),
        city=st.session_state.profile_data.get("city", ""),
        state=st.session_state.profile_data.get("state", ""),
        linkedin=clean_url(st.session_state.profile_data.get("linkedin")),
        portfolio=clean_url(st.session_state.profile_data.get("portfolio")),
        security_clearance=st.session_state.profile_data.get("security_clearance", "None"),
        branch=st.session_state.get("selected_branch") or "Army",
    )

    # MOS information
    mos = MOS(
        code=st.session_state.profile_data.get("mos_code", ""),
        branch=st.session_state.get("selected_branch") or "Army",
        title=st.session_state.profile_data.get("mos_title", ""),
        years_served=st.session_state.profile_data.get("years_of_service", ""),
    )

    # Work history
    work_history = []
    for role in st.session_state.work_history:
        # Parse dates
        start_date = parse_date(role.get("start_date", ""))
        end_date = parse_date(role.get("end_date", ""))

        # Check if current - handle None safely
        end_date_str = role.get("end_date", "") or ""
        if isinstance(end_date_str, str):
            is_current = end_date_str.strip().lower() in ["present", "current"]
        else:
            is_current = False

        # Get bullets - prioritize ai_bullets, fallback to responsibilities
        bullets = role.get("ai_bullets", [])
        if not bullets:
            resp = role.get("responsibilities", "")
            bullets = [resp] if resp else []

        wh = WorkHistory(
            title=role.get("job_title", "Position"),  # Required field
            organization=role.get("employer", "Organization"),  # Required field
            location=role.get("location", ""),
            start_date=start_date or datetime.now().replace(year=2020, month=1, day=1).date(),
            end_date=end_date,
            current=is_current,
            bullets=bullets,
            ai_generated_bullets=role.get("ai_bullets", []),
            scope_metrics=role.get("impact_metrics", ""),
        )
        work_history.append(wh)

    # Helper function to convert GPA to 4.0 scale
    def convert_gpa(gpa_value):
        """Convert GPA from various scales to 4.0 scale."""
        if gpa_value is None or gpa_value == "" or str(gpa_value).strip() == "":
            return None
        try:
            # Strip and convert to float
            gpa = float(str(gpa_value).strip())
            # If GPA is already on 4.0 scale or below
            if gpa <= 4.0:
                return round(gpa, 2)
            # If GPA is on 10-point scale (common in many countries)
            elif gpa <= 10.0:
                return round((gpa / 10.0) * 4.0, 2)
            # If GPA is on 100-point scale
            elif gpa <= 100.0:
                return round((gpa / 100.0) * 4.0, 2)
            else:
                # Cap at 4.0 for any unexpected values
                return 4.0
        except (ValueError, TypeError):
            return None

    # Helper function to convert year
    def convert_year(year_value):
        """Convert year to integer."""
        if year_value is None or year_value == "" or str(year_value).strip() == "":
            return None
        try:
            return int(str(year_value).strip())
        except (ValueError, TypeError):
            return None

    # Education
    education = []
    for edu in st.session_state.education:
        ed = Education(
            institution=edu.get("institution", ""),
            degree=edu.get("degree", ""),
            graduation_year=convert_year(edu.get("year")),
            gpa=convert_gpa(edu.get("gpa")),
        )
        education.append(ed)

    # Certifications
    certifications = []
    for cert in st.session_state.certifications:
        c = Certification(
            name=cert.get("name", ""), issuer=cert.get("issuer", ""), year=cert.get("year")
        )
        certifications.append(c)

    # Volunteer Experience - keep as structured data
    volunteer_list = []
    for vol in st.session_state.get("volunteer_experience", []):
        # Check if it's already a string or structured data
        if isinstance(vol, str):
            volunteer_list.append(vol)
        elif isinstance(vol, dict):
            # Keep as dict if it has required fields
            if vol.get("organization") or vol.get("role") or vol.get("description"):
                # Normalize field names: map 'duration' to 'date_range' if needed
                vol_entry = {
                    "organization": vol.get("organization", ""),
                    "role": vol.get("role", ""),
                    "description": vol.get("description", ""),
                    "location": vol.get("location", ""),
                    "date_range": vol.get("date_range") or vol.get("duration", "")  # Support both field names
                }
                volunteer_list.append(vol_entry)
    
    # Create AdditionalInfo with volunteer data
    additional_info = None
    if volunteer_list:
        from models import AdditionalInfo
        additional_info = AdditionalInfo(volunteer=volunteer_list)

    # Document preferences
    doc_prefs = DocumentPreferences(template="classic", bullet_density=4)

    # Create profile with error handling
    try:
        profile = ResumeProfile(
            contact=contact,
            mos=mos,
            target_roles=[st.session_state.profile_data.get("target_role", "")],
            summary=st.session_state.ai_summary or "",
            core_skills=st.session_state.profile_data.get("core_skills", []),
            tools_technologies=st.session_state.profile_data.get("technical_skills", []),
            work_history=work_history,
            education=education,
            certifications=certifications,
            additional_info=additional_info,
            preferences=doc_prefs,
        )
    except Exception as e:
        # Log detailed error information for debugging
        st.error(f"❌ Error creating resume profile: {e}")

        # Show what data we're trying to create the profile with
        with st.expander("🔍 Debug Information"):
            st.write(
                "**Contact data:**",
                type(contact),
                contact if hasattr(contact, "model_dump") else str(contact),
            )
            st.write("**MOS data:**", type(mos), mos if hasattr(mos, "model_dump") else str(mos))
            st.write("**Work history count:**", len(work_history))
            st.write("**Education count:**", len(education))
            st.write("**Certifications count:**", len(certifications))
            st.write(
                "**Document preferences:**",
                type(doc_prefs),
                doc_prefs if hasattr(doc_prefs, "model_dump") else str(doc_prefs),
            )

        # Return a minimal profile to prevent complete failure
        from models import Contact, MOS, DocumentPreferences

        minimal_contact = Contact(
            full_name="Error",
            email="error@example.com",
            phone="0000000000",
            city="Error",
            state="ER",
            security_clearance="None",
        )
        profile = ResumeProfile(contact=minimal_contact, target_roles=["Error Recovery"])
        return profile

    return profile


def main():
    """Main application entry point."""
    load_custom_css()
    initialize_session_state()

    # Show header on all pages
    # if st.session_state.current_step > 0:
    #     render_header()
    render_header()

    if st.session_state.current_step == 0:
        render_landing_page()
    else:
        render_progress_bar()

        if st.session_state.current_step == 1:
            render_step_1_contact()
        elif st.session_state.current_step == 1.5:
            render_step_1_5_mos_translation()
        elif st.session_state.current_step == 1.6:
            render_step_1_6_professional_summary()
        elif st.session_state.current_step == 2:
            render_step_2_work_history()
        elif st.session_state.current_step == 3:
            render_step_3_education()
        elif st.session_state.current_step == 4:
            render_step_4_review()


if __name__ == "__main__":
    main()
