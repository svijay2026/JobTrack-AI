import pytest
from app.core.nlp.matcher import matcher


def test_tokenize():
    text = "We are seeking a Senior Python Developer with FastAPI and Docker skills."
    tokens = matcher.tokenize(text)
    assert "senior" in tokens
    assert "python" in tokens
    assert "developer" in tokens
    assert "fastapi" in tokens
    assert "docker" in tokens
    # Verify stopwords are removed
    assert "we" not in tokens
    assert "are" not in tokens
    assert "with" not in tokens


def test_tf_idf_cosine_similarity():
    text_a = "Senior Python Backend Engineer skilled in FastAPI, Docker, and PostgreSQL databases."
    text_b = "Looking for a Python Backend Engineer with experience in FastAPI and PostgreSQL."
    text_c = "Experienced Chef specializing in French cuisine and pastry preparation."

    sim_ab = matcher.compute_tf_idf_cosine_similarity(text_a, text_b)
    sim_ac = matcher.compute_tf_idf_cosine_similarity(text_a, text_c)

    assert 0.4 <= sim_ab <= 1.0
    assert sim_ac <= 0.1
    assert sim_ab > sim_ac


def test_compute_skill_overlap():
    candidate_skills = ["Python", "FastAPI", "Docker", "PostgreSQL", "React"]
    job_description = """
    We need an engineer experienced with Python, FastAPI, Docker, AWS, and Kubernetes.
    """
    matching, missing, score = matcher.compute_skill_overlap(candidate_skills, job_description)

    assert "Python" in matching
    assert "FastAPI" in matching
    assert "Docker" in matching
    assert "AWS" in missing
    assert "Kubernetes" in missing
    assert score == 60.0  # 3 matching out of 5 required


def test_experience_alignment():
    # Candidate with 5 years
    assert matcher.compute_experience_alignment(candidate_years=5.0, required_years=3.0) == 100.0
    assert matcher.compute_experience_alignment(candidate_years=2.0, required_years=4.0) == 50.0
    assert matcher.compute_experience_alignment(candidate_years=5.0, required_years=0.0) == 100.0


def test_analyze_match_pipeline():
    resume_text = "Senior Python Developer with 5 years experience in FastAPI, Docker, PostgreSQL, and Microservices."
    candidate_skills = ["Python", "FastAPI", "Docker", "PostgreSQL"]
    candidate_years = 5.0

    job_description = "Seeking a Python Engineer with 3+ years experience in Python, FastAPI, Docker, AWS, and Microservices."

    result = matcher.analyze_match(
        resume_text=resume_text,
        candidate_skills=candidate_skills,
        candidate_experience_years=candidate_years,
        job_description=job_description,
    )

    assert 50.0 <= result["match_score"] <= 100.0
    assert result["skill_match_score"] > 0
    assert result["semantic_score"] > 0
    assert result["experience_score"] == 100.0
    assert "Python" in result["matching_skills"]
    assert "AWS" in result["missing_skills"]
    assert len(result["recommendations"]) > 0
    assert len(result["summary"]) > 0


def test_generate_cover_letter():
    candidate_skills = ["Python", "FastAPI", "React", "Docker"]
    letter_data = matcher.generate_cover_letter(
        candidate_skills=candidate_skills,
        candidate_experience_years=4.0,
        company_name="InnovateTech",
        job_title="Senior Developer",
        job_description="Looking for Senior Developer with Python and FastAPI experience.",
        tone="professional",
    )

    assert letter_data["company_name"] == "InnovateTech"
    assert letter_data["job_title"] == "Senior Developer"
    assert "InnovateTech" in letter_data["cover_letter"]
    assert "Senior Developer" in letter_data["cover_letter"]
    assert len(letter_data["key_highlights"]) > 0

