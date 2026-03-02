"""Reflex application state — flat substates for performance."""
import reflex as rx

from lighthouse.seed_data import get_seed_strategy_dict


class CaseState(rx.State):
    """Core case data and navigation state."""

    # Case strategy (loaded from seed data or API)
    case_strategy: dict = {}
    criteria_list: list[dict] = []
    demographic_fields: list[dict] = []

    # Flattened fields per criterion for display (avoids nested foreach on untyped dicts)
    # Key: criterion index, Value: list of field dicts
    criteria_fields: list[list[dict]] = []

    # Navigation
    current_section: int = 0  # 0=overview, 1=demographics, 2+=criteria
    criterion_sub_step: int = 0  # 0=intro, 1=fields

    # Form data
    form_data: dict = {}

    # Case metadata
    case_id: str = ""
    applicant_name: str = ""
    case_status: str = "intake"

    # File uploads
    uploaded_files: dict = {}  # {field_name: [filename1, filename2, ...]}
    _upload_field_name: str = ""  # tracks which field is being uploaded
    show_upload_dialog: bool = False

    # Chat copilot
    chat_messages: list[dict] = []  # [{"role": "user"|"assistant", "content": str}]
    chat_input: str = ""
    is_chat_open: bool = False
    is_chat_streaming: bool = False

    # AI Review
    is_reviewing: bool = False
    review_results: list[dict] = []
    review_progress: int = 0
    review_error: str = ""

    # Outreach
    outreach_actions: list[dict] = []
    show_email_preview: str = ""  # criterion_name of expanded preview, "" = none

    @rx.var
    def total_sections(self) -> int:
        """Total number of sections: overview + demographics + N criteria."""
        return 2 + len(self.criteria_list)

    @rx.var
    def progress_percent(self) -> int:
        """Progress through the wizard as a percentage."""
        total = self.total_sections
        if total == 0:
            return 0
        return int((self.current_section / total) * 100)

    @rx.var
    def current_criterion(self) -> dict:
        """The criterion for the current section (if in a criterion section)."""
        idx = self.current_section - 2
        if 0 <= idx < len(self.criteria_list):
            return self.criteria_list[idx]
        return {}

    @rx.var
    def current_section_label(self) -> str:
        """Label for the current section."""
        if self.current_section == 0:
            return "Overview"
        if self.current_section == 1:
            return "Demographics"
        idx = self.current_section - 2
        if 0 <= idx < len(self.criteria_list):
            return self.criteria_list[idx].get("name", "Criterion")
        return ""

    @rx.var
    def is_first_section(self) -> bool:
        return self.current_section == 0

    @rx.var
    def is_last_section(self) -> bool:
        return self.current_section >= self.total_sections - 1

    @rx.var
    def step_labels(self) -> list[str]:
        """Labels for the step indicator."""
        labels = ["Overview", "Demographics"]
        for c in self.criteria_list:
            labels.append(c.get("name", "Criterion"))
        return labels

    @rx.var
    def current_criterion_fields(self) -> list[dict]:
        """Fields for the current criterion section."""
        idx = self.current_section - 2
        if 0 <= idx < len(self.criteria_fields):
            return self.criteria_fields[idx]
        return []

    @rx.var
    def chat_suggested_prompts(self) -> list[str]:
        """Context-aware suggested prompts for the current criterion."""
        from lighthouse.ai.copilot import get_suggested_prompts

        criterion = self.current_criterion
        return get_suggested_prompts(criterion.get("name", ""))

    @rx.var
    def chat_message_count(self) -> int:
        """Number of chat messages — used in UI instead of .length()."""
        return len(self.chat_messages)

    @rx.var
    def review_count(self) -> int:
        return len(self.review_results)

    @rx.var
    def review_sufficient_count(self) -> int:
        return sum(
            1 for r in self.review_results if r.get("verdict") == "sufficient"
        )

    @rx.var
    def review_needs_improvement_count(self) -> int:
        return sum(
            1
            for r in self.review_results
            if r.get("verdict") == "needs_improvement"
        )

    @rx.var
    def review_insufficient_count(self) -> int:
        return (
            self.review_count
            - self.review_sufficient_count
            - self.review_needs_improvement_count
        )

    @rx.var
    def review_avg_score(self) -> int:
        """Average review score as percentage (0-100)."""
        if not self.review_results:
            return 0
        avg = sum(r.get("score", 0) for r in self.review_results) / len(
            self.review_results
        )
        return int(avg * 100)

    @rx.var
    def case_strength_label(self) -> str:
        avg = self.review_avg_score
        if avg >= 70:
            return "Strong"
        if avg >= 40:
            return "Moderate"
        return "Needs Work"

    @rx.var
    def criterion_summaries(self) -> list[dict]:
        """Per-criterion aggregated review results."""
        summaries = []
        for i, criterion in enumerate(self.criteria_list):
            name = criterion.get("name", "")
            results = [
                r
                for r in self.review_results
                if r.get("criterion_name") == name
            ]
            if not results:
                continue
            avg = sum(r.get("score", 0) for r in results) / len(results)
            sufficient = sum(
                1 for r in results if r.get("verdict") == "sufficient"
            )
            needs = sum(
                1
                for r in results
                if r.get("verdict") == "needs_improvement"
            )
            insufficient = len(results) - sufficient - needs
            # Worst verdict determines criterion status
            if insufficient > 0:
                verdict = "insufficient"
            elif needs > 0:
                verdict = "needs_improvement"
            else:
                verdict = "sufficient"
            summaries.append(
                {
                    "name": name,
                    "description": criterion.get("description", ""),
                    "section_index": i + 2,
                    "avg_score": int(avg * 100),
                    "verdict": verdict,
                    "total_fields": len(results),
                    "sufficient_count": sufficient,
                    "needs_improvement_count": needs,
                    "insufficient_count": insufficient,
                }
            )
        return summaries

    @rx.var
    def outreach_action_count(self) -> int:
        """Number of outreach actions — used in UI instead of .length()."""
        return len(self.outreach_actions)

    @rx.var
    def is_demo_mode(self) -> bool:
        """True when running with mock/placeholder API keys."""
        import os

        api_key = os.environ.get("OPENAI_API_KEY", "")
        return not api_key or api_key.startswith("sk-placeholder")

    @rx.var
    def review_total_fields(self) -> int:
        """Total text fields eligible for review (for X of Y display)."""
        total = 0
        for criterion in self.criteria_list:
            for field in criterion.get("fields", []):
                if field.get("type") == "text":
                    total += 1
        return total

    @rx.event
    def next_section(self):
        """Advance to next section."""
        if self.current_section < self.total_sections - 1:
            self.current_section += 1
            self.criterion_sub_step = 0

    @rx.event
    def prev_section(self):
        """Go back to previous section."""
        if self.current_section > 0:
            self.current_section -= 1
            self.criterion_sub_step = 0

    @rx.event
    def go_to_section(self, section: int):
        """Jump to a specific section."""
        if 0 <= section < self.total_sections:
            self.current_section = section
            self.criterion_sub_step = 0

    @rx.event
    def show_criterion_fields(self):
        """Switch from criterion intro to fields sub-step."""
        self.criterion_sub_step = 1

    @rx.event
    def handle_step_submit(self, data: dict):
        """Merge step form data into parent dict, advance or trigger review."""
        self.form_data.update(data)
        if self.current_section >= self.total_sections - 1:
            # Last section: trigger AI review
            self.case_status = "submitted"
            self.review_results = []
            return CaseState.run_evidence_review
        self.current_section += 1
        self.criterion_sub_step = 0

    @rx.event
    def handle_final_submit(self, data: dict):
        """Merge final step data and start AI review."""
        self.form_data.update(data)
        self.case_status = "submitted"
        self.review_results = []
        return CaseState.run_evidence_review

    @rx.event(background=True)
    async def run_evidence_review(self):
        """Background task: review all text evidence with AI."""
        import asyncio

        from lighthouse.ai.review import grade_evidence

        async with self:
            self.is_reviewing = True
            self.review_results = []
            self.review_progress = 0
            self.review_error = ""

        # Collect text fields to review (read state snapshot)
        criteria = self.criteria_list
        form = self.form_data
        fields_to_review = []
        for criterion in criteria:
            for field in criterion.get("fields", []):
                if field.get("type") == "text":
                    value = form.get(field["name"], "").strip()
                    if value:
                        fields_to_review.append(
                            {
                                "criterion_name": criterion["name"],
                                "criterion_description": criterion.get(
                                    "description", ""
                                ),
                                "field_name": field["name"],
                                "field_type": field["type"],
                                "value": value,
                            }
                        )

        if not fields_to_review:
            async with self:
                self.is_reviewing = False
                self.case_status = "reviewed"
            return

        results: list[dict] = []
        for i, item in enumerate(fields_to_review):
            try:
                grade = await asyncio.to_thread(
                    grade_evidence,
                    item["criterion_name"],
                    item["criterion_description"],
                    item["field_name"],
                    item["field_type"],
                    item["value"],
                )
                feedback = grade.get("feedback", "")
                suggestions = grade.get("suggestions", [])
                if suggestions:
                    feedback += "\n\nSuggestions:\n" + "\n".join(
                        f"\u2022 {s}" for s in suggestions
                    )
                results.append(
                    {
                        "criterion_name": item["criterion_name"],
                        "field_name": item["field_name"],
                        "verdict": grade.get("verdict", "error"),
                        "score": grade.get("score", 0.0),
                        "feedback": feedback,
                    }
                )
            except Exception as e:
                results.append(
                    {
                        "criterion_name": item["criterion_name"],
                        "field_name": item["field_name"],
                        "verdict": "error",
                        "score": 0.0,
                        "feedback": "We couldn't review this field automatically. Please check your text is complete and try again.",
                    }
                )

            async with self:
                self.review_results = list(results)
                self.review_progress = int(
                    ((i + 1) / len(fields_to_review)) * 100
                )

        async with self:
            self.is_reviewing = False
            self.case_status = "reviewed"
            # Auto-generate outreach actions after review completes
            from lighthouse.ai.outreach import generate_outreach_actions

            summaries = self.criterion_summaries
            self.outreach_actions = generate_outreach_actions(
                summaries, self.case_id
            )

    @rx.event
    def restart_for_improvement(self):
        """Reset to intake so user can improve flagged evidence."""
        self.case_status = "intake"
        self.current_section = 2  # First criterion
        self.criterion_sub_step = 0

    @rx.event
    def go_to_criterion_for_improvement(self, section_index: int):
        """Jump to a specific criterion's evidence fields for improvement."""
        self.case_status = "intake"
        self.current_section = section_index
        self.criterion_sub_step = 1  # Skip intro, go directly to fields

    # ------------------------------------------------------------------
    # Outreach handlers
    # ------------------------------------------------------------------

    @rx.event
    def generate_outreach(self):
        """Generate outreach actions from current review results."""
        from lighthouse.ai.outreach import generate_outreach_actions

        self.outreach_actions = generate_outreach_actions(
            self.criterion_summaries, self.case_id
        )

    @rx.event
    def simulate_time_passage(self):
        """Simulate 24h passing — triggers reminder generation for demo."""
        from lighthouse.ai.outreach import generate_outreach_actions

        self.outreach_actions = generate_outreach_actions(
            self.criterion_summaries, self.case_id, hours_elapsed=24
        )

    @rx.event
    def toggle_email_preview(self, criterion_name: str):
        """Toggle email preview expansion for a specific action."""
        if self.show_email_preview == criterion_name:
            self.show_email_preview = ""
        else:
            self.show_email_preview = criterion_name

    @rx.var
    def fields_with_uploads(self) -> list[str]:
        """List of field names that have at least one uploaded file."""
        return [k for k, v in self.uploaded_files.items() if v]

    @rx.event
    def set_upload_field(self, field_name: str):
        """Track which field is being uploaded for."""
        self._upload_field_name = field_name

    @rx.event
    def open_upload_for_field(self, field_name: str):
        """Set upload field context and open upload dialog."""
        self._upload_field_name = field_name
        self.show_upload_dialog = True

    @rx.event
    def set_show_upload_dialog(self, value: bool):
        """Toggle upload dialog visibility."""
        self.show_upload_dialog = value

    async def handle_upload(self, files: list[rx.UploadFile]):
        """Save uploaded files and track per field."""
        from pathlib import Path

        for file in files:
            try:
                upload_data = await file.read()
                filename = Path(file.filename).name  # cross-browser safety
                outfile = rx.get_upload_dir() / filename
                with outfile.open("wb") as f:
                    f.write(upload_data)

                field_name = self._upload_field_name
                if field_name:
                    current = self.uploaded_files.get(field_name, [])
                    if filename not in current:
                        current.append(filename)
                    self.uploaded_files[field_name] = current
            except Exception:
                pass  # Skip failed uploads gracefully for prototype

    @rx.event
    def remove_uploaded_file(self, field_name: str, filename: str):
        """Remove a file from a field's upload list."""
        current = self.uploaded_files.get(field_name, [])
        if filename in current:
            current.remove(filename)
            self.uploaded_files[field_name] = current

    # ------------------------------------------------------------------
    # Chat copilot handlers
    # ------------------------------------------------------------------

    @rx.event
    def toggle_chat(self):
        """Open/close chat drawer."""
        self.is_chat_open = not self.is_chat_open

    @rx.event
    def set_is_chat_open(self, value: bool):
        """Set chat drawer open state (for drawer on_open_change)."""
        self.is_chat_open = value

    @rx.event
    def set_chat_input(self, value: str):
        """Update chat input text."""
        self.chat_input = value

    @rx.event
    def send_chat_message(self):
        """Send user message and trigger AI response."""
        if not self.chat_input.strip():
            return
        self.chat_messages = self.chat_messages + [
            {"role": "user", "content": self.chat_input.strip()}
        ]
        self.chat_input = ""
        return CaseState.stream_chat_response

    @rx.event
    def send_suggested_prompt(self, prompt: str):
        """Send a suggested prompt as a message."""
        self.chat_messages = self.chat_messages + [
            {"role": "user", "content": prompt}
        ]
        return CaseState.stream_chat_response

    @rx.event(background=True)
    async def stream_chat_response(self):
        """Background task: stream AI copilot response."""
        import asyncio

        from lighthouse.ai.copilot import (
            stream_chat_response as _stream,
        )

        async with self:
            self.is_chat_streaming = True

        # Read state snapshot
        messages = self.chat_messages
        section_label = self.current_section_label
        criterion = self.current_criterion
        criterion_name = criterion.get("name", "")
        criterion_description = criterion.get("description", "")

        # Add empty assistant message to stream into
        async with self:
            self.chat_messages = messages + [
                {"role": "assistant", "content": ""}
            ]

        # Run synchronous generator in thread, collect chunks
        try:
            gen = await asyncio.to_thread(
                lambda: list(
                    _stream(
                        messages,
                        section_label,
                        criterion_name,
                        criterion_description,
                    )
                )
            )
        except Exception:
            async with self:
                updated = list(self.chat_messages)
                if updated and updated[-1]["role"] == "assistant":
                    updated[-1] = {
                        "role": "assistant",
                        "content": "Sorry, I encountered an issue. Please try again.",
                    }
                    self.chat_messages = updated
                self.is_chat_streaming = False
            return

        full_response = ""
        for chunk in gen:
            full_response += chunk
            async with self:
                updated = list(self.chat_messages)
                if updated and updated[-1]["role"] == "assistant":
                    updated[-1] = {
                        "role": "assistant",
                        "content": full_response,
                    }
                    self.chat_messages = updated

        async with self:
            self.is_chat_streaming = False

    def load_seed_case(self):
        """Load the seed case strategy for demo purposes."""
        strategy = get_seed_strategy_dict()
        self.case_strategy = strategy
        self.criteria_list = strategy.get("criteria", [])
        self.demographic_fields = strategy.get("demographic_fields", [])
        self.criteria_fields = [
            c.get("fields", []) for c in self.criteria_list
        ]
        self.case_id = "demo-case-001"
        self.case_status = "intake"
