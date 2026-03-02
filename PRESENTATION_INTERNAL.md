# Lighthouse — Internal Technical Presentation

## Slide 1: Requirements → Design Decisions

**Starting point:** Build an O-1 visa onboarding experience that (1) adapts to any case strategy, (2) educates during collection, (3) handles pushback/resubmission, (4) is deployable.

**Key constraint:** Hackathon timeline → maximize prototype fidelity, minimize infrastructure.

| Requirement | Decision | Why |
|------------|----------|-----|
| "Adapt to any case strategy" | Data-driven wizard from JSON, not hardcoded views | One component renders any criteria combination |
| "Educate during collection" | Inline AI copilot + per-criterion intros | Users learn *while* filling fields, not in separate docs |
| "Handle pushback" | Structured verdict system (sufficient/needs_improvement/insufficient) | Clean state machine: intake → submitted → reviewed, with explicit re-entry paths |
| "Deployable" | Reflex (Python full-stack) + Docker | Single-language stack, no JS/API split, single container |

> **Presenter note:** Every design decision traces back to a requirement. The data-driven approach was critical — hardcoding 4 criteria means rebuilding for every new client. JSON-driven means zero code changes per strategy.

---

## Slide 2: Why Reflex (and What It Cost Us)

**Choice:** Reflex 0.8.27 — Python-only full-stack with WebSocket real-time UI.

**Why Reflex:**
- Single language (Python) for frontend + backend + AI pipeline
- Native WebSocket state sync — real-time streaming without custom socket code
- `@rx.event(background=True)` for long-running AI tasks without blocking UI
- Rapid prototyping: component-level Python code, no React/API boilerplate

**What it cost us (framework-specific workarounds):**

| Issue | Root Cause | Workaround |
|-------|-----------|------------|
| No `>`, `<`, `!=` on dict subscript vars | `ObjectItemOperation` doesn't support comparison operators | Use `rx.match` with string equality + default case |
| `.length()` fails on `Var[list]` | Reflex runtime limitation | Computed `@rx.var` returning `len(self.list)` |
| List `.append()` doesn't trigger re-render | Reflex state mutation tracking | Reassignment: `self.var = self.var + [new]` |
| `rx.upload_files(upload_id=...)` needs static string | Dynamic Var not accepted as upload_id | Single static upload ID, track field context via separate state var |

> **Presenter note:** These are real gotchas we hit and solved. Reflex was net-positive for velocity, but these issues added ~20% overhead. A Next.js stack would avoid these but require Python API + TypeScript frontend — doubling the surface area.

---

## Slide 3: AI Workflow Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    AI LAYER                               │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │ review.py    │  │ copilot.py   │  │ outreach.py  │   │
│  │              │  │              │  │              │   │
│  │ LangGraph    │  │ LangChain    │  │ Rule-based   │   │
│  │ StateGraph   │  │ Streaming    │  │ from review  │   │
│  │ + Structured │  │ + Context    │  │ verdicts     │   │
│  │   Output     │  │   Injection  │  │              │   │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘   │
│         │                 │                 │            │
│     Pydantic          System Prompt      Verdict        │
│     EvidenceGrade     per-criterion      Analysis       │
│         │                 │                 │            │
│  ┌──────┴─────────────────┴─────────────────┴────────┐  │
│  │              Mock Mode Fallback                     │  │
│  │  No API key → deterministic responses               │  │
│  │  (length-based grading, keyword-based chat)         │  │
│  └────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

**Three AI modules, each with a distinct pattern:**

### 1. Evidence Grading (`review.py`)
- **Pattern:** LangGraph `StateGraph` → single `review_evidence` node → structured output
- **LLM:** GPT-4o-mini with `with_structured_output(EvidenceGrade)`
- **Output:** `{verdict, score, feedback, suggestions}` — Pydantic-enforced schema
- **Mock:** Length-based: >200 chars → sufficient, >50 → needs_improvement, else → insufficient
- **Why LangGraph?** Extensible to multi-node (e.g., add document parsing node, salary benchmark node) without refactoring

### 2. AI Copilot (`copilot.py`)
- **Pattern:** LangChain streaming with context-injected system prompt
- **Context injection:** System prompt includes current section + criterion name + description
- **Suggested prompts:** Per-criterion prompt bank (Critical Role, High Remuneration, etc.) with defaults fallback
- **Mock:** Keyword matching on user message → canned responses

### 3. Autonomous Outreach (`outreach.py`)
- **Pattern:** Pure rule-based, no LLM call — operates on verdict data from grading
- **Logic:** insufficient/needs_improvement → reminder email, sufficient → approval email
- **Time simulation:** `hours_elapsed` parameter: 0 = pending, 24 = sent + "schedule call" suggestion
- **Why not LLM?** Deterministic actions from structured verdicts. LLM would add latency/cost with no quality gain.

> **Presenter note:** Design principle: use LLMs where judgment is needed (evidence grading, coaching), use rules where verdicts already provide the signal (outreach). This keeps the outreach instant and predictable.

---

## Slide 4: State Machine & Real-Time UX

**Case status flow:**
```
intake ──submit──► submitted ──review──► reviewed
  ▲                                        │
  └──────── restart_for_improvement ◄──────┘
```

**Background task pattern:**
```python
@rx.event(background=True)
async def run_evidence_review(self):
    async with self:              # Lock state, update UI
        self.is_reviewing = True

    for field in fields:
        grade = await asyncio.to_thread(grade_evidence, ...)  # Sync LLM → thread
        async with self:          # Progressive update
            self.review_results = list(results)
            self.review_progress = pct

    async with self:
        self.is_reviewing = False
        self.outreach_actions = generate_outreach_actions(...)  # Inline, not chained
```

**Key patterns:**
- `async with self` — Reflex state lock for thread-safe UI updates from background tasks
- `asyncio.to_thread()` — Wraps synchronous LangChain/LangGraph calls without blocking event loop
- Progressive updates — UI shows "3 of 10 fields reviewed" in real-time via WebSocket
- Inline outreach generation — runs inside final `async with self` block instead of event chaining (safer than `yield` in background tasks)

> **Presenter note:** The `async with self` pattern is the most important Reflex pattern to understand. Every state mutation from a background task MUST be inside this context manager. Missing it = silent state corruption.

---

## Slide 5: Component Architecture

```
lighthouse.py (app entry)
    └── layout.py
        ├── Demo mode banner (rx.cond on is_demo_mode)
        ├── Step indicator (progress bar)
        ├── wizard.py (main content router)
        │   ├── overview_step()
        │   ├── demographics_step()
        │   ├── criterion_step() ──► criterion_intro() | criterion_fields()
        │   │   └── Field type dispatch:
        │   │       ├── text → rx.text_area
        │   │       ├── date → rx.input(type="date")
        │   │       ├── file → upload dialog
        │   │       ├── url → rx.text_area
        │   │       └── files_or_urls → upload + URL combo
        │   ├── reviewing_step() ──► "X of Y fields reviewed" progress
        │   └── results_step()
        │       ├── Score summary cards
        │       ├── Per-criterion verdict cards (rx.match on verdict)
        │       └── outreach_panel() (outreach.py)
        └── chat.py (floating drawer)
            ├── Message history
            ├── Streaming response
            └── Suggested prompts (per-criterion)
```

**Data-driven rendering pattern:**
- `criteria_list` drives which sections exist (any number of criteria)
- `rx.foreach` + `rx.match` for dynamic field type rendering
- `rx.cond` for conditional UI (e.g., intro vs fields sub-step, reviewed vs intake state)
- No hardcoded criterion references — everything routes through `current_section` index

> **Presenter note:** The wizard is essentially a state machine renderer. `current_section` (int) + `criterion_sub_step` (0 or 1) + `case_status` (string) determines what the user sees. All data comes from the JSON strategy.

---

## Slide 6: Key Design Decisions & Reasoning

### Decision 1: Structured Output over Free-form LLM
**Options:** (a) Free-form LLM response with regex parsing, (b) Pydantic structured output
**Chose (b):** Guarantees `verdict` is one of 3 values, `score` is 0-1 float. No parsing failures. Downstream logic (outreach, UI rendering) depends on clean data.

### Decision 2: Single LangGraph Node (for now)
**Options:** (a) Multi-node graph from the start, (b) Single node, extensible later
**Chose (b):** The review task is a single LLM call with structured output. Multi-node adds complexity without current value. But LangGraph makes adding nodes (doc parsing, benchmark lookup) a one-line change later.

### Decision 3: Rule-based Outreach over LLM-generated
**Options:** (a) LLM writes outreach emails, (b) Template emails from verdict data
**Chose (b):** Verdicts already encode all needed information. LLM would add 2-3s latency per email with no quality gain. Rule-based is instant and deterministic.

### Decision 4: Mock Mode as First-Class
**Options:** (a) Require API key, (b) Graceful fallback to mock
**Chose (b):** Demo mode with `sk-placeholder` enables full UX walkthrough without API costs. Mock grading uses text length as a heuristic — short text = insufficient, medium = needs improvement, long = sufficient. Surprisingly effective for demos.

### Decision 5: Flat State over Substates
**Options:** (a) Reflex substates (nested state classes), (b) Single flat CaseState
**Chose (b):** Substates add indirection for cross-state access. A single flat state with computed vars keeps everything accessible. Tradeoff: larger state class (~580 lines), but zero cross-reference complexity.

> **Presenter note:** Each decision has a clear "why not the alternative." In a production context, Decision 2 and 5 would likely flip — multi-node graph for richer review pipeline, substates for maintainability at scale.

---

## Slide 7: Tech Stack Summary

| Layer | Technology | Role |
|-------|-----------|------|
| Framework | Reflex 0.8.27 | Python full-stack with WebSocket UI |
| AI Orchestration | LangGraph 0.3+ | Evidence review pipeline (StateGraph) |
| LLM Provider | OpenAI GPT-4o-mini | Grading + copilot chat (via LangChain) |
| Structured Output | Pydantic | `EvidenceGrade` schema enforcement |
| LLM Integration | LangChain Core + OpenAI | Chat streaming, structured LLM calls |
| Deployment | Docker (Python 3.11-slim + Node 20) | Single container, `reflex run --env prod` |
| State Sync | Reflex WebSocket | Real-time background task progress |

**Lines of code (approximate):**

| Module | Lines | Purpose |
|--------|-------|---------|
| `state.py` | ~580 | All application state + event handlers |
| `wizard.py` | ~740 | Wizard UI + field rendering |
| `review.py` | ~135 | LangGraph evidence grading |
| `copilot.py` | ~135 | AI chat streaming |
| `outreach.py` | ~140 | Autonomous action generation |
| `chat.py` | ~130 | Chat drawer component |
| `layout.py` | ~60 | App shell + demo banner |
| **Total** | **~2,000** | Full prototype |

> **Presenter note:** ~2,000 lines for a full AI-powered wizard with grading, chat, outreach, and real-time updates. Reflex's Python-only approach is why — no separate API layer, no TypeScript frontend, no state sync boilerplate.

---

## Slide 8: Room for Improvement

### High Priority (would build next)
1. **Document parsing** — PDF/image uploads currently stored but not analyzed. Add a LangGraph node using vision LLM (GPT-4o) to extract and grade document content.
2. **Persistent storage** — Currently in-memory (Reflex state). Add database (SQLite/Postgres) for case persistence across sessions.
3. **Authentication** — No auth in prototype. Add magic link or OAuth for multi-user.

### Medium Priority (architectural upgrades)
4. **Multi-node LangGraph** — Add nodes for: document parsing → evidence extraction → grading → fact-checking. Current single-node is a placeholder for richer pipeline.
5. **Salary benchmarking tool** — Integrate DOL prevailing wage data for the High Remuneration criterion (currently self-reported).
6. **Attorney dashboard** — Case manager view showing all applicant progress, flagged evidence, and approval workflow.
7. **Streaming evidence review** — Currently batch-reviews all fields sequentially. Could parallelize with `asyncio.gather()` for 3-4x speedup.

### Lower Priority (polish)
8. **Accessibility** — ARIA labels, keyboard navigation, screen reader testing.
9. **i18n** — Many O-1 applicants aren't native English speakers.
10. **Analytics** — Track funnel metrics (completion rate, time per step, revision count) for hypothesis validation.

### Architectural Debt
11. **Reflex `ObjectItemOperation` workarounds** — Multiple `rx.match` chains where simple comparisons should work. Framework upgrade may resolve.
12. **Single flat state class** — At 580 lines, should split into substates (Navigation, AI, Outreach) for maintainability.
13. **No test suite** — Prototype has zero automated tests. Critical path: state transitions, grading pipeline, outreach logic.

> **Presenter note:** Items 1-3 are the gap between "prototype" and "MVP." The architecture already supports them — persistent storage is a Reflex config change, document parsing is a new LangGraph node, auth is Reflex middleware.

---

## Q&A Prep

**Q: Why not Next.js + Python API?**
A: Hackathon timeline. Reflex gives us real-time WebSocket UI, background tasks, and streaming — all in Python. The tradeoff: framework maturity issues (ObjectItemOperation, list mutation). For production, the team should evaluate whether Reflex scales or if a Next.js + FastAPI split is worth the velocity cost.

**Q: Why GPT-4o-mini over Claude?**
A: Structured output support was more mature in LangChain-OpenAI at development time. The architecture is provider-agnostic — `_get_structured_llm()` is a 5-line swap. Requirements.txt already includes `langchain-anthropic`.

**Q: How would you handle concurrent users?**
A: Reflex manages state per WebSocket session. Each user gets isolated `CaseState`. The LLM calls are the bottleneck — add rate limiting and queuing for production. Background tasks already run without blocking other sessions.

**Q: What's the accuracy of the mock grading?**
A: Mock grading is intentionally simple (text length heuristic). It's designed to demonstrate the UX flow, not evaluate evidence. Real accuracy comes from GPT-4o-mini with structured output — which we observed produces consistent, explainable grading in testing.

**Q: How long did this take to build?**
A: [Defer to presenter's actual timeline]. The PRP workflow (Plan → Research → Plan → Implement) with Claude Code handled 8 phases systematically. Each phase: codebase analysis → plan → implementation → validation → report.
