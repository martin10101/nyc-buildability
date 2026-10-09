# DCV — M0-T152 (D-033 T-A: supervisor gate-wave engine), pre-acceptance verification

**Verifier:** directive-compliance-verifier (independent, read-only). Producer of the five
applicable requirements per the registry: orchestrator; unit work produced by
supervised-loop-fable-worker (runs persistent-local-08/09).

## Identity verification (reproduced)

- **HEAD** `26693cf7fd77b110cbf577fb42c7426d9d06312f` on `candidate/D-024-mrl-option-b` (`git rev-parse HEAD`).
- **Material identity** `183da5e5e30938b08d6b81b5048b22f4fc7e762e72fe6700ecaa37bfc459ca2d` — reproduced via `directive_registry.frozen_git_identity(allowed_paths, reviewed_sha=None)` = `183da5e5…ca2d`, `resolved_sha=26693cf7…`, `err=None` (clean working tree over scoped paths). Exact match to `directive_registry.frozen_git_identity` expected value.
- **Seven packet blobs byte-identical** between `cc25bdc1` and HEAD (`git rev-parse HEAD:<p>` vs `cc25bdc1:<p>` for all 7 allowed_paths → IDENTICAL blob hashes each). `cc25bdc1` is an ancestor of HEAD.
- **Applicable set** = exactly `{D-033-R001, D-033-R003, D-033-R005, D-033-R006, D-033-R007}` — `derive_applicable` over all 33 active directives returns these 5 with `unresolved=[]`; `evaluate_task_refs` returns `ok=True, missing_ids=[], invalid_refs=[], cited==applicable`. No other directive applicable (whole-registry sweep).
- **Intake review:** `source-001.md` + `source-002-amendment.md` decompose faithfully into `requirements.json` (9 reqs); for the applicable 5 nothing is missing/weakened/combined/invented; amendment 2 is reflected as R009; `python tools/validate_directive_compliance.py --check` exit 0 (source digests + locked_requirement_ids intact).
- **Producer commits** (`09fdea16`, `cc25bdc1`) touch only the 7 allowed_paths; `project_control.py` NOT touched. Task status `awaiting_gate` (NOT accepted); no activation exercised. Gates G0/G2/G3/G5 all PASS (G3 code-reviewer, G5 security-reviewer, at HEAD).

## Per-requirement rows

The five strict rows (id/state/evidence/note, all **PASS**) are recorded verbatim in
`project-control/directives/D-033-supervisor-management-layer/verification.json` →
`task_verifications[]` → task `M0-T152` → `requirements[]`, stamped `verified_by:
directive-compliance-verifier`, `reviewed_sha: 26693cf7…`, at material identity `183da5e5…`.
That machine record is the authoritative copy of the row content; this report preserves the
verifier's identity-verification preamble and verdict.

**DCV VERDICT: PASS**

Material identity verified: `183da5e5e30938b08d6b81b5048b22f4fc7e762e72fe6700ecaa37bfc459ca2d` at HEAD `26693cf7fd77b110cbf577fb42c7426d9d06312f` (branch `candidate/D-024-mrl-option-b`).

Notes for the orchestrator (advisory, non-blocking — do not affect any requirement verdict): both independent reviews carried non-blocking advisories routed to T-B — G3 D-1 (the captured `M0-T152-documented-commands-cc25bdc1.txt` artifact shows a filtered 5-of-13 modularity warning set; the real tool output is 13 warnings / 0 failures / exit 0, which I reproduced), and G5 L1 (the G2 self-check report path persists unredacted command transcripts; the reviewer-facing independent-gate packet is redacted). Neither impacts the five applicable requirements.

---

*Orchestrator preservation note: preamble, verdict, and advisory notes saved VERBATIM from the directive-compliance-verifier agent-return channel (2026-09-07 overnight gate wave, task notification ad1c4129ac144668b; leading corroboration sentences removed as transport framing, HTML entity-encoding of `<p>` decoded). The five JSON rows from the same return were transcribed unaltered (ASCII-normalized dashes only) into the D-033 verification.json machine record by the orchestrator, with `verified_at`/`verified_by`/`reviewed_sha` stamps added per the v2 row schema.*
