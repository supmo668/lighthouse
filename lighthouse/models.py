"""SQLModel database tables for Lighthouse."""
import json
from datetime import datetime
from typing import Optional

import reflex as rx
from sqlalchemy import Column, DateTime, Text, func
from sqlmodel import Field


class Case(rx.Model, table=True):
    """An immigration case with its strategy and status."""

    case_id: str = Field(unique=True, index=True)
    applicant_name: str = Field(default="")
    status: str = Field(default="intake")
    case_strategy_json: str = Field(
        default="{}",
        sa_column=Column(Text, nullable=False, server_default="{}"),
    )
    form_data_json: str = Field(
        default="{}",
        sa_column=Column(Text, nullable=False, server_default="{}"),
    )
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True), server_default=func.now(), nullable=False
        ),
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
            nullable=False,
        ),
    )

    def get_strategy(self) -> dict:
        return json.loads(self.case_strategy_json)

    def set_strategy(self, strategy: dict) -> None:
        self.case_strategy_json = json.dumps(strategy)

    def get_form_data(self) -> dict:
        return json.loads(self.form_data_json)

    def set_form_data(self, data: dict) -> None:
        self.form_data_json = json.dumps(data)


class CriterionEvidence(rx.Model, table=True):
    """Evidence submitted for a specific criterion."""

    case_id: str = Field(index=True)
    criterion_name: str
    field_name: str
    field_type: str
    value: str = Field(default="")
    status: str = Field(default="pending")
    ai_score: Optional[float] = Field(default=None)
    ai_feedback: str = Field(default="")
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True), server_default=func.now(), nullable=False
        ),
    )
