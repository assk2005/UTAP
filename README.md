# UTAP — Unified Talent Acquisition Platform

UTAP is a Django-based **end-to-end talent acquisition platform** that brings recruitment, resume screening, skill assessment, and AI-assisted video interviews into a single workflow.

## Overview

UTAP is designed around the complete candidate journey:

**Job Discovery → Application → Resume Screening → Skill Assessment → Video Interview → Candidate Evaluation**

The platform provides separate workflows for **Candidates, Recruiters, and Administrators**, with an AI-powered resume evaluation pipeline and automated interview analysis.

## Key Features

### Candidate
- Register and manage a candidate profile
- Browse available job openings
- Apply for jobs
- Upload resumes in PDF/DOCX/TXT formats
- Receive resume-based skill matching
- Complete skill-based MCQ assessments
- Complete coding/output-based assessments
- Participate in browser-based video interviews
- View assessment and interview results

### Recruiter
- Register and receive administrator approval
- Create and manage job postings
- Review applicants
- View candidate resume evaluation results
- View assessment status and scores
- View interview results
- Review ranked applicants

### Administrator
- Manage users
- Approve recruiter accounts
- Manage candidates and recruiters
- Access platform administration through Django Admin

## AI / ML Components

### Resume Evaluation Engine

The resume engine processes candidate resumes through multiple stages:

1. **Text Extraction**
   - PDF extraction using PyMuPDF
   - DOCX extraction using `python-docx`

2. **Preprocessing**
   - Text cleaning
   - Language detection
   - Resume preprocessing

3. **Experience Analysis**
   - Extracts experience-related information from resume text

4. **Semantic Skill Matching**
   - Uses `sentence-transformers`
   - Compares resume content with job/skill requirements using semantic similarity

5. **Scoring**
   - Combines extracted information and skill-matching signals into an overall evaluation

### AI-Assisted Video Interview

The interview module combines:

- **OpenAI Whisper** for speech-to-text
- **DeepFace** for facial/emotion analysis
- **OpenCV** for video-frame processing
- **MoviePy** for audio extraction

The interview workflow requires a webcam and microphone in the browser.

## Skill Assessment

UTAP includes both:

- **MCQ assessments** using JSON-based question banks
- **Coding/output-based assessments**

Question banks currently cover areas including:

- Python
- C++
- Java
- SQL
- Data Structures
- Operating Systems
- Computer Networks
- Machine Learning
- Django
- Web Development

## Technology Stack

| Layer | Technologies |
|---|---|
| Backend | Python, Django |
| APIs | Django REST Framework, Simple JWT |
| Database | SQLite |
| Resume Processing | PyMuPDF, python-docx |
| NLP / Semantic Matching | Sentence Transformers, Scikit-learn, NumPy |
| Speech Processing | OpenAI Whisper |
| Video / Vision | OpenCV, DeepFace |
| Video Processing | MoviePy, FFmpeg |
| Frontend | HTML, CSS, JavaScript |
| Data Storage | JSON question banks |
| Development | Git, GitHub |

## Architecture

```text
                         ┌──────────────────────┐
                         │       UTAP           │
                         │ Talent Acquisition   │
                         │      Platform        │
                         └──────────┬───────────┘
                                    │
             ┌──────────────────────┼──────────────────────┐
             │                      │                      │
             ▼                      ▼                      ▼
       ┌───────────┐          ┌────────────┐         ┌────────────┐
       │ Candidate │          │ Recruiter  │         │   Admin    │
       └─────┬─────┘          └─────┬──────┘         └─────┬──────┘
             │                      │                      │
             └──────────────────────┼──────────────────────┘
                                    ▼
                         ┌──────────────────────┐
                         │    Django Backend    │
                         └──────────┬───────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              │                     │                     │
              ▼                     ▼                     ▼
       ┌─────────────┐      ┌─────────────┐      ┌─────────────┐
       │ Resume      │      │ Assessment  │      │ Interview   │
       │ Engine      │      │ Engine      │      │ Engine      │
       └──────┬──────┘      └──────┬──────┘      └──────┬──────┘
              │                    │                    │
              ▼                    ▼                    ▼
       Semantic Skill       MCQ + Coding        Whisper +
       Matching + Scoring   Evaluation           DeepFace
```

## Project Structure

```text
UTAP/
├── project/                    # Django project configuration
├── accounts/                   # Users, jobs, applications, recruiter workflows
├── resume_engine/              # Resume processing and AI evaluation
│   └── services/
│       ├── processor.py        # Resume-processing orchestrator
│       ├── text_extractor.py   # PDF/DOCX/TXT extraction
│       ├── preprocessing.py    # Resume preprocessing
│       ├── experience_engine.py# Experience extraction
│       ├── semantic_engine.py  # Semantic skill matching
│       └── scoring_engine.py   # Evaluation scoring
├── assessment/                 # MCQ and coding/output assessments
│   ├── question_bank/          # Skill-specific question banks
│   └── output_Questions/       # Coding/output question data
├── interview/                  # Video interview processing
├── templates/                  # Django HTML templates
├── static/                     # JavaScript and static assets
├── requirements.txt            # Python dependencies
├── manage.py                   # Django management entry point
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.9+
- FFmpeg
- Webcam and microphone for the interview module
- Internet connection for first-time AI model downloads

### 1. Clone the repository

```bash
git clone https://github.com/assk2005/UTAP.git
cd UTAP
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

**Windows:**

```bash
venv\Scripts\activate
```

**macOS / Linux:**

```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the Django secret key

For local development, the application has a development fallback.

For a custom secret, set:

**Windows PowerShell:**

```powershell
$env:DJANGO_SECRET_KEY="your-secret-key"
```

**macOS / Linux:**

```bash
export DJANGO_SECRET_KEY="your-secret-key"
```

Do not commit `.env` files or production secrets to GitHub.

### 5. Apply migrations

```bash
python manage.py migrate
```

### 6. Create an administrator

```bash
python manage.py createsuperuser
```

### 7. Start the server

```bash
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

Django Admin:

```text
http://127.0.0.1:8000/admin/
```

## FFmpeg Setup

FFmpeg is required for audio extraction from interview videos.

**Windows:**

```bash
winget install ffmpeg
```

**macOS:**

```bash
brew install ffmpeg
```

**Ubuntu / Debian:**

```bash
sudo apt install ffmpeg
```

Restart the terminal after installation so the executable is available on `PATH`.

## AI Model Downloads

Some components download model weights the first time they are used:

- Whisper downloads its speech-recognition model
- DeepFace downloads required model weights

The exact download size and startup time depend on the selected models and environment.

## Environment & Security

The repository intentionally excludes local/runtime data such as:

- `.env`
- `db.sqlite3`
- `media/`
- `venv/`
- `__pycache__/`
- IDE-specific files

The Django secret key is read from the `DJANGO_SECRET_KEY` environment variable when provided.

## Project Status

UTAP is a completed academic major-project implementation and is maintained as a portfolio/research project.

## License

No open-source license has been added to this repository yet.
