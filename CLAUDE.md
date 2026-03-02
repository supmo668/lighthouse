# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the **Lighthouse** project — a prototype for an O-1 visa onboarding/data-intake experience. The goal is to collect immigration case information while educating users about their visa requirements and what "good" evidence looks like, adapted to their specific case strategy.

The product specification is in `takehome.md`.

## Domain Context

- An **O-1 visa** requires demonstrating "extraordinary ability" by satisfying at least 3 of 8 USCIS criteria (e.g., High Remuneration, Original Contributions, Critical Role, Membership).
- A **case strategy** defines which criteria an applicant targets based on their background. Different strategies require different evidence.
- The onboarding experience must adapt dynamically to any combination of O-1 criteria in the format "[Criteria] - [Description]".
- Data collection includes demographic information plus criteria-specific fields with types: text, date, file, URL, or files_or_urls.

## Key Requirements

- Works for any O-1 case strategy (not hardcoded to test data)
- Validates inputs dynamically with real LLM-driven responses
- Supports clarifying questions from users at any point
- Handles "pushback" scenarios where insufficient evidence is flagged for resubmission
- Must be deployable (deliverable includes a deployed link)
