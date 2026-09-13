# G5 SECURITY/PRIVACY GATE REPORT — M4-T014

> Preservation note: saved VERBATIM by the orchestrator from the reviewer's agent-return channel
> (transport entity-decoding only; the reviewer's opening note about the read-only guard blocking
> its final redundant Bash call is folded into scope area 2, which it summarized). Reviewer:
> independent security-reviewer agent.

## VERDICT: PASS (no blocking corrections; 1 low/advisory note for downstream reviewers)

Task: M4-T014 — R3/R4 series height/setback draft rule families (data-only rulesets + snapshots + tests).
Producer: rules-engineer. Material commit: `c8d94f38`. CI authority: run 34740497612 @ `6fc8a878` (18/18 green).
Reviewer: security-reviewer (read-only). Frozen material verified identical to CI head.

## Material identity confirmed
- `git diff c8d94f38..6fc8a878 -- services/api docs/research/zr-snapshots` is **EMPTY** — the 18/18-green CI run at `6fc8a878` covers the exact frozen M4-T014 source. Intervening commits touch only `docs/ARCHITECT_REVIEW_QUESTIONS.md` + control-plane files (gates/reports/state/tasks).
- Material commit files: 3 rulesets, 3 canonical + 3 bundle snapshots, 1 test file, 2 producer reports (all in allowed_paths); plus orchestrator-owned control-plane (`state.json`, `tasks/M4-T014.json`) and producer agent-memory (`.claude/agent-memory/rules-engineer/*`). Producer left work uncommitted; orchestrator committed — no producer scope violation.

## Findings by scope area

### 1. Supply chain / dependencies — CLEAN
No dependency, lockfile, `requirements*.txt`, `pyproject.toml`, `tools/`, or `.github/` file in `c8d94f38` (verified via `--stat` filter → NONE). Test file `services/api/tests/rules/test_r3_r4_height.py:48-59` imports only the established stack: `hashlib`, `json`, `pathlib`, `pytest`, `app.rules.*`. No new package import.

### 2. Snapshot provenance integrity — CLEAN
Recomputed `sha256(verbatim_excerpt)` for all three new snapshots; each equals its stored `content_digest_sha256`:
- `zr-23-42` = `3fea4ca5…4070d`
- `zr-23-421-r3-r4` = `68e4d147…e046`
- `zr-23-422-r3-r4` = `0268089074…1b18`

Every ruleset citation `content_digest_sha256` matches the corresponding snapshot digest (7 citation refs across 3 rulesets, all MATCH). Canonical (`docs/research/zr-snapshots/v1`) vs bundle (`services/api/app/_zr_snapshots/v1`) are byte-identical for all three `.snapshot.json` files (`diff -rq` shows only `__init__.py`/`__pycache__` in bundle, as expected; sync `--check` EXIT 0 per CI evidence). Each snapshot carries `request_url` (official `zr.planning.nyc.gov`), `retrieved_at` (2026-09-13), and `content_digest_sha256`. Verbatim excerpts are plain zoning text with no HTML tags/scripts (the lone `<time>` string lives in the descriptive `document_currency_banner_note`/`verification_required` fields — not in the hashed `verbatim_excerpt` — and is inert JSON never parsed as HTML). Tamper-evidence proven live: `test_as2_tampered_snapshot_fails_closed` and `test_as2_mismatched_recorded_citation_digest_fails_closed_at_load` (test_r3_r4_height.py:219-241).

### 3. Injection / eval surfaces — CLEAN
No new DSL construct. Ops in the new rulesets are exactly `in_set`, `identity`, `equals` — all present in the pilot `r5a_height.rule.json`. Exception effects are exactly `documented_limitation`, `professional_review_required` — identical to the pilot set. Schema dir untouched (`git show c8d94f38 -- services/api/app/rules/schemas engine* evaluator* dsl*` → empty). Engine dispatches ops via whitelist dicts `COMPUTE_OPS`/`PREDICATE_OPS` (operations.py:117-189) with no `eval`/`exec`/`compile`/`__import__`/`subprocess`/`pickle` anywhere in `services/api/app/rules/` (operations.py:9 explicitly documents "NO eval anywhere"). Rulesets are inert data consumed by the frozen engine.

### 4. Honesty / legal-safety posture — CLEAN
- All three rulesets `status: "needs_review"`, `qualified_human_approval: "pending"` (r3_r4_pitched_height.rule.json:7,14; r3_2_r4_flat_height.rule.json:7,14; r4b_height.rule.json:7,14). Asserted by `test_as5_every_family_rule_is_needs_review_and_verified_ineligible` and `test_as1_conditional_never_verified_for_every_variant` (verified_eligible=False).
- Gaps fail CLOSED, never default numeric: sloping-plane setback → `documented_limitation` exception, never a number (`test_nc8_pitched_setback_is_documented_limitation_not_numeric`); `building_type` unavailable → `professional_review_required` with empty outputs (`test_nc4_*`); missing district → PRR (`test_nc5_*`); overlay/special/historic → PRR (`test_nc3_*`); districts outside R3/R4 → `not_applicable` empty outputs (`test_nc1_*`, `test_nc8_*`). Cross-variant and cross-section isolation proven (`test_nc1_*`, `test_nc2_*`), including R4B's 25 ft never merging with R3-2/R4's 35 ft.
- No compliance-determination language: grep for `feasible|compliant|compliance|as-of-right|massing|guaranteed` found none as assertions. "buildable-envelope" appears only in negated disclaimers ("not a buildable-envelope result", 3 places). "permitted" appears only inside a verbatim source quote. Best-case coverage is `conditional`, never `verified`.

### 5. Secrets / PII — CLEAN
Only artifacts matching the secret/URL scan are the three official `zr.planning.nyc.gov` request URLs (expected provenance). No API keys, tokens, credentials, private keys, BBLs, addresses, or user PII in the rulesets, snapshots, test file, or agent-memory files.

### 6. Scope — CLEAN
All producer material is within `allowed_paths` including the recorded correction adding `docs/research/zr-snapshots` (packet line 32; disclosed in producer report §3). The two forbidden-path files in the commit (`project-control/state.json`, `project-control/tasks/M4-T014.json`) contain only orchestrator-owned control-plane changes (status arrays; allowed_paths correction + progress log) — not producer material. Engine/evaluator/api/scenario/connectors/schema all untouched.

## Advisory (non-blocking; for qa-engineer / code-reviewer, not a G5 stop)
- **A1 (low, test robustness):** the honesty-posture guard `test_as5_no_buildable_or_compliance_language_in_rulesets` (test_r3_r4_height.py:315-326) bans the space-form `"buildable envelope"`, but the rulesets use the hyphenated `"buildable-envelope"`. The guard therefore passes trivially against the string actually present; it does not substantively assert on the phrasing in the files. Current content is safe (negated disclaimers), so this is defense-in-depth robustness only, not a live posture violation. Suggest broadening the banned list to catch the hyphenated form and bare `envelope`/`as-of-right`.

## Accepted disclosures (correct posture, not findings)
- `raw_html_verified: false` / `extraction_status: extracted_draft` on all three snapshots is the honest draft posture; byte-for-byte raw-HTML re-verification and value confirmation are explicitly deferred to G6 (qualified-human legal approval). Nothing here claims Verified; D-045-R009 (DRAFT-until-G6) is preserved.
- The `building_type` `attached`/`other` axis is a disclosed modeling representation of §23-422's negative definition ("residences not subject to §23-421"); it has no canonical field and fails closed to PRR in practice — disclosed in producer report §Disclosure 2 for G6 attention. Not a security concern (fails safe).

## Reproduction commands used (read-only)
- `git show c8d94f38 --stat`; `git show c8d94f38 -- <schemas/engine>` (empty)
- `git diff c8d94f38..6fc8a878 -- services/api docs/research/zr-snapshots` (empty)
- Python recompute of `sha256(verbatim_excerpt)` vs stored digests and citation refs (all MATCH)
- `diff -rq docs/research/zr-snapshots/v1 services/api/app/_zr_snapshots/v1` (json byte-identical)
- Grep sweeps: DSL ops/effects vs pilot; eval surfaces; secrets/URLs; compliance language

**G5 verdict: PASS.** No blocking security/privacy corrections. One low advisory (A1) routed to the code/qa reviewers. The orchestrator records the gate.
