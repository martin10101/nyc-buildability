# M0-T033 — G0 readiness (administrative)

**Task:** M0-T033 — Governance-orchestrator unblock-roster semantics
**Recorded by:** orchestrator (main session, Opus 5 under the D-004-R307 availability exception)
**Base identity:** `abb89b821d3cb7beacc916784c92c9d5570122e0` (origin/main after PR #131)
**Authority:** owner directive D-004 amendment 9 (`source-010-amendment.md`), rows D-004-R332, R337–R343
**Gate class:** G0 is administrative. It records that the packet is contractible and ready to claim.
It is **not** an independent review and satisfies no independent-gate requirement.

## 1. Packet completeness

| Field | Value | Source |
|---|---|---|
| `task_type` | `governance` | contracted |
| `milestone_id` | `M0` | contracted |
| `required_gates` | G0, G2, G3, G5 | D-004-R340 (exact) |
| `reviewer_agents` | code-reviewer, security-reviewer, control-plane-verifier, directive-compliance-verifier | D-004-R339 (exact) |
| `producer_agent` | assigned at claim → `backend-engineer` | D-004-R338 |
| `directive_refs` | `D-001:ALL`, `D-004:ALL` | D-004-R341 |
| `allowed_paths` | 5 entries (see §3) | D-004-R342 |
| `forbidden_paths` | 9 entries | D-004-R343 |
| `acceptance_scenarios` | 12 executable | D-004-R362–R371 + no-hard-coding/containment |
| `dependencies` | none | — |

## 2. Producer qualification and independence (D-004-R338)

`backend-engineer` was selected after live roster inspection of `.claude/agents/`:

- **Real and existing:** `.claude/agents/backend-engineer.md` is present.
- **Non-orchestrator:** it is not the reserved `orchestrator` label.
- **Qualified for Python control-plane tooling:** its charter covers FastAPI services, contracts,
  job control, provenance, and **analysis state transitions** — i.e. Python service and
  state-machine code, which is exactly what `tools/project_control.py` is.
- **Distinct from every reviewer:** `backend-engineer` ∉ {code-reviewer, security-reviewer,
  control-plane-verifier, directive-compliance-verifier}, and all four reviewer definitions exist
  as separate agent files. Producer ≠ reviewer holds for all four gates.

## 3. Scope is exactly the owner's authorization (D-004-R342/R343)

Authorized: `tools/project_control.py`; `tools/test_project_control.py`;
`docs/GATES_AND_CHECKPOINTS.md` **only if its invariant must be corrected**;
M0-T033's own packet and reports.

`docs/GATES_AND_CHECKPOINTS.md` is **conditional**. If the corrected semantics do not contradict a
stated invariant there, the file must remain byte-identical and the producer report must say so.
Touching it without a real contradiction is an unauthorized change.

Everything else — other `tools/`, `.claude/hooks/`, `.claude/agents/`, settings, product code,
deployment files, and unrelated control-plane behavior — is forbidden.

## 4. Directive coverage derived through the canonical resolver (D-004-R341)

`directive_registry.derive_applicable()` returned **42 applicable requirement ids** for this packet
(`D-004-R332`, `R335`–`R373`, `R387`, `R389`); the set was derived, not hand-selected. A `pending`
`task_verification` row exists in D-004 `verification.json` with one pending row per applicable id.
The verdict is written **only** by the independent `directive-compliance-verifier` at the gate;
producer self-verification is prohibited.

## 5. Baseline evidence at the base identity

- `python tools/test_project_control.py` → **14/14 groups OK, exit 0**. Group 9 already covers the
  "blocked-task roster precondition" that this task modifies — that test must stay green (AS-1).
- `python tools/validate_directive_compliance.py --check` → registry **VALID, exit 0**.

## 6. Readiness verdict

**PASS — ready to claim.** The packet is complete, its scope matches the owner's authorization
exactly, the producer is real, qualified, and independent of all four reviewers, directive coverage
is resolver-derived, and the baseline suites are green.

M0-T027 is **not** touched by this task (D-004-R374).
