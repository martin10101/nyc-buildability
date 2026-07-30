<!-- Orchestrator note: security-reviewer return saved VERBATIM from the agent-return channel
     (transport entity-decoding only: &amp;&amp; -> &&). Reviewed head
     1891ef3f886c7ba65413ddd9727b5a596c8e705a; recorded for gate G5 of M0-T031. Verdict PASS;
     the prior M0-T030 G5 LOW advisory (graph.json not hash-bound) is formally CLOSED here. -->

# Gate Report

- Gate ID: G5 (security)
- Task ID: M0-T031 — code-graph hardening + selective routing guidance (D-005 amendment 2)
- Reviewer: security-reviewer (independent; read-only; producer ≠ reviewer)
- Producer: backend-engineer
- Result: **PASS**
- Clean environment/worktree used: yes — `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\.claude\worktrees\M0-T031-codegraph-hardening` at frozen head `1891ef3f886c7ba65413ddd9727b5a596c8e705a`; `git status --porcelain` empty before and after all executions (worktree byte-clean throughout).

## Acceptance criteria reviewed

AS-1..AS-6 executed/reproduced live; AS-7..AS-9 verified by diff evidence (details below). All security-relevant criteria hold at the frozen SHA.

## Directive/requirement verification

Scope note: the full D-005 requirements pass (refs = "ALL") is assigned to the `directive-compliance-verifier` lane per the packet's `reviewer_agents`; this G5 report independently re-derives the security-relevant requirements below from source at the frozen SHA. None is claimed on producer say-so.

| Requirement ID | Reviewed SHA / content identity | Verdict | Reproduced evidence |
|---|---|---|---|
| D-005-R092/R096 (selective, never universal graph-first) | 1891ef3f | PASS | `git diff cc273b5..HEAD` grep: no "graph-first for every task" wording anywhere; README §"Selective routing" states "Graph use is NEVER required on every task"; SKILL.md paragraph states "Graph use is never required on every task"; CLAUDE.md row labeled "selective, advisory" |
| D-005-R094-c4 (no product runtime dependency) | 1891ef3f | PASS | Delta file list = 7 files, none under `services/**`, `apps/**`, `packages/**`, `supabase/**` |
| D-005-R101 (no token/time-savings claims) | 1891ef3f | PASS | README explicitly disclaims: "No token or time savings are claimed"; no such claim in SKILL.md/CLAUDE.md rows |
| D-005-R105 (no watchers/schedulers/git hooks) | 1891ef3f | PASS | Delta grep for `watch\|schedule\|cron\|hook\|daemon\|inotify`: only one negative-assertion prose hit; `.claude/hooks/**`, `.git`-adjacent, and settings surfaces have zero diff |
| D-005-R105/R107 (`.claude` surfaces: only the single SKILL.md paragraph) | 1891ef3f | PASS | Only `.claude` path in delta is `.claude/skills/start-controlled-task/SKILL.md`, +3 lines (blank + one prose paragraph + blank), purely additive; surrounding packet-completeness bullets byte-unchanged in context |
| D-005-R109 (no forbidden injection surfaces) | 1891ef3f | PASS | Delta touches none of Mission Control / layer-B / six-PRD / evidence-KG / Graphify / Agent-Teams surfaces (full delta file list below) |

## Steps independently executed

All from the frozen worktree; exact commands:

1. `git rev-parse HEAD && git status --porcelain` → `1891ef3f886c7ba65413ddd9727b5a596c8e705a`, clean.
2. `git diff --stat cc273b5..1891ef3f...` and `git diff --name-only cc273b5..HEAD` → exactly 7 files: `.claude/skills/start-controlled-task/SKILL.md`, `CLAUDE.md`, `project-control/reports/M0-T031-producer-report.md`, `tools/code_graph/README.md`, `tools/code_graph/generate.py`, `tools/code_graph/query.py`, `tools/test_code_graph.py`.
3. `git diff --name-only cc273b5..HEAD -- .github/ '*.yml' '*.yaml' '*.toml' '*.lock' 'package*.json' 'requirements*.txt' '*.cfg' '.claude/hooks/' '.claude/settings*'` → empty; explicit `git diff cc273b5..HEAD -- .github/workflows/` → **empty (ci.yml zero diff)**.
4. Full hunk-level review of the diffs for all 5 non-report files.
5. Import audit: `grep -n "^import \|^from " tools/code_graph/generate.py tools/code_graph/query.py tools/test_code_graph.py` → generate.py: argparse/ast/hashlib/json/os/re/shutil/sys/tempfile; query.py: argparse/hashlib/json/os/sys + sibling `generate`; test: adds only `hashlib`. All stdlib. `subprocess` in the test file is pre-existing at cc273b5 (lines 19/124/127/168) and invokes only `sys.executable` against the CLI under test.
6. Dangerous-pattern scan over `tools/code_graph/*.py` + test: no `subprocess/eval/exec/socket/urllib/requests/os.system/popen/__import__/importlib/ctypes/pickle/threading/sched/atexit` in shipped tool code.
7. `python tools/test_code_graph.py` → **Ran 36 tests … OK** (36/36).
8. `python tools/code_graph/generate.py --repo . --check` → "determinism check PASS: 2 generations byte-identical (235 input files)".
9. `python tools/context_budget_check.py` → **PASS** with the CLAUDE.md row present.
10. **Live tamper probe (my own, outside the test suite)** — temp fixture repo + `CODEGRAPH_CACHE_DIR` in temp, driving the real CLI via subprocess:
    - [1] warm query rc=0; cache dir name observed: `310fd593d644-repo` (hash-prefixed key exists only in the out-of-repo temp cache dir name).
    - [2] flip one byte mid-`graph.json`, `--no-regen` → rc=3, `STALE (cache integrity): refusing to serve the cached graph`, no traceback, no result line served.
    - [3] same tamper, regen allowed → rc=0, `regenerated (cache integrity)`, correct answer; cache bytes restored byte-identical to pre-tamper (deterministic rebuild).
    - [4] set `meta.graph_sha256` to 64 zeros, `--no-regen` → rc=3, refused.
    - [5] consistent same-privilege rewrite of BOTH `graph.json` and `meta.graph_sha256` → served (documented residual, see Finding 1).
11. Secret scan of the full delta (`api key/secret/token/password/bearer/AKIA/sk-/eyJ/supabase`) → no secrets; only prose hits ("STALE token", "no token savings").
12. Absolute-path scan of the full delta (`c:\`, `/home/`, `/Users/`, `MLFLL`) → zero hits; nothing committed embeds absolute paths. Meta fields (generate.py:790-805 + :869) contain no absolute paths either.
13. Write-surface audit: only write-mode opens in shipped code are `generate.py:867/:870` into `out_dir`, guarded by the intact symlink-safe `_assert_outside_repo` (generate.py:845-855, unchanged); `query.py:76/:87` opens are `rb` only. **No new filesystem writes inside the repo.**
14. Post-run `git status --porcelain` → still empty at `1891ef3f`.

## Expected versus actual

Every dispatch dimension matched expectation:

1. **Supply chain** — expected stdlib-only, no manifest/workflow diff → actual: confirmed (steps 3, 5, 6). ci.yml has NO diff.
2. **SKILL.md** — expected exactly one additive prose paragraph → actual: +3 lines (blank/paragraph/blank) inserted between item 3's gate bullet and item 4; no tool-invocation mandate ("Graph use is never required on every task"), no hook-like behavior, packet-completeness rules around it byte-unchanged, and it *strengthens* source verification ("graph output is advisory only, and material conclusions must be verified in the actual source") — it cannot route agents to bypass source verification.
3. **CLAUDE.md** — expected one additive table row, budget PASS → actual: single `+` row in the routing table (doc pointer to `tools/code_graph/README.md`, "selective, advisory"), no behavioral/config semantics; `context_budget_check.py` PASS at frozen head.
4. **Integrity feature** — expected verify-on-load covering meta and graph, no stale-serve escape → actual: `query.py:60-100 _read_cache_attempt` covers BOTH artifacts: meta unreadable/unparseable/non-dict → refuse-or-regenerate; meta bound to live sources via recomputed `source_fingerprint`; graph bytes hash-verified against `meta.graph_sha256` (query.py:91-93), with missing hash treated as failure. Failure paths cannot force serving stale data: `--no-regen` → exit 3 before any read of the graph into an answer; regen `OSError` → exit 3; post-regeneration bytes are **re-verified** (query.py:103-124) and still-bad caches exit 3. No repo-internal writes; realpath cache key (`generate.py:822-842`) exists only in the out-of-repo cache dir name.
5. **No network/exec/eval/subprocess regressions; no watchers/schedulers/git hooks** — confirmed (steps 3, 6, D-005-R105 row).
6. **Protected-main/CI/secret-scan/dependency/directive processes untouched** — confirmed by the delta file list (step 2) and empty forbidden-path diff (step 3).

Generic G5 checklist items from the dispatch (cross-tenant isolation, service-role secrecy, private storage, SSRF, upload controls, least privilege beyond the above, log redaction): **N/A for this delta** — no product/API/storage/tenant/credential surface is touched (scope proof, steps 2-3). CLI output prints only repo-relative paths, identifiers, and one-line status messages; nothing sensitive to redact.

## Evidence paths

- `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\.claude\worktrees\M0-T031-codegraph-hardening\tools\code_graph\query.py` (lines 60-124, 185-189, 414-425, 442)
- `...\tools\code_graph\generate.py` (lines 822-842, 845-855, 858-872)
- `...\tools\test_code_graph.py` (new tests at lines ~496-623)
- `...\tools\code_graph\README.md`, `...\CLAUDE.md`, `...\.claude\skills\start-controlled-task\SKILL.md`
- Prior advisories: `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\project-control\reports\M0-T030-G5-security.md` (lines 81-90)
- Task packet: `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\project-control\tasks\M0-T031.json`

## Human-style walkthrough findings

N/A (no UI). CLI behavior walked through live in step 10; refusal/regeneration messages are one-line, actionable, and traceback-free.

## Regression/security/provenance findings

**Prior G5 advisory closure status (M0-T030-G5-security.md):**
- **Advisory 1 (LOW — cache artifact not hash-bound, silently served when tampered): CLOSED.** `generate.py:869` records sha256 of the exact written `graph.json` bytes in `graph.meta.json`; `query.py:91-93` verifies on every load; live probes [2]/[3] reproduced refusal (`exit 3`) and regeneration (`regenerated (cache integrity)`); fixture tests `test_tampered_graph_*` lock the behavior. The prior repro ("edit graph.json without touching sources; query serves the edit silently") now fails to reproduce.
- Advisory 2 (INFO — basename-only cache key): CLOSED — `generate.py:826-833` keys by `sha256(realpath(repo_root))[:12] + "-" + basename`; probe and `test_same_basename_checkouts_get_distinct_cache_dirs` confirm distinct namespaces.
- Advisory 4 (INFO — OSError uncaught on meta read): CLOSED — `query.py:77-78/:86-89` catch `OSError` on both reads; directory-in-place-of-file test proves exit 3 with no traceback in both `--no-regen` and regen modes.
- Advisory 3 (INFO — symlinked files inside include roots): out of this task's scope; behavior unchanged, no regression.

**Findings (numbered, severity-tagged):**

1. **INFO (residual, by design — not a defect)** — `tools/code_graph/query.py:91-93`: a same-privilege actor who rewrites BOTH `graph.json` and `meta.graph_sha256` consistently is still served (probe [5] reproduced: rc=0, tampered symbol returned). This is inherent to an unkeyed local per-user cache: any actor with write access to `%LOCALAPPDATA%\nyc-codegraph` can equally rewrite `tools/` itself, so no security boundary is crossed; the prior LOW advisory targeted *unbound* tampering/corruption, which is now detected. Preventing this would require a secret-keyed MAC/signature — out of scope and of no value inside a single-user trust domain. Mitigations already in place: fingerprint bound to live sources, advisory-only trust model with mandatory source verification, bounded output. Repro: rewrite both files consistently in the cache dir, query with unchanged sources. No remediation required.
2. **INFO** — `tools/code_graph/query.py:117-119`: `cache regeneration failed (%s): %s % (reason, exc)` may echo an absolute cache path from the `OSError` text to local stdout. Out-of-repo path, local CLI only, never committed, no secret content — no action required.

No CRITICAL, HIGH, MEDIUM, or LOW defects.

## Defects

None blocking. Two INFO notes above, neither requiring rework.

## Required rework

None.

## Reviewer conclusion

**PASS.** At frozen head `1891ef3f886c7ba65413ddd9727b5a596c8e705a` the M0-T031 delta touches exactly the 7 allowed paths and nothing else (ci.yml and every protected surface byte-untouched); the tool remains stdlib-only with no network/exec/eval/subprocess, no watchers/schedulers/git hooks, and no writes inside the repository; the SKILL.md change is exactly one additive advisory paragraph that reinforces (not bypasses) source verification; the CLAUDE.md change is one additive doc-pointer row with the context budget check PASS; the `graph_sha256` verify-on-load covers both meta and graph artifacts with no failure path capable of serving stale or altered data (36/36 tests plus my independent live tamper, meta-tamper, and OSError probes all confirm refusal/regeneration with no traceback); no secrets or absolute paths appear in any committed file. **The prior G5 LOW advisory (graph.json not hash-bound) is now CLOSED**, as are both related INFO advisories (cache key, OSError handling).
