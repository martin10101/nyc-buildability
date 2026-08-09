---
name: project-control-cli-hardening-review
description: G5 probe method for tools/project_control.py (M0-T014) - gate classes, accept-time recheck, fail-closed-via-crash pattern, known accepted residuals
metadata:
  type: project
---

M0-T014 hardened `tools/project_control.py` with structural gate classes (G2=self_check by
"orchestrator" only; G0/G7 administrative; G1/G3/G4/G5/G6 independent = rostered reviewer !=
producer), a progress transition enum (never `accepted`, percent 0-99), accept preconditions
(awaiting_gate + all gates PASS + deps accepted + zero open blockers, blocker fail-closed on
missing/corrupt status), task-id regex `^M\d+-T\d{3}(-R\d+)?$`, report-path containment into
project-control/reports/, and mkstemp+os.replace atomic writes.

**Why:** owner code-audit P0; the CLI is the orchestrator's own control plane and --agent is a
caller-provided label (documented as non-cryptographic; enforcement is procedural per ADR-005).

**How to apply (future re-reviews of this tool):** rerun this probe set in a temp project:
whitespace/case reviewer names ("orchestrator ", "Reviewer-Y") — must fail closed on exact match;
gate-before-claim then claim as the same agent — accept-time recheck (reviewer==producer) must
reject; ADS report path `x.json:stream` — contained, fails on exists(); corrupt task/gate JSON and
JSON-list blocker files at accept — fail closed via unhandled traceback (exit 1, no write), which
is accepted behavior, not a defect. Known accepted residuals (low, documented in the M0-T014 G5
report): "orchestrator" placed on reviewer_agents can record an independent gate with role
independent_review; `new-task --gates` accepts arbitrary gate names (unsatisfiable = fail-closed);
legacy role-less gate records satisfy accept by design (validate-on-write). Direct file forging is
outside the tool's authority — anyone with FS write can edit the ledger directly.
