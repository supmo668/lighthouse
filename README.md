# Lighthouse

AI-powered O-1 visa onboarding prototype. Replaces static forms with a guided wizard that grades evidence in real-time, coaches applicants via AI copilot, and auto-generates follow-up actions.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run (demo mode — no API key needed)
reflex run
```

Open http://localhost:3000

### With real AI grading

```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
OPENAI_API_KEY=sk-... reflex run
```

## What It Does

- **Adaptive wizard** — Renders dynamically from a JSON case strategy. Works for any O-1 criteria combination.
- **AI evidence grading** — GPT-4o-mini scores each field against USCIS standards via LangGraph + Pydantic structured output.
- **AI copilot** — Context-aware chat that knows which criterion you're on. Streaming responses, per-criterion suggested prompts.
- **Autonomous outreach** — Auto-generates reminder/approval emails and scheduling suggestions from review verdicts.
- **Demo mode** — Full UX without an API key. Simulated grading uses text length as a heuristic.

## Project Structure

```
lighthouse/
├── lighthouse/
│   ├── ai/
│   │   ├── review.py       # LangGraph evidence grading pipeline
│   │   ├── copilot.py      # Context-aware AI chat
│   │   ├── outreach.py     # Autonomous outreach actions
│   │   └── schemas.py      # Pydantic EvidenceGrade schema
│   ├── components/
│   │   ├── wizard.py       # Adaptive wizard UI
│   │   ├── chat.py         # AI copilot panel
│   │   ├── outreach.py     # Outreach activity feed
│   │   └── layout.py       # App shell
│   ├── state.py            # Application state + handlers
│   ├── seed_data.py        # Test case strategy
│   └── schemas.py          # Data models
├── requirements.txt
├── rxconfig.py
├── Dockerfile
└── .env.example
```

## Docker

```bash
docker build -t lighthouse .
docker run -p 3000:3000 -p 8000:8000 -e OPENAI_API_KEY=sk-... lighthouse
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | Reflex 0.8.27 |
| AI Pipeline | LangGraph + LangChain |
| LLM | GPT-4o-mini (structured output) |
| Deployment | Docker (Python 3.11 + Node 20) |
