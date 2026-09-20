# UTAP — Unified Talent Acquisition Platform

A Django-based recruitment automation system that takes a candidate from job application all the way through resume screening, skill assessment, and AI-powered video interview.

---

## Project Structure

```
UTAP/
├── project/                  # Django project config (settings, root urls)
├── accounts/                 # Users, Jobs, Applications, Recruiter Profiles
├── resume_engine/            # AI resume evaluation pipeline
│   └── services/
│       ├── processor.py      # Orchestrator — calls all engines
│       ├── text_extractor.py # PDF / DOCX / TXT extraction
│       ├── preprocessing.py  # Clean, anonymize, language detect
│       ├── experience_engine.py  # Date-range + phrase experience extraction
│       ├── semantic_engine.py    # Skill scoring via sentence-transformers
│       └── scoring_engine.py    # Final weighted score
├── assessment/               # MCQ + coding output tests
│   ├── question_bank/        # Per-skill JSON question files
│   └── output_Questions/     # Coding output question JSON files
├── interview/                # AI video interview (Whisper + DeepFace)
├── templates/                # All HTML templates (central)
│   ├── accounts/
│   ├── registration/
│   ├── assessment/
│   └── interview/
├── static/                   # CSS, JS, images (central)
│   ├── assets/
│   └── js/
├── media/                    # Uploaded files at runtime (gitignored)
├── requirements.txt
└── manage.py
```

---

## Setup

### 1. Create and activate a virtual environment
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate
```

### 2. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 3. Install FFmpeg (required for interview audio extraction)
FFmpeg is a system tool, not a Python package — install it separately.

**Windows:**
```bash
winget install ffmpeg
```
**Mac:**
```bash
brew install ffmpeg
```
**Linux:**
```bash
sudo apt install ffmpeg
```
After installing, restart your terminal so the PATH updates.

### 4. Run migrations
```bash
python manage.py migrate
```

### 5. Create a superuser (admin)
```bash
python manage.py createsuperuser
```

### 6. Seed the Resume Engine config
Go to `http://127.0.0.1:8000/admin/` → **Engine Configs** → Add one row with default values.

### 7. Run the development server
```bash
python manage.py runserver
```

---

## User Roles & Flow

| Role | Flow |
|---|---|
| **Admin** | Login → Approve recruiters → Manage users |
| **Recruiter** | Register → Await approval → Post jobs → View ranked applicants |
| **Candidate** | Register → Browse jobs → Apply → Upload resume → Take MCQ test → Do video interview |

---

## Known Issues Fixed in This Version
- `job_rankings` view was missing — now added
- `assessment/models.py` had a duplicate `TestResult` class — removed
- `resume_engine/services/preprocessing.py` had duplicated function definitions — cleaned up
- `mcq_system/` (dead legacy config) — removed
- Templates and static files consolidated to root-level folders
- `interview.js` static path was incorrect — fixed
- `FileExistsError` on Windows during interview video rename — fixed
- Interview result page had no navigation back to dashboard — fixed
- Candidate dashboard now shows Interview Score column — added
- Recruiter applications page now shows Interview Score and Test status — added

---

## Notes
- Whisper downloads the `base` model (~150 MB) on first use — internet required
- DeepFace downloads face detection weights on first use — internet required
- The interview module requires a webcam and microphone in the browser
- FFmpeg must be installed at system level for audio extraction to work
