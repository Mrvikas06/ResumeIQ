"""FastAPI backend — AI Resume Intelligence API."""
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field
import sys, os, io
from pathlib import Path

# Resolve paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from models.pipeline import (
    classify_resume, extract_skills, match_resume_to_job,
    load_classifier, train_classifier, load_skill_keywords
)

# Optional PDF support
try:
    from pypdf import PdfReader
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False

app = FastAPI(title="AI Resume Intelligence", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend static files
frontend_dir = PROJECT_ROOT / "frontend"
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")

# Lazy-load classifier
_clf = None

def get_clf():
    global _clf
    if _clf is None:
        _clf = load_classifier()
    return _clf


# ─── Request / Response Models ────────────────────────────────────────────────

class AnalyzeRequest(BaseModel):
    resume_text: str = Field(..., min_length=1, max_length=100000, description="Resume text content")
    job_description: str = Field(..., min_length=1, max_length=100000, description="Job description text content")


class TextRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=100000, description="Input text")


# ─── Routes ───────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "healthy", "version": "1.0"}

@app.get("/")
def read_root():
    """Redirect to the frontend."""
    return RedirectResponse(url="/static/index.html")


@app.post("/api/v1/resume/analyze")
async def analyze_resume(body: AnalyzeRequest):
    """
    Main analysis endpoint.
    Runs: classifier + skill extraction + semantic matching.
    Returns classification, extracted skills, and matching results.
    """
    if not body.resume_text.strip():
        raise HTTPException(400, "resume_text cannot be empty")
    if not body.job_description.strip():
        raise HTTPException(400, "job_description cannot be empty")

    try:
        c = get_clf()
        classification = classify_resume(body.resume_text, c)
        extracted_skills = extract_skills(body.resume_text)
        matching = match_resume_to_job(body.resume_text, body.job_description)

        return {
            "classification": classification,
            "extracted_skills": extracted_skills,
            "matching": matching,
        }
    except Exception as e:
        raise HTTPException(500, f"Analysis failed: {str(e)}")


@app.get("/api/v1/skills")
def get_skills_vocab():
    """
    Return the curated list of recognized technical skills.
    """
    skills = load_skill_keywords()
    return {"skills": skills, "count": len(skills)}


@app.post("/api/v1/skills/extract")
async def extract_skills_endpoint(body: TextRequest):
    """
    Extract technical skills from text using boundary-safe regex matching.
    """
    if not body.text.strip():
        raise HTTPException(400, "text cannot be empty")
    skills = extract_skills(body.text)
    return {"skills": skills, "count": len(skills)}


@app.post("/api/v1/resume/classify")
async def classify_resume_endpoint(body: TextRequest):
    """
    Classify resume text into one of 6 industry categories with confidence scores.
    """
    if not body.text.strip():
        raise HTTPException(400, "text cannot be empty")
    try:
        c = get_clf()
        classification = classify_resume(body.text, c)
        return classification
    except Exception as e:
        raise HTTPException(500, f"Classification failed: {str(e)}")


@app.post("/api/v1/resume/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a PDF or TXT file and extract its text content.
    Returns the extracted text for the frontend to display in the textarea.
    """
    allowed = {".pdf", ".txt"}
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in allowed:
        raise HTTPException(400, f"File type '{ext}' not supported. Use: {', '.join(allowed)}")

    content = await file.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(400, "File too large. Maximum size is 5MB.")
    if len(content) == 0:
        raise HTTPException(400, "File is empty.")

    text = ""
    if ext == ".pdf":
        if not PDF_SUPPORT:
            raise HTTPException(400, "PDF support not installed. Run: pip install pypdf")
        try:
            reader = PdfReader(io.BytesIO(content))
            pages = [page.extract_text() for page in reader.pages if page.extract_text()]
            text = " ".join(pages)
        except Exception as e:
            raise HTTPException(400, f"Error parsing PDF: {str(e)}")
    else:
        text = content.decode("utf-8", errors="ignore")

    if not text.strip():
        raise HTTPException(400, "No text could be extracted from the file.")

    return {
        "filename": file.filename,
        "text_preview": text,
        "char_count": len(text),
    }


@app.get("/api/v1/models")
def list_models():
    """List the ML models used in the pipeline."""
    return {
        "models": [
            {
                "name": "Resume Classifier",
                "type": "TF-IDF (bigrams, 10k features) + Logistic Regression",
                "version": "1.0",
                "classes": ["AI/ML", "Software Development", "Data Science",
                            "Cloud/DevOps", "Cybersecurity", "Data Engineering"],
                "status": "loaded" if _clf is not None else "not_loaded",
            },
            {
                "name": "Skill Extractor",
                "type": "Rule-based regex keyword matching",
                "version": "1.0",
                "vocab_size": 64,
                "status": "available",
            },
            {
                "name": "Semantic Matcher",
                "type": "TF-IDF cosine similarity",
                "version": "1.0",
                "formula": "0.6 × semantic_score + 0.4 × skill_overlap",
                "status": "available",
            },
        ]
    }
