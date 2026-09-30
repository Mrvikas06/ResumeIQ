"""
AI Resume Intelligence — ML Pipeline
3 components: classifier, skill extractor, semantic matcher.

- Classifier: TF-IDF bigrams (10k features) + Logistic Regression
- Skill Extractor: regex keyword match against a curated vocabulary
- Semantic Matcher: TF-IDF cosine similarity (resume vs job description)
"""
import json, re, pickle, os
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.pipeline import Pipeline

# Use absolute paths anchored to the PROJECT root, not the file's location.
# This works whether called from uvicorn (cwd=project root) or directly.
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent   # ai-resume-intel/
DATA_DIR     = PROJECT_ROOT / "data"
MODEL_DIR    = PROJECT_ROOT / "backend" / "models" / "saved"
MODEL_DIR.mkdir(parents=True, exist_ok=True)


# ─── 1. RESUME CLASSIFIER ────────────────────────────────────────────────────

def train_classifier():
    """Train TF-IDF + LR classifier on the synthetic resume dataset."""
    train = pd.read_csv(DATA_DIR / "classification" / "train.csv")
    val   = pd.read_csv(DATA_DIR / "classification" / "validation.csv")
    test  = pd.read_csv(DATA_DIR / "classification" / "test.csv")

    clf = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), max_features=10000, sublinear_tf=True)),
        ("lr",    LogisticRegression(max_iter=1000, C=1.0)),
    ])
    clf.fit(train["resume_text"], train["category"])

    val_preds = clf.predict(val["resume_text"])
    print("=== Validation ===")
    print(classification_report(val["category"], val_preds))

    test_preds = clf.predict(test["resume_text"])
    print("=== Test ===")
    print(classification_report(test["category"], test_preds))

    with open(MODEL_DIR / "classifier.pkl", "wb") as f:
        pickle.dump(clf, f)
    print(f"Saved classifier.pkl → {MODEL_DIR / 'classifier.pkl'}")
    return clf


def load_classifier():
    """Load the trained classifier from disk."""
    model_path = MODEL_DIR / "classifier.pkl"
    if not model_path.exists():
        print(f"[WARNING] classifier.pkl not found at {model_path}. Training now...")
        return train_classifier()
    with open(model_path, "rb") as f:
        return pickle.load(f)


def classify_resume(text: str, clf=None) -> dict:
    """Classify a resume into one of 6 categories with confidence scores."""
    clf = clf or load_classifier()
    label = clf.predict([text])[0]
    proba = clf.predict_proba([text])[0]
    classes = clf.classes_
    return {
        "category":   label,
        "confidence": round(float(proba.max()), 3),
        "scores":     {c: round(float(p), 3) for c, p in zip(classes, proba)},
    }


# ─── 2. SKILL EXTRACTOR ──────────────────────────────────────────────────────

_skill_keywords_cache = None

def load_skill_keywords() -> list[str]:
    """Load the skill vocabulary from data/skills.json (cached)."""
    global _skill_keywords_cache
    if _skill_keywords_cache is None:
        skills_path = DATA_DIR / "skills.json"
        with open(skills_path) as f:
            _skill_keywords_cache = json.load(f)
    return _skill_keywords_cache


def extract_skills(text: str, skill_keywords: list[str] = None) -> list[str]:
    """
    Extract skills from text using regex keyword matching.
    This is a rule-based approach, NOT an ML model.
    """
    kws = skill_keywords or load_skill_keywords()
    text_lower = text.lower()
    found = []
    for skill in kws:
        pattern = r'\b' + re.escape(skill.lower()) + r'\b'
        if re.search(pattern, text_lower):
            found.append(skill)
    return sorted(set(found))


# ─── 3. SEMANTIC MATCHER ─────────────────────────────────────────────────────

def match_resume_to_job(resume_text: str, job_text: str,
                         required_skills: list[str] = None) -> dict:
    """
    Compute resume-to-job match using:
      - TF-IDF cosine similarity for semantic score
      - Keyword overlap for skill score
      - Weighted combination: 0.6 × semantic + 0.4 × skill_overlap
    """
    # Fresh vectorizer per call — fit_transform needs to see both docs together
    vec = TfidfVectorizer(ngram_range=(1, 2))
    matrix = vec.fit_transform([resume_text, job_text])
    semantic_score = float(cosine_similarity(matrix[0], matrix[1])[0][0])

    resume_skills = extract_skills(resume_text)
    job_skills    = required_skills or extract_skills(job_text)

    matched = [s for s in job_skills if s in resume_skills]
    missing = [s for s in job_skills if s not in resume_skills]

    skill_score = len(matched) / max(len(job_skills), 1)

    # Weighted: 60% semantic + 40% skill overlap
    overall = round((0.6 * semantic_score + 0.4 * skill_score) * 100, 1)

    return {
        "match_score":    overall,
        "semantic_score": round(semantic_score * 100, 1),
        "skill_score":    round(skill_score * 100, 1),
        "matched_skills": matched,
        "missing_skills": missing,
        "resume_skills":  resume_skills,
        "recommendation": f"Focus on: {', '.join(missing[:3])}" if missing else "Strong match.",
    }


# ─── FULL PIPELINE ────────────────────────────────────────────────────────────

def analyze(resume_text: str, job_text: str, clf=None) -> dict:
    """Run the complete analysis pipeline."""
    category = classify_resume(resume_text, clf)
    match    = match_resume_to_job(resume_text, job_text)
    return {**category, **match}


if __name__ == "__main__":
    sample_resume = (
        "Experienced ML engineer. Expert in Python, PyTorch, scikit-learn, "
        "Hugging Face transformers, and MLflow. Built NLP pipelines and deployed on AWS."
    )
    sample_job = (
        "Looking for AI/ML engineer with Python, PyTorch, deep learning, AWS, "
        "Kubernetes, and Terraform experience."
    )
    result = analyze(sample_resume, sample_job)
    print(json.dumps(result, indent=2))
