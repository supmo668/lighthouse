"""AI copilot chat sidebar components."""
import reflex as rx

from lighthouse.state import CaseState


def _message_bubble(msg: dict) -> rx.Component:
    """Single chat message bubble."""
    return rx.box(
        rx.text(
            msg["content"],
            size="2",
            white_space="pre-wrap",
        ),
        background=rx.cond(
            msg["role"] == "user",
            rx.color("accent", 3),
            rx.color("gray", 3),
        ),
        padding="0.75em 1em",
        border_radius="12px",
        max_width="85%",
        align_self=rx.cond(
            msg["role"] == "user",
            "flex-end",
            "flex-start",
        ),
    )


def _suggested_prompt_chip(prompt: str) -> rx.Component:
    """Clickable suggested prompt chip."""
    return rx.button(
        prompt,
        size="1",
        variant="soft",
        color_scheme="gray",
        on_click=CaseState.send_suggested_prompt(prompt),
        cursor="pointer",
        white_space="normal",
        text_align="left",
        height="auto",
        padding="0.5em 0.75em",
    )


def chat_drawer() -> rx.Component:
    """Right-side drawer with chat interface."""
    return rx.box(
        # Sliding panel — always rendered, translated off-screen when closed
        rx.box(
            rx.vstack(
                # Header
                rx.hstack(
                    rx.icon(
                        "message-circle",
                        size=20,
                        color=rx.color("accent", 9),
                    ),
                    rx.heading("AI Copilot", size="4"),
                    rx.spacer(),
                    rx.icon(
                        "x",
                        size=20,
                        cursor="pointer",
                        on_click=CaseState.toggle_chat,
                        color=rx.color("gray", 9),
                        _hover={"color": rx.color("gray", 12)},
                    ),
                    align="center",
                    width="100%",
                    padding_bottom="0.5em",
                    border_bottom="1px solid var(--gray-4)",
                ),
                # Context badge
                rx.cond(
                    CaseState.current_section >= 2,
                    rx.badge(
                        CaseState.current_criterion["name"],
                        variant="soft",
                        color_scheme="blue",
                        size="1",
                    ),
                ),
                # Suggested prompts (show when no messages)
                rx.cond(
                    CaseState.chat_message_count == 0,
                    rx.vstack(
                        rx.text(
                            "Need help with this section?",
                            size="2",
                            color=rx.color("gray", 10),
                        ),
                        rx.foreach(
                            CaseState.chat_suggested_prompts,
                            _suggested_prompt_chip,
                        ),
                        spacing="2",
                        width="100%",
                        padding_y="1em",
                    ),
                ),
                # Messages
                rx.vstack(
                    rx.foreach(CaseState.chat_messages, _message_bubble),
                    rx.cond(
                        CaseState.is_chat_streaming,
                        rx.hstack(
                            rx.spinner(size="1"),
                            rx.text(
                                "Generating response...",
                                size="1",
                                color=rx.color("gray", 9),
                            ),
                            spacing="2",
                        ),
                    ),
                    spacing="3",
                    width="100%",
                    overflow_y="auto",
                    flex="1",
                    padding_y="0.5em",
                ),
                # Input area
                rx.hstack(
                    rx.input(
                        value=CaseState.chat_input,
                        placeholder="Ask about what makes strong evidence...",
                        on_change=CaseState.set_chat_input,
                        width="100%",
                        size="2",
                    ),
                    rx.button(
                        rx.icon("send", size=16),
                        on_click=CaseState.send_chat_message,
                        size="2",
                        variant="solid",
                        disabled=CaseState.is_chat_streaming,
                    ),
                    align="center",
                    width="100%",
                    spacing="2",
                ),
                spacing="3",
                width="100%",
                height="100%",
                padding="1.5em",
            ),
            position="fixed",
            top="0",
            right="0",
            width=["90vw", "90vw", "380px"],
            height="100vh",
            background="var(--color-background)",
            border_left="1px solid var(--gray-4)",
            box_shadow=rx.cond(
                CaseState.is_chat_open,
                "-4px 0 24px rgba(0,0,0,0.08)",
                "none",
            ),
            transform=rx.cond(
                CaseState.is_chat_open,
                "translateX(0)",
                "translateX(100%)",
            ),
            transition="transform 0.3s ease, box-shadow 0.3s ease",
            z_index="40",
            overflow="hidden",
        ),
    )


def chat_fab() -> rx.Component:
    """Floating action button to open chat."""
    return rx.box(
        rx.button(
            rx.icon("message-circle", size=24),
            on_click=CaseState.toggle_chat,
            size="4",
            variant="solid",
            border_radius="50%",
            width="56px",
            height="56px",
            box_shadow="0 4px 12px rgba(0,0,0,0.15)",
        ),
        position="fixed",
        bottom="2em",
        right="2em",
        z_index="50",
    )
