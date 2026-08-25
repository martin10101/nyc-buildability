---
paths:
  - "tools/agent_supervisor/**"
---
# Supervisor Freeze — Defect-Only Maintenance Lane (D-010 Phase 1; AD-065; AD-093)

Path-scoped (2026-08-06): loads only when touching `tools/agent_supervisor/**`.

The M0-T036 supervisor is **FROZEN**. Its behavior identity (merged main SHA, the
`tools/agent_supervisor/` git tree hash, and the passing test-suite baseline) is pinned in
`project-control/reports/M0-T039-supervisor-freeze.md`. That report is the baseline every
supervisor change diffs against. Freezing pins an identity; it activates nothing (the
supervisor is SHADOW-ONLY).

## 1. No speculative supervisor features

No supervisor feature additions unrelated to a D-010 requirement. Per D-010 Section 0A.10, no
new supervisor task may be created merely because a feature would be nicer, more complete,
enterprise-ready, reusable by others, future-proof, elegant, or theoretically safer.

## 2. AD-093 qualifying evidence (verbatim, Section 0A.10)

A new supervisor task requires at least one of:

- a reproduced defect;
- a failed acceptance scenario;
- a demonstrated security risk;
- provider CLI/API drift;
- a measured context or usage problem;
- an unresolved crash/recovery problem;
- inability to complete an authorized product task;
- or a requirement explicitly listed in this directive.

**D-024 recognition (amendment 2026-08-25, task M0-T086):** a requirement explicitly listed in
owner directive **D-024** (the captured Fable–Codex continuous-agent-loop directive,
`project-control/directives/D-024-fable-codex-loop/`) is equally qualifying evidence. Cite the
specific captured `D-024-R###` requirement ID in **both** the task packet and the commit message,
exactly as §3 requires. Authorized by D-024 §1 ("every task that touches that area must cite this
directive's captured requirement ID as qualifying evidence … amend or supersede the rule
transparently under this directive's authority"); this amendment changes nothing else — the
defect-only lane, gates, R595 prerequisite, and suite-baseline duty below stand unchanged.

## 3. Evidence-citation duty

Every new supervisor task must cite the qualifying evidence (from §2) that authorizes it in
**both** the task packet and the commit message. A change to `tools/agent_supervisor/**`
without a cited qualifying-evidence item is out of scope and must be refused at the gate.

## 4. Standard gates, no new approval path

The defect lane runs under the **standard governance gates** (this task's set: G0/G2/G3/G5).
This rule creates **no** new or expedited approval path. It does **not** lift or alter the
R595 pre-activation prerequisite (MANDATORY BLOCKING per
`project-control/reports/M0-T036-ACTIVATION-CHECKLIST.md`); the supervisor stays SHADOW-ONLY.
Any supervisor change is expected to change the tree hash and must re-establish the
`M0-T039-supervisor-freeze.md` suite baseline (>= 1165 tests, 0 failures) under those gates.
