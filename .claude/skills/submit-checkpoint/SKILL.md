---
description: Submits producer evidence and a project checkpoint without self-approving the task. Use after a meaningful task increment or producer self-check.
---

Create a structured report using `docs/templates/AGENT_REPORT.md`. Include exact commands, outputs, examples, changed files, assumptions, source evidence, risks, and incomplete work.

Include a **requirement-to-evidence map** — one row per packet-named requirement **and per governing directive requirement ID** (`D-<nnn>-R<nnn>`), mapping each to the specific test/output/file path that satisfies it, with any unmet item explicitly flagged. For an in-regime task this map is mandatory: submit through `python tools/project_control.py submit --evidence-map <path>` (a JSON `{"requirements": {"D-001-R001": ["…"]}}` in `project-control/reports/`); submission is refused if any applicable requirement is uncovered.

Run the relevant tests and save artifacts. Submit through `python tools/project_control.py submit`. Set requested status to `awaiting_gate`, `blocked`, or `needs_split`. Never set your own task to accepted or 100%.
