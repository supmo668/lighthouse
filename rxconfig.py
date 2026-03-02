import os

import reflex as rx

config = rx.Config(
    app_name="lighthouse",
    frontend_port=int(os.environ.get("PORT", 3000)),
    backend_port=int(os.environ.get("BACKEND_PORT", 8000)),
)
