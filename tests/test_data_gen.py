"""Tests for data generation logic and dataset integrity."""
import pytest
import sys
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.gen_data import CATEGORIES, TEMPLATES

EXPECTED_CATEGORIES = {
    "AI/ML",
    "Software Development",
    "Data Science",
    "Cloud/DevOps",
    "Cybersecurity",
    "Data Engineering"
}


def test_categories_structure():
    """Verify category mapping contains required tech domains and skills."""
    assert set(CATEGORIES.keys()) == EXPECTED_CATEGORIES
    for cat, skills in CATEGORIES.items():
        assert len(skills) >= 6, f"{cat} must have at least 6 skills"
        for s in skills:
            assert isinstance(s, str) and len(s) > 0


def test_templates_placeholders():
    """Verify templates contain required placeholders."""
    for tmpl in TEMPLATES:
        assert "{cat}" in tmpl
        assert "{s1}" in tmpl
        assert "{s2}" in tmpl
        assert "{s3}" in tmpl


def test_existing_datasets():
    """Verify pre-generated datasets are non-empty and well-formed."""
    data_dir = ROOT / "data" / "classification"
    for name in ["train.csv", "validation.csv", "test.csv"]:
        path = data_dir / name
        assert path.exists(), f"{name} must exist"
        df = pd.read_csv(path)
        assert "resume_text" in df.columns
        assert "category" in df.columns
        assert len(df) > 0
        assert df["resume_text"].isna().sum() == 0
        assert df["category"].isna().sum() == 0
        unique_cats = set(df["category"].unique())
        assert unique_cats.issubset(EXPECTED_CATEGORIES)
