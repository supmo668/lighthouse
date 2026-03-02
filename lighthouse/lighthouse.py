"""Lighthouse app entry point."""
import reflex as rx

import lighthouse  # noqa: F401 -- triggers import chain for pages/state/models

app = rx.App(
    theme=rx.theme(
        appearance="light",
        accent_color="blue",
        radius="medium",
    ),
)
