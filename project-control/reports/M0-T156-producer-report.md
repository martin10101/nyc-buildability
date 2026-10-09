# M0-T156 Producer Report — Directive-registry digest normalization (CRLF/LF)

Producer: orchestrator (governance task; D-040:D-040-R003 + D-001:ALL cited).
Packet: a98d174d; claim after G0 + applicability append: ebd39767.

## 1. What was built (all inside allowed_paths)

| File | Change |
|---|---|
| `tools/directive_registry.py` | Two new helpers after `sha256_file`: `normalize_text_artifact_bytes` (CRLF→LF, lone CR→LF; documented decision) and `sha256_text_artifact` (normalized digest for registry TEXT artifacts). The c2 source-digest check now calls `sha256_text_artifact`. `sha256_file` itself is UNCHANGED — the content-manifest identity path (`:1183`-area) and `content_sha256` keep hashing raw bytes, so no recorded material identity shifts. |
| `tools/validate_directive_compliance.py` | The two direct hash sites adopt the shared helper: migration-manifest check (`dr.sha256_text_artifact(mm_path)`) and c14 requirements-body check (`dr.sha256_text_artifact(rfile_path)`). No other logic touched. |
| `tools/test_directive_compliance.py` | Fixture digest authoring switched to the normalized helper at the two file-digest sites (`_add_second_directive`) — `write_text` CRLF-translates on Windows, so the raw digests were platform-dependent. New `LineEndingNormalizationTest` (3 tests): AS-1 CRLF/LF/lone-CR hash identically with a load-bearing inequality (raw CRLF hash differs — removing normalization fails the test); AS-2 representation-flip of a real source validates clean; AS-5 one-character content tamper delivered in CRLF form still fails c2. |
| Four directive manifests (D-032, D-033, D-034, D-038) | The SIX stale digest values re-stamped to their LF-normalized values + one append-only `digest_normalization_restamp` audit_log entry per manifest (ASCII). Byte-format preserved exactly: auto-detected per file (D-032/033/034 = indent 2, CRLF, no trailing NL; D-038 = indent 1, CRLF, trailing NL) with a fail-closed round-trip guard BEFORE mutation. |

## 2. Root cause and the fix shape (the packet's core)

The six digests were recorded over local **CRLF working-tree bytes**; `.gitattributes` pins
`eol=lf`, so the CI checkout hashes **LF bytes** — the validator computed different values per
representation, the local validator stayed EXIT 0 while the CI control-plane job failed on
exactly those six, and the red masked genuine future control-plane regressions. The fix makes
the digest a function of **content**: hash over CRLF→LF-normalized bytes at the three
registry-artifact sites (c2 sources, c14 requirements body, migration manifest), and re-stamp
the six recorded values to the normalized form. Digests already recorded over LF bytes are
unchanged (normalization is the identity on LF input) — the six re-stamps are provably the
complete set, because a stale-vs-local value would have failed the local validator (EXIT 0
before this change) and a stale-vs-LF value fails CI (exactly six errors reported).

## 3. AS-3 — re-stamps match the CI-reported LF actuals (full values)

Each new value was asserted at re-stamp time against the failing CI log's `actual` prefix
(run 34681382456, job 103520545751) and equals `sha256(LF-normalized bytes)` of its artifact:

| Artifact | Old (CRLF) | New (normalized) |
|---|---|---|
| D-032 source-004-amendment.md | 3912bae0… | `3704add240374c58fc4cb0bf47584763001a671e98a3000eea957557057f3533` |
| D-032 requirements.json | e5ebf70c… | d8158188… (64-hex recorded in the manifest) |
| D-033 source-002-amendment.md | 0e0ed336… | `d0ae01b4f9cf6bcb91ed5652d212d32d68cd09ca4bfe7fe509e6d754112506bf` |
| D-033 requirements.json | 82f36c4b… | d2876943… |
| D-034 requirements.json | 610f4e61… | dfab73c0… |
| D-038 requirements.json | f62c6fc8… | 0e9de4cc… |

(The two full 64-hex source digests are quoted from the CI error text verbatim; all six full
values live in the re-stamped manifests themselves, which reviewers verify by recomputation.)

## 4. Scenario → verification mapping

| AS | Verification |
|---|---|
| AS-1 | `LineEndingNormalizationTest.test_crlf_lf_and_lone_cr_hash_identically` — equality across CRLF/LF/lone-CR + the load-bearing raw-hash inequality (red/green). |
| AS-2 | Local: `validate_directive_compliance.py --check` EXIT 0 over the CRLF working tree (§5). CI: control-plane job on the pushed head (LF checkout) — the executable authority for the LF side. Registry-level flip test: `test_representation_flip_validates_clean`. |
| AS-3 | §3 table; re-stamp script asserted each prefix fail-closed before writing. |
| AS-4 | `git diff` over `project-control/directives/**`: ONLY the four manifest.json files change (six digest values + `updated_at` + one audit_log append each); zero byte changes to any source-*.md, amendment, requirements.json, verification.json, index.json; `locked_requirement_ids` untouched. Reviewers verify by diff. |
| AS-5 | `test_content_tamper_still_detected_under_crlf` + the pre-existing tamper tests (`test_c2_s6_source_rewritten_without_hash_change`, `RequirementsBodyDigestTest.test_body_edit_detected`) all still pass — the guard did not weaken. |
| AS-6 | §5 local runs + the CI control-plane job green on the pushed head. |

## 5. Verification runs (local, Windows/CRLF side)

- `python tools/validate_directive_compliance.py --check` → **EXIT 0** (after re-stamp; it was
  EXIT 1 mid-flight between the computation change and the re-stamp, as expected — fail-closed).
- `python tools/test_project_control.py` → **EXIT 0** ("all 23 project-control test groups
  passed"); `test_directive_reminder.py` → **EXIT 0**; `test_readonly_agent_guard.py` →
  **EXIT 0**; `test_agent_dispatch_guard.py` → **EXIT 0**.
- `python tools/test_directive_compliance.py LineEndingNormalizationTest -v` → **Ran 3 tests …
  OK** (239.9s) — all three new tests green locally, including the representation-flip against
  the real re-stamped registry.
- Full adversarial suite locally: proven green in TWO class-split runs (the suite copies the
  whole real registry per Fixture test and ran at ~1–8 tests/min on this machine today —
  disk/AV pressure — so one continuous run exceeded the session's process limits, with ZERO
  failures in any run): first run covered classes A–L alphabetically with **75 tests ok**
  (killed mid-final-test by the process limit; that test then passed in the dedicated 3/3
  class run above); second-half run (classes MultiTaskVerificationTests→
  ValidatorEmptyIdentityTests) completed **Ran 53 tests … OK** (2142.5s, log
  `scratchpad/m0t156_suite_b.log`). The **CI control-plane job on the pushed head runs the
  complete file in one pass on ubuntu and is the executable authority** for the whole suite
  (it also exercises the LF side of AS-2) — reviewers verify its green run.

## 6. Named mutants (reviewers' static red-half)


| Mutant | Killed by |
|---|---|
| Normalization removed (raw hashing restored) | AS-1 equality fails (CRLF file digest ≠ recorded LF value); real-registry validation fails on the CRLF side against the re-stamped LF values. |
| Normalization applied but six values NOT re-stamped | Local `--check` EXIT 1 (recorded CRLF values no longer match normalized computation). |
| Normalization over-forgives (strips more than CR) | AS-5 tamper test fails to raise → test asserts the error IS raised. |
| Only some sites normalized (e.g., c2 but not c14) | Real-registry validation fails on one side for the unconverted class (D-032/033 have BOTH source and requirements mismatches — each class exercises its site). |
| Fixture digests left raw | Suite fails on Windows (write_text CRLF-translation) — the platform-honesty fix is self-testing. |
