# M5-T049 producer report — DB-030f named-street-override matcher extraction

**Task:** M5-T049 (DB-030f cohesion ruling) — split
`services/api/app/rules/named_street_override.py` (853 lines, above the 600 warn
tier) into focused modules behind the original file as a compatibility facade.
**Directive binding:** D-066-R001 (modularity extraction).
**Posture:** PURE extraction — no behavior change. Moved code is byte-for-byte the
original; the unchanged M5-T039/T040 acceptance suite is the behavior proof.
**Revision note (loop-1 run 52):** the earlier increment left
`named_street_override_matching.py` above the 600 warn tier and justified it with
the 750/1000 tiers, which AS-3 forbids. This revision completes the split so
**every** resulting module is below 600, and corrects the recorded validation and
failure descriptions (see §Validation). No claim of ruff/pytest passing is made
here; those run in CI.

## The split (three modules + facade)

| File | Responsibility after extraction | Below 600? |
|---|---|---|
| `app/rules/named_street_override_table.py` | The override table's VALUE layer: the typed data model (`MatchStatus`, the query/provenance/result dataclasses, `_Row`, `SNAPSHOT_ID`, `BOUNDARY_OPEN_QUESTION`, `NamedStreetOverrideError`) AND the pure normalization / source-anchoring helpers (`_collapse`, `_normalize_cd`, `_normalize_district`, `_word_bounded`, `_anchored_in`, `_bounded_repr`) that produce/compare its normalized values. Stdlib-only; no snapshot/matcher dependency. | yes |
| `app/rules/named_street_override_matching.py` | The STATEFUL engine: `NamedStreetOverrideMatcher` (fail-closed snapshot validation + `match` + `classify_alternate_width_district`) and `load_default_matcher`. Imports the value layer from `_table`. | yes |
| `app/rules/named_street_override.py` | **Compatibility facade** — re-exports every original name (public API + the internal helpers consumers import) so all import paths are byte-identical. No logic. | yes |

Import chain is one-directional (`matching -> table`); no cycle. The normalization
helpers were relocated from `_matching` into `_table` (from the earlier increment)
because they are leaf-level value semantics with no snapshot/matcher dependency —
a `_Row`'s `norm_*` fields are literally the output of `_collapse` — so they belong
with the value model, and moving them is what drops `_matching` below 600 without
touching the engine class (preserving byte-identity).

## Seven modularity-boundary answers (`.claude/rules/code-architecture.md`)

1. **Inspected the target first.** Original `named_street_override.py` = 853 lines
   (> 600 warn tier), one file mixing four responsibilities: the value types, the
   normalization helpers, the snapshot-bound engine, and the loader. Consumers:
   `named_street_override_status.py:33`, `wide_street_live_provider.py:104`,
   `tests/rules/test_named_street_override.py:29`, `test_wide_street_wiring.py:68`.
2. **Owning responsibility / boundary.** Two stable boundaries emerged: (a) a
   dependency-free VALUE layer (types + the pure functions that normalize/compare
   their values) and (b) a STATEFUL engine that reads a snapshot and applies that
   value layer. The public surface stays on the original module as a facade.
3. **Separation by reason-to-change.** Value semantics (types + normalization)
   change when the data shape or the normalization contract changes; the engine
   changes when matching/validation logic changes. External I/O (the `SnapshotStore`
   / `SectionSnapshot`) is imported only by the engine, not the value layer. No
   persistence, serialization, or presentation lives in these modules.
4. **Extracted with tests; interfaces preserved.** Focused per-module tests cover
   the moved boundaries; the facade re-exports the byte-same public interface (a
   thin compatibility facade); the import chain is acyclic (`matching -> table`).
5. **No dumping ground.** `_table` is not a miscellaneous bucket: both halves are
   leaf value semantics for the SAME override table (the types and the functions
   that produce their normalized fields). No unrelated domain logic, I/O, or wiring
   was placed there.
6. **Threshold decision.** Rather than justify a > 600 module, the file was SPLIT so
   each module clears the 600 warn tier outright (AS-3). The 750/1000 tiers are not
   used to excuse any module here.
7. **Checker run before checkpoint.** `python tools/modularity_check.py --check`
   from the repo root: **failures 0, exit 0**; none of the 20 remaining warnings
   references `named_street_override.py`, `_table`, or `_matching` (the matcher
   warning present in the earlier increment is gone). See §Validation for the
   verbatim result.

Approximate computed SLOC (policy definition: non-blank, non-comment-only lines):
`_table` ≈ 163, `_matching` ≈ 545, facade ≈ 40 — the checker's absence of any
`review_signal` on the three files is the authoritative proof they are < 600.

## Byte-identity / correctness proof

1. **Moved code is unchanged.** Every constant, helper, method, and the loader were
   moved verbatim from the original `named_street_override.py`. The engine class
   body (the DB-023a metadata-bypass closure, complete-span binding, source
   anchoring, and the C5-3/C6-4/C6-6 alternate-width refusal) is untouched by this
   revision; only module docstrings and `import`/re-export lines differ.
2. **Acceptance suite unchanged.** `test_named_street_override.py` (M5-T039/T040) is
   not in the diff; it imports through the facade and is the behavior proof.
3. **Facade preserves the full import surface** (zero consumer edits):
   - `named_street_override_status.py` → `MatchStatus`, `NamedStreetOverrideMatcher`, `OverrideQuery`, **`_normalize_cd`** (private, re-exported).
   - `spatial/wide_street_live_provider.py` → `NamedStreetOverrideMatcher`, `OverrideQuery`, `load_default_matcher`.
   - `tests/rules/test_wide_street_wiring.py` → `MatchStatus`, `NamedStreetOverrideMatcher`, `OverrideQuery`, `load_default_matcher`.
   The facade `__all__` is unchanged (same 17 names); only the *source module* of
   the six helper re-exports moved from `_matching` to `_table`.
4. **Structural identity test.** `test_facade_reexports_are_the_same_objects`
   asserts the facade exposes the SAME objects (identity, not copies) as the two
   impl modules, and that `_matching` applies the same helper objects it imports
   from `_table`.

## Test-count reconciliation (existing / moved / added)

Baseline = HEAD `e04e6aad`, where the two focused test files are empty placeholders
and `test_named_street_override.py` is the pre-existing acceptance suite.

- **Existing, UNCHANGED (byte-identity proof):** `test_named_street_override.py` —
  **46 test functions / 63 collected items** (7 parametrized). Zero edits; not in
  the diff. (CI is the authoritative collected count.)
- **Added (new focused coverage of the extracted boundaries):** **14 test
  functions**, none parametrized:
  - `test_named_street_override_table.py` — **12** (6 data-model + 6 normalization
    helpers).
  - `test_named_street_override_matching.py` — **2** (`load_default_matcher`;
    facade/engine re-export identity).
- **Moved (within this task's own working set, this revision):** the **6**
  normalization-helper focused tests were relocated from the `_matching` test file
  to the `_table` test file to sit with the helpers' new home. Bodies are
  unchanged; **no assertion weakened or deleted**. Net focused-test total is
  **14 before and 14 after** the relocation (8+6 → 2+12).

## Bounded per-file patch sections (for verbatim-movement review)

Line anchors are the current worktree files; the moved bodies are byte-identical to
the original `named_street_override.py` at HEAD `e04e6aad` (git diff at the
harvested head is the authoritative patch).

- **`named_street_override.py` (facade, ~40 SLOC).** No logic. Docstring module-map
  updated (helpers now attributed to `_table`). Import block: engine names
  (`NamedStreetOverrideMatcher`, `load_default_matcher`) from `_matching`; the 9
  data names + 6 helper names from `_table`. `__all__` unchanged (17 names).
- **`named_street_override_table.py` (~163 SLOC).** Data model (lines ~26–120)
  unchanged from the earlier increment. Added: `import re`; a `# -- normalization
  vocabulary` section (lines ~123–223) holding `_WS`, `_STREET_TYPE_WORDS`,
  `_MAX_QUERY_REPR` and the six helpers `_bounded_repr`, `_collapse`,
  `_normalize_cd`, `_normalize_district`, `_word_bounded`, `_anchored_in` — each
  body verbatim from the original. Module docstring rewritten to name both halves.
- **`named_street_override_matching.py` (~545 SLOC).** Removed the normalization
  section (the three constants + six helpers) — now imported from `_table`. Import
  block extended to pull the five helpers the engine uses (`_anchored_in`,
  `_bounded_repr`, `_collapse`, `_normalize_cd`, `_normalize_district`;
  `_word_bounded` is used only inside `_anchored_in`, so it is not imported here).
  Kept: the six engine-validation constants (`_ALLOWED_DISPOSITIONS`,
  `_QUALIFIER_SCOPE_RESOLVED`, `_UNCONDITIONAL_DESIGNATION_WORDS`,
  `_NUMERIC_LOCATOR_TOKEN`, `_SOURCE_WORD_TOKEN`, `_REQUIRED_BLOCK_FIELDS`) and the
  entire `NamedStreetOverrideMatcher` class + `load_default_matcher` — verbatim.
- **`tests/rules/test_named_street_override_table.py` (12 tests).** 6 data-model
  tests unchanged; 6 helper tests appended verbatim (imported from `_table`).
- **`tests/rules/test_named_street_override_matching.py` (2 tests).**
  `load_default_matcher` test retained; the re-export identity test now asserts the
  data model + helpers resolve to `_table` and the engine/loader to `_matching`.
- **`tests/rules/test_named_street_override.py`** — NOT MODIFIED (byte-identity
  proof); listed in allowed_paths but intentionally untouched.

## Validation (accurate; no unsupported clean/complete claims)

- **modularity (`python tools/modularity_check.py --check`, repo root):** EXECUTED
  here → `selected 449 files; failures 0; warnings 20`, **exit 0**. None of the 20
  warnings references `named_street_override.py` / `_table` / `_matching`; the
  matcher `review_signal` present in the earlier increment is cleared. This proves
  AS-3's size requirement and the modularity half of AS-5.
- **ruff (`python -m ruff check .`, cwd `services/api`):** NOT EXECUTED here. The
  approval runner executes documented commands only from the worktree root and
  **rejects a `cd services/api` prefix** (attempted this run; both the piped
  modularity variant and `cd services/api && python -m ruff check .` were refused
  as "not a packet-documented test command"). The documented ruff scope (cwd
  `services/api`) therefore cannot be set here; ruff proof must come from CI at the
  pushed head. A static review of the six touched files found no unused
  imports/re-exports, but that is a review note, **not** an executed clean result.
- **pytest `tests/rules`, `tests/spatial`, `tests/api` (cwd `services/api`):** NOT
  EXECUTED here — same working-directory limitation (thin client; the rules suite
  from repo root fails collection with `No module named 'app'`, an invocation
  artifact, not a defect). These are deferred to CI at the harvested head; no pass
  is claimed.
- **Correction of the earlier record:** the prior report's "the 5 touched files are
  clean" (ruff) and "warn-tier ~745 lines … below the 750/1000 thresholds"
  (modularity) are withdrawn — the first was unexecuted, and the second used the
  750/1000 tiers AS-3 forbids. The matcher is now genuinely below 600.

## For the orchestrator / gate

- Producer no-commit posture: changes are in the worktree working tree (HEAD
  unchanged at `e04e6aad`); harvest + trigger CI for the ruff + pytest proof. Keep
  CI pending for orchestrator capture; do not merge or accept from this checkpoint.
- CI must show, at the harvested head: `ruff check` clean (services/api scope);
  green `tests/rules` (unchanged acceptance suite + the two focused modules),
  `tests/spatial`, `tests/api`; and modularity exit 0 (reproduced here).
