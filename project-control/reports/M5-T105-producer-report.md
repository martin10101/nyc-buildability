# M5-T105 — producer report (D-087 PKT-B1: PDF sheet writer wiring-hardening)

Producer: backend-engineer (orchestrator-dispatched subagent). Worktree
`C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t105`, branch
`task/M5-T105-pdf-writer-hardening`. Claim seam / parent HEAD
`2368fb73e2999eed152fc495825ba8942cd1502f` (guards verified: `rev-parse
--show-toplevel` printed the wt-m5t105 path; `rev-parse HEAD` == the claim seam).

Scope: exactly `services/api/app/cad/pdf_sheet_writer.py`,
`services/api/tests/cad/test_pdf_sheet_writer.py`, and this report. No route,
`main.py`, `__init__`, sibling writer, `test_cad_owner_samples.py`, `docs/samples/`,
web, or dependency change. Zero new dependencies (module stays stdlib:
`math`/`numbers`/`dataclasses` + the accepted `app.cad.claim_words`). Writer remains
UNWIRED.

## What this packet changed vs what M5-T091 already closed (DB re-check)

| Item | State before M5-T105 | Action here |
|---|---|---|
| DB-053 (a) malformed vertex (non-numeric / wrong-arity / None / nested) -> typed refusal, never raises | CLOSED by M5-T091 (`_validate_ring`/`_coerce_vertex`; tests H-1). Re-verified against the current file. | No code change; re-verified green. |
| DB-053 (b) non-finite path = typed refusal via the public API + honest docstrings | Functionally CLOSED by M5-T091 (`_num` raises `_RenderRefused`, caught at the public boundary), but the docstrings were DISHONEST: a "never raises on caller data" claim sat over a function that raises internally (M5-T099-G5 observation). | Docstrings made honest (module purity para, `_num`, `_escape_pdf_text`); the boundary try/except extracted into a named `_finish` helper so the never-raise catch is testable by in-process mutation; AS-2 mutation test added. |
| DB-053 (c) claim-word screen | CLOSED by M5-T091 + the shared module M5-T102; DB-072 says do not re-implement. | Out of scope; untouched. |
| DB-053 (d) unbalanced parens + backslash escaping | CLOSED by M5-T091 (H-4 round-trip + paren-skip mutants). Re-verified. | Added 2 combined "unbalanced paren AND backslash" fixtures to `_UNBALANCED_TEXTS`; ISO 32000-1 §7.3.4.2 now cited on `_escape_pdf_text`. |
| DB-059 (a) caller-text length bound | OPEN (M5-T091 G3-F3, G5-LOW: a 200k-char address -> ~201 kB PDF). | NEW guard: `_MAX_TEXT_CHARS = 120` shared cap enforced in `_screen_caller_text` before any drawing; typed `text_too_long` naming the field, never echoing caller text; tests + per-field mutation. |
| DB-059 (d) y-only non-finite probe | OPEN (M5-T091 G4 EX2 survivor: finiteness tested on x only). | NEW tests: y-only exact-code parametrization + an in-process EX2 mutant proving the y half of the check is load-bearing. |

## Per-AS evidence

- AS-1 (bounded caller text). `_MAX_TEXT_CHARS = 120` (input-bounds block); enforced
  per field in `_screen_caller_text` in order type -> length -> claim-word, BEFORE
  any drawing (no partial output). Refusal `SitePlanRefusal("text_too_long", "<field>
  exceeds the 120-character limit")` names the field, never the caller text. Tests:
  `test_over_long_caller_text_is_refused_nothing_drawn` (×4 fields; asserts field in
  detail, caller text NOT echoed, `build_calls == []`),
  `test_exactly_at_cap_caller_text_still_renders` (inclusive bound, ×4),
  `test_length_cap_precedes_the_claim_word_screen`,
  `test_length_cap_does_not_change_valid_output` (golden held). Chosen cap comfortably
  holds a real address/bbl/provenance line on one 9 pt title-block row of landscape US
  Letter and accepts the golden (max field 22 chars) and the committed sample (max
  field 33 chars) unchanged.
- AS-2 (never-raise honesty). `_num` docstring now states it RAISES the private
  `_RenderRefused` on non-finite input; the module docstring and new `_finish`
  docstring state the one public boundary catches it and RETURNS a typed refusal.
  Tests: `test_public_api_converts_internal_raise_to_a_returned_refusal`;
  `test_boundary_conversion_is_load_bearing_raise_path_reddens` (mutation: a `_finish`
  without the catch makes the public API raise); malformed-vertex + hostile-field
  sweeps unchanged; y-only via `test_y_only_non_finite_vertex_is_non_finite_coordinate`
  and `test_y_only_finiteness_check_is_load_bearing`.
- AS-3 (escaping). `_escape_pdf_text` cites ISO 32000-1 §7.3.4.2 (literal-string
  escaping of unbalanced `(`/`)` and every `\`; the exact standard wording is marked
  "[recalled - verify]"). We escape all three unconditionally (conservative superset),
  keeping every literal string balanced. Proven by the REAL in-repo strict reader:
  `test_unbalanced_parens_round_trip_through_writer_and_reader` (now incl. combined
  paren+backslash fixtures) and the paren-skipping/full-bypass escaper mutants.
- AS-4 (byte identity + scope). `test_golden_sha256` unchanged
  (`c38360f9b803299c75dd837ec65de3e3a4dc046a11aa2bcb386fe74aa5312db2`);
  `test_cad_owner_samples.py` passed UNCHANGED (11 passed, incl. the byte-identity of
  `docs/samples/cad/example-site-plan.pdf`). Zero new deps; unwired; exactly the two
  code files + this report changed.

## Mutation table (all in-process, mutating the CONSUMING `writer` namespace)

| Mutation | Target test | Result |
|---|---|---|
| `_MAX_TEXT_CHARS = 10**9` | `test_length_cap_is_load_bearing_for_every_field` (×4 fields) | over-long field now renders bytes -> the one shared cap is load-bearing for every field |
| `_finish` -> a variant that does NOT catch `_RenderRefused` | `test_boundary_conversion_is_load_bearing_raise_path_reddens` | public API RAISES the carrier -> the never-raise contract depends on the single boundary catch |
| `_coerce_vertex` -> x-only finiteness (EX2) | `test_y_only_finiteness_check_is_load_bearing` (nan, inf) | y-only refusal code moves off `non_finite_coordinate` (still typed, never raises) -> the y half is load-bearing for the specific code |
| (re-verified, unchanged) escaper paren-skip / full bypass | `test_paren_skipping_escaper_mutant_breaks_unbalanced_roundtrip`, `test_escaper_bypass_mutant_reddens_roundtrip` | redden as before |

## Commands (explicit cwd; verbatim tails)

- `git -C .../wt-m5t105 rev-parse --show-toplevel` -> `C:/Users/MLFLL/Downloads/nyc-zoning/wt-m5t105`; `rev-parse HEAD` -> `2368fb73...` [OBSERVED].
- cwd `services/api`: `python --version` -> `Python 3.11.9`; `import reportlab` -> ModuleNotFoundError (writer is stdlib-only; CI 3.12 is the authority) [OBSERVED].
- cwd `services/api`: `python -m ruff check .` -> `All checks passed!` [OBSERVED].
- cwd `services/api`: `python -m pytest tests/cad -q` -> `368 passed in 1.96s` (baseline was 338; +30 new cases; `test_cad_owner_samples.py` among them, unchanged) [OBSERVED].
- cwd repo root: `python tools/modularity_check.py --check` -> `EXIT=0` (warnings only; `pdf_sheet_writer.py` NOT flagged; file is 551 lines) [OBSERVED].

## Deviations

1. Extracted the public-boundary `try/except _RenderRefused` from
   `render_site_plan_pdf` into a new module-level `_finish(...)` helper. Pure
   structural refactor — output is byte-identical (golden + samples held) — done so
   the never-raise boundary catch (AS-2) can be neutered by in-process mutation.
2. One SHARED `_MAX_TEXT_CHARS` cap for all four caller fields (AS-1 explicitly
   allows a shared check proven to cover every field) rather than per-field caps; the
   per-field mutation test proves coverage.
3. Length is checked BEFORE the claim-word screen (bound-first; also avoids running
   the separator-collapse on a huge string). Pinned by
   `test_length_cap_precedes_the_claim_word_screen`.

## Discoveries (D-069)

None new that require a backlog row. Context only: DB-072 (a),(b),(c),(f) remain OPEN
for the next app/cad test touch but concern `dxf_writer`/`test_dxf_writer.py`
(forbidden here). Content-Disposition filename sanitization (M5-T099 G5-F1) and
refusal-message caller-echo redaction (DB-059 h) are PKT-D export-seam concerns, not
writer-side; no action here. The `_num` non-finite guard stays reachable today only
via monkeypatched constants (writer unwired); it is defense-in-depth once PKT-D wires
bounded caller geometry.

END-OF-REPORT
