"""Pydantic schemas for case strategy JSON parsing and validation."""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class FieldSchema(BaseModel):
    """A single data field within a criterion."""

    name: str
    type: str  # "text", "date", "file", "files", "files_or_urls"
    hint: Optional[str] = None


class CriterionSchema(BaseModel):
    """An O-1 visa criterion with its required evidence fields."""

    name: str  # e.g. "Critical Role", "High Remuneration"
    description: str  # e.g. "Founding Engineer at Bland"
    fields: list[FieldSchema] = []


class DemographicField(BaseModel):
    """A demographic information field."""

    name: str
    type: str  # "text", "file"


class CaseStrategy(BaseModel):
    """Complete case strategy defining what evidence to collect."""

    demographic_fields: list[DemographicField] = []
    criteria: list[CriterionSchema] = []

    @property
    def total_fields(self) -> int:
        return len(self.demographic_fields) + sum(
            len(c.fields) for c in self.criteria
        )
