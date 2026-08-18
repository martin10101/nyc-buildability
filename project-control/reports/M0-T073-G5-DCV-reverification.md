# M0-T073 security + directive-compliance re-verification — condensed record

CONDENSED transcription by the orchestrator (report-preservation rule): captures
the verifier's PASS verdict, the full per-requirement table, and the probe
evidence; the full verbatim return is in the session task-notification record.
NOT labeled verbatim. Independent verifier (security + directive-compliance),
read-only, at frozen HEAD `50721c3e1c16ecdc6f90d235b0d085380630ab12`
(`git status --porcelain` empty before/after; all fixtures in temp). Producer ≠
verifier. This is the held-head re-verification after rounds 1-3 of rework.

## OVERALL VERDICT: PASS

## Gate commands
- `python tools/test_modularity_check.py` → **24 passed**.
- `python tools/modularity_check.py --check` → selected 240, **0 failures**, 4 symbol_ceiling warnings; two `--check --json` runs **byte-identical** (`bc3801ec…`).
- `python tools/context_budget_check.py` → **PASS** (eager 2925 / 6000 tok).
- `--check --today 2026-12-31` → exit 0 (no expiry cliff; the regeneration approval goes inert, not red).

## SEC — quote-aware TS scanner (10 adversarial probes ALL PASS)
`import.meta.glob("./x/*.ts")` counts correctly, no false uncertain; `/*` in one string "closed" by `*/` in another counts correctly; multi-line template interiors count; genuinely unterminated block comment → `sloc_scan_uncertain`; `//`/`/*`/`*/` inside `''`/`""`/backtick never treated as comment delimiters; escaped quotes handled; the documented `${...}`-backtick bound fails LOUD (warning), never silent. **Divergence scan vs an independent full-text streaming tokenizer across all 94 selected .ts/.tsx files: 0 disagreements; 0 files trip scan_uncertain.**

## SEC — enforcement integrity (11/11 PASS)
(a) new >1000-SLOC file fails without exception; (b) edited baseline → `baseline_digest mismatch` fail; (c) expired file exception fails closed in BOTH --check and --report; (d) regeneration approval single-use `for_version`-bound (reuse refused); (e) file shrunk below ceiling → `stale_exception` WARNING not failure (G4-D2); (f) over-broad ceiling on a still-large file (incl. 700 SLOC > 660) still FAILS `exception_too_broad` — the D2 fix does not open a laundering path; (g) glob/dir/unselected/horizon>90d exceptions all rejected.

## SEC — CI modularity job
`git diff 57b80c2..HEAD -- .github/workflows/ci.yml` = +17 lines, 0 deletions, 0 modifications (strictly additive). SHA-pinned checkout (same SHA as 14 sibling jobs); no secrets; `permissions: contents: read`; no `${{}}` in run blocks; unconditional (no if/needs/paths filter); `modularity_check.py` has exactly one subprocess (`git ls-files`, list form, no shell=True); stdlib only, no network.

## DCV — D-017-R105..R113 (9 rows, re-derived at 50721c3)
| Req | Verdict | Evidence |
|---|---|---|
| R105 permanent, not initiative-scoped | PASS | CLAUDE.md item 16 in "Permanent principles"; AGENTS.md "Modularity (permanent)"; rule titled permanent; policy title; unconditional CI job; 90-day horizon forbids standing waivers |
| R106 concise CLAUDE.md principle | PASS | +1 line, all 7 clauses verbatim; context_budget PASS (2925/6000) |
| R107 AGENTS.md Codex rule | PASS | all 5 finding classes verbatim; check answers against actual diff |
| R108 path-scoped rule | PASS | frontmatter Py+TS+TSX congruent with INCLUDE_RULES; all 10 behaviors; 34 lines; auto-loaded in session |
| R109 policy doc | PASS | 184 lines §1-12; all enumerated contents incl. 6 boundary domains, tests-before-extraction, circular-dep prevention |
| R110 deterministic CI checker | PASS | behaviorally re-derived: handwritten-only, exclusions, new/growth fail, warnings, symbol signal, digest-locked baseline, single-use regen, byte-identical output, expiring path-exact exceptions |
| R111 task/review integration | PASS (+obs) | 7 questions 1:1 in start-controlled-task; run-quality-gate checks vs actual diff; AGENTS.md checklist. Obs: docs/templates/*.md not amended (non-blocking) |
| R112 continuing enforcement | PASS | CI unconditional on all branches; CLAUDE.md always-apply; AGENTS.md; rule frontmatter; no expiry cliff |
| R113 proof tests | PASS | all 7 mandated named tests + 17 more; 24/24; verifier reproduced (a)-(f) independently |

Scope: `git diff --name-only 57b80c2..HEAD -- project-control/directives/` empty; `validate_directive_compliance.py --check` exit 0.

## Non-blocking observations (do not gate merge)
1. docs/templates/TASK_PACKET.md / GATE_REPORT.md not amended (obligation lives in the two executed skills).
2. modularity CI job runs runner `python3` while siblings pin setup-python — stdlib-only, low risk; consider pinning for parity.
3. rule TS scope is `apps/web/src/**` only (matches checker); revisit if TS moves to packages/.
4. one live exception entry (consumed for_version:1 regeneration approval, expires 2026-08-25, cannot be reused, goes inert); no file exceptions in force.

**Gate result: PASS. Recommend acceptance and merge.**
