# M4-T019 producer report (verbatim producer return; saved by the orchestrator per the report-preservation rule)

Producer: backend-engineer (claude-sonnet-5 via recorded harness override, D-047-R001).
Material: services/api/app/connectors/dcm_street_width_policy.py +
services/api/tests/connectors/test_dcm_street_width_policy.py, producer commit 2eaba13d
(worktree agent-acd38556e27cb595f, base 293d6c03), integrated by the orchestrator as
cherry-pick a6c73ec0; both file sha256 values LF-normalized verified at integration.
Orchestrator pre-gate re-run at the integrated head: `cd services/api && python -m ruff
check .` EXIT 0; policy suite 93/93 passed.

---

## Verbatim producer return

**Worktree:** `C:/Users/MLFLL/Downloads/nyc-zoning/nyc-development-feasibility-claude-pack/.claude/worktrees/agent-acd38556e27cb595f`
**Commit SHA:** `2eaba13d` (parent `293d6c03`, message "M4-T019 producer: D-052 street-width classification-policy layer")

**Files changed (exactly two, as scoped):**
- `services/api/app/connectors/dcm_street_width_policy.py` — sha256 `932bbfe4f076c1dc5fc81b9801f52e2ac1e39239c6e3ed98bef086f2fcfe253b`
- `services/api/tests/connectors/test_dcm_street_width_policy.py` — sha256 `9885bb3757abae2776722e8f86d34ef5455792627659e137b43abc1314b750d1`

**Test counts / self-checks (all commands actually run in this sandbox — Python 3.11.9,
pytest 8.4.2, ruff 0.13.0):**
- `pytest tests/connectors/test_dcm_street_width_policy.py -q` → 93 passed, exit 0
- `pytest tests/connectors -q` (full accepted suite, regression) → 712 passed, exit 0
- `ruff check .` (whole `services/api` tree) → "All checks passed!", exit 0
- `python tools/validate_directive_compliance.py --check` → exit 0 (no output)
- `python tools/modularity_check.py --check` → "selected 402 files; failures 0; warnings 17"
  (new file not among the 17 warnings), exit 0
- `git status --porcelain` before commit showed only the two files modified; `git diff --stat`
  on the classifier/connector files was empty (byte-immutable confirmed)

**Design summary:**
- `AttestedPreconditions` (frozen dataclass, no field defaults): `source_documented`,
  `source_version`, `street_status_checked`, `frontage_match_method`, `matched_geometry_ref`,
  `exceptions_checked`. `frontage_match_method` is a string constant field — only
  `FRONTAGE_MATCH_COVERAGE_ESTABLISHED` satisfies it; `FRONTAGE_MATCH_NEAREST_CENTERLINE_ONLY`
  and any other value fail closed (typo-safe).
- Decision states are four plain string constants (mirrors the accepted classifier's
  `DISPOSITION_*` style rather than `enum.Enum`): `wide`, `narrow`, `unresolved`, `unknown`.
  `unresolved` = policy refusal (missing precondition, or a derivable-but-straddling
  interval); `unknown` = the classifier's own data-ambiguity classes, routed to
  `map_resolution` — never collapsed into each other (D-052-R006/D-051-R002).
- `CLASS_INTERPRETED_BOUNDS: dict[str, InterpretedBounds]` — one row per each of the
  classifier's 24 `ambiguity_class` values (11 derivable: 3 one-sided-wide, 4
  one-sided-narrow, 4 straddling; 13 not-derivable: approximations/hedges/labelled-non-
  answers/schema-drift/order-broken/negative/unrecognized). Built by reading the classifier's
  class names + docstring semantics, not by re-parsing raw text a second time. An import-time
  `assert` checks this table stays exhaustive against
  `classify_street_width_classifier.AMBIGUITY_CLASS_DISPOSITIONS`; a test re-asserts it and
  checks `len == 24`.
- `classify_street_width_policy(classification, preconditions) -> PolicyDecision`: order is
  (1) precondition gate first (any failure → `unresolved`, listing every failed attestation,
  regardless of what the data says — "never silently thresholded"), (2) not-derivable →
  `unknown` + `routed_to="map_resolution"`, (3) derivable-but-straddling → `unresolved`,
  (4) derivable one-sided → `wide`/`narrow` + `assumption_notice` (owner-approved-DRAFT
  wording, only on issued classifications). `draft_label` is populated on every decision.
- `PolicyDecision` carries the full provenance quintuple: `original_label`, `source_version`,
  `matched_geometry_ref`, `interpreted_bounds`, `classification_reason`.
- Owner's R003 literal examples (`<75`→narrow, `>75`/`>=75`/`75-90`→wide,
  `<=75`/`60-75`/`70-80`→unresolved) verified as exact test cases against the real classifier
  output (not hand-built classifier objects).
- A dedicated test proves the classifier's own `disposition="narrow_fail_closed"` for e.g.
  `"Unknown"` does NOT leak into the policy's `unknown` decision — the policy layer
  independently resolves OQ-3 rather than mirroring the classifier's fail-closed convention.

**Open questions / assumptions (none blocking):**
- "Interpreted bounds" (R005) is represented qualitatively (derivable/one-sided/side/
  interval-description text), not as re-parsed exact numeric endpoints, since the accepted
  classifier's public API (`__all__`) does not expose parsed numeric values — only
  `ambiguity_class` + `raw_text` + `basis` string. Re-parsing raw text a second time in this
  module would duplicate the classifier's private regex logic; the packet's own instruction
  ("Build the interpreted-bounds mapping from the accepted classifier's 24 typed classes")
  supports this class-name-driven approach. Flagged for reviewer confirmation this satisfies
  R005's "interpreted bounds" provenance field intent.
- `source_version` / `matched_geometry_ref` are pass-through caller-supplied provenance
  strings (no validation against the accepted connector's actual field shapes), consistent
  with the packet's note that geometry matching is deferred to B3/B4.
