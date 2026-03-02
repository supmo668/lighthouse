"""Shared page layout wrapper."""
import reflex as rx

from lighthouse.components.chat import chat_fab
from lighthouse.state import CaseState


def page_layout(*children, **props) -> rx.Component:
    """Standard page layout with header and content area."""
    return rx.box(
        rx.vstack(
            # Demo mode banner
            rx.cond(
                CaseState.is_demo_mode,
                rx.callout(
                    "Demo Mode \u2014 Using simulated AI reviews. Add a real OPENAI_API_KEY for live grading.",
                    icon="flask-conical",
                    color_scheme="orange",
                    variant="surface",
                    size="1",
                    width="100%",
                ),
            ),
            # Header
            rx.hstack(
                rx.icon("compass", size=28, color=rx.color("accent", 9)),
                rx.heading("Lighthouse", size="6", weight="bold"),
                rx.spacer(),
                rx.badge("O-1 Visa", variant="soft", color_scheme="blue"),
                align="center",
                width="100%",
                padding_x=["1em", "1.5em", "2em"],
                padding_y="0.75em",
                border_bottom=f"1px solid {rx.color('gray', 4)}",
            ),
            # Content
            rx.container(
                *children,
                size="2",
                padding_y=["1.5em", "2em", "2.5em"],
                padding_x=["1em", "1.5em", "2em"],
                max_width="720px",
            ),
            spacing="0",
            width="100%",
            min_height="100vh",
        ),
        chat_fab(),
        **props,
    )
