# M0-T073 G4 QA review — verbatim reviewer return

Preserved verbatim by the orchestrator (report-preservation rule; transport
entity-decoding only). Reviewer: independent qa-engineer subagent, read-only,
at frozen HEAD `6bfc60a`.

---

## G4 QA VERDICT: **PASS** — with two required corrections (C1 blocking evidence accuracy, C2 blocking measurement defect)

Task M0-T073 at frozen HEAD `6bfc60a` (impl commit `ad3408d`). All five mandated verification items reproduce. Fixtures were built in system temp only (`C:\Users\MLFLL\AppData\Local\Temp\claude\...\scratchpad\qa`, `%TEMP%\qa_mod_*`, `%TEMP%\qa_probe_*`); no worktree writes, no git/gh/project_control writes.

---

## 1. Mandated re-runs

**1a. Proof tests — PASS (17/17)**
```
$ cd C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t073 && python tools/test_modularity_check.py
.................
Ran 17 tests in 2.094s
OK

$ python -m pytest tools/test_modularity_check.py -q
17 passed in 3.54s
```

**1b. Checker — PASS (`ok: true`, 0 failures)**
```
$ python tools/modularity_check.py --check --json
 "selected_files": 240,
 "thresholds": {"warn":600,"justify":750,"hard":1000,"symbol_ceiling":40},
 "failures": [],
 "ok": true
EXIT=0
```
Full warning list (4, all `symbol_ceiling`, report-only):
| path | symbols |
|---|---|
| `apps/web/src/lib/surveyReview/types.ts` | 44 (approximate count) |
| `services/api/app/connectors/mappluto_geometry_arcgis.py` | 47 |
| `tools/agent_supervisor/cli.py` | 87 |
| `tools/agent_supervisor/policy.py` | 55 |

Zero `review_signal` and zero `baseline_entry_gone` warnings. Determinism confirmed independently: two consecutive `--check --json` runs are byte-identical (`diff r1.json r2.json` empty).

**1c. `selected_files` is 240, not the claimed 239** — see Finding 1.

**5. Context budget — PASS**
```
$ python tools/context_budget_check.py
  ---- eager total: 11870B  146L  ~2920 tok  (budget 6000 tok)
Result
PASS - automatic context budget within limits; no stale/duplicate/retired regressions.
EXIT=0
```

---

## 2. Independent reproduction of the seven owner proofs

Reproduced in my **own** fixture (`.../scratchpad/qa/qa_proofs.py`), not by trusting `tools/test_modularity_check.py`. Deliberate independence choices: my SLOC generator interleaves blank + comment-only padding lines (so a proof only passes if the s10 definition is honored), and every baseline is produced through the tool's own approved `--regenerate-baseline` path rather than by copying the digest algorithm from the implementation. Empty baselines are created in a repo holding only a tiny file, then the oversized files are added, so they are genuinely classified NEW.

```
$ python qa_proofs.py C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t073/tools/modularity_check.py
```
| # | Proof | Result | Evidence |
|---|---|---|---|
| 1 | normal module passes | PASS | 300 SLOC → `rc=0 ok=True failures=[] warnings=[]` |
| 2 | new 1100-SLOC module fails | PASS | `rc=1`, `new_oversized services/api/giant.py sloc=1100 limit=1000` |
| 3 | grandfathered growth fails | PASS | regenerated baseline recorded 800; at 880 `rc=0`; at **881 `rc=1`**; at 900 `baseline_growth recorded=800 limit=880` |
| 4 | generated-path files excluded | PASS | 7 × 3000-SLOC files under `generated/`, `migrations/`, `vendor/`, `fixtures/`, `tests/`, `*_test.py`, `test_*.py`, `*.test.ts`, `node_modules/` → `selected=1` (only the tiny control file), `rc=0` |
| 5 | valid narrow exception passes, ceiling binds | PASS | ceiling 1200: 1100 `rc=0`, **1200 `rc=0`**, **1201 `rc=1`** `exception_exceeded limit=1200` |
| 6 | expired / broadened / mistargeted fail closed | PASS | expired 2026-08-17 → `rc=1 "EXPIRED"`; glob `services/api/*.py` → `rc=1 "broadened"`; dir `services/api/` → `rc=1`; `no_such.py` → `rc=1 "not a selected handwritten production file"`; **plus extras I added**: missing `review_evidence` → `rc=1`; `kind:"directory"` → `rc=1`; `max_lines:"1200"` (string) → `rc=1`; `expires == today` → `rc=0` (inclusive boundary, correct) |
| 7 | regeneration gated + debt carried + edited baseline fails | PASS | no approval → `rc=1 "cannot be casually regenerated"`; wrong `approval_id` → `rc=1`; expired approval → `rc=1` for regen but **inert for `--check` (`rc=0`)**; with approval v1 records 1400; file grown to 1500 → re-regen v2 still records **1400** (min carry-forward, growth not laundered); hand-edited baseline → `rc=1 "baseline_digest mismatch"` |

Duplicate-exception and vanished-baseline-entry probes also behave correctly (`rc=1 "duplicate exception for ..."`; `baseline_entry_gone` warning, `rc=0`).

The single `FAIL` line in my script output (`boundary 750 justification wording`) is a defect in **my** assertion — I truncated the note to 35 chars before substring-matching. The tool's actual notes are correct: 750 → "above the warning threshold; consider the module boundary…", 751 → "above the justification threshold; record a cohesion justification…".

---

## 3. Baseline cross-check (own one-liner, s10 definition)

Recounted with an independent counter (`strip()`; skip empty; skip `#`-leading for `.py`) — 5 entries checked (3 required):

| entry | recorded | my count | delta |
|---|---|---|---|
| `tools/project_control.py` | 1196 | 1196 | 0 |
| `services/api/app/rules/evaluator.py` | 624 | 624 | 0 |
| `services/api/app/connectors/pluto_soda.py` | 685 | 685 | 0 |
| `tools/agent_supervisor/cli.py` | 2685 | 2685 | 0 |
| `packages/contracts/scripts/generate_ts_types.py` | 630 | 630 | 0 |

Digest independently recomputed from the documented canonicalization: `885cf1c36ec7fbf1bbfef02aa1220ce8312dfd1a22fbbf0676ac3541dd5f605e` — matches `baseline_digest` in `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m0t073\tools\modularity_baseline.json`. All 23 entries are within their material-growth limits.

---

## 4. Boundary QA — matches policy "below/above" semantics

Single fixture repo, empty baseline, files at exactly 600 / 601 / 1000 / 1001 SLOC:

| SLOC | checker | policy §3 wording | match |
|---|---|---|---|
| 600 | no warning, no failure | "should normally stay **below** this" | yes |
| 601 | `review_signal` "above the warning threshold" | — | yes |
| 750 | `review_signal` warning-tier note | "**crossing** it requires justification" | yes |
| 751 | `review_signal` "above the justification threshold; record a cohesion justification" | — | yes |
| 1000 | warning only, **no** failure | "a NEW file **above** this fails CI" | yes |
| 1001 | `new_oversized` failure, `rc=1` | — | yes |
| growth 880 / 881 (recorded 800) | pass / fail | "**more than** max(50, 10%)" | yes |
| exception ceiling 1200 / 1201 | pass / fail | ceiling is inclusive | yes |
| `expires == today` | pass; `today-1` fails | expiry is inclusive of the stated day | yes |

`--report` returns `rc=0` on the same fixture that `--check` fails — report mode never gates, as documented.

---

## Findings

**F1 — LOW (blocking correction C1): `239 selected files` does not reproduce; actual is 240.**
Claimed in `project-control/reports/M0-T073-producer-report.md` (Evidence bullet 2) and in `project-control/reports/M0-T073-evidence-map.json` under `D-017-R110` ("Run at ad3408d: 239 files"). Reproduction — name-only selection replay against both trees plus the live run:
```
$ git ls-tree -r --name-only ad3408d | <apply INCLUDE_RULES/EXCLUDED_SEGMENTS>  -> 240
$ git ls-tree -r --name-only 6bfc60a | <same>                                    -> 240
$ python tools/modularity_check.py --check   -> selected 240 files; failures 0; warnings 4
```
No selected-scope file changed after `ad3408d` (the three later commits touch only `project-control/**`), so the recorded number was almost certainly taken before `tools/modularity_check.py` itself was `git add`ed. Not a functional defect; the evidence map is read as claims at the reviewed identity, so the number should be corrected to 240 before acceptance.

**F2 — MEDIUM (blocking correction C2): TS/TSX SLOC is undercounted ~50% for inline block comments, opening a hard-threshold bypass.**
`source_lines()` in `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m0t073\tools\modularity_check.py` (lines 121–131) discards the **entire** line when a block comment ends on it or when a line begins with `/*`, so code sharing that line is never counted — contradicting the policy's own §10 definition ("physical lines that are non-blank and **not comment-only**"). Reproduction (`.../scratchpad/qa/probe2.py`), 400 repetitions of a 6-line block containing 4 non-comment-only lines:
```
   still block */ const b = 2      <- dropped (code after block terminator)
/* one */ const c = 3              <- dropped (code after inline block comment)
intended SLOC 1600 -> checker measured: 800 -> review_signal
  rc: 0
```
A `.tsx` file with 1600 policy-SLOC therefore **passes** the 1000 hard threshold. The mirror case (`const x = 1; /* start block`) is not detected as opening a block and over-counts instead — safe direction, but it shows the scanner is not comment-state-accurate. Fix: count a line when any non-comment content remains after stripping comment spans, rather than `continue`-ing on the whole line. Non-blocking for the governance artifacts, but it must be fixed before the gate is relied on for `apps/web/src/**`.

**F3 — LOW: malformed JSON and non-git `--repo` raise raw tracebacks instead of the structured error object.**
`json.JSONDecodeError` and `subprocess.CalledProcessError` are not wrapped in `CheckError`. Verified fail-closed (good) but ugly and non-machine-readable:
```
malformed-exceptions EXIT=1   malformed-baseline EXIT=1   non-git-repo EXIT=1
(stderr = Python traceback, not {"command":"modularity-check","ok":false,"error":...})
```
CI safety is intact; only `--json` consumers are affected.

**F4 — LOW: exceptions have no maximum expiry horizon.** An entry with `"expires": "9999-12-31"` and `max_lines: 5000` is accepted (`rc=0`), so "temporary" in `docs/CODE_MODULARITY_POLICY.md` §8 is prose-only. Consider a hard cap (e.g. ≤ 90 days) enforced in `load_exceptions`.

**F5 — LOW: `schemas` and `prompts` in `EXCLUDED_SEGMENTS` contradict policy §5.** §5 explicitly directs serialization code into `schemas/*.py` as a module boundary, while §9 + the checker permanently exclude any path containing a `schemas` segment — so a module the policy *recommends* creating would be unmeasurable. Zero live exposure today (no `.py` under a `schemas/` or `prompts/` segment in the selected roots), so this is a forward-looking gap, not a current hole.

**F6 — LOW: handwritten Python outside `INCLUDE_RULES` is unmeasured** — `.claude/hooks/*.py` (3 files, including the governance-critical dispatch guard) and `.github/scripts/*.py` (2). I verified there is **no** live exposure: across all 442 tracked `py/ts/tsx/js/jsx` files (excluding `node_modules`), **0** unselected non-test files exceed 600 SLOC. Also note `.js/.jsx` are outside every include rule.

**F7 — INFORMATIONAL (for G5 / directive-compliance, not G4): packet path scope drifted.** `ad3408d` also wrote `project-control/reports/M0-T073-G0-readiness.md`, and `02af5f2` added `project-control/reports/M0-T073-evidence-map.json` — neither is in `allowed_paths` (which names `project-control/reports/M0-T073-evidence.md`). `project-control/tasks/M0-T073.json` is listed in `forbidden_paths` yet was modified, though only through the control CLI under orchestrator authority (ADR-005), which I read as intended rather than a violation. Recommend the orchestrator reconcile `allowed_paths` with the artifacts actually produced.

**F8 — INFORMATIONAL: docstring/CI mismatch on `--today`.** `tools/modularity_check.py` docstring says "CI passes the commit date", but the `modularity` job in `.github/workflows/ci.yml` (lines 518–526) runs `python3 tools/modularity_check.py --check` with no `--today`, so it uses the current UTC date. Behavior is correct (expiry must be wall-clock); only the docstring is inaccurate.

---

## Corroborating checks (not requested, but load-bearing for the gate)

- **CI wiring is genuinely additive**: `git show --numstat ad3408d` → `.github/workflows/ci.yml 17/0`, `AGENTS.md 11/0`, `CLAUDE.md 1/0` — zero deletions, so no existing job or principle was edited. The `on:` block is `push:` + `pull_request:` with no branch filter, supporting the R112 permanence claim.
- **No time bomb from the initial approval**: the sole entry in `tools/modularity_exceptions.json` is a `baseline-regeneration` approval expiring 2026-08-25. I confirmed empirically that an expired regeneration approval is refused by `--regenerate-baseline` (`rc=1`) yet **inert** for `--check` (`rc=0`), so CI will not break on 2026-08-26.
- **Rule delivery verified**: `.claude/rules/code-architecture.md` carries real `paths:` frontmatter (`services/**/*.py`, `tools/**/*.py`, `packages/**/*.py`, `apps/web/src/**/*.ts`, `.tsx`) — and it auto-loaded into this session when I read `tools/modularity_check.py`, which is direct behavioral proof of R108. The seven boundary questions are present verbatim in `.claude/skills/start-controlled-task/SKILL.md` step 3, and the reviewer counterpart ("check … against the ACTUAL diff") in `.claude/skills/run-quality-gate/SKILL.md` line 9.

**Verdict rationale:** every mandated check reproduces, all seven owner proofs reproduce independently in a fixture I built, the committed baseline is arithmetically exact and digest-consistent, and boundary semantics match the policy's below/above wording exactly. Recorded as **PASS**; corrections **C1** (F1, evidence number 239 → 240) and **C2** (F2, TS inline-block-comment undercount) are blocking for the next gate and for acceptance per the repo's gate-verdict semantics.
