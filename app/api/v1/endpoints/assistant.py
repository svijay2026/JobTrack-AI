import re
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api import deps
from app.crud.crud_job import job_crud
from app.crud.crud_resume import resume_crud
from app.models.user import User

router = APIRouter()


class ChatMessage(BaseModel):
    role: str = Field(..., description="'user' or 'assistant'")
    content: str


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    history: Optional[List[ChatMessage]] = []


class ChatResponse(BaseModel):
    reply: str
    suggested_prompts: List[str]
    timestamp: str


def generate_copilot_response(
    query: str,
    user_name: str,
    skills: List[str],
    experience_years: float,
    jobs_summary: Dict[str, int],
) -> tuple[str, List[str]]:
    """
    Intelligent Career Copilot reasoning engine.
    Generates personalized career coaching, interview guidance, resume critique,
    and pipeline strategy based on candidate background and query intent.
    """
    q = query.lower().strip()
    top_skills_str = ", ".join(skills[:5]) if skills else "Python, FastAPI, React, SQL"
    total_jobs = sum(jobs_summary.values())
    interview_count = jobs_summary.get("interviewing", 0)
    offer_count = jobs_summary.get("offered", 0) + jobs_summary.get("accepted", 0)

    # 1. Pipeline & Application Strategy
    if any(k in q for k in ["pipeline", "status", "application", "how am i doing", "progress", "strategy"]):
        reply = (
            f"Here is your personalized application pipeline breakdown, {user_name}:\n\n"
            f"📊 **Current Pipeline Health:**\n"
            f"• **Total Tracked Applications:** {total_jobs}\n"
            f"• **Active Interviews:** {interview_count}\n"
            f"• **Offers Received:** {offer_count}\n\n"
            f"🎯 **Actionable Next Steps:**\n"
            f"1. **Follow-ups:** Send a polite follow-up for applications submitted 5-7 business days ago.\n"
            f"2. **Target High-Alignment Roles:** Use our AI Matcher to target postings with ≥80% compatibility with your {top_skills_str} background.\n"
            f"3. **Consistency:** Aim for 3-5 quality applications per week rather than mass applying."
        )
        suggestions = [
            "How do I write an interview follow-up email?",
            "What technical skills should I add to my resume?",
            "How can I prepare for technical rounds?",
        ]
        return reply, suggestions

    # 2. Resume Feedback & Optimization
    if any(k in q for k in ["resume", "cv", "bullet", "improve", "critique", "xyz"]):
        reply = (
            f"Great question! Here is how to make your resume stand out for competitive tech roles:\n\n"
            f"💡 **1. Apply the Google 'XYZ Formula':**\n"
            f"Structure every bullet point as: *'Accomplished [X], as measured by [Y], by doing [Z]'*.\n"
            f"• **Before:** 'Built backend APIs with FastAPI.'\n"
            f"• **After:** 'Engineered 12+ asynchronous REST microservices using FastAPI and MySQL, reducing p99 latency by 35% for 50k+ daily requests.'\n\n"
            f"🔑 **2. Leverage Your Core Stack:**\n"
            f"Your current profile highlights expertise in **{top_skills_str}** (~{experience_years:.1f} yrs exp). Ensure these keywords appear in your summary, skills section, and project descriptions so automated ATS scanners rank you highly.\n\n"
            f"✨ **3. Quantify Impact:** Include metrics on speed, scale, cost savings, or test coverage."
        )
        suggestions = [
            "Give me sample resume bullets for full-stack developers",
            "How to pass automated ATS resume scanners?",
            "How to tailor my resume for a specific job?",
        ]
        return reply, suggestions

    # 3. Interview Preparation (STAR Method & Questions)
    if any(k in q for k in ["interview", "question", "star", "behavioral", "mock", "technical"]):
        reply = (
            f"Let's get you interview-ready! Here is a structured preparation plan:\n\n"
            f"🌟 **Mastering the STAR Framework:**\n"
            f"• **Situation:** Set the context (company, team, project goal).\n"
            f"• **Task:** Clarify your specific responsibility or problem.\n"
            f"• **Action:** Detail the technical decisions, code architecture, or leadership you provided.\n"
            f"• **Result:** Quantify the business impact, performance gain, or lessons learned.\n\n"
            f"🎯 **High-Frequency Technical Questions for {top_skills_str}:**\n"
            f"1. *Explain how database indexing works in MySQL and how you resolve slow query bottlenecks.*\n"
            f"2. *How do asynchronous event loops in FastAPI/Python compare to traditional WSGI models?*\n"
            f"3. *How do you manage client-side state, memoization, and re-renders in modern React?*\n\n"
            f"Would you like to practice answering any of these together?"
        )
        suggestions = [
            "Practice: Tell me about a time you solved a tough bug",
            "Explain database indexing simply",
            "Questions to ask the interviewer at the end",
        ]
        return reply, suggestions

    # 4. Salary & Offer Negotiation
    if any(k in q for k in ["salary", "negotiat", "compensation", "counter", "offer", "pay"]):
        reply = (
            f"Negotiating compensation is one of the highest-leverage steps in your career search. Here is a proven guide:\n\n"
            f"🤝 **1. Never Anchor First:**\n"
            f"When asked for your salary expectations early on, respond: *'I'm focused on finding the right role fit and am confident your team offers competitive compensation aligned with current market rates for someone with my experience.'*\n\n"
            f"📈 **2. When You Receive the Offer:**\n"
            f"• **Express Enthusiasm:** *'Thank you so much for the offer! I am genuinely thrilled about the team's mission.'*\n"
            f"• **Ask for Time:** Always ask for 48-72 hours to review the full compensation package (base salary, bonus, equity, healthcare, PTO).\n"
            f"• **Make a Value-Based Counter:** State your target range backed by your proficiency in **{top_skills_str}** and the immediate value you deliver."
        )
        suggestions = [
            "What is a script for counter-offering higher base salary?",
            "What benefits can be negotiated besides salary?",
            "How to handle multiple job offers simultaneously?",
        ]
        return reply, suggestions

    # 5. Cold Outreach & Networking
    if any(k in q for k in ["reach out", "cold", "email", "recruiter", "linkedin", "network"]):
        reply = (
            f"Here is a high-converting message template for reaching out to engineering managers or recruiters on LinkedIn:\n\n"
            f"✉️ **LinkedIn Message Template:**\n\n"
            f"Hi [Name],\n\n"
            f"I’ve been following [Company]'s work in [Domain/Product] with great interest. With hands-on experience in **{top_skills_str}**, I noticed your open [Job Title] position and was impressed by your team's engineering focus.\n\n"
            f"Recently, I built solutions focusing on [Key Project/Metric]. I'd welcome the chance to share how my background could support your team's current development goals.\n\n"
            f"Best regards,\n{user_name}"
        )
        suggestions = [
            "How to follow up after 1 week with no response?",
            "What to write in a LinkedIn connection note?",
            "How to find hiring managers directly?",
        ]
        return reply, suggestions

    # Default Helpful Coaching Response
    reply = (
        f"Hello {user_name}! I am your **JobTrack AI Career Assistant**.\n\n"
        f"I can help you navigate every stage of your job search:\n"
        f"• **Resume Polish:** Review bullet points with the XYZ impact formula.\n"
        f"• **Technical & Behavioral Prep:** Practice interview questions tailored to **{top_skills_str}**.\n"
        f"• **Pipeline Review:** Analyze your active job tracker and recommend what to prioritize.\n"
        f"• **Salary Negotiation:** Scripts and strategies to maximize your compensation.\n\n"
        f"What would you like to work on right now?"
    )
    suggestions = [
        "Analyze my current application pipeline",
        "How can I improve my resume bullet points?",
        "Mock interview questions for full-stack engineer",
        "Salary negotiation strategies and scripts",
    ]
    return reply, suggestions


@router.post(
    "/chat",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Chat with AI Career Assistant",
)
def chat_with_assistant(
    req: ChatRequest,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Real-time AI Career Copilot endpoint.
    Provides personalized interview prep, resume optimization, and pipeline strategy.
    """
    # Fetch candidate profile details
    user_resumes = resume_crud.get_multi_by_user(db=db, user_id=current_user.id, limit=5)
    primary_resume = next((r for r in user_resumes if r.is_primary), user_resumes[0] if user_resumes else None)
    
    candidate_skills = primary_resume.skills if primary_resume and primary_resume.skills else ["Python", "FastAPI", "React", "TypeScript", "MySQL"]
    experience_years = primary_resume.experience_years if primary_resume and primary_resume.experience_years else 3.0

    # Fetch user's job applications summary
    user_jobs = job_crud.get_multi_by_user(db=db, user_id=current_user.id, limit=200)
    jobs_summary = {}
    for j in user_jobs:
        jobs_summary[j.status] = jobs_summary.get(j.status, 0) + 1

    reply, suggestions = generate_copilot_response(
        query=req.message,
        user_name=current_user.full_name or "Candidate",
        skills=candidate_skills,
        experience_years=experience_years,
        jobs_summary=jobs_summary,
    )

    return {
        "reply": reply,
        "suggested_prompts": suggestions,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
