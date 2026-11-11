"""Integration tests for FastAPI endpoints."""
import pytest
import sys
from pathlib import Path
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

from app.main import app

client = TestClient(app)


def test_health_endpoint():
    """Verify health check endpoint returns 200 and healthy status."""
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "healthy", "version": "1.0"}


def test_root_redirect():
    """Verify root path redirects to static index."""
    res = client.get("/", follow_redirects=False)
    assert res.status_code == 307
    assert res.headers["location"] == "/static/index.html"


def test_index_redirect():
    """Verify /index.html redirects to static index."""
    res = client.get("/index.html", follow_redirects=False)
    assert res.status_code == 307
    assert res.headers["location"] == "/static/index.html"


def test_models_endpoint():
    """Verify models metadata endpoint."""
    res = client.get("/api/v1/models")
    assert res.status_code == 200
    data = res.json()
    assert "models" in data
    assert len(data["models"]) >= 3


def test_skills_vocab_endpoint():
    """Verify skills vocabulary endpoint returns list."""
    res = client.get("/api/v1/skills")
    assert res.status_code == 200
    data = res.json()
    assert "skills" in data
    assert data["count"] >= 50
    assert "Python" in data["skills"]


def test_skills_extract_endpoint():
    """Verify skill extraction endpoint."""
    res = client.post("/api/v1/skills/extract", json={"text": "Proficient in Python, AWS, and Docker."})
    assert res.status_code == 200
    data = res.json()
    assert set(data["skills"]) == {"AWS", "Docker", "Python"}
    assert data["count"] == 3


def test_skills_extract_empty_validation():
    """Verify error on empty extraction text."""
    res = client.post("/api/v1/skills/extract", json={"text": "   "})
    assert res.status_code == 400


def test_resume_classify_endpoint():
    """Verify resume classification endpoint."""
    res = client.post("/api/v1/resume/classify", json={"text": "Cloud Engineer skilled in AWS, Terraform, Docker, and Kubernetes."})
    assert res.status_code == 200
    data = res.json()
    assert data["category"] == "Cloud/DevOps"
    assert "scores" in data
    assert "confidence" in data


def test_resume_analyze_endpoint():
    """Verify complete analysis endpoint."""
    payload = {
        "resume_text": "AI Engineer skilled in Python, PyTorch, transformers, and NLP.",
        "job_description": "Seeking AI/ML engineer with Python, PyTorch, and deep learning."
    }
    res = client.post("/api/v1/resume/analyze", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "classification" in data
    assert "extracted_skills" in data
    assert "matching" in data
    assert data["classification"]["category"] == "AI/ML"
    assert data["matching"]["match_score"] > 0


def test_resume_analyze_empty_inputs():
    """Verify error on empty resume text."""
    res = client.post("/api/v1/resume/analyze", json={"resume_text": "   ", "job_description": "Valid job description"})
    assert res.status_code == 400


def test_file_upload_txt():
    """Verify text file upload and extraction."""
    files = {"file": ("test_resume.txt", b"Software Engineer with Java, React, and SQL.", "text/plain")}
    res = client.post("/api/v1/resume/upload", files=files)
    assert res.status_code == 200
    data = res.json()
    assert data["filename"] == "test_resume.txt"
    assert "Java" in data["text_preview"]
    assert data["char_count"] > 0


def test_file_upload_empty():
    """Verify empty file is rejected."""
    files = {"file": ("empty.txt", b"", "text/plain")}
    res = client.post("/api/v1/resume/upload", files=files)
    assert res.status_code == 400


def test_file_upload_invalid_type():
    """Verify unsupported file types are rejected."""
    files = {"file": ("malicious.exe", b"binary content", "application/octet-stream")}
    res = client.post("/api/v1/resume/upload", files=files)
    assert res.status_code == 400


def test_not_found_handling():
    """Verify 404 responses for JSON and HTML requests."""
    res_json = client.get("/api/v1/unknown", headers={"Accept": "application/json"})
    assert res_json.status_code == 404
    assert res_json.json() == {"detail": "Not Found"}

    res_html = client.get("/unknown-page", headers={"Accept": "text/html"})
    assert res_html.status_code == 404
    assert "404" in res_html.text
