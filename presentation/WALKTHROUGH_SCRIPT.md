Hi, I'm presenting Lighthouse — an AI-powered onboarding experience for O-1 visa applicants.

The problem: O-1 visa onboarding is brutal. Applicants face 8 USCIS criteria, dozens of evidence fields, and zero feedback on whether their evidence is actually strong enough. Today it's long email chains, spreadsheets, back-and-forth calls — averaging 3 to 4 revision cycles per criterion. That doesn't scale, especially with H-1B fees tripling and O-1 demand surging.

---

The core insight: assess evidence quality *during* collection, not after. Every existing tool evaluates post-submission, which is what creates the revision loop in the first place. I moved evaluation upstream — the AI coaches you while you're writing.

Three AI capabilities work together here: real-time evidence grading via structured LLM output, a context-aware copilot that adapts to whichever criterion you're on, and autonomous outreach that generates follow-up actions from review verdicts.

---

Key assumptions:
- Case strategy arrives as JSON — criteria, fields, types. The wizard renders dynamically, so it handles any criteria combination with zero code changes.
- AI grading is coaching, not legal advice. It helps applicants self-improve before attorney review.
- Text evidence is the primary review target. Files are stored but not parsed — document analysis via vision model is the natural next step.
- Single-user prototype — no auth or persistence. Both are straightforward additions.

---

Let me walk through the full experience.

Overview page. The applicant sees their case strategy — four criteria: Critical Role, High Remuneration, Original Contributions, and Membership. Estimated time: 20 to 30 minutes. Notice the demo mode banner — that means we're running simulated reviews since no API key is configured.

Demographics first. Standard fields — name, passport upload, visa status. Each field type renders differently: text inputs, file upload zones, date pickers. All dynamically generated from the JSON schema.

Now Critical Role. Notice the two-step flow: first an intro explaining what USCIS looks for in this criterion, then the actual evidence fields. This progressive disclosure gives applicants context before they start typing.

The AI copilot is available at any point. The chat panel slides in from the right without obscuring the main content. Suggested prompts are criterion-specific — "What counts as a critical role?", "How do I describe key responsibilities effectively?" — and they update automatically as you navigate between criteria.

Responses stream in real-time over WebSocket. The system prompt is injected with current criterion context, so the copilot gives targeted guidance, not generic boilerplate.

Submitting now. Watch the review progress — "Analyzing Your Evidence" with a live counter: "1 of 3 fields reviewed", "2 of 3"... This runs as a background task so the UI stays responsive. Each field gets graded against USCIS standards.

Results. Overall case strength: Moderate. Each criterion gets a verdict — sufficient, needs improvement, or insufficient — with a score bar and field-level breakdown. Per-field feedback includes actionable suggestions. For example, this field scored 55% with recommendations to add specific metrics and dates.

Below that, the outreach panel. These are autonomous actions — reminder emails for weak criteria, approval notifications for strong ones. All generated deterministically from review verdicts, no LLM call needed. After 24 hours, pending reminders fire and a "schedule a review call" action appears. This is exactly what a case manager would do manually.

Clicking "Improve Evidence" drops you back into the first criterion with all prior data preserved. No lost work.

---

Quick architecture note: evidence grading runs on a LangGraph StateGraph with Pydantic structured output. The LLM is constrained to return verdict, score, feedback, and suggestions — no free-form text to parse. Mock mode activates automatically when no API key is set, using text length as a grading heuristic.

---

With more time, three priorities:

First, document parsing — vision model to extract and grade evidence from uploaded PDFs and images. The LangGraph pipeline makes this a single new node.

Second, persistent storage — state currently lives in memory. Adding a database is a config change.

Third, multi-node review pipeline — separate nodes for document parsing, evidence extraction, grading, and fact-checking.

The architecture was designed for exactly these extensions. Thank you.
