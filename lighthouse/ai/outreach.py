"""Autonomous outreach action generation for incomplete/weak criteria."""
from datetime import datetime


def generate_reminder_email(
    criterion_name: str,
    criterion_description: str,
    verdict: str,
    avg_score: int,
) -> dict:
    """Generate a simulated reminder email for a weak criterion.

    Returns {"subject": str, "body": str}.
    """
    if verdict == "insufficient":
        urgency = "Action Required"
        tone = (
            f"Your evidence for **{criterion_name}** ({criterion_description}) "
            f"scored {avg_score}% and needs significant strengthening before submission. "
            f"USCIS officers require detailed, specific evidence for this criterion.\n\n"
            f"Key areas to improve:\n"
            f"- Add specific metrics and measurable outcomes\n"
            f"- Include third-party validation (letters, press, awards)\n"
            f"- Provide comparative context showing extraordinary ability\n\n"
            f"Click the link below to return to this criterion and improve your evidence."
        )
    else:
        urgency = "Reminder"
        tone = (
            f"Your evidence for **{criterion_name}** ({criterion_description}) "
            f"scored {avg_score}% — a solid foundation that needs a few improvements. "
            f"With some additional detail, this criterion can be fully approved.\n\n"
            f"Suggestions:\n"
            f"- Expand on the impact and significance of your contributions\n"
            f"- Add dates, numbers, and specific outcomes\n"
            f"- Consider adding supporting documentation\n\n"
            f"Click the link below to revisit and strengthen your evidence."
        )

    return {
        "subject": f"[{urgency}] {criterion_name} — Evidence needs improvement",
        "body": tone,
    }


def generate_approval_email(
    criterion_name: str,
    criterion_description: str,
    avg_score: int,
) -> dict:
    """Generate a simulated approval notification email.

    Returns {"subject": str, "body": str}.
    """
    return {
        "subject": f"[Approved] {criterion_name} — Evidence looks strong!",
        "body": (
            f"Great news! Your evidence for **{criterion_name}** "
            f"({criterion_description}) scored {avg_score}% and meets "
            f"USCIS standards for the O-1 visa.\n\n"
            f"No further action is needed for this criterion. "
            f"Focus your energy on improving any remaining weak areas."
        ),
    }


def generate_outreach_actions(
    criterion_summaries: list[dict],
    case_id: str,
    hours_elapsed: int = 0,
) -> list[dict]:
    """Generate outreach actions based on criterion review summaries.

    Args:
        criterion_summaries: List of per-criterion summary dicts from CaseState.
        case_id: The case identifier.
        hours_elapsed: Simulated hours since review (0 = immediate, 24 = reminder).

    Returns:
        List of action dicts with keys: type, criterion_name, subject, body,
        section_index, timestamp, status.
    """
    actions: list[dict] = []
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    for criterion in criterion_summaries:
        name = criterion.get("name", "")
        description = criterion.get("description", "")
        verdict = criterion.get("verdict", "")
        avg_score = criterion.get("avg_score", 0)
        section_index = criterion.get("section_index", 2)

        if verdict in ("insufficient", "needs_improvement"):
            email = generate_reminder_email(name, description, verdict, avg_score)
            status = "sent" if hours_elapsed >= 24 else "pending"
            actions.append(
                {
                    "type": "reminder",
                    "criterion_name": name,
                    "subject": email["subject"],
                    "body": email["body"],
                    "section_index": section_index,
                    "timestamp": now,
                    "status": status,
                }
            )
        elif verdict == "sufficient":
            email = generate_approval_email(name, description, avg_score)
            actions.append(
                {
                    "type": "approval",
                    "criterion_name": name,
                    "subject": email["subject"],
                    "body": email["body"],
                    "section_index": section_index,
                    "timestamp": now,
                    "status": "sent",
                }
            )

    # Add a scheduling suggestion if there are any reminders
    has_reminders = any(a["type"] == "reminder" for a in actions)
    if has_reminders and hours_elapsed >= 24:
        actions.append(
            {
                "type": "schedule",
                "criterion_name": "",
                "subject": "Schedule a review call with your case manager",
                "body": (
                    "You have criteria that need improvement. Consider scheduling "
                    "a 15-minute call with your case manager to discuss strategy "
                    "and get personalized guidance on strengthening your evidence."
                ),
                "section_index": 0,
                "timestamp": now,
                "status": "pending",
            }
        )

    return actions
