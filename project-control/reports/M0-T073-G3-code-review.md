# M0-T073 G3 code review — verbatim reviewer return

Preserved verbatim by the orchestrator (report-preservation rule; transport
entity-decoding only). Reviewer: independent code-reviewer subagent, read-only,
at frozen HEAD `6bfc60a`.

---

# G3 Code Review — M0-T073 (modularity enforcement) @ `6bfc60a`

## VERDICT: **PASS with required corrections** (3 BLOCKING, listed as C1–C3)

The deliverable is genuinely fail-closed, deterministic, and additive. All seven mandated D-017-R113 proofs are really proved (with negative controls), the CI job matches repo convention exactly, and every threshold is consistent across all five texts. The blocking items are three factual corrections to permanent-law artifacts and evidence — each a one-line fix, none requiring redesign.

## Scope check
`git diff 57b80c2..HEAD --stat` → **15 files, 1158 insertions / 69 deletions**. Every path is inside the declared reviewed set. Nothing outside it. Untracked working-tree files (`project-control/gates/M0-T073-G0.json`, `-G2.json`, `reports/M0-T073.json`, modified `state.json`) are orchestrator control-plane artifacts, not part of the diff.

Packet integrity: semantic diff of `project-control/tasks/M0-T073.json` base→HEAD shows **only** `producer_agent: null → "orchestrator"` plus lifecycle fields (`status backlog→awaiting_gate`, `progress 0→85`). **No goalpost movement** — objective, acceptance criteria, allowed/forbidden paths unchanged.

## Mandated commands

```
$ python tools/test_modularity_check.py -v
... 17 tests ... Ran 17 tests in 2.102s   OK
```
**17/17 pass.**

```
$ python tools/modularity_check.py --check ; echo EXIT=$?
selected 240 files; failures 0; warnings 4
  warn symbol_ceiling: apps/web/src/lib/surveyReview/types.ts ...
  warn symbol_ceiling: services/api/app/connectors/mappluto_geometry_arcgis.py ...
  warn symbol_ceiling: tools/agent_supervisor/cli.py ...
  warn symbol_ceiling: tools/agent_supervisor/policy.py ...
EXIT=0
```
**0 failures confirmed.**

---

# BLOCKING corrections

### C1 — MAJOR — `tools/modularity_check.py:28` states a determinism property CI does not implement
The module docstring (permanent-law artifact) reads:
> `expiry comparison uses --today when supplied (CI passes the commit date; ...)`

`.github/workflows/ci.yml` runs `python3 tools/modularity_check.py --check` — **no `--today` argument**. CI therefore uses the runner's wall clock, not the commit date.

Reproduction: `grep -n 'modularity_check.py' .github/workflows/ci.yml` → `run: python3 tools/modularity_check.py --check` (no `--today`).

Impact is real, not cosmetic: once any *file* exception exists, re-running CI on a previously-green commit will flip red after the expiry date, and the docstring promises the opposite. (The one committed exception is `kind: baseline-regeneration`, which correctly goes inert rather than failing — verified by `test_7b` and code path `modularity_check.py:212-214` — so nothing breaks on 2026-08-25.)

**Fix either way:** add `--today ${{ commit date }}` to the CI step, or delete the parenthetical. Do not ship the false claim.

### C2 — MAJOR — `docs/CODE_MODULARITY_POLICY.md` §5 steers production code into the checker's blind spot (contradicts §9)
- §5, line 75: `... → repositories/*.py (storage) → **schemas/*.py** (serialization)` — recommends a `schemas/` directory for handwritten production serialization code.
- §9, line 135: `Excluded: generated code, vendored code, lockfiles, **schemas**, migrations, ...`
- `tools/modularity_check.py:65`: `"schemas"` is in `EXCLUDED_SEGMENTS`.

An agent obeying the policy's own §5 boundary example creates permanently unmeasured production code. Reproduction:
```
services/api/app/schemas/huge.py  ->  selected=False
```
Currently zero impact (`grep` for a `schemas/` segment in the include roots returns 0 files; the repo uses `services/api/app/_contract_schemas/`, which *is* correctly selected). But this is permanent law being written with a self-defeating instruction.

**Fix:** change §5's example to a non-excluded name (e.g. `serializers/*.py`, matching the existing `_contract_schemas/`), or drop `"schemas"` from `EXCLUDED_SEGMENTS`. The two must agree.

### C3 — MINOR (blocking as evidence accuracy) — producer evidence records a file count that does not reproduce
`project-control/reports/M0-T073-producer-report.md:33` and the `D-017-R110` row of `M0-T073-evidence-map.json` both claim **"239 selected files"** at `ad3408d`.

Reproduced by replaying the selection predicate over `git ls-tree -r --name-only`:
```
ad3408d: selected 240
HEAD:    selected 240
only in HEAD: []  | only in ad3408d: []
```
The count is **240**, not 239 (almost certainly captured before `modularity_check.py` was itself staged, so it did not appear in `git ls-files`). Failure/warning counts (0 / 4) reproduce exactly. Correct the two evidence artifacts.

---

# Non-blocking findings

### F4 — MINOR — TS/TSX SLOC counter under-counts code sharing a line with a block comment (`modularity_check.py:121-131`)
Verified against the policy §10 definition ("physical lines that are non-blank and **not comment-only**"):

| Input (`.ts`) | SLOC | Correct |
|---|---|---|
| `/* c */ export const x = 1;` ×2 | **0** | 2 |
| `/*\nc\n*/ export const z = 3;` | **0** | 1 |
| `export const x = 1; /*` … `*/` (4 non-blank lines) | **4** | 1 |

Cause: line 126 `continue`s on any line *starting* with `/*` regardless of trailing code; line 123 `continue`s on the closing line; and a mid-line `/*` opener never sets `in_block_comment`. Python has the mirror issue: `#`-leading lines inside a triple-quoted string are dropped (5 non-blank → 2 SLOC).

Direction is mostly permissive (`/**/ code` on every line measures 0 SLOC — a theoretical evasion), but implausibly conspicuous in review. Worth a comment acknowledging the heuristic's bounds, since §10 asserts an exact definition.

### F5 — MINOR — non-`CheckError` exceptions escape the error contract (`modularity_check.py:166, 190, 398`)
`main()` catches only `CheckError`. A malformed exceptions entry that isn't an object raises an uncaught `AttributeError`:
```
UNCAUGHT AttributeError: 'str' object has no attribute 'get'   <- entry is a bare string
```
Same for a syntactically corrupt `modularity_baseline.json` / `modularity_exceptions.json` (`json.JSONDecodeError`). Still **fails closed** (traceback → exit 1), but the documented `{"ok": false, "error": ...}` `--json` envelope is never emitted. Suggest wrapping the two `json.loads` calls and adding an `isinstance(e, dict)` guard at line 196.

### F6 — MINOR — two documented fail-closed branches are unproved by the suite
Policy §8 and the packet promise that *malformed, expired, broadened, or incorrectly targeted* exceptions fail closed, plus duplicate rejection. Tests cover expired (`test_6`), broadened (`6b`), mistargeted (`6c`) — but **not malformed (missing/blank required field, bad date format, non-positive `max_lines`) and not duplicate**. I exercised those branches directly and they all work correctly:
```
fail-closed: exceptions[0]: missing required field 'owner'
fail-closed: exceptions[0]: bad expires date '31-12-2026'
fail-closed: exceptions[0]: file exception needs positive int max_lines
fail-closed: exceptions[1]: duplicate exception for 'services/a.py'
fail-closed: exceptions[0]: unknown kind 'directory'
```
No defect in behavior; a test-coverage gap against the stated contract. Two short tests would close it.

### F7 — MINOR — `--regenerate-baseline` can absorb an *active* violation into legacy debt (`modularity_check.py:343-344`; policy §7 lines 116-120)
Policy §7 says regeneration "never erases live debt" — true for *existing* entries (`min(recorded, current)` carry-forward is correct and proved by `test_7`). But a brand-new file that is **currently failing** `new_oversized` is admitted at full size:
```
before regen: FAIL
after regen, baseline now contains: {'services/api/brand_new_giant.py': 5000}
re-check with regenerated baseline: PASS (violation laundered into legacy debt)
```
This is the single escape hatch for a hard-threshold failure. It is approval-gated (requires an unexpired `baseline-regeneration` entry with a matching `approval_id`, which is itself reviewed), so the control is real — but neither §7 nor any test states it. Recommend one sentence in §7 naming this as the reviewed absorption path.

### F8 — MINOR — coverage gap: handwritten production Python outside the four include roots
`INCLUDE_RULES` (`modularity_check.py:54-59`) omits roots that hold real enforcement code:
```
  319  .claude/hooks/readonly_agent_guard.py
  226  .github/scripts/secret_scan.py
  522  .github/scripts/validate_contracts.py     <- 78 SLOC below the warning threshold
```
Confirmed unselected: `scripts/`, `.claude/hooks/`, `.github/scripts/`, and `packages/**/*.ts` (the `packages/` rule maps to `.py` only). Not currently violated, but `validate_contracts.py` is close to warn and `.claude/hooks/agent_dispatch_guard.py` is explicitly protected repository infrastructure. Good news checked: `apps/web/src/app/**` (the App Router) **is** covered — this repo uses `src/app`, not `app/`.

### F9 — MINOR — rename semantics (informational; behavior is correct)
I tested the "rename to escape the growth limit" attack. It **fails harder**, which is the right outcome:
```
cli.py@2685 in baseline (status quo)   -> ok=True
RENAMED to cli_main.py@2685            -> ok=False FAIL=new_oversized(2685) + warn=baseline_entry_gone(cli.py)
```
For a 600–1000 SLOC baseline file, a rename silently drops the debt entry (emitting `baseline_entry_gone`) and the file passes as a new under-threshold file — acceptable, since the result is still under the hard threshold. **Not a defect.** Likewise the 999-SLOC new file is warn-only by explicit design (`review_signal`), matching policy §3.

### F10 — MINOR — two soft spots in the test suite
- `test_warnings_do_not_fail_and_report_never_fails:210-212` adds a 1100-SLOC file, runs `--report`, and asserts only `code == 0`. The comment claims "report mode **surfaces**, never gates" but surfacing is never asserted. Add `assertTrue(payload["failures"])`. (I confirmed by code trace that `--report` does populate `failures` and only overrides `ok` at line 395 — so the behavior is right, the assertion is half-empty.)
- `test_output_is_deterministic` compares two in-process runs with `--today` pinned, so it structurally cannot detect wall-clock leakage. The `sorted()` discipline throughout makes the property sound regardless; the test just doesn't prove that half.

### F11 — MINOR — symbol-ceiling warning is skipped for a file that trips `exception_exceeded` (`modularity_check.py:268`)
The `continue` short-circuits the `symbols > SYMBOL_CEILING` block at line 291. Cosmetic loss of a report-only signal on already-failing files.

### F12 — MINOR — ledger hygiene
- `acceptance_scenarios` is `[]`. CLAUDE.md principle 8 requires executable acceptance examples. In substance `tools/test_modularity_check.py` (17 tests) plus the evidence map's proof-to-test mapping satisfy the intent, and there is precedent both ways among governance tasks (M0-T055/T057/T062 accepted with 0; M0-T034/T036/T070 with 14/8/12). Recommend backfilling the field since this packet ships real tooling.
- `allowed_paths` names `project-control/reports/M0-T073-evidence.md`, but the producer delivered `M0-T073-evidence-map.json` and `M0-T073-G0-readiness.md` (neither listed). `project-control/tasks/` is in `forbidden_paths` yet `M0-T073.json` changed — that is the control CLI's own lifecycle write, not a hand edit, so it is expected. Update `allowed_paths` to match what was actually produced.

---

## Item-by-item verification of the review brief

**1. Checker correctness.** Selection logic is sound: `git ls-files` (tracked only), segment exclusion, test predicate (`test_`, `_test.py`, `.test.`, `.spec.`), prefix+extension include. I sampled real repo paths — 92 test files and 4 generated + 5 fixture files correctly excluded; `_contract_schemas/` correctly *included*; no false inclusion found. False-exclusion risks are C2 and F8. Growth math `recorded + max(50, 10%)` matches §3 exactly, with `>` (at-limit passes) consistent with "more than". Digest canonicalization is stable (`sort_keys=True`, `separators`, `ensure_ascii` default, keys coerced `str`/`int` before recompute) — note it covers only `version` + `files`, so `thresholds`/`generated_with_approval_id`/`note` are unprotected, but none is load-bearing (the checker uses module constants). Regeneration correctly refuses to run on a tampered baseline (it calls `load_baseline` at line 336 before writing). Determinism: no randomness; the only time input is the documented `--today` default.

**2. Adversarial.** Five attacks run and reported above (F7, F8, F9, C2, plus the 999-SLOC design case). Only F7 and C2/F8 are genuine gaps; the rest are documented design.

**3. CI.** Strictly additive — `--numstat` shows `17 0`, a pure append after `supervisor-bridge`, zero existing lines touched. `actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5 # v4.3.1` is byte-identical to the pin at ci.yml:29. Omitting `setup-python` matches the established stdlib-only-job convention (`code-graph`, `control-plane`, `product-map` jobs all use bare `python3`). `on: push: / pull_request:` has no branch filter, so R112's continuing-enforcement claim holds. Portability confirmed: no Windows-only assumptions — tests use `tempfile.TemporaryDirectory` + `git init -q` + `git -C … add` and **never commit**, so no `user.email` config is needed on a bare runner; selection reads the index via `git ls-files`. Deferred annotations (`from __future__ import annotations`) make the `tuple[...]`/`dict[...]` hints safe on any Python ≥3.9; ubuntu-latest ships 3.12.

**4. Docs.** Thresholds are **600 / 750 / 1000 everywhere** — `AGENTS.md:70`, policy §3 lines 51-53, `code-architecture.md:26`, `modularity_check.py:45-47`, `modularity_baseline.json:5-7`. CLAUDE.md p16 cites no numbers and defers to the policy — no contradiction. The rule's frontmatter (`code-architecture.md:1-8`) covers `services|tools|packages/**/*.py` plus `apps/web/src/**/*.ts` **and** `*.tsx`, exactly matching `INCLUDE_RULES` — the R108 claim is accurate. The only doc contradiction found is C2.

**5. Tests / the seven proofs.** All seven are genuinely proved, several with negative controls: P1 `test_1` (exit 0 + empty failures); P2 `test_2` (exit 1 + kind + path); P3 `test_3` **plus `test_3b`** in-limit control; P4 `test_4` (asserts `selected_files == 0` — strong, not just exit 0); P5 `test_5` (passes, then proves the ceiling bites); P6 `test_6`/`6b`/`6c` (each asserts a distinct error substring); P7 `test_7` (a: refused without approval, b: carried forward at `min` = 1400 not 1500, c: edited baseline → digest mismatch) **plus `7b`** (expired approval refused for regeneration yet inert for `--check`). Plus 4 integrity/determinism tests and 2 real-repo tests. Hollow assertions: only the half-assertion in F10. Untested documented branches: F6.

## Recommendation
Record **PASS**. C1, C2, and C3 are **BLOCKING for acceptance and for the next gate** — all three are one-line edits to permanent-law text or evidence, no code redesign. F4–F12 should be logged as carried defects or folded into the same correction pass at the orchestrator's discretion.
