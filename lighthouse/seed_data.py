"""Seed data from the takehome.md specification."""
from lighthouse.schemas import CaseStrategy

SEED_CASE_STRATEGY_RAW: dict = {
    "demographic_fields": [
        {"name": "legal_name", "type": "text", "hint": "Full legal name as on passport"},
        {"name": "passport", "type": "file", "hint": "Upload passport photo page"},
        {"name": "country_of_birth", "type": "text", "hint": ""},
        {"name": "current_visa", "type": "text", "hint": "e.g. H-1B, F-1, B-1/B-2"},
        {"name": "address", "type": "text", "hint": "Current US address"},
    ],
    "criteria": [
        {
            "name": "Critical Role",
            "description": "Founding Engineer at Bland",
            "fields": [
                {"name": "start_date", "type": "date", "hint": ""},
                {"name": "end_date", "type": "date", "hint": ""},
                {"name": "key_responsibilities", "type": "text", "hint": "Describe your key responsibilities"},
                {
                    "name": "examples",
                    "type": "files_or_urls",
                    "hint": "Product roadmaps, technical diagrams, speaking invites, blog posts, dashboards showing project ownership",
                },
            ],
        },
        {
            "name": "High Remuneration",
            "description": "Founding Engineer at Bland",
            "fields": [
                {"name": "work_location", "type": "text", "hint": "City and state"},
                {"name": "salary", "type": "text", "hint": "Include currency"},
                {"name": "paystubs", "type": "files", "hint": "Last 4 paystubs"},
                {
                    "name": "equity_proof",
                    "type": "files_or_urls",
                    "hint": "Carta screenshot or equivalent",
                },
            ],
        },
        {
            "name": "Original Contributions",
            "description": "Bland",
            "fields": [
                {
                    "name": "work_description",
                    "type": "text",
                    "hint": "Describe your work and unique contributions",
                },
                {
                    "name": "impact_description",
                    "type": "text",
                    "hint": "Describe the impact to the field/world",
                },
                {"name": "supporting_evidence", "type": "files_or_urls", "hint": ""},
            ],
        },
        {
            "name": "Membership",
            "description": "Y Combinator",
            "fields": [
                {"name": "date_selected", "type": "date", "hint": ""},
                {"name": "proof_of_membership", "type": "files_or_urls", "hint": ""},
            ],
        },
    ],
}


def get_seed_strategy() -> CaseStrategy:
    """Parse and validate the seed case strategy."""
    return CaseStrategy(**SEED_CASE_STRATEGY_RAW)


def get_seed_strategy_dict() -> dict:
    """Get seed strategy as a plain dict (for Reflex state)."""
    return SEED_CASE_STRATEGY_RAW
