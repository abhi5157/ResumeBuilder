"""Clean Live Preview Component (replacement for corrupted live_preview.py)."""

from typing import Dict
import streamlit as st
from streamlit.components.v1 import html as st_html


def render_live_preview_panel(profile_data: Dict):
    """Render the resume live preview using a single HTML block."""
    # Dynamic data
    name = st.session_state.get("full_name_input", profile_data.get("full_name", "Your Name"))
    email = st.session_state.get("email_input", profile_data.get("email", ""))
    phone = st.session_state.get("phone_input", profile_data.get("phone", ""))
    location_input = st.session_state.get("location_input", "")
    city = location_input.split(", ")[0] if location_input else profile_data.get("city", "")
    state = location_input.split(", ")[1] if ", " in location_input else profile_data.get("state", "")
    linkedin = st.session_state.get("linkedin_input", profile_data.get("linkedin", ""))
    portfolio = st.session_state.get("portfolio_input", profile_data.get("portfolio", ""))
    years_of_service = st.session_state.get("years_service_input", profile_data.get("years_of_service", ""))
    last_duty_title = st.session_state.get("last_duty_input", profile_data.get("last_duty_title", ""))
    deployments = st.session_state.get("deployments_input", profile_data.get("deployments", ""))

    # Contact line
    contact_items = []
    if email: contact_items.append(email)
    if phone: contact_items.append(phone)
    loc = f"{city}, {state}".strip(", ")
    if loc: contact_items.append(loc)
    if linkedin: contact_items.append(linkedin.replace("https://", "").replace("http://", ""))
    if portfolio: contact_items.append(portfolio.replace("https://", "").replace("http://", ""))
    contact_html = "".join([f"<span class='preview-contact-item'>{c}</span>" for c in contact_items])

    extras = []
    if years_of_service: extras.append(f"Years of Service: {years_of_service}")
    if last_duty_title: extras.append(f"Last Duty: {last_duty_title}")
    if deployments: extras.append(f"Deployments: {deployments}")
    additional_html = " • ".join(extras) if extras else ""

    badges = []
    branch = st.session_state.get("selected_branch")
    if branch: badges.append(branch.upper())
    clearance = st.session_state.get("clearance_select", profile_data.get("security_clearance", "None"))
    if clearance and clearance != "None": badges.append(clearance.upper())
    badges_html = "".join([f"<span class='preview-badge'>{b}</span>" for b in badges])
    if badges_html: badges_html = f"<div class='preview-badges'>{badges_html}</div>"

    def section(title: str, body: str, divider: bool = True) -> str:
        return f"<p class='preview-section-title'>{title}</p>{body}" + ("<div class='preview-divider'></div>" if divider else "")

    content = f"""
    <div class="preview-contact-section">
      <h2 class="preview-name">{name}</h2>
      <div class="preview-contact">{contact_html if contact_html else '<span class="preview-empty">Contact info will appear here</span>'}</div>
      {f'<div class="preview-contact" style="font-size:.55rem;color:#94a3b8;margin-top:.3rem;">{additional_html}</div>' if additional_html else ''}
      {badges_html}
    </div>
    <div class="preview-divider"></div>
    """
    if profile_data.get("target_role"):
        content += section("Target Role", f"<p class='preview-text'>{profile_data['target_role']}</p>")
    if st.session_state.get("ai_summary"):
        content += section("Professional Summary", f"<p class='preview-text'>{st.session_state.ai_summary}</p>")

    # Skills
    all_skills = st.session_state.get("mos_skills", []) + profile_data.get("core_skills", [])
    if all_skills:
        skills_html = "".join([f"<span class='preview-skill'>{s}</span>" for s in all_skills[:12]])
        content += section("Core Skills", f"<div>{skills_html}</div>")
    else:
        content += section("Core Skills", "<div class='preview-empty'>Skills will appear here as you add them</div>")

    # Work history
    work_history = st.session_state.get("work_history", [])
    work_body = ""
    if work_history:
        for role in work_history[:3]:
            job_title = role.get("job_title", "Position")
            employer = role.get("employer", "Company")
            start_date = role.get("start_date", "Start")
            end_date = role.get("end_date", "Present")
            if hasattr(start_date, "strftime"): start_date = start_date.strftime("%b %Y")
            if hasattr(end_date, "strftime"): end_date = end_date.strftime("%b %Y")
            dates = f"{start_date} - {end_date}".strip()
            work_body += f"<div class='preview-card'><p class='preview-card-title'>{job_title}</p><p class='preview-card-subtitle'>{employer} • {dates}</p></div>"
        if len(work_history) > 3:
            work_body += f"<p class='preview-text' style='text-align:center;font-style:italic;color:#64748b;'>+ {len(work_history) - 3} more role(s)</p>"
    else:
        work_body = "<div class='preview-empty'>Work history will appear here</div>"
    content += section("Work History", work_body)

    # Education
    education = st.session_state.get("education", [])
    edu_body = ""
    if education:
        for edu in education:
            institution = edu.get("institution", "Institution")
            degree = edu.get("degree", "Degree")
            year = edu.get("year", "")
            gpa = edu.get("gpa", "")
            details = []
            if year: details.append(str(year))
            if gpa: details.append(f"GPA: {gpa}")
            tail = " • ".join(details)
            edu_body += f"<div class='preview-card'><p class='preview-card-title'>{degree}</p><p class='preview-card-subtitle'>{institution}{' • ' + tail if tail else ''}</p></div>"
    else:
        edu_body = "<div class='preview-empty'>Education will appear here</div>"
    content += section("Education", edu_body)

    # Certifications
    certifications = st.session_state.get("certifications", [])
    cert_body = ""
    if certifications:
        for cert in certifications:
            cert_name = cert.get("name", "Certification")
            issuer = cert.get("issuer", "")
            issuer_html = f"<p class='preview-card-subtitle'>{issuer}</p>" if issuer else ""
            cert_body += f"<div class='preview-card'><p class='preview-card-title'>{cert_name}</p>{issuer_html}</div>"
    else:
        cert_body = "<div class='preview-empty'>Certifications will appear here</div>"
    content += section("Certifications", cert_body, divider=False)

    preview_html = f"""
    <div class="preview-wrapper">
      <style>
        .preview-wrapper {{background:#0f1729;border-radius:20px;box-shadow:0 12px 44px rgba(0,0,0,.5);border:2px solid #1e293b;position:sticky;top:80px;max-height:calc(100vh - 100px);display:flex;flex-direction:column;}}
        .live-preview-panel {{display:flex;flex-direction:column;height:100%;}}
        .preview-header {{background:linear-gradient(135deg,#0a0f1a,#0f172a);padding:1.05rem 1.4rem;border-bottom:3px solid #22d3ee;border-radius:20px 20px 0 0;}}
        .preview-title {{font-size:.9rem;font-weight:700;letter-spacing:1px;text-transform:uppercase;color:#fff;margin:0;}}
        .preview-subtitle {{font-size:.7rem;color:#94a3b8;margin:.35rem 0 0;}}
        .preview-contact-section {{background:#0f1729;padding:1.3rem 0 1.1rem;margin-bottom:1rem;border-radius:7px;}}
        .preview-name {{font-size:1.7rem;font-weight:700;margin:0 0 .4rem;color:#fff;line-height:1.15;text-shadow:0 2px 6px rgba(0,0,0,.55);}}
        .preview-contact {{display:flex;flex-wrap:wrap;align-items:center;font-size:.72rem;line-height:1.3;color:#cbd5e1;}}
        .preview-contact-item {{position:relative;padding-right:.6rem;margin:0 .6rem .3rem 0;font-weight:500;color:#cbd5e1;}}
        .preview-contact-item:not(:last-child)::after {{content:"";position:absolute;right:.2rem;top:50%;transform:translateY(-50%);width:6px;height:6px;background:#22d3ee;border-radius:50%;box-shadow:0 0 0 2px rgba(34,211,238,.25);}}
        .preview-badges {{margin-top:.4rem;}}
        .preview-badge {{display:inline-block;background:#22d3ee;color:#0f172a;padding:.32rem .65rem;border-radius:7px;font-size:.58rem;font-weight:700;margin:.35rem .35rem 0 0;letter-spacing:.4px;}}
        .preview-content-wrapper {{flex:1;overflow-y:auto;}}
        .preview-content {{padding:1.15rem 1.2rem 1.4rem;}}
        .preview-section-title {{font-size:.68rem;font-weight:700;text-transform:uppercase;letter-spacing:.5px;color:#fff;margin:0 0 .55rem;padding-bottom:.3rem;border-bottom:3px solid #22d3ee;}}
        .preview-divider {{height:2px;background:linear-gradient(to right,transparent,#2d3e50,transparent);margin:.9rem 0;}}
        .preview-text {{font-size:.64rem;line-height:1.4;color:#cbd5e1;margin:.45rem 0;}}
        .preview-skill {{display:inline-block;background:rgba(34,211,238,.15);color:#67e8f9;padding:.26rem .55rem;border-radius:5px;font-size:.56rem;font-weight:600;margin:.18rem .18rem .18rem 0;border:1px solid rgba(34,211,238,.3);}}
        .preview-card {{background:rgba(26,35,50,.6);border:1px solid #2d3e50;border-left:3px solid #22d3ee;border-radius:7px;padding:.55rem .8rem;margin:.5rem 0;}}
        .preview-card-title {{font-size:.6rem;font-weight:700;color:#fff;margin:0 0 .2rem;}}
        .preview-card-subtitle {{font-size:.55rem;color:#94a3b8;margin:0;}}
        .preview-empty {{font-size:.58rem;color:#64748b;font-style:italic;text-align:center;padding:.7rem .55rem;border-radius:7px;}}
        .preview-content::-webkit-scrollbar {{width:6px;}}
        .preview-content::-webkit-scrollbar-track {{background:#1a2332;}}
        .preview-content::-webkit-scrollbar-thumb {{background:#2d3e50;border-radius:3px;}}
        .preview-content::-webkit-scrollbar-thumb:hover {{background:#22d3ee;}}
      </style>
      <div class="live-preview-panel">
        <div class="preview-header">
          <p class="preview-title">Live Preview</p>
          <p class="preview-subtitle">Updated in Real Time</p>
        </div>
        <div class="preview-content-wrapper"><div class="preview-content">{content}</div></div>
      </div>
    </div>
    """

    st_html(preview_html, height=920, scrolling=True)
