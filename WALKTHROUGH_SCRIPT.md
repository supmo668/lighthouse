Lighthouse is an AI-powered onboarding experience for O-1 visa applicants.

The problem: O-1 onboarding produces 3 to 4 revision cycles per criterion because every existing tool evaluates evidence after submission. My insight: move evaluation upstream — grade evidence while the applicant is writing it. Three capabilities: real-time grading via GPT-4o-mini with structured output, a context-aware copilot, and autonomous outreach from review verdicts.

The wizard is fully schema-driven — case strategy is a JSON object of criteria, fields, and types. Any criteria combination renders without code changes.

---

The overview shows the case strategy: Critical Role, High Remuneration, Original Contributions, Membership, plus a time estimate. Demographics first — text, file, and date fields all rendered from the schema.

Each criterion has a two-step flow: an intro explaining what USCIS looks for, then the evidence fields. The AI copilot slides in from the right — suggested prompts are criterion-specific, the system prompt is injected with current context, responses stream in real-time.

After submitting, field reviews run as a background task with a live progress counter. Results show per-criterion verdicts — sufficient, needs improvement, insufficient — with field-level feedback and concrete suggestions. The outreach panel auto-generates actions from those verdicts: reminders for weak criteria, approvals for strong ones — no extra LLM call. Simulate 24 hours and pending actions fire automatically. Clicking "Improve Evidence" returns to the first weak criterion with all prior data intact.

---

The grading pipeline is a LangGraph StateGraph — the LLM returns a typed verdict, score, feedback, and suggestions via Pydantic structured output. Mock mode activates without an API key.

Three natural extensions: document parsing via vision LLM as a single new graph node, persistent storage as a config change, and a multi-node pipeline splitting parsing, extraction, grading, and fact-checking. The architecture was designed for exactly that. Thank you.
