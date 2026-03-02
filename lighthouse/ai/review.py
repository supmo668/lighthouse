"""LangGraph evidence review agent — single-node graph with structured output."""
import os
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END

from lighthouse.ai.schemas import EvidenceGrade


class ReviewState(TypedDict):
    """LangGraph state for evidence review."""

    criterion_name: str
    criterion_description: str
    field_name: str
    field_type: str
    evidence_text: str
    grade: dict


REVIEW_PROMPT = """You are an immigration expert reviewing O-1 visa evidence for extraordinary ability.

Criterion: {criterion_name} — {criterion_description}
Field: {field_name}

Evidence submitted:
{evidence_text}

Evaluate this evidence against USCIS O-1 visa standards for the "{criterion_name}" criterion.
Consider:
- Is this evidence specific and detailed enough?
- Does it demonstrate extraordinary ability or achievement?
- Would an immigration officer find this compelling?
- What concrete improvements would strengthen this submission?"""


def _get_structured_llm():
    """Get LLM with structured output, or None if no API key."""
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key or api_key.startswith("sk-placeholder"):
        return None
    from langchain_openai import ChatOpenAI

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=api_key)
    return llm.with_structured_output(EvidenceGrade)


def _mock_grade(state: ReviewState) -> dict:
    """Return mock grade for demo without API key."""
    text = state["evidence_text"]
    length = len(text.strip())
    if length > 200:
        return EvidenceGrade(
            verdict="sufficient",
            score=0.85,
            feedback=(
                f"Strong evidence for {state['criterion_name']}. "
                "Your description provides good detail and specificity."
            ),
            suggestions=[],
        ).model_dump()
    elif length > 50:
        return EvidenceGrade(
            verdict="needs_improvement",
            score=0.55,
            feedback=(
                f"Your evidence for {state['criterion_name']} has a good foundation "
                "but needs more specific details and measurable outcomes."
            ),
            suggestions=[
                "Add specific metrics or numbers to quantify your impact",
                "Include dates and duration of involvement",
                "Reference any third-party validation or recognition",
            ],
        ).model_dump()
    else:
        return EvidenceGrade(
            verdict="insufficient",
            score=0.2,
            feedback=(
                f"This evidence is too brief to support {state['criterion_name']}. "
                "USCIS requires detailed, substantive evidence."
            ),
            suggestions=[
                "Expand with specific examples of your contributions",
                "Describe the significance and impact of your work",
                "Add supporting context about the organization and your role",
                "Include any recognition, awards, or press coverage",
            ],
        ).model_dump()


def review_evidence_node(state: ReviewState) -> dict:
    """LangGraph node: grade a single evidence field."""
    structured_llm = _get_structured_llm()
    if structured_llm is None:
        return {"grade": _mock_grade(state)}

    prompt = REVIEW_PROMPT.format(
        criterion_name=state["criterion_name"],
        criterion_description=state["criterion_description"],
        field_name=state["field_name"],
        evidence_text=state["evidence_text"],
    )
    result = structured_llm.invoke(prompt)
    return {"grade": result.model_dump()}


# Build and compile the review graph
_workflow = StateGraph(ReviewState)
_workflow.add_node("review", review_evidence_node)
_workflow.add_edge(START, "review")
_workflow.add_edge("review", END)
review_graph = _workflow.compile()


def grade_evidence(
    criterion_name: str,
    criterion_description: str,
    field_name: str,
    field_type: str,
    evidence_text: str,
) -> dict:
    """Grade a single evidence field. Returns EvidenceGrade as dict."""
    result = review_graph.invoke(
        {
            "criterion_name": criterion_name,
            "criterion_description": criterion_description,
            "field_name": field_name,
            "field_type": field_type,
            "evidence_text": evidence_text,
            "grade": {},
        }
    )
    return result["grade"]
