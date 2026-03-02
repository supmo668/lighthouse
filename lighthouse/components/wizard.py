"""Adaptive wizard UI components — step indicator, field renderer, step screens."""
import reflex as rx

from lighthouse.components.outreach import outreach_panel
from lighthouse.state import CaseState


# ---------------------------------------------------------------------------
# Step indicator
# ---------------------------------------------------------------------------

def step_indicator(label: str, idx: int) -> rx.Component:
    """Single step dot in the horizontal stepper."""
    return rx.hstack(
        rx.box(
            rx.text((idx + 1).to(str), size="1", weight="bold"),
            width="28px",
            height="28px",
            border_radius="50%",
            display="flex",
            align_items="center",
            justify_content="center",
            background=rx.cond(
                idx < CaseState.current_section,
                rx.color("green", 9),
                rx.cond(
                    idx == CaseState.current_section,
                    rx.color("accent", 3),
                    rx.color("gray", 3),
                ),
            ),
            color=rx.cond(
                idx < CaseState.current_section,
                "white",
                rx.cond(
                    idx == CaseState.current_section,
                    rx.color("accent", 11),
                    rx.color("gray", 9),
                ),
            ),
        ),
        rx.text(
            label,
            size="1",
            weight=rx.cond(idx == CaseState.current_section, "bold", "regular"),
            color=rx.cond(
                idx <= CaseState.current_section,
                rx.color("accent", 11),
                rx.color("gray", 9),
            ),
            display=["none", "none", "block"],
        ),
        align="center",
        spacing="1",
        cursor="pointer",
        on_click=CaseState.go_to_section(idx),
    )


def stepper_bar() -> rx.Component:
    """Horizontal step indicator bar."""
    return rx.hstack(
        rx.foreach(CaseState.step_labels, step_indicator),
        spacing="3",
        width="100%",
        overflow_x="auto",
        padding_y="0.75em",
        padding_x="0.25em",
    )


# ---------------------------------------------------------------------------
# Field renderer (type-aware)
# ---------------------------------------------------------------------------

def upload_dialog() -> rx.Component:
    """Shared upload dialog with static ID — avoids dynamic ID issues in foreach."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Upload Evidence Documents"),
            rx.upload(
                rx.vstack(
                    rx.icon("upload", size=32, color=rx.color("accent", 9)),
                    rx.text(
                        "Drag & drop files here",
                        size="3",
                    ),
                    rx.text(
                        "or click to browse",
                        size="2",
                        color=rx.color("gray", 10),
                    ),
                    align="center",
                    spacing="2",
                    padding="2em",
                ),
                id="evidence_upload",
                on_drop=CaseState.handle_upload(
                    rx.upload_files(upload_id="evidence_upload"),
                ),
                border="2px dashed var(--gray-6)",
                border_radius="8px",
                padding="1em",
                width="100%",
                cursor="pointer",
            ),
            rx.flex(
                rx.dialog.close(
                    rx.button("Done", size="2", width="100%"),
                ),
                width="100%",
                padding_top="1em",
            ),
            max_width="480px",
        ),
        open=CaseState.show_upload_dialog,
        on_open_change=CaseState.set_show_upload_dialog,
    )


def _file_upload_zone(field: dict) -> rx.Component:
    """Clickable upload trigger — opens shared upload dialog."""
    return rx.box(
        rx.vstack(
            rx.cond(
                CaseState.fields_with_uploads.contains(field["name"]),
                rx.icon("circle-check", size=24, color=rx.color("green", 9)),
                rx.icon("upload", size=24, color=rx.color("accent", 9)),
            ),
            rx.cond(
                CaseState.fields_with_uploads.contains(field["name"]),
                rx.text(
                    "Documents uploaded — add more if needed",
                    size="2",
                    color=rx.color("green", 10),
                ),
                rx.text(
                    "Upload supporting documents",
                    size="2",
                    color=rx.color("gray", 10),
                ),
            ),
            rx.text(
                "PDF, images accepted \u2014 you can add more later",
                size="1",
                color=rx.color("gray", 8),
            ),
            align="center",
            spacing="1",
        ),
        border=rx.cond(
            CaseState.fields_with_uploads.contains(field["name"]),
            "2px solid var(--green-7)",
            "2px dashed var(--gray-6)",
        ),
        border_radius="8px",
        padding="2em",
        width="100%",
        text_align="center",
        cursor="pointer",
        _hover={"border_color": rx.color("accent", 7)},
        on_click=CaseState.open_upload_for_field(field["name"]),
    )


def _files_or_urls_input(field: dict) -> rx.Component:
    """Upload zone + URL text area for mixed input fields."""
    return rx.vstack(
        _file_upload_zone(field),
        rx.text(
            "Or paste links to evidence (one per line):",
            size="1",
            color=rx.color("gray", 9),
        ),
        rx.text_area(
            name=field["name"],
            placeholder="https://linkedin.com/in/your-profile",
            rows="2",
        ),
        spacing="2",
        width="100%",
    )


def render_field(field: dict) -> rx.Component:
    """Render appropriate input control based on field type."""
    return rx.vstack(
        rx.vstack(
            rx.text(
                field["name"].to(str).replace("_", " ").title(),
                size="2",
                weight="medium",
            ),
            rx.cond(
                field["hint"] != "",
                rx.text(field["hint"], size="1", color=rx.color("gray", 9)),
            ),
            spacing="1",
            width="100%",
        ),
        rx.match(
            field["type"],
            ("text", rx.input(name=field["name"], placeholder=field["hint"])),
            ("date", rx.input(name=field["name"], type="date")),
            ("file", _file_upload_zone(field)),
            ("files", _file_upload_zone(field)),
            ("files_or_urls", _files_or_urls_input(field)),
            rx.input(name=field["name"]),  # default fallback
        ),
        spacing="2",
        width="100%",
    )


# ---------------------------------------------------------------------------
# Wizard navigation
# ---------------------------------------------------------------------------

def wizard_nav(show_submit: bool = False) -> rx.Component:
    """Back / Continue|Submit navigation bar."""
    return rx.hstack(
        rx.cond(
            ~CaseState.is_first_section,
            rx.button(
                "Back",
                type="button",
                variant="outline",
                size="3",
                on_click=CaseState.prev_section,
            ),
        ),
        rx.spacer(),
        rx.button(
            rx.cond(
                CaseState.is_last_section,
                "Submit Case",
                "Continue",
            ),
            type="submit",
            size="3",
        ),
        width="100%",
        padding_top="1.5em",
        border_top=f"1px solid {rx.color('gray', 4)}",
        margin_top="0.5em",
    )


# ---------------------------------------------------------------------------
# Wizard step screens
# ---------------------------------------------------------------------------

def _criterion_summary(criterion: dict) -> rx.Component:
    """Single criterion row in overview list."""
    return rx.hstack(
        rx.icon("circle-check", size=16, color=rx.color("green", 9)),
        rx.text(criterion["name"], size="2", weight="medium"),
        rx.text("\u2014", size="2", color=rx.color("gray", 8)),
        rx.text(criterion["description"], size="2", color=rx.color("gray", 10)),
        spacing="2",
    )


def overview_step() -> rx.Component:
    """Step 0 — case strategy overview + Start button."""
    return rx.vstack(
        rx.heading("Your O-1 Visa Journey", size="7"),
        rx.text(
            "We'll guide you through collecting evidence for your case. "
            "Each section focuses on one criterion at a time. "
            "This typically takes 20\u201330 minutes.",
            size="3",
            color=rx.color("gray", 10),
            line_height="1.6",
        ),
        rx.separator(),
        rx.vstack(
            rx.text("Your case strategy includes:", size="2", weight="medium"),
            rx.foreach(CaseState.criteria_list, _criterion_summary),
            spacing="3",
            width="100%",
        ),
        rx.button(
            "Start Onboarding",
            size="3",
            on_click=CaseState.next_section,
            width="100%",
            margin_top="0.5em",
        ),
        spacing="5",
        width="100%",
    )


def demographics_step() -> rx.Component:
    """Step 1 — demographics form."""
    return rx.fragment(
        upload_dialog(),
        rx.form(
            rx.vstack(
                rx.vstack(
                    rx.heading("Demographic Information", size="5"),
                    rx.text(
                        "Let's start with some basic information to help us understand your background.",
                        size="2",
                        color=rx.color("gray", 10),
                        line_height="1.6",
                    ),
                    spacing="2",
                    width="100%",
                ),
                rx.separator(),
                rx.vstack(
                    rx.foreach(CaseState.demographic_fields, render_field),
                    spacing="5",
                    width="100%",
                ),
                wizard_nav(),
                spacing="5",
                width="100%",
            ),
            on_submit=CaseState.handle_step_submit,
            reset_on_submit=False,
        ),
    )


def criterion_intro_step() -> rx.Component:
    """Criterion intro sub-step — teach before asking."""
    return rx.vstack(
        rx.hstack(
            rx.icon("file-check", size=24, color=rx.color("accent", 9)),
            rx.heading(CaseState.current_criterion["name"], size="5"),
            align="center",
            spacing="3",
        ),
        rx.text(
            CaseState.current_criterion["description"],
            size="3",
            color=rx.color("gray", 10),
            line_height="1.6",
        ),
        rx.separator(),
        rx.callout(
            rx.text(
                "We'll collect evidence for this criterion. "
                "Take your time \u2014 there are no wrong answers, and you can always come back to improve.",
                size="2",
                line_height="1.6",
            ),
            icon="info",
            color_scheme="blue",
        ),
        rx.vstack(
            rx.button(
                "Provide Evidence",
                size="3",
                on_click=CaseState.show_criterion_fields,
                width="100%",
            ),
            rx.button(
                "Skip for now",
                variant="ghost",
                size="2",
                on_click=CaseState.next_section,
                width="100%",
            ),
            spacing="2",
            width="100%",
            align="center",
        ),
        spacing="5",
        width="100%",
    )


def criterion_fields_step() -> rx.Component:
    """Criterion fields sub-step — evidence collection form."""
    return rx.fragment(
        upload_dialog(),
        rx.form(
            rx.vstack(
                rx.hstack(
                    rx.icon("file-check", size=20, color=rx.color("accent", 9)),
                    rx.heading(CaseState.current_criterion["name"], size="4"),
                    align="center",
                    spacing="3",
                ),
                rx.separator(),
                rx.vstack(
                    rx.foreach(CaseState.current_criterion_fields, render_field),
                    spacing="5",
                    width="100%",
                ),
                wizard_nav(),
                spacing="5",
                width="100%",
            ),
            on_submit=CaseState.handle_step_submit,
            reset_on_submit=False,
        ),
    )


def completion_step() -> rx.Component:
    """Post-submission success screen."""
    return rx.vstack(
        rx.icon("circle-check", size=48, color=rx.color("green", 9)),
        rx.heading("Case Submitted!", size="6"),
        rx.text(
            "Your evidence has been collected. Our team will review your case.",
            size="3",
            color=rx.color("gray", 10),
            text_align="center",
        ),
        rx.button(
            "Review Submissions",
            variant="outline",
            size="3",
            on_click=CaseState.go_to_section(0),
        ),
        spacing="4",
        width="100%",
        align="center",
        padding_top="3em",
    )


# ---------------------------------------------------------------------------
# AI Review screens
# ---------------------------------------------------------------------------

def reviewing_step() -> rx.Component:
    """Review in progress — spinner and progress bar."""
    return rx.vstack(
        rx.spinner(size="3"),
        rx.heading("Analyzing Your Evidence", size="5"),
        rx.text(
            "Evaluating your submissions against USCIS O-1 visa standards...",
            size="2",
            color=rx.color("gray", 10),
            text_align="center",
            line_height="1.6",
        ),
        rx.vstack(
            rx.progress(value=CaseState.review_progress, width="100%"),
            rx.text(
                CaseState.review_count.to(str)
                + " of "
                + CaseState.review_total_fields.to(str)
                + " fields reviewed",
                size="1",
                color=rx.color("gray", 9),
            ),
            spacing="2",
            width="80%",
            align="center",
        ),
        rx.text(
            "This usually takes about a minute",
            size="1",
            color=rx.color("gray", 8),
        ),
        spacing="5",
        width="100%",
        align="center",
        padding_top="4em",
        padding_bottom="4em",
    )


def _review_result_card(result: dict) -> rx.Component:
    """Single field review result card."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.text(
                    result["field_name"].to(str).replace("_", " ").title(),
                    size="2",
                    weight="medium",
                ),
                rx.spacer(),
                rx.match(
                    result["verdict"],
                    (
                        "sufficient",
                        rx.badge(
                            "Sufficient",
                            color_scheme="green",
                            variant="soft",
                        ),
                    ),
                    (
                        "needs_improvement",
                        rx.badge(
                            "Needs Improvement",
                            color_scheme="yellow",
                            variant="soft",
                        ),
                    ),
                    (
                        "insufficient",
                        rx.badge(
                            "Insufficient",
                            color_scheme="red",
                            variant="soft",
                        ),
                    ),
                    (
                        "error",
                        rx.badge(
                            "Error",
                            color_scheme="red",
                            variant="outline",
                        ),
                    ),
                    rx.badge("Pending", color_scheme="gray", variant="soft"),
                ),
                align="center",
                width="100%",
            ),
            rx.text(
                result["criterion_name"],
                size="1",
                color=rx.color("gray", 9),
            ),
            rx.match(
                result["verdict"],
                (
                    "sufficient",
                    rx.callout(
                        result["feedback"],
                        icon="circle-check",
                        color_scheme="green",
                        variant="soft",
                    ),
                ),
                (
                    "needs_improvement",
                    rx.callout(
                        result["feedback"],
                        icon="triangle-alert",
                        color_scheme="yellow",
                        variant="soft",
                    ),
                ),
                (
                    "insufficient",
                    rx.callout(
                        result["feedback"],
                        icon="circle-x",
                        color_scheme="red",
                        variant="soft",
                    ),
                ),
                rx.callout(
                    result["feedback"],
                    icon="info",
                    color_scheme="gray",
                    variant="soft",
                ),
            ),
            spacing="2",
        ),
        width="100%",
    )


def _criterion_summary_card(criterion: dict) -> rx.Component:
    """Per-criterion review summary card with aggregate stats."""
    return rx.card(
        rx.vstack(
            # Header: icon + name + verdict badge
            rx.hstack(
                rx.match(
                    criterion["verdict"],
                    (
                        "sufficient",
                        rx.icon(
                            "circle-check",
                            size=20,
                            color=rx.color("green", 9),
                        ),
                    ),
                    (
                        "needs_improvement",
                        rx.icon(
                            "triangle-alert",
                            size=20,
                            color=rx.color("yellow", 9),
                        ),
                    ),
                    (
                        "insufficient",
                        rx.icon(
                            "circle-x",
                            size=20,
                            color=rx.color("red", 9),
                        ),
                    ),
                    rx.icon("circle", size=20, color=rx.color("gray", 9)),
                ),
                rx.text(criterion["name"], size="3", weight="bold"),
                rx.spacer(),
                rx.match(
                    criterion["verdict"],
                    (
                        "sufficient",
                        rx.badge(
                            "Strong",
                            color_scheme="green",
                            variant="soft",
                        ),
                    ),
                    (
                        "needs_improvement",
                        rx.badge(
                            "Needs Work",
                            color_scheme="yellow",
                            variant="soft",
                        ),
                    ),
                    (
                        "insufficient",
                        rx.badge(
                            "Weak",
                            color_scheme="red",
                            variant="soft",
                        ),
                    ),
                    rx.badge("Pending", color_scheme="gray", variant="soft"),
                ),
                align="center",
                width="100%",
            ),
            # Description
            rx.text(
                criterion["description"],
                size="1",
                color=rx.color("gray", 9),
            ),
            # Score bar
            rx.hstack(
                rx.progress(
                    value=criterion["avg_score"],
                    width="100%",
                ),
                rx.text(
                    criterion["avg_score"].to(str) + "%",
                    size="1",
                    color=rx.color("gray", 9),
                    white_space="nowrap",
                ),
                align="center",
                width="100%",
                spacing="2",
            ),
            # Field counts
            rx.hstack(
                rx.badge(
                    criterion["sufficient_count"].to(str) + " OK",
                    color_scheme="green",
                    variant="soft",
                    size="1",
                ),
                rx.badge(
                    criterion["needs_improvement_count"].to(str)
                    + " Needs Work",
                    color_scheme="yellow",
                    variant="soft",
                    size="1",
                ),
                rx.badge(
                    criterion["insufficient_count"].to(str) + " Weak",
                    color_scheme="red",
                    variant="soft",
                    size="1",
                ),
                spacing="2",
                wrap="wrap",
            ),
            # Improve button (only for non-sufficient criteria)
            rx.match(
                criterion["verdict"],
                (
                    "sufficient",
                    rx.fragment(),
                ),
                rx.button(
                    "Improve This Criterion",
                    size="2",
                    variant="outline",
                    on_click=CaseState.go_to_criterion_for_improvement(
                        criterion["section_index"]
                    ),
                ),
            ),
            spacing="2",
        ),
        width="100%",
    )


def results_step() -> rx.Component:
    """Review results summary with per-criterion cards."""
    return rx.vstack(
        rx.heading("Evidence Review Complete", size="6"),
        # Overall case strength summary
        rx.card(
            rx.vstack(
                rx.hstack(
                    rx.text("Case Strength:", size="3", weight="medium"),
                    rx.text(
                        CaseState.case_strength_label,
                        size="3",
                        weight="bold",
                    ),
                    spacing="2",
                    align="center",
                ),
                rx.progress(value=CaseState.review_avg_score, width="100%"),
                rx.hstack(
                    rx.badge(
                        CaseState.review_sufficient_count.to(str)
                        + " Sufficient",
                        color_scheme="green",
                        variant="soft",
                    ),
                    rx.badge(
                        CaseState.review_needs_improvement_count.to(str)
                        + " Needs Work",
                        color_scheme="yellow",
                        variant="soft",
                    ),
                    rx.badge(
                        CaseState.review_insufficient_count.to(str)
                        + " Insufficient",
                        color_scheme="red",
                        variant="soft",
                    ),
                    spacing="2",
                    wrap="wrap",
                ),
                spacing="3",
            ),
            width="100%",
        ),
        # Per-criterion summary cards
        rx.vstack(
            rx.separator(),
            rx.text("Per-Criterion Results", size="3", weight="medium"),
            rx.vstack(
                rx.foreach(CaseState.criterion_summaries, _criterion_summary_card),
                spacing="3",
                width="100%",
            ),
            spacing="4",
            width="100%",
        ),
        # Detailed field reviews
        rx.vstack(
            rx.separator(),
            rx.text(
                "Detailed Field Reviews",
                size="2",
                weight="medium",
                color=rx.color("gray", 10),
            ),
            rx.vstack(
                rx.foreach(CaseState.review_results, _review_result_card),
                spacing="3",
                width="100%",
            ),
            spacing="4",
            width="100%",
        ),
        # Outreach activity feed
        outreach_panel(),
        # Actions
        rx.hstack(
            rx.button(
                "Improve Evidence",
                variant="outline",
                size="3",
                on_click=CaseState.restart_for_improvement,
            ),
            rx.spacer(),
            rx.button(
                "Back to Overview",
                size="3",
                color_scheme="green",
                on_click=CaseState.go_to_section(0),
            ),
            width="100%",
            padding_top="0.5em",
        ),
        spacing="5",
        width="100%",
    )
