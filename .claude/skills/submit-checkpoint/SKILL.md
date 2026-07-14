---
description: Submits producer evidence and a project checkpoint without self-approving the task. Use after a meaningful task increment or producer self-check.
---

Create a structured report using `docs/templates/AGENT_REPORT.md`. Include exact commands, outputs, examples, changed files, assumptions, source evidence, risks, and incomplete work.

Run the relevant tests and save artifacts. Submit through `python tools/project_control.py submit`. Set requested status to `awaiting_gate`, `blocked`, or `needs_split`. Never set your own task to accepted or 100%.
