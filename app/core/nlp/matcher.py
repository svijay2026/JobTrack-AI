import math
import re
from collections import Counter
from typing import Any, Dict, List, Set, Tuple

from app.services.resume_parser import resume_parser

# Common English stopwords to filter during lexical analysis
STOPWORDS: Set[str] = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't",
    "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", "by",
    "can", "can't", "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't", "doing",
    "don't", "down", "during", "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't",
    "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here", "here's", "hers", "herself",
    "him", "himself", "his", "how", "how's", "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is",
    "isn't", "it", "it's", "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself",
    "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought", "our", "ours",
    "ourselves", "out", "over", "own", "same", "shan't", "she", "she'd", "she'll", "she's", "should",
    "shouldn't", "so", "some", "such", "than", "that", "that's", "the", "their", "theirs", "them",
    "themselves", "then", "there", "there's", "these", "they", "they'd", "they'll", "they're", "they've",
    "this", "those", "through", "to", "too", "under", "until", "up", "very", "was", "wasn't", "we",
    "we'd", "we'll", "we're", "we've", "were", "weren't", "what", "what's", "when", "when's", "where",
    "where's", "which", "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would",
    "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves"
}


class ResumeJobMatcher:
    """
    AI/NLP engine for calculating multi-dimensional match scores between
    a candidate's resume and a target job description.
    """

    def tokenize(self, text: str) -> List[str]:
        """Tokenizes text into cleaned alphanumeric words, removing stopwords."""
        words = re.findall(r"\b[a-zA-Z0-9+#.-]+\b", text.lower())
        return [w for w in words if w not in STOPWORDS and len(w) > 1]

    def compute_tf_idf_cosine_similarity(self, text_a: str, text_b: str) -> float:
        """
        Computes TF-IDF Cosine Similarity (0.0 to 1.0) between two text documents.
        """
        tokens_a = self.tokenize(text_a)
        tokens_b = self.tokenize(text_b)

        if not tokens_a or not tokens_b:
            return 0.0

        tf_a = Counter(tokens_a)
        tf_b = Counter(tokens_b)

        vocabulary = set(tf_a.keys()).union(set(tf_b.keys()))
        doc_count = 2

        vector_a = []
        vector_b = []

        for term in vocabulary:
            df = (1 if term in tf_a else 0) + (1 if term in tf_b else 0)
            idf = math.log((doc_count + 1) / (df + 1)) + 1.0

            val_a = (tf_a.get(term, 0) / len(tokens_a)) * idf
            val_b = (tf_b.get(term, 0) / len(tokens_b)) * idf

            vector_a.append(val_a)
            vector_b.append(val_b)

        # Dot product
        dot_product = sum(a * b for a, b in zip(vector_a, vector_b))
        norm_a = math.sqrt(sum(a * a for a in vector_a))
        norm_b = math.sqrt(sum(b * b for b in vector_b))

        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0

        similarity = dot_product / (norm_a * norm_b)
        return min(max(similarity, 0.0), 1.0)

    def extract_required_experience_years(self, text: str) -> float:
        """Extracts required years of experience from job description."""
        patterns = [
            r"(\d+(?:\.\d+)?)\+?\s*(?:years|yrs)\s+(?:of\s+)?experience",
            r"(\d+)\s*(?:-|to)\s*(\d+)\s*(?:years|yrs)",
            r"minimum\s+(?:of\s+)?(\d+)\s*(?:years|yrs)",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1))
                except (ValueError, IndexError):
                    continue

        return 0.0

    def compute_skill_overlap(
        self, candidate_skills: List[str], job_description: str
    ) -> Tuple[List[str], List[str], float]:
        """
        Extracts required skills from job description and computes
        matching skills, missing skills, and skill match percentage.
        """
        jd_skills = resume_parser.extract_skills(job_description)
        candidate_skills_set = {s.lower(): s for s in candidate_skills}

        matching: List[str] = []
        missing: List[str] = []

        for skill in jd_skills:
            if skill.lower() in candidate_skills_set:
                matching.append(skill)
            else:
                missing.append(skill)

        if not jd_skills:
            # If job description didn't specify distinct keywords, default score to 80%
            return [], [], 80.0

        score = (len(matching) / len(jd_skills)) * 100.0
        return matching, missing, round(score, 1)

    def compute_experience_alignment(
        self, candidate_years: float, required_years: float
    ) -> float:
        """Computes experience alignment score (0 to 100%)."""
        if required_years <= 0.0:
            return 100.0

        if candidate_years >= required_years:
            return 100.0

        ratio = (candidate_years / required_years) * 100.0
        return max(round(ratio, 1), 25.0)

    def generate_recommendations(
        self,
        overall_score: float,
        missing_skills: List[str],
        matching_skills: List[str],
        candidate_years: float,
        required_years: float,
    ) -> List[str]:
        """Generates actionable recommendations to optimize resume for target job."""
        recommendations: List[str] = []

        if missing_skills:
            top_missing = missing_skills[:5]
            recommendations.append(
                f"Add explicit experience or projects highlighting your knowledge of: {', '.join(top_missing)}."
            )

        if required_years > 0 and candidate_years < required_years:
            recommendations.append(
                f"The job requires ~{int(required_years)} years of experience (your resume indicates ~{int(candidate_years)}). Highlight high-impact projects and fast career progression to demonstrate senior capability."
            )

        if overall_score >= 80.0:
            recommendations.append(
                "Strong alignment! Make sure your top matching skills appear in the top third of your resume for maximum recruiter visibility."
            )
        elif overall_score >= 60.0:
            recommendations.append(
                "Moderate alignment. Tailor your bullet points using the exact terminology from the job description."
            )
        else:
            recommendations.append(
                "Significant keyword gap detected. Incorporate the missing technical requirements into your experience section before applying."
            )

        return recommendations

    def analyze_match(
        self,
        resume_text: str,
        candidate_skills: List[str],
        candidate_experience_years: float,
        job_description: str,
        job_title: str = "",
    ) -> Dict[str, Any]:
        """
        Executes complete match analysis pipeline.
        Returns comprehensive match score breakdown, skill gaps, and recommendations.
        """
        # 1. Skill Overlap Analysis (50% weight)
        matching_skills, missing_skills, skill_score = self.compute_skill_overlap(
            candidate_skills=candidate_skills, job_description=job_description
        )

        # 2. Semantic & Lexical TF-IDF Relevance (35% weight)
        cosine_sim = self.compute_tf_idf_cosine_similarity(
            text_a=resume_text, text_b=job_description
        )
        semantic_score = round(cosine_sim * 100.0, 1)

        # 3. Experience Alignment (15% weight)
        required_years = self.extract_required_experience_years(job_description)
        experience_score = self.compute_experience_alignment(
            candidate_years=candidate_experience_years, required_years=required_years
        )

        # 4. Overall Weighted Score
        overall_score = round(
            (0.50 * skill_score) + (0.35 * semantic_score) + (0.15 * experience_score), 1
        )
        overall_score = min(max(overall_score, 0.0), 100.0)

        # 5. Recommendations & Summary
        recommendations = self.generate_recommendations(
            overall_score=overall_score,
            missing_skills=missing_skills,
            matching_skills=matching_skills,
            candidate_years=candidate_experience_years,
            required_years=required_years,
        )

        if overall_score >= 80.0:
            summary = f"Excellent Match ({overall_score}%). Your resume is well-suited for this position."
        elif overall_score >= 60.0:
            summary = f"Good Potential ({overall_score}%). Minor adjustments to missing skills will strengthen your application."
        else:
            summary = f"Low Alignment ({overall_score}%). Several required skills or domain terms are missing from your resume."

        return {
            "match_score": overall_score,
            "skill_match_score": skill_score,
            "semantic_score": semantic_score,
            "experience_score": experience_score,
            "matching_skills": matching_skills,
            "missing_skills": missing_skills,
            "required_experience_years": required_years,
            "candidate_experience_years": candidate_experience_years,
            "recommendations": recommendations,
            "summary": summary,
        }

    def generate_cover_letter(
        self,
        candidate_skills: List[str],
        candidate_experience_years: float,
        company_name: str,
        job_title: str,
        job_description: str,
        tone: str = "professional",
    ) -> Dict[str, Any]:
        """
        Generates a tailored cover letter and key application highlights
        synthesizing candidate skills and target job description requirements.
        """
        matching_skills, _, _ = self.compute_skill_overlap(candidate_skills, job_description)
        top_skills = matching_skills[:4] if matching_skills else candidate_skills[:4]
        skills_phrase = ", ".join(top_skills) if top_skills else "software engineering and modern technology frameworks"

        exp_str = f"{candidate_experience_years:.1f} years" if candidate_experience_years > 0 else "extensive hands-on project"

        if tone.lower() == "enthusiastic":
            opening = f"I am thrilled to submit my application for the {job_title} role at {company_name}! Having followed {company_name}'s innovation in the industry, I am eager to bring my expertise in {skills_phrase} to your engineering team."
            closing = f"I am extremely excited about the prospect of contributing to {company_name}'s mission. I look forward to discussing how my background and enthusiasm align with your team's goals."
        elif tone.lower() == "concise":
            opening = f"Please accept this application for the {job_title} position at {company_name}. With {exp_str} of experience specializing in {skills_phrase}, I am confident in my ability to deliver immediate value."
            closing = f"Thank you for reviewing my application. I welcome the opportunity to discuss my qualifications for the {job_title} position further."
        else: # professional
            opening = f"I am writing to express my strong interest in the {job_title} position at {company_name}. With over {exp_str} of proven technical experience and demonstrated competency in {skills_phrase}, I am well-prepared to contribute effectively to your organization."
            closing = f"Thank you for your time and consideration. I welcome the opportunity to interview and discuss how my technical expertise in {skills_phrase} can advance {company_name}'s objectives."

        body = (
            f"Throughout my career, I have focused on designing scalable solutions, driving clean code standards, "
            f"and optimizing performance. My core competencies in {skills_phrase} directly align with the requirements "
            f"outlined in your posting for the {job_title} role. I excel at bridging technical implementation with business outcomes, "
            f"ensuring robust software architecture and efficient development lifecycles."
        )

        full_letter = f"Dear Hiring Manager,\n\n{opening}\n\n{body}\n\n{closing}\n\nSincerely,\nCandidate"

        highlights = [
            f"Core Skill Alignment: Strong background in {skills_phrase}",
            f"Experience Depth: {exp_str} of hands-on technical execution",
            f"Role Alignment: Direct match for {job_title} at {company_name}",
        ]

        return {
            "company_name": company_name,
            "job_title": job_title,
            "tone": tone,
            "cover_letter": full_letter,
            "key_highlights": highlights,
        }


matcher = ResumeJobMatcher()
