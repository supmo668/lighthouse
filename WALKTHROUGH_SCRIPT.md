# Lighthouse — Video Walkthrough Script

**Duration target:** 4-5 minutes
**Format:** Screen recording with voiceover
**Setup:** App running at localhost, browser open

---

## [0:00 - 0:30] Opening — The Problem

> Hi, I'm presenting Lighthouse — an AI-powered onboarding experience for O-1 visa applicants.
>
> The problem: O-1 visa onboarding is overwhelming. Applicants face 8 possible USCIS criteria, dozens of evidence fields, and no intuitive way to know if their evidence is strong enough. The current process — long emails, spreadsheets, phone calls — leads to 3 to 4 revision cycles per criterion. That doesn't scale, especially with H-1B fees tripling and O-1 demand surging.

**[Show the presentation slide 2 — "The Problem"]**

---

## [0:30 - 1:00] The Insight & Approach

> My key insight was: assess evidence quality *during* collection, not after. Every existing tool evaluates evidence post-submission, which creates the revision loop. I moved the evaluation upstream — the AI coaches you while you're writing.
>
> My approach has three AI capabilities working together: real-time evidence grading using GPT-4o-mini with structured output, a context-aware AI copilot that knows which criterion you're on, and autonomous outreach that auto-generates follow-up actions based on review verdicts.

**[Show presentation slide 3 — "The Key Insight" with Mermaid diagram, then slide 4 — "Three AI Capabilities"]**

---

## [1:00 - 1:15] Assumptions

> A few key assumptions I made:
> - The case strategy comes as a JSON structure — criteria, fields, and types. The wizard renders dynamically from this, so it works for any criteria combination without code changes.
> - AI grading is coaching, not legal advice. It helps applicants self-improve before attorney review.
> - Text evidence is the primary review target. Files are stored but not parsed — document analysis via vision LLM is the natural next step.
> - This is a single-user prototype — no auth or persistence. Those are straightforward to add.

---

## [1:15 - 3:30] Live Demo

**[Switch to the running app]**

> Let me walk through the full experience.

### Overview [1:15]
> This is the overview page. The applicant sees their case strategy — four criteria: Critical Role, High Remuneration, Original Contributions, and Membership. The time estimate says 20 to 30 minutes. Notice the demo mode banner — that tells us we're using simulated AI reviews since no API key is set.

**[Click "Start Onboarding"]**

### Demographics [1:30]
> First, demographics. Standard fields — name, passport upload, visa status. Each field type renders differently: text inputs, file upload zones, date pickers. All dynamically generated from the JSON schema.

**[Fill in a couple fields, click Continue]**

### Criterion — Critical Role [1:45]
> Now we're on Critical Role. Notice the two-step flow: first an intro that explains what USCIS looks for in this criterion, then the actual evidence fields. This progressive disclosure means the applicant understands the context before they start typing.

**[Click "Provide Evidence", fill in "key_responsibilities" with a detailed paragraph]**

### AI Copilot [2:00]
> At any point, the applicant can open the AI copilot.

**[Click the chat bubble in bottom-right]**

> Notice the chat panel slides in from the right without blocking the main content. The suggested prompts are specific to Critical Role — "What counts as a critical role?", "How do I describe key responsibilities effectively?". These change automatically when you navigate to a different criterion.

**[Click a suggested prompt, watch the response stream]**

> The response streams in real-time via WebSocket. And the system prompt is injected with the current criterion context, so the copilot gives targeted advice, not generic answers.

**[Close the chat panel, continue through remaining criteria with brief entries]**

### AI Evidence Review [2:45]
> Now I'll submit. Watch the review progress.

**[Click Submit on last criterion]**

> You can see "Analyzing Your Evidence" with a live progress counter — "1 of 3 fields reviewed", "2 of 3"... This runs as a background task so the UI stays responsive. Each field gets graded against USCIS standards.

### Results [3:00]
> Here are the results. Overall case strength: Moderate. Each criterion has a verdict — sufficient, needs improvement, or insufficient — with a score bar and field-level breakdown.

**[Scroll through criterion summary cards]**

> The detailed reviews show per-field feedback with actionable suggestions. For example, this field scored 55% with suggestions to add specific metrics and dates.

### Outreach [3:15]
> At the bottom, the outreach panel. These are autonomous actions — reminder emails for weak criteria, approval notifications for strong ones. All generated automatically from the review verdicts, no LLM needed.

**[Click "Demo: Simulate 24h Later"]**

> After 24 hours, pending reminders get sent and a "schedule a review call" action appears. This is what a case manager would normally do manually.

### Improve Flow [3:25]
> If I click "Improve Evidence", it takes me back to the first criterion's fields with all my prior data preserved. No lost work.

---

## [3:30 - 4:00] Architecture Summary

**[Switch back to presentation — AI Architecture slide with Mermaid diagram]**

> Quickly on the architecture: the evidence grading uses a LangGraph StateGraph with Pydantic structured output. The LLM is constrained to return a verdict, score, feedback, and suggestions — no free-form text to parse. Mock mode activates automatically when no API key is set, using text length as a grading heuristic.
>
> The whole prototype is about 2,000 lines of Python. Reflex handles the full stack — frontend, backend, and WebSocket state sync — so there's no separate API server or TypeScript to manage.

---

## [4:00 - 4:30] What I'd Do Differently

> With more time, the three biggest additions would be:
>
> **First**, document parsing — using a vision LLM to extract and grade evidence from uploaded PDFs and images. The LangGraph pipeline makes this a single new node.
>
> **Second**, persistent storage — right now state lives in memory. Adding a database is a Reflex config change.
>
> **Third**, a multi-node review pipeline — separate nodes for document parsing, evidence extraction, grading, and fact-checking.
>
> The architecture was designed for these extensions. Thank you.

---

## Recording Tips

- Keep the browser zoom at 100-110% for readability
- Use a clear, steady pace — not rushed
- Pause briefly between sections for visual transitions
- Pre-fill some form data to avoid dead typing time
- If using demo mode, mention it — the grading logic is intentionally simple but demonstrates the full UX flow
