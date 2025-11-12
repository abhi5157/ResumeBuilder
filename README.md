# 🎖️ Veteran Resume Builder

> **Turn Your Service Into Opportunity** - Military-themed resume builder for veterans transitioning to civilian careers

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 🚀 **Quick Start** (3 Steps)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Launch the app
streamlit run app.py

# 3. Open browser
# → http://localhost:8501
```

**OR use the quick launch script:**
```bash
./launch.sh
```

---

## 🎯 **What You Get**

✅ **Military-Themed UI** - Professional dark gradient design  
✅ **6 Branch Selection** - Army, Navy, Marines, Air Force, Space Force, Coast Guard  
✅ **4-Step Form** - Contact → Work History → Education → Review & Export  
✅ **Live Preview** - See your resume build in real-time  
✅ **AI-Powered** - Auto-generate summaries and STAR-format bullets  
✅ **MOS Translation** - Convert military codes to civilian skills  
✅ **ATS-Ready** - Download optimized Word documents  

---

A professional resume builder designed specifically for veterans transitioning to civilian careers. This application translates military experience (MOS codes) into civilian-friendly language and uses AI to generate compelling resume content.

## ✨ Features

- **Streamlit Web Application**: User-friendly interface with step-by-step form
- **MOS Translation**: Automatic translation of 50+ Military Occupational Specialties to civilian skills
- **AI-Powered Content**: Generate professional summaries and STAR-method bullet points
- **ATS-Friendly Output**: Download polished DOCX resumes optimized for Applicant Tracking Systems
- **Command-Line Tool**: Batch processing for resume generation from JSON profiles
- **Privacy-First**: No data persistence, PII redaction in logs
- **Test-Driven**: Comprehensive test suite with golden-text validation

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)

### Installation

1. **Clone or download this repository**

```bash
cd Resume-Builder
```

2. **Create a virtual environment**

```bash
python -m venv venv

# On Linux/Mac:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Set up environment variables**

```bash
cp .env.example .env
```

Edit `.env` and configure:
- For **Mock AI** (default, no API key needed): `AI_PROVIDER=mock`
- For **OpenAI**: Set `AI_PROVIDER=openai` and add your `OPENAI_API_KEY`

5. **Create the resume template**

```bash
python scripts/create_template.py
```

This creates `templates/classic/Resume.docx` with the ATS-friendly template.

### Running the Web Application

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

### Using the Command-Line Tool

Generate a resume from a JSON profile:

```bash
python build_resume.py --in profile.sample.json --docx
```

With AI generation:

```bash
python build_resume.py --in profile.sample.json --docx --generate-ai
```

Custom output:

```bash
python build_resume.py --in profile.sample.json --docx --outdir ~/Desktop --output-filename my_resume
```

## 📖 Usage Guide

### Web Application Workflow

1. **Contact Information** (Step 1)
   - Enter your name, email, phone, and target civilian role
   - Add LinkedIn URL and location (optional)

2. **Military Background** (Step 2)
   - Search for your MOS codes
   - See real-time translation to civilian skills
   - Add multiple MOS codes if applicable

3. **Experience** (Step 3)
   - Add work/military experience entries
   - Use "Generate with AI" to create STAR-method bullets
   - Edit generated content as needed

4. **Education & Skills** (Step 4)
   - Add education history
   - Auto-populate skills from MOS codes
   - Add custom skills

5. **Review & Generate** (Step 5)
   - Generate AI summary
   - Review complete resume
   - Download as DOCX or export as JSON

### Creating a JSON Profile

See `profile.sample.json` for the complete structure. Key fields:

```json
{
  "contact": {
    "full_name": "Your Name",
    "email": "your.email@example.com",
    "phone": "5551234567",
    "city": "City",
    "state": "State"
  },
  "target_role": "Desired Position",
  "mos_codes": [
    {
      "code": "11B",
      "branch": "Army",
      "title": "Infantryman",
      "civilian_skills": ["Leadership", "Team coordination"]
    }
  ],
  "experience": [...],
  "education": [...],
  "skills": [...],
   "certifications": [...],
   "additional_info": {
      "veteran_experience": ["Mentor - American Corporate Partners (ACP)", "Member - Veterans in Cybersecurity"],
      "volunteer": ["Big Brothers Big Sisters"],
      "awards": ["Navy Achievement Medal"],
      "languages": ["English", "Spanish"]
   }
}
```

## 🏗️ Project Structure

```
Resume-Builder/
├── app.py                      # Streamlit web application
├── build_resume.py             # CLI tool
├── models.py                   # Pydantic data models
├── config.py                   # Configuration management
├── requirements.txt            # Python dependencies
├── pyproject.toml             # Project metadata
├── .env.example               # Environment template
├── profile.sample.json        # Sample resume data
│
├── services/                  # Core business logic
│   ├── mapping_service.py    # MOS translation
│   ├── ai_service.py         # AI content generation
│   └── resume_service.py     # DOCX generation
│
├── data/
│   └── mos_mapping.csv       # MOS to civilian mapping (50 entries)
│
├── templates/
│   └── classic/
│       └── Resume.docx       # ATS-friendly template
│
├── utils/
│   └── logging_utils.py      # PII-redacting logger
│
├── scripts/
│   └── create_template.py    # Template generation script
│
├── tests/                     # Test suite
│   ├── test_models.py
│   ├── test_mapping_service.py
│   ├── test_ai_service.py
│   ├── test_resume_service.py
│   ├── test_integration.py
│   ├── test_golden.py        # Golden-text validation
│   └── conftest.py
│
└── output/                    # Generated resumes (created automatically)
```

## 🧪 Running Tests

Run all tests with coverage:

```bash
pytest
```

Run specific test file:

```bash
pytest tests/test_models.py -v
```

Run with coverage report:

```bash
pytest --cov=services --cov=app --cov-report=html
```

View coverage report:

```bash
open htmlcov/index.html  # Mac/Linux
# or
start htmlcov/index.html  # Windows
```

### Golden Text Test

The golden text test validates that generated resumes match expected output:

```bash
pytest tests/test_golden.py -v
```

## 🔧 Development

### Code Quality

Format code with Black:

```bash
black app.py models.py services/ tests/
```

Lint with Ruff:

```bash
ruff check .
```

Type checking with mypy:

```bash
mypy services/ --ignore-missing-imports
```

### Adding New MOS Codes

Edit `data/mos_mapping.csv`:

```csv
CODE,BRANCH,TITLE,CIVILIAN_EQUIVALENT,SKILLS,KEYWORDS
35F,Army,Intelligence Analyst,Data Analyst,Intelligence analysis,Report writing,...
```

### Creating Custom Templates

1. Create new directory: `templates/my_template/`
2. Design `Resume.docx` with Jinja2 placeholders
3. Available template variables:
   - `{{ contact.name }}`, `{{ contact.email }}`, etc.
   - `{{ summary }}`
   - `{% for exp in experience %}...{% endfor %}`
   - `{% for edu in education %}...{% endfor %}`
   - `{{ edu.overview }}` (optional one-line program overview under an education entry)
   - `{% if veteran_experience %}{% for v in veteran_experience %}{{ v }}{% endfor %}{% endif %}` (optional veteran experience bullets)
   - `{% for skill in skills %}...{% endfor %}`

### AI Provider Configuration

**Mock Provider** (default, for development/testing):
```bash
AI_PROVIDER=mock
```

**OpenAI Provider**:
```bash
AI_PROVIDER=openai
OPENAI_API_KEY=sk-...
AI_MODEL=gpt-4
```

To add a new AI provider, extend the `AIProvider` class in `services/ai_service.py`.

## 📋 Requirements

### Must-Have Features (Implemented ✅)

- ✅ Streamlit UI with stepper-based form
- ✅ Live MOS → civilian skills preview
- ✅ AI-generated summary and STAR bullets (visible, editable, regenerate)
- ✅ DOCX download matching template layout
- ✅ MOS mapping service (50 entries)
- ✅ AI service with mock provider
- ✅ Resume generation with docxtpl
- ✅ CLI tool with same logic as UI
- ✅ ATS-friendly template
- ✅ Optional Education overview line
- ✅ Optional Veteran Experience section
- ✅ Pydantic v2 validation
- ✅ pytest with coverage
- ✅ Golden-text test
- ✅ PII redaction in logs

### Tech Stack

- **Frontend**: Streamlit with custom CSS
- **Backend**: Python 3.10+
- **Validation**: Pydantic v2
- **Document Generation**: docxtpl (Jinja2 + python-docx)
- **AI**: OpenAI API (optional) + Mock provider
- **Testing**: pytest, pytest-cov
- **Code Quality**: black, ruff, mypy

## 🎯 Acceptance Criteria

- [x] Enter data → see MOS skills → AI summary & bullets appear (editable) → Download DOCX
- [x] CLI writes DOCX for profile.sample.json
- [x] Golden-text test passes with mock AI
- [x] README steps reproduce on clean machine

## 🔒 Privacy & Security

- **No Persistence**: No database, no saved profiles
- **PII Redaction**: Automatic redaction of names, emails, phone numbers in logs
- **Local Processing**: All data processed locally (except AI API calls)
- **Mock AI**: Default provider requires no external API

## 🐛 Troubleshooting

### Template Not Found Error

Run the template creation script:
```bash
python scripts/create_template.py
```

### Import Errors

Ensure virtual environment is activated and dependencies installed:
```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### OpenAI API Errors

Check your API key in `.env`:
```bash
OPENAI_API_KEY=sk-your-actual-key-here
```

Or use mock provider:
```bash
AI_PROVIDER=mock
```

### Streamlit Not Opening

Manually open browser to: `http://localhost:8501`

## 📄 License

This is a proof-of-concept application. Use and modify as needed.

## 🤝 Contributing

This is an MVP. Potential enhancements:

- [ ] Additional templates (modern, creative, technical)
- [ ] PDF export
- [ ] More AI providers (Anthropic, Cohere, etc.)
- [ ] Database persistence (PostgreSQL)
- [ ] User authentication
- [ ] Resume versioning
- [ ] Cover letter generation
- [ ] LinkedIn profile import
- [ ] More MOS codes (1000+)
- [ ] Multi-language support

## 📞 Support

For issues with the application, review:
1. This README
2. Test files for usage examples
3. `profile.sample.json` for data structure
4. Code comments in `services/` modules

---

**Built with ❤️ for veterans transitioning to civilian careers**
