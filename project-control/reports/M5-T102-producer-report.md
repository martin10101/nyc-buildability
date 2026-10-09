# M5-T102 producer report — D-087 PKT-A: one shared claim-word module

Producer: backend-engineer. Worktree: `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t102`
(branch `task/M5-T102-shared-claim-words`). Claim seam / parent:
`442b2dd263be079393d776d9d53f830d881cc1e3`.

## Summary

Created `services/api/app/cad/claim_words.py` as the single source of truth for the
claim-class vocabulary and the separator-collapsing screen, and rewired all three
writers to it:

- `claim_words.CLAIM_CLASS_WORDS` — the ONLY word literal (content unchanged from the
  accepted writers).
- `claim_words.claim_key(text)` — the ONLY matching key (upper-case + collapse every
  non-alphanumeric run to one space); lifted from the PDF writer's former `_claim_key`.
- `claim_words.contains_claim_word(*texts)` — the ONE screen every writer calls; varargs
  so a caller that prints an ASCII-sanitised form (the PDF writer) passes BOTH forms.

Rewires: GLB `_check_name` (was a raw substring match — DB-059 (b)) now calls the shared
screen; the GLB writer's own literal word list was removed (DB-059 (c)); the DXF writer's
`_assert_no_claim_words` now calls the shared screen; the PDF writer's `_screen_caller_text`
now calls the shared screen for the caller title-block address/bbl passthrough (DB-053 (c))
and its local `_claim_key`/`_CLAIM_SEPARATOR_RUN`/`import re` were removed. AS-5 closes the
M5-T096 G4 A1 advisory (DB-067 (a)): the DXF import-allowlist test now also flags
`__import__(...)` calls and any `importlib` reference.

Compatibility: `dxf_writer.CLAIM_CLASS_WORDS` and `pdf_sheet_writer.CLAIM_CLASS_WORDS` remain
importable as identity-equal aliases of the shared tuple (`is` the same object). DXF uses the
explicit `import ... as ...` re-export idiom; PDF adds `CLAIM_CLASS_WORDS` to `__all__`.

## Files changed (all inside allowed_paths)

- `services/api/app/cad/claim_words.py` — new canonical module (was a placeholder).
- `services/api/app/cad/dxf_writer.py` — import shared list+screen; drop local word literal;
  `_assert_no_claim_words` calls the shared screen. (932 → 928 lines; the change shrinks it.)
- `services/api/app/cad/glb_writer.py` — import shared screen; drop local word literal;
  `_check_name` calls the shared screen.
- `services/api/app/cad/pdf_sheet_writer.py` — import shared list+screen; drop `import re`,
  `_CLAIM_SEPARATOR_RUN`, `_claim_key`; `_screen_caller_text` calls the shared screen;
  `CLAIM_CLASS_WORDS` added to `__all__`.
- `services/api/tests/cad/test_claim_words.py` — new (35 tests): AS-3 by-value pin, key +
  screen behaviour, AS-1 drift/AST + identity.
- `services/api/tests/cad/test_dxf_writer.py` — allowlist adds `app.cad.claim_words`;
  `_imported_modules` flags `__import__`/`importlib` (AS-5); new `__import__` mutant + AS-2
  DXF separator-variant refusal + raw-substring mutant.
- `services/api/tests/cad/test_glb_writer.py` — stdlib+shared import test; AS-2 separator
  variants refused as names + raw-substring mutant; AS-3 full-word coverage + no-local-copy.
- `services/api/tests/cad/test_pdf_sheet_writer.py` — identity strengthened to the shared
  module; AS-2 title-block screen-removal mutant.
- `project-control/reports/M5-T102-producer-report.md` — this report.

## Per-acceptance-scenario evidence

- **AS-1 (one source).** `test_claim_words.py::test_as3_canonical_word_list_pinned_by_value`
  (by-value pin), `test_as1_only_claim_words_holds_the_word_literal` (AST: no writer keeps a
  word literal), `test_as1_only_claim_words_holds_the_matcher` (AST: no writer defines its own
  `claim_key`/separator regex), `test_as1_each_writer_imports_the_shared_module`, and
  `test_as1_dxf_alias_is_identity_equal_to_the_shared_tuple` (`dxf_writer.CLAIM_CLASS_WORDS is
  claim_words.CLAIM_CLASS_WORDS`). PDF: `test_claim_word_set_is_the_dxf_writers_pinned_set`.
- **AS-2 (separator variants refused everywhere).** GLB:
  `test_as2_separator_variant_names_refused` (As_of_right / Maximum_allowed / MAXIMUM  ALLOWED
  / as-of-right / As.of.right / Maximum.allowed refused as mesh names) +
  `test_as2_raw_substring_mutant_lets_separator_variant_through`. DXF:
  `test_as2_dxf_separator_variant_in_annotation_refused` +
  `test_as2_dxf_raw_substring_mutant_emits_separator_variant`. PDF (given + printed form):
  `test_claim_word_separator_variants_are_refused` (existing) +
  `test_as2_removing_the_title_block_screen_lets_claim_word_through`.
- **AS-3 (full word coverage + drift guard).** `test_claim_words.py::
  test_every_canonical_word_is_detected` (all 11), GLB
  `test_as3_every_canonical_word_refused_as_name` (all 11 — was 2/11 before, DB-059 (c)),
  DXF `test_as4_claim_class_words_are_the_expected_set` (existing by-value pin), PDF
  `test_claim_word_in_caller_text_is_refused_nothing_emitted` (all 11 × 4 fields). Drift guard:
  the by-value pin in `test_claim_words.py` reddens on any list edit.
- **AS-4 (byte-identical valid output).** All goldens pinned and unchanged and green:
  DXF `GOLDEN_SHA256 = 6a8dbd94…` (`test_as1_golden_digest_is_byte_stable`), PDF
  `_GOLDEN_SHA256 = c38360f9…` (`test_golden_sha256`), GLB `GOLDEN_SHA256 = 30d79d80…`
  (`test_as1_golden_sha256_and_determinism`). Read-only consumers pass UNCHANGED:
  `test_cad_owner_samples.py` (samples byte-identical) and `tests/drawings/test_dxf_roundtrip.py`.
  `git diff --name-only` shows no golden/sample/roundtrip/__init__ file changed.
- **AS-5 (allowlist + scope).** `test_dxf_writer.py::test_as5_allowlist_flags_dunder_import_and_importlib`
  (constant `__import__('json')` → {"json"}; non-constant `__import__(name)` → "__import__";
  `importlib.import_module` → "importlib"), and `test_as4_module_import_allowlist` /
  `test_as4_allowlist_is_load_bearing` still green with `app.cad.claim_words` added. Zero new
  dependencies (no requirements/lockfile change; shared module is stdlib `re` only); unwired
  (`test_as5_not_wired_into_the_app` green); exactly the allowed paths changed.

## Mutation table (in-process; mutate the CONSUMING namespace)

| Guard | Test | Mutation | Reddens because |
|---|---|---|---|
| GLB claim screen (`glb_writer._check_name` → shared screen) | `test_glb_writer::test_as2_raw_substring_mutant_lets_separator_variant_through` | `monkeypatch g.contains_claim_word` → raw upper-case substring | real screen refuses `As_of_right tower`; the raw mutant renders it (variant slips) |
| DXF claim screen (`dxf_writer._assert_no_claim_words` → shared screen) | `test_dxf_writer::test_as2_dxf_raw_substring_mutant_emits_separator_variant` | `monkeypatch d.contains_claim_word` → raw substring | real screen refuses `As_of_right` in GENERATOR_NOTE; raw mutant emits it into the DXF |
| PDF title-block screen (`pdf_sheet_writer._screen_caller_text` → shared screen) | `test_pdf_sheet_writer::test_as2_removing_the_title_block_screen_lets_claim_word_through` | `monkeypatch writer.contains_claim_word` → `lambda *t: None` | real screen refuses `12 maximum allowed st` (nothing drawn); neutered screen renders it |
| DXF import allowlist blind spot | `test_dxf_writer::test_as5_allowlist_flags_dunder_import_and_importlib` | prepend `__import__('json')` / `__import__(name)` / `importlib.import_module(...)` to real source | detector now flags each; the plain Import/ImportFrom scan did not (M5-T096 G4 A1) |

Existing load-bearing mutants stay green: DXF `test_as3_sanitizer_guard_is_necessary`,
`test_as4_claim_word_guard_is_load_bearing`; PDF `test_escaper_bypass_mutant_reddens_roundtrip`,
`test_paren_skipping_escaper_mutant_breaks_unbalanced_roundtrip`; GLB
`test_as4_refusal_yields_no_partial_output`.

## Commands (explicit cwd; verbatim tails)

- `[OBSERVED]` cwd `services/api`: `python -m ruff check .` → `All checks passed!` (exit 0).
- `[OBSERVED]` cwd `services/api`: `python -m pytest tests/cad tests/drawings/test_dxf_roundtrip.py -q`
  → `345 passed in 6.11s` (rc 0). Baseline before the change was `284 passed`; +61 tests.
- `[OBSERVED]` cwd repo root: `python tools/modularity_check.py --check` → exit 0
  (`failures 0; warnings 27`; `dxf_writer.py` stays a pre-existing WARN review_signal and the
  change SHRINKS it 932→928 lines, it does not grow it).
- Env: sandbox Python 3.11.9 (repo CI runs 3.12). The PDF suite's 3.11 reader-sideload path
  exercised and green. ruff 0.13.0.

## Deviations

- None from scope. The GLB and DXF refusal messages still echo the writer's own name/text
  constant `{name!r}`/`{text!r}` (unchanged); DB-059 (h) caller-name redaction stays routed to
  the wiring packet (out of PKT-A scope), so I did not touch it.
- `pdf_sheet_writer` now imports `CLAIM_CLASS_WORDS` from `app.cad.claim_words` rather than from
  `app.cad.dxf_writer`; identity is preserved (both alias the shared tuple), so the existing
  `writer.CLAIM_CLASS_WORDS is dxf_writer.CLAIM_CLASS_WORDS` assertion stays true.

## DISCOVERIES (D-069; route at the seam — not fixed in-packet)

- The `docs/samples/cad/` owner samples and every writer golden were reproduced byte-for-byte
  by the READ-ONLY consumers after the rewire; nothing needed re-pinning. This confirms the
  separator-collapse change affects ONLY refusal behaviour, never valid output — a useful
  invariant for the export-wiring packet (PKT-D) to rely on.
- DB-059 (b), (c) and DB-053 (c) are addressed by this packet and can be marked accordingly at
  the accept seam. DB-067 (a) (the `__import__`/importlib allowlist blind spot) is closed here.
  DB-059 (h) (redact caller name in GLB/DXF refusal messages) and DB-059 (a)/(d) remain OPEN
  for the wiring / PKT-B1 packets as previously routed.

END-OF-REPORT
