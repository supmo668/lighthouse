"""Main wizard page — adaptive multi-step onboarding."""
import reflex as rx

from lighthouse.components.chat import chat_drawer
from lighthouse.components.layout import page_layout
from lighthouse.components.wizard import (
    stepper_bar,
    overview_step,
    demographics_step,
    criterion_intro_step,
    criterion_fields_step,
    completion_step,
    reviewing_step,
    results_step,
)
from lighthouse.state import CaseState


def criterion_step() -> rx.Component:
    """Criterion section with intro/fields sub-steps."""
    return rx.match(
        CaseState.criterion_sub_step,
        (0, criterion_intro_step()),
        (1, criterion_fields_step()),
        criterion_intro_step(),  # default
    )


def wizard_steps() -> rx.Component:
    """Normal wizard flow (intake mode)."""
    return rx.vstack(
        # Step indicator
        stepper_bar(),
        # Progress bar
        rx.hstack(
            rx.progress(value=CaseState.progress_percent, width="100%"),
            rx.text(
                CaseState.progress_percent.to(str) + "%",
                size="1",
                color=rx.color("gray", 9),
            ),
            align="center",
            width="100%",
        ),
        # Step content
        rx.match(
            CaseState.current_section,
            (0, overview_step()),
            (1, demographics_step()),
            criterion_step(),  # default: all sections >= 2 are criteria
        ),
        spacing="4",
        width="100%",
    )


def wizard_content() -> rx.Component:
    """Main wizard content area with step routing."""
    return rx.match(
        CaseState.case_status,
        ("submitted", reviewing_step()),
        ("reviewed", results_step()),
        # default: normal wizard (intake or any other status)
        wizard_steps(),
    )


@rx.page(
    route="/",
    title="Lighthouse — O-1 Visa Onboarding",
    on_load=CaseState.load_seed_case,
)
def index() -> rx.Component:
    """Landing page with adaptive wizard."""
    return rx.fragment(
        page_layout(wizard_content()),
        chat_drawer(),
    )
