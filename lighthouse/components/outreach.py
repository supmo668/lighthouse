"""Outreach activity feed components — simulated email reminders and status notifications."""
import reflex as rx

from lighthouse.state import CaseState


def _action_icon(action: dict) -> rx.Component:
    """Icon for an outreach action based on type."""
    return rx.match(
        action["type"],
        (
            "reminder",
            rx.icon("mail", size=18, color=rx.color("yellow", 9)),
        ),
        (
            "approval",
            rx.icon("circle-check", size=18, color=rx.color("green", 9)),
        ),
        (
            "schedule",
            rx.icon("calendar", size=18, color=rx.color("blue", 9)),
        ),
        rx.icon("bell", size=18, color=rx.color("gray", 9)),
    )


def _status_badge(action: dict) -> rx.Component:
    """Status badge for an outreach action."""
    return rx.match(
        action["status"],
        (
            "sent",
            rx.badge("Sent", color_scheme="green", variant="soft", size="1"),
        ),
        (
            "pending",
            rx.badge("Pending", color_scheme="yellow", variant="soft", size="1"),
        ),
        rx.badge("Unknown", color_scheme="gray", variant="soft", size="1"),
    )


def _outreach_action_card(action: dict) -> rx.Component:
    """Single outreach action card in the activity feed."""
    return rx.card(
        rx.vstack(
            # Header: icon + subject + status badge
            rx.hstack(
                _action_icon(action),
                rx.text(action["subject"], size="2", weight="medium"),
                rx.spacer(),
                _status_badge(action),
                align="center",
                width="100%",
            ),
            # Timestamp
            rx.text(
                action["timestamp"],
                size="1",
                color=rx.color("gray", 8),
            ),
            # Body preview (always visible)
            rx.text(
                action["body"],
                size="1",
                color=rx.color("gray", 10),
                white_space="pre-wrap",
            ),
            # Action buttons (only for reminders — use rx.match to avoid ObjectItemOperation !=)
            rx.match(
                action["type"],
                (
                    "reminder",
                    rx.hstack(
                        rx.button(
                            rx.icon("arrow-right", size=14),
                            "Jump to Criterion",
                            size="1",
                            variant="outline",
                            on_click=CaseState.go_to_criterion_for_improvement(
                                action["section_index"]
                            ),
                        ),
                        rx.button(
                            rx.icon("mail", size=14),
                            "Preview Email",
                            size="1",
                            variant="ghost",
                            on_click=CaseState.toggle_email_preview(
                                action["criterion_name"]
                            ),
                        ),
                        spacing="2",
                        wrap="wrap",
                    ),
                ),
                (
                    "schedule",
                    rx.button(
                        rx.icon("calendar", size=14),
                        "Schedule Call",
                        size="1",
                        variant="outline",
                        color_scheme="blue",
                    ),
                ),
                # approval and default: no action buttons
                rx.fragment(),
            ),
            # Email preview (expandable for reminders)
            rx.match(
                action["type"],
                (
                    "reminder",
                    rx.cond(
                        CaseState.show_email_preview == action["criterion_name"],
                        rx.card(
                            rx.vstack(
                                rx.hstack(
                                    rx.icon(
                                        "mail",
                                        size=14,
                                        color=rx.color("accent", 9),
                                    ),
                                    rx.text(
                                        "Email Preview",
                                        size="1",
                                        weight="bold",
                                    ),
                                    align="center",
                                    spacing="1",
                                ),
                                rx.separator(),
                                rx.text(
                                    "To: demo-applicant@lighthouse.app",
                                    size="1",
                                    color=rx.color("gray", 9),
                                ),
                                rx.text(
                                    "Subject: " + action["subject"].to(str),
                                    size="1",
                                    weight="medium",
                                ),
                                rx.separator(),
                                rx.text(
                                    action["body"],
                                    size="1",
                                    color=rx.color("gray", 10),
                                    white_space="pre-wrap",
                                ),
                                spacing="2",
                            ),
                            variant="surface",
                            width="100%",
                        ),
                    ),
                ),
                rx.fragment(),
            ),
            spacing="2",
        ),
        width="100%",
    )


def outreach_panel() -> rx.Component:
    """Activity feed panel showing all outreach actions."""
    return rx.cond(
        CaseState.outreach_action_count > 0,
        rx.vstack(
            rx.separator(),
            rx.hstack(
                rx.icon("bell", size=20, color=rx.color("accent", 9)),
                rx.text(
                    "Outreach & Follow-ups",
                    size="3",
                    weight="medium",
                ),
                rx.badge(
                    CaseState.outreach_action_count.to(str) + " actions",
                    color_scheme="blue",
                    variant="soft",
                    size="1",
                ),
                align="center",
                spacing="2",
            ),
            rx.foreach(CaseState.outreach_actions, _outreach_action_card),
            # Simulate time passage button
            rx.button(
                rx.icon("clock", size=16),
                "Demo: Simulate 24h Later",
                variant="outline",
                size="2",
                color_scheme="gray",
                on_click=CaseState.simulate_time_passage,
                width="100%",
            ),
            spacing="3",
            width="100%",
        ),
    )
