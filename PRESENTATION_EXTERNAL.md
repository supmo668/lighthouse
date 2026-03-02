# Lighthouse — AI-Powered O-1 Visa Onboarding

## Slide 1: The Problem

**O-1 visa onboarding is broken.**

- Applicants face 8 USCIS criteria, dozens of evidence fields, zero guidance on "good enough"
- Current process: long emails, spreadsheets, phone calls → high abandonment, 3-4 revision cycles per criterion
- H-1B fee tripling to $100K is driving explosive O-1 demand — manual intake doesn't scale

> **Presenter note:** Open with: "Imagine you just got accepted to a prestigious program, and now you need to prove you're extraordinary — but nobody tells you what that means. That's the O-1 experience today."

---

## Slide 2: The Insight

Evidence quality should be assessed **during** collection, not after.

Current tools (e.g., OpenSphere) score evidence as a separate step *after* submission. That creates the revision loop. What if the system coached you in real-time *while* you're writing?

> **Presenter note:** This is the core differentiator. Every other tool is post-hoc. We moved the evaluation upstream.

---

## Slide 3: The Solution — Lighthouse

A TurboTax-style wizard that **adapts to each applicant's case strategy** and provides real-time AI coaching.

**Three AI capabilities working together:**

| Capability | What It Does |
|------------|-------------|
| Evidence Grading | LLM scores each field against USCIS standards with structured verdicts (sufficient / needs improvement / insufficient) |
| AI Copilot | Context-aware chat that knows which criterion you're on and coaches you through it |
| Autonomous Outreach | Auto-generates follow-up emails for weak criteria, approval notifications for strong ones |

> **Presenter note:** Walk through the wizard flow: Overview → Demographics → Criterion 1 (intro + fields) → ... → Criterion N → AI Review → Results + Outreach. Each step is progressive disclosure — applicant only sees what's relevant to their strategy.

---

## Slide 4: Live Demo Walkthrough

**Demo flow (3-4 minutes):**

1. **Overview** — Case strategy loaded, time estimate shown ("20-30 minutes")
2. **Demographics** — Standard intake (name, passport, visa status)
3. **Criterion: Critical Role** — Intro explains what USCIS needs, then fields with text/file/URL inputs
4. **Open AI Copilot** — Click chat bubble, ask "What counts as a critical role?" → streaming response with criterion-specific guidance
5. **Submit all criteria** → Watch real-time review: "3 of 10 fields reviewed..."
6. **Results dashboard** — Score breakdown per criterion, color-coded verdicts
7. **Outreach panel** — Auto-generated emails: reminders for weak criteria, approvals for strong ones
8. **Simulate 24h** — Shows escalated actions: sent reminders + "Schedule a review call" suggestion

> **Presenter note:** Demo mode uses simulated AI reviews (length-based scoring) when no API key is set. With a real key, GPT-4o-mini grades each field against actual USCIS standards. Both paths demonstrate the full UX.

---

## Slide 5: AI Pipeline Architecture

```
User submits evidence
        │
        ▼
┌─────────────────────┐
│  LangGraph Pipeline  │
│  (StateGraph)        │
│                      │
│  ┌────────────────┐  │
│  │ review_evidence │──┼──► Structured Output (Pydantic)
│  │    node         │  │    → verdict, score, feedback, suggestions
│  └────────────────┘  │
│                      │
│  GPT-4o-mini         │
│  + mock fallback     │
└─────────────────────┘
        │
        ▼
┌─────────────────────┐
│  Outreach Engine     │
│  Rule-based actions  │
│  from verdict data   │
└─────────────────────┘
        │
        ▼
  Reminder / Approval / Schedule actions
```

- **Structured output** ensures consistent grading (no free-form LLM responses to parse)
- **Mock mode** enables full demo without API costs
- **Background tasks** keep the UI responsive during multi-field review

> **Presenter note:** Key technical point: we use Pydantic `EvidenceGrade` schema with `with_structured_output()` — the LLM is constrained to return verdict/score/feedback/suggestions. No regex parsing, no prompt-and-pray.

---

## Slide 6: Key Metrics & Targets

| Metric | Target | Mechanism |
|--------|--------|-----------|
| First-submission acceptance | >70% fields pass on first try | Real-time AI coaching reduces guesswork |
| Revision cycles per criterion | <1.5 (from industry ~3-4) | Inline scoring catches issues before submission |
| Full intake completion | <45 min for 3-criteria case | Progressive disclosure + copilot reduce confusion |
| Case completion rate | >80% started → submitted | Guided wizard vs. blank spreadsheet |

> **Presenter note:** These are prototype targets. Real measurement requires a production deployment with analytics instrumentation.

---

## Slide 7: What's Next

**Immediate (production-ready):**
- Document parsing (PDF/image → LLM for evidence extraction)
- Attorney dashboard for case oversight
- Multi-strategy support (any combination of 8 O-1 criteria)

**Future:**
- DOL prevailing wage API integration for salary benchmarking
- Multi-visa expansion (EB-1, O-1B)
- Human-in-the-loop review gates for borderline evidence

> **Presenter note:** The architecture already supports any criteria combination — the seed data is just one example strategy. The wizard dynamically renders based on whatever JSON strategy is loaded.

---

## Q&A Prep

**Expected questions and answers:**

**Q: How accurate is the AI grading?**
A: With GPT-4o-mini + structured output, grading is consistent and explainable. The threshold for auto-approve vs human review (currently 0.7) would be tuned with real case data. This is a coaching tool, not a legal decision-maker.

**Q: What about document/file analysis?**
A: Current scope handles text evidence and file uploads. Document parsing (extracting text from PDFs/images via vision LLM) is the natural next step and fits cleanly into the existing LangGraph pipeline.

**Q: How does this handle different case strategies?**
A: The wizard is fully data-driven. Load a different `case_strategy` JSON (different criteria, different fields) and the entire UX adapts. No code changes required.

**Q: What about data privacy / security?**
A: Immigration data is sensitive. Production deployment would need encryption at rest, audit logging, SOC 2 compliance, and data residency controls. The prototype focuses on UX and AI pipeline validation.
