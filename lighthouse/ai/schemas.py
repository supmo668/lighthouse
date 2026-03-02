"""Pydantic schemas for AI evidence grading."""
from pydantic import BaseModel, Field


class EvidenceGrade(BaseModel):
    """Structured AI assessment of a single evidence field."""

    verdict: str = Field(
        description="One of: sufficient, needs_improvement, insufficient"
    )
    score: float = Field(
        ge=0.0,
        le=1.0,
        description="Quality score from 0.0 (worst) to 1.0 (best)",
    )
    feedback: str = Field(
        description="Clear, actionable feedback for the applicant",
    )
    suggestions: list[str] = Field(
        default_factory=list,
        description="Specific improvement suggestions",
    )
