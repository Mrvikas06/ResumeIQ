"""Unit tests for ML pipeline components."""
import pytest
import sys
from pathlib import Path

# Anchored import
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

from models.pipeline import (
    classify_resume,
    extract_skills,
    match_resume_to_job,
    load_classifier,
    load_skill_keywords,
    analyze,
    DEFAULT_SKILLS
)


def test_load_skills():
    """Verify skill keywords load correctly."""
    skills = load_skill_keywords()
    assert isinstance(skills, list)
    assert len(skills) >= 50
    assert "Python" in skills
    assert "Docker" in skills


def test_extract_skills_standard():
    """Verify standard skill extraction."""
    text = "Candidate has strong proficiency in Python, Docker, Kubernetes, and AWS."
    skills = extract_skills(text)
    assert "Python" in skills
    assert "Docker" in skills
    assert "Kubernetes" in skills
    assert "AWS" in skills


def test_extract_skills_special_characters():
    """Verify skills with special symbols like C++, CI/CD, and Node.js."""
    text = "Proficient in C++, CI/CD pipelines, Node.js, and A/B testing."
    skills = extract_skills(text)
    assert "C++" in skills
    assert "CI/CD" in skills
    assert "Node.js" in skills
    assert "A/B testing" in skills


def test_extract_skills_word_boundaries():
    """Verify word boundary checks avoid false positives."""
    text = "Reacting to events in JavaScript with Regular expressions."
    skills = extract_skills(text)
    assert "React" not in skills
    assert "Java" not in skills
    assert "R" not in skills


def test_classify_resume():
    """Verify resume classification output structure and values."""
    clf = load_classifier()
    text = "Senior Machine Learning Engineer specializing in PyTorch, transformers, NLP, and MLflow."
    result = classify_resume(text, clf)
    assert "category" in result
    assert "confidence" in result
    assert "scores" in result
    assert result["category"] == "AI/ML"
    assert 0.0 <= result["confidence"] <= 1.0
    assert len(result["scores"]) == 6
    assert abs(sum(result["scores"].values()) - 1.0) < 0.05


def test_match_resume_to_job():
    """Verify semantic matching and ATS scoring formula."""
    resume = "Experienced with Python, PyTorch, Docker, and AWS. Built NLP models."
    job = "Looking for an engineer with Python, PyTorch, Kubernetes, and Docker experience."
    res = match_resume_to_job(resume, job)
    assert "match_score" in res
    assert "semantic_score" in res
    assert "skill_score" in res
    assert "matched_skills" in res
    assert "missing_skills" in res
    assert "Python" in res["matched_skills"]
    assert "Docker" in res["matched_skills"]
    assert "Kubernetes" in res["missing_skills"]
    assert res["match_score"] > 0


def test_empty_and_punctuation_handling():
    """Verify graceful handling of non-text inputs without crashing."""
    res = match_resume_to_job("!@#$%", "^&*()")
    assert res["semantic_score"] == 0.0
    assert res["match_score"] == 0.0
    assert res["matched_skills"] == []


def test_analyze_pipeline():
    """Verify full end-to-end analyze pipeline."""
    resume = "Data Engineer with Apache Spark, Airflow, and BigQuery."
    job = "Data Engineering role requiring Apache Spark and Kafka."
    res = analyze(resume, job)
    assert res["category"] == "Data Engineering"
    assert "Apache Spark" in res["matched_skills"]
    assert "Kafka" in res["missing_skills"]
