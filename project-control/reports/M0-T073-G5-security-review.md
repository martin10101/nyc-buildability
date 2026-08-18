# M0-T073 G5 security review — verbatim reviewer return

Preserved verbatim by the orchestrator (report-preservation rule; transport
entity-decoding only: HTML entities decoded; a harness transport notice that
prefixed the return — flagging instruction-shaped patterns in the reviewer's
own quoted settings text — was transport metadata, not reviewer content).
Reviewer: independent security-reviewer subagent, read-only, at frozen HEAD
`6bfc60a`.

---

## VERDICT: **PASS**

No SEC-CRITICAL and no SEC-MAJOR findings. All five verification areas hold. Seven SEC-MINOR items, all defense-in-depth or documentation accuracy — none is a regression, none blocks.

---

## 1. CI workflow change — CLEAN

`git diff -U0 57b80c2 HEAD -- .github/workflows/ci.yml` → **one hunk**: `@@ -509,0 +510,17 @@` (pure insertion at EOF).

Blob-level proof that every existing job is byte-identical:
```
$ git show 57b80c2:.github/workflows/ci.yml | head -509 | sha256sum
6d01347f3396405ed79262ac063108eaa7fb836d4aee5082048c4fbf2eccbe17
$ git show HEAD:.github/workflows/ci.yml     | head -509 | sha256sum
6d01347f3396405ed79262ac063108eaa7fb836d4aee5082048c4fbf2eccbe17
$ diff <(git show 57b80c2:...) <(git show HEAD:...)
509a510,526        <-- additions only, no `<` lines
```
- Action pin `actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5 # v4.3.1` is the **identical SHA** used by all 13 existing checkout steps (`ci.yml:29,66,134,193,229,257,285,361,384,415,428,460,478,500`). No new external action introduced.
- Workflow `permissions: contents: read` (`ci.yml:12-13`) unchanged; the new job adds no job-level `permissions:`, no `env:`, no `secrets.*`, no `token`, no network fetch (`curl`/`wget`/`pip install`/`npm`) — grep over `ci.yml:510-526` returns `NONE`.
- Both steps run stdlib-only local Python. No exfiltration or escalation surface.

## 2. `tools/modularity_check.py` — subprocess, I/O, exception schema: fail-closed

- `modularity_check.py:89` — `subprocess.run(["git","ls-files"], cwd=str(repo), capture_output=True, text=True, check=True)`. Fixed argv, no `shell=True`, no interpolation from any data file. The only `--repo` influence is the operator's own CLI argv.
- No `eval`/`exec`/`import` of data, no network, no `os.system`. File reads are confined to paths emitted by `git ls-files` (tracked, repo-relative).
- Exception-file adversarial matrix (ephemeral `tempfile.TemporaryDirectory` fixture, repo untouched), 23 cases — **every** malicious/malformed shape fails closed:

```
A1  path traversal '../../etc/passwd'  -> CheckError: not a selected handwritten production file
A2  absolute '/services/api/big.py'    -> CheckError: not a selected ...
A3  'C:\repo\services\api\big.py'      -> CheckError: not a selected ...
A4  glob 'services/api/*.py'           -> CheckError: broadened (glob or directory)
A5  directory 'services/api/'          -> CheckError: broadened ...
A6  unselected path                    -> CheckError: incorrectly targeted
A7  EXPIRED file exception             -> CheckError: EXPIRED ... fail closed
A9  max_lines=true (bool-as-int)       -> FAILURES (stricter: limit 1)
A10 max_lines=-1 / A11 max_lines="99999" -> CheckError: needs positive int max_lines
A12 kind='wildcard' / A13 kind={dict}  -> CheckError: unknown kind
A15 duplicate exception                -> CheckError: duplicate exception
A16 missing owner / A17 blank reason   -> CheckError: missing required field
A18 expires='soon'                     -> CheckError: bad expires date
A20 NUL byte in path                   -> CheckError: not a selected ...
A21 exceptions not a list              -> CheckError: `exceptions` must be a list
```
- Kind-confusion escalation retested properly: a `kind: baseline-regeneration` entry carrying `path` + `max_lines` **cannot** waive a file — `ok=False, failures=['new_oversized']`.
- Exceptions file deleted → `{}` exceptions (strictly stricter). Baseline file missing → `CheckError` exit 1.

## 3. Enforcement integrity — demonstrated

Temp-fixture proof run (`--repo/--baseline/--exceptions/--today` overrides, real CLI, exit codes shown):
```
T2  NEW 1500-SLOC file, no exception       -> exit 1  FAIL new_oversized ... above the hard threshold
T3  baseline edited, digest NOT updated    -> exit 1  FAIL: baseline_digest mismatch
T5  reviewed exception (max_lines 1600)    -> exit 0  (warn review_signal only)
T6  file grew past exception ceiling       -> exit 1  FAIL exception_exceeded (1700 > 1600)
T7  EXPIRED file exception, --check        -> exit 1  FAIL: EXPIRED ... fail closed
T7b EXPIRED file exception, --report       -> exit 1  (expiry is NOT downgraded to a warning)
T8  baseline file 1200 -> 1400             -> exit 1  FAIL baseline_growth
T10 --regenerate-baseline, no approval     -> exit 1  FAIL: no unexpired approval
T11 --regenerate-baseline, EXPIRED approval-> exit 1  FAIL: no unexpired approval
T12 regen w/ valid approval, file at 1300  -> baseline retains 1200 (min(recorded,current); debt not laundered)
T13 baseline missing                       -> exit 1  FAIL: baseline missing
```
**No-warning-only-gates (CLAUDE.md p15 analogue) holds**: an expired exception fails closed in *both* `--check` and `--report`, because `CheckError` short-circuits before `payload["ok"]=True` is applied (`modularity_check.py:391-403`). Only *findings* are downgraded in report mode; CI uses `--check`.

Committed state: `python tools/modularity_check.py --check` → `exit 0, selected 240 files; failures 0; warnings 4`. `python tools/test_modularity_check.py` → `Ran 17 tests ... OK`. No expiry time bomb: `--check --today {2026-08-25, 2026-08-26, 2027-01-01}` all exit 0 (the sole committed exception is a `baseline-regeneration` approval, correctly inert for `--check` after expiry).

## 4. Governance surface — covered

- `project-control/config.json → directive_compliance_regime.governance_paths` = `["CLAUDE.md", ".claude/hooks/", ".claude/rules/", ".claude/agents/", ".claude/skills/", ".claude/settings.json", "tools/project_control.py", "tools/directive_registry.py", "tools/validate_directive_compliance.py", "project-control/directives/", ".github/workflows/"]`. The packet's `allowed_paths` touch four of these.
- Packet `directive_refs` = `[{D-001: ALL}, {D-017: ALL}]`; D-017-R110 present at `project-control/directives/D-017-a-to-z-completion-authorization/requirements.json:3630`. `directive_registry.load_registry().covers_governance(task)` → **True**.
- `git diff --name-only 57b80c2 HEAD -- project-control/directives/` → **0 files**. No directive text, requirement, or verification record altered.
- `python tools/validate_directive_compliance.py` → `directive registry OK: 17 directive(s), 17 active; source hashes, ID append-only, and producer/verifier separation verified.`

## 5. No degradation of existing protections

- CLAUDE.md diff is a single `+` line (new p16). p15 dependency-security text appears in the diff **only as context** — `git diff ... | grep -E "^[+-]" | grep -c "Dependency security"` → **0**. Byte-untouched.
- AGENTS.md / both SKILL.md edits are pure additions; no existing sentence removed or weakened. The `run-quality-gate` addition adds a reviewer obligation; it does not relax the read-only or PASS/FAIL/BLOCKED contract.
- No existing CI job, hook, or gate weakened. `tools/project_control.py` is in the packet's `forbidden_paths` and untouched.

---

## Numbered findings (all SEC-MINOR)

**SEC-MINOR-1 — Baseline digest is unkeyed; the FAIL message overstates what it proves.** `tools/modularity_check.py:153-178`. `baseline_digest()` is a plain SHA-256 over `{version, files}` and ships in the repo, so a deliberate hand-edit that recomputes the digest passes:
```
T3 baseline edited, digest NOT updated  -> exit 1
T4 same edit + digest RECOMPUTED        -> exit 0, "selected 2 files; failures 0"   <-- 1500-SLOC file laundered
```
The message at `:174-177` ("was edited without regeneration approval; debt cannot be erased by editing the baseline") asserts more than the mechanism supports. It is a silent-drift detector, not an authenticity control — the true control is human review of the baseline diff. Accepted risk for an in-repo CI gate (a hostile committer can equally edit the checker or `ci.yml`), but the wording should be softened, and `generated_with_approval_id` should be folded into the digest input plus cross-checked against an exceptions entry so a laundered baseline cannot keep claiming a stale approval at an unbumped `version`.

**SEC-MINOR-2 — Baseline-regeneration approvals are reusable and unbound.** `tools/modularity_check.py:327-347`; `tools/modularity_exceptions.json:5-12`. `approved = [r for r in regenerations if r["approval_id"] == approval_id and not r["_expired"]]` — nothing marks the approval consumed or binds it to the resulting version/digest. `M0-T073-initial-baseline` is live until **2026-08-25** (7 days from today), and `regenerate_baseline` grandfathers *any* currently-selected file at or above WARN that is absent from `old_entries` (`:343-344`). So during that window a re-run grandfathers arbitrary new oversized files at their current size. Recommend: single-use approvals bound to the produced `version`.

**SEC-MINOR-3 — The new enforcement artifacts are not in `governance_paths`.** `project-control/config.json → directive_compliance_regime.governance_paths` lists `tools/project_control.py`, `tools/directive_registry.py`, `tools/validate_directive_compliance.py` but **not** `tools/modularity_check.py`, `tools/modularity_baseline.json`, or `tools/modularity_exceptions.json` — which now gate CI. A future packet can edit the baseline or exceptions without tripping the governance-directive coverage requirement (`tools/project_control.py:437-484`). Combined with SEC-MINOR-1/2 this leaves the baseline-laundering path with no control-plane guard beyond ordinary review. `config.json` is outside this packet's `allowed_paths`, so this is a follow-up, not a defect of this diff.

**SEC-MINOR-4 — "Narrow and temporary" is not machine-enforced in either dimension.** `tools/modularity_check.py:202-232`; policy §8 (`docs/CODE_MODULARITY_POLICY.md:122-128`). No maximum expiry horizon (`A19 expires=9999-12-31 -> ok`) and no bound on `max_lines` (`A8 max_lines=10**9 -> ok`, fully neutralizing the growth check for that path). Contrast CLAUDE.md p15, whose waiver is single-package and auto-expiring. Suggest capping `expires` (e.g. ≤90 days) and requiring `max_lines` to be within the growth limit of the current count.

**SEC-MINOR-5 — Malformed policy data escapes as an uncaught traceback rather than a structured `CheckError`.** `tools/modularity_check.py:166,190` (`json.loads` / `data.get`). `T14` (`{not json`) → `json.decoder.JSONDecodeError`; `T15` (top-level JSON list) → `AttributeError: 'list' object has no attribute 'get'`; both **exit 1**, so CI still fails closed. Hygiene only: wrap in `CheckError` so `--json` consumers get the structured `{"ok": false, "error": ...}` envelope.

**SEC-MINOR-6 — Docstring/workflow mismatch on the expiry clock.** `tools/modularity_check.py:28-30` states "CI passes the commit date"; `.github/workflows/ci.yml:524` runs `python3 tools/modularity_check.py --check` with **no** `--today`, so expiry uses the runner's current UTC date (`:382-383`). Impact is in the safe direction (a replayed green commit correctly turns red once an exception expires), but the comment is inaccurate.

**SEC-MINOR-7 (informational) — Scope coverage of handwritten enforcement code.** `INCLUDE_RULES` (`:54-59`) covers `services/`, `tools/`, `packages/`, `apps/web/src/` only. Measured out-of-scope handwritten code: `.github/scripts/validate_contracts.py` (522 SLOC), `.claude/hooks/readonly_agent_guard.py` (319), `.github/scripts/secret_scan.py` (226). Of the 202 unselected tracked `.py/.ts` files, 93 are excluded by segment and all but one (`packages/contracts/fixtures/legal_source_manifest/check_m3_t001.py`, 162 SLOC) are tests — so `EXCLUDED_SEGMENTS` (including the broad-looking `schemas`/`prompts`/`generated`) is **not** currently hiding production code. Not a weakening; noted so a future scope expansion is a deliberate decision.

Also noted, pre-existing and outside this packet: `AGENTS.md` is an agent-instruction file that is edited here but is **not** listed in `governance_paths`. Immaterial for this task (D-017:ALL covers it via the other four governance paths).
