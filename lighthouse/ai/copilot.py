"""AI copilot for contextual O-1 visa coaching."""
import os
from typing import Generator


COPILOT_SYSTEM_PROMPT = """You are an expert O-1 visa immigration coach helping an applicant gather evidence.

Current wizard context:
- Section: {section_label}
- Criterion: {criterion_name} — {criterion_description}

Your role:
- Answer questions about what evidence is needed for the current criterion
- Explain USCIS standards in plain language
- Give specific examples of strong vs weak evidence
- Be encouraging but honest about evidence quality
- Keep responses concise (2-3 paragraphs max)

Do NOT provide legal advice. Always recommend consulting with their attorney for legal questions."""


SUGGESTED_PROMPTS = {
    "Critical Role": [
        "What counts as a 'critical role'?",
        "How do I describe key responsibilities effectively?",
        "What supporting documents strengthen this criterion?",
    ],
    "High Remuneration": [
        "How does USCIS define 'high remuneration'?",
        "What salary benchmarks should I compare against?",
        "What proof of compensation is most compelling?",
    ],
    "Original Contributions": [
        "What qualifies as an 'original contribution'?",
        "How do I describe technical impact effectively?",
        "What third-party evidence supports originality?",
    ],
    "Membership": [
        "What organizations qualify for this criterion?",
        "How selective does the membership need to be?",
        "What proof of membership is needed?",
    ],
}

DEFAULT_PROMPTS = [
    "What makes strong O-1 evidence?",
    "How many criteria do I need to satisfy?",
    "What are common mistakes applicants make?",
]


def get_suggested_prompts(criterion_name: str) -> list[str]:
    """Get suggested prompts for the current criterion."""
    return SUGGESTED_PROMPTS.get(criterion_name, DEFAULT_PROMPTS)


def _get_chat_llm():
    """Get chat LLM, or None if no API key (triggers mock mode)."""
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key or api_key.startswith("sk-placeholder"):
        return None
    from langchain_openai import ChatOpenAI

    return ChatOpenAI(model="gpt-4o-mini", temperature=0.7, api_key=api_key)


def _mock_response(user_message: str, criterion_name: str) -> str:
    """Return mock response for demo without API key."""
    msg_lower = user_message.lower()
    if "example" in msg_lower or "what" in msg_lower:
        return (
            f"Great question! For the **{criterion_name}** criterion, USCIS looks for "
            f"evidence that demonstrates your extraordinary ability. "
            f"Strong evidence includes:\n\n"
            f"- **Specific metrics**: Numbers that quantify your impact (revenue, users, etc.)\n"
            f"- **Third-party validation**: Awards, press coverage, expert letters\n"
            f"- **Comparative context**: How your work stands out from peers\n\n"
            f"Would you like me to help you draft a specific section?"
        )
    if "enough" in msg_lower or "sufficient" in msg_lower:
        return (
            f"The key to sufficient evidence for **{criterion_name}** is specificity. "
            f"USCIS officers review thousands of petitions, so generic statements won't stand out.\n\n"
            f"A good rule of thumb: if someone unfamiliar with your work could understand "
            f"*exactly* what you did and *why it mattered*, you're on the right track.\n\n"
            f"Try adding concrete numbers, dates, and outcomes to your descriptions."
        )
    return (
        f"I'm here to help with your **{criterion_name}** evidence! "
        f"Here are some things I can help with:\n\n"
        f"- Explaining what USCIS looks for in this criterion\n"
        f"- Reviewing your evidence descriptions\n"
        f"- Suggesting improvements to strengthen your case\n\n"
        f"What would you like to know?"
    )


def stream_chat_response(
    messages: list[dict],
    section_label: str,
    criterion_name: str,
    criterion_description: str,
) -> Generator[str, None, None]:
    """Stream chat response token by token. Yields text chunks.

    messages: list of {"role": "user"|"assistant", "content": str}
    """
    llm = _get_chat_llm()

    if llm is None:
        # Mock mode: yield full response as single chunk
        user_msg = messages[-1]["content"] if messages else ""
        yield _mock_response(user_msg, criterion_name or "O-1 Visa")
        return

    from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

    system_prompt = COPILOT_SYSTEM_PROMPT.format(
        section_label=section_label,
        criterion_name=criterion_name or "General",
        criterion_description=criterion_description or "O-1 visa application",
    )

    lc_messages = [SystemMessage(content=system_prompt)]
    for msg in messages:
        if msg["role"] == "user":
            lc_messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            lc_messages.append(AIMessage(content=msg["content"]))

    for chunk in llm.stream(lc_messages):
        if chunk.content:
            yield chunk.content
