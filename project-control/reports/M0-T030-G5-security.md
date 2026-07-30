<!-- Orchestrator note: security-reviewer return saved VERBATIM from the agent-return channel
     (transport entity-decoding only: &amp;&amp; -> &&, &lt;/&gt; -> </>). Reviewed head
     baa09f87780057dc1c5cb29cd7a9f6caf9b4b170; recorded for gate G5 of M0-T030. -->

All evidence is in. Here is the G5 report content, returned verbatim for the orchestrator to save and record.

---

# Gate Report

- Gate ID: G5 (security)
- Task ID: M0-T030
- Reviewer: security-reviewer (independent G5, this agent; read-only)
- Producer: task producer per `project-control/reports/M0-T030-producer-report.md` (reviewer ≠ producer)
- Result: **PASS**
- Clean environment/worktree used: yes — frozen worktree `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\.claude\worktrees\M0-T030-codegraph` at `baa09f87780057dc1c5cb29cd7a9f6caf9b4b170` (verified `git rev-parse HEAD`; `git status --porcelain` empty before AND after all executions; base `613c4b1` confirmed ancestor of frozen head)

## Acceptance criteria reviewed

Security-relevant subset for G5: AS-4 (pollution exclusion), AS-6 (bounded query, never full dump), AS-7 (stdlib-only imports, temp fixtures), AS-8 (additive CI job, no new third-party actions), AS-10 (isolation: diff touches only allowed paths). All reproduced; details below. Functional depth of AS-1/2/3/5/9 belongs to G3/G4; the full D-005 requirement matrix (D-005-R001..R089) belongs to the directive-compliance-verifier pass — this report covers the eight security dimensions assigned to G5 plus the D-005 standing prohibitions.

## Directive/requirement verification (security-relevant D-005 prohibitions, re-derived at baa09f87)

| Requirement (source) | Reviewed identity | Verdict | Reproduced evidence |
|---|---|---|---|
| Zero new dependencies (owner clarification 8; packet forbidden_paths) | baa09f87 | PASS | `git diff --stat 613c4b1..baa09f87` = exactly 7 files; no requirements*/lockfile/package.json/pyproject touched. Import inventory (grep below): generate.py imports argparse, ast, hashlib, json, os, re, shutil, sys, tempfile; query.py imports argparse, os, sys, sibling `generate`; test imports ast, json, os, subprocess, sys, tempfile, unittest — all stdlib. Test `test_generator_query_tests_import_stdlib_only` enforces this via `sys.stdlib_module_names` (tools/test_code_graph.py:439-455) and passes. |
| No hook/config surface (owner clarification 8) | baa09f87 | PASS | Diff contains nothing under `.claude/**` or `.git/hooks/**`. No `os.environ[` writes, no `putenv`, no settings-file writes anywhere in the three Python files (grep evidence below). Env access is read-only: `os.environ.get("CODEGRAPH_CACHE_DIR"/"LOCALAPPDATA")` (generate.py:809,813); test mutates only a child-process env copy (test_code_graph.py:125-126). Sole config READ is in-repo `apps/web/tsconfig.json` (generate.py:423). |
| No network, no execution of scanned code | baa09f87 | PASS | Zero matches for urllib/socket/http/requests/httpx/aiohttp/ftplib/smtplib and for eval(/exec(/compile(/`__import__`/importlib/os.system/os.popen/shell= across all three files (the only grep hits are regex variable names `_TS_*_RE` at generate.py:368-379 and a fixture URL string at test:81). Python analysis is `ast.parse` only (generate.py:297); TS is regex/state-machine; scanned files are read as bytes, never imported. |
| Artifacts only outside repo; worktree husks excluded, never modified (owner clarifications 3, 9) | baa09f87 | PASS | `_assert_outside_repo` (generate.py:819-829) realpath-resolves both paths and refuses `commonpath == repo` — probe `--out ./services/api/graphout` refused, exit 1. Only deletions in code are the tool's own `tempfile.mkdtemp` dirs (generate.py:871-872) and test TemporaryDirectory cleanup. `.claude` is in EXCLUDE_DIRS (generate.py:48) and is not an include root, so husks are never traversed; AS-4 sentinel test plants `.claude/worktrees/husk` files and asserts zero indexing (test:87-110, 213-225) — passes. `git status --porcelain` empty after live generation + check runs. |
| Graphify prohibition (D-005-R068) | baa09f87 | PASS | No install/download/tool-env anywhere in diff; "graphify" appears only as the excluded dir name `graphify-out` (generate.py:62) and the README "No Graphify" statement. |
| CI: additive job only, no new third-party action | baa09f87 | PASS | `git diff 613c4b1..baa09f87 -- .github/workflows/ci.yml` is a single pure-append hunk `@@ -380,3 +380,21 @@` — existing jobs byte-untouched. New job uses only `actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5 # v4.3.1`, the identical SHA pinned by every existing job; runs `python3` stdlib only; inherits workflow-level `permissions: contents: read` (ci.yml:12-13); references no secrets. |

## Steps independently executed (exact commands)

All run in the frozen worktree; artifact writes went only to the session scratchpad/system temp.

1. `git rev-parse HEAD && git status --porcelain && git diff --stat 613c4b1..baa09f87780057dc1c5cb29cd7a9f6caf9b4b170` → HEAD matches, clean, 7 files / 2272 insertions, 0 deletions.
2. Full read of `tools/code_graph/generate.py` (915 lines), `tools/code_graph/query.py` (401), `tools/test_code_graph.py` (460), `tools/code_graph/README.md`, task packet, D-005 amendment.
3. `git diff 613c4b1..baa09f87 -- .github/workflows/ci.yml` → single append-only hunk.
4. `grep -n "uses:" .github/workflows/ci.yml | sort -u` and `grep -n -E "^permissions:|secrets\." .github/workflows/ci.yml` → one checkout/setup-python/setup-node/upload-artifact set, all SHA-pinned; workflow `permissions: contents: read`; no secrets.
5. `grep -n -E "^\s*(import|from)\s" tools/code_graph/generate.py tools/code_graph/query.py tools/test_code_graph.py` → stdlib-only inventory above.
6. `grep -n -E "eval\(|exec\(|compile\(|__import__|importlib|os\.system|os\.popen|shell\s*=|os\.environ\[|putenv|ctypes|pickle|marshal|urllib|socket|http|requests|ftplib|smtplib" <same three files>` → only regex-name/fixture-URL false positives; `grep -n "subprocess"` → test file only, list-args + `sys.executable`, `shell` never set (test_code_graph.py:124-130, 167-171).
7. `python tools/test_code_graph.py` → **26/26 OK** (5.4s), including the stdlib-import enumeration, in-repo-write refusal, sentinel exclusion, no-absolute-paths, bounded-query, and stale-fingerprint tests.
8. `python tools/code_graph/generate.py --repo . --check` → `determinism check PASS: 2 generations byte-identical (235 input files, fingerprint 18d461e2...)`.
9. `python tools/code_graph/generate.py --repo . --out ./services/api/graphout` → `refusing to write artifacts inside the repository`, exit 1.
10. Hostile-input probes against `query.py` (generation into scratchpad first): `find "a b'; touch pwned #\" $(whoami) \`id\`"` → `(no results)`, exit 0, no side-effect file created; `file "../../../../etc/passwd"` → `node not found`, exit 2 (treated as inert node id, no filesystem access); `find "zonage☃日本語"` → `(no results)`, exit 0 (UTF-8 stdout reconfigure, query.py:346-347).
11. Artifact leakage scan on generated `graph.json`/`graph.meta.json`: `grep -c -i -E "c:\\|c:/|MLFLL|Users\\\\|home/"` → 0/0; secret-pattern grep (`eyJ...`, `sk-`, `AKIA`, `ghp_`, `service_role`) → zero hits; programmatic field inventory → node keys {id, kind, path, line, qualname, module, confidence, is_test, name, stem, schema_id}, edge keys {type, from, to, line, specifier, confidence, resolution}; longest field value 142 chars — structurally incapable of carrying file contents.
12. `git status --porcelain` after all executions → empty (no repo mutation; husks untouched).
13. `git ls-tree -r baa09f87 services/api tools apps/web/src packages/contracts | grep -c "^120000"` → 0 committed symlinks in indexed roots; `git merge-base --is-ancestor 613c4b1 baa09f87` → yes.
14. `grep -n -i -E "c:\\|c:/users|MLFLL|api[_-]?key|secret|token|password|service_role|eyJ" project-control/reports/M0-T030-*.md` → single benign hit ("No token counts are claimed").

## Expected versus actual

Every dimension matched expectation; no divergence between producer claims and reproduced behavior in the security scope.

## Evidence paths

- `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\.claude\worktrees\M0-T030-codegraph\tools\code_graph\generate.py`
- `...\tools\code_graph\query.py`, `...\tools\code_graph\README.md`, `...\tools\test_code_graph.py`
- `...\.github\workflows\ci.yml` (job `code-graph`, lines 382-399 at frozen head)
- `...\project-control\tasks\M0-T030.json`, `...\project-control\directives\D-005-codebase-knowledge-graph-pilot\source-002-amendment.md`
- Generated inspection artifacts (outside repo): `C:\Users\MLFLL\AppData\Local\Temp\claude\...\99edbbfc-...\scratchpad\g5-out\graph.json` / `graph.meta.json`

## Human-style walkthrough findings

N/A (no UI). CLI behavior walked through under hostile inputs; error paths (`ambiguous node`, `node not found`, `STALE` exit 3, in-repo write refusal) behave as documented.

## Regression/security/provenance findings — dimension verdicts

1. **Supply chain — PASS.** Stdlib only (read + test-enforced); no manifest/lockfile touched; no new action; existing CI jobs byte-untouched (pure-append hunk).
2. **Hook/config surface — PASS.** Nothing under `.claude/**` / `.git/hooks/**`; env reads only; single in-repo tsconfig read.
3. **Network/execution — PASS.** Zero network modules; ast/regex parsing only; scanned code never imported/eval'd.
4. **Filesystem safety — PASS.** Realpath-based outside-repo assertion (symlink-safe both directions); `os.walk` default `followlinks=False`; deletes only its own temp dirs; husks excluded and untouched; worktree clean after all runs.
5. **Injection/robustness — PASS.** No subprocess in generator or CLI; metacharacter/traversal/unicode args inert (probes above); output bounded (hard cap 200, query.py:44-45, 132-139).
6. **Secrets — PASS.** No credential paths matched by include patterns (`.py/.ts/.tsx/.schema.json` under four code roots — `.env` structurally excluded); artifacts contain zero absolute paths, usernames, or secret-shaped strings.
7. **CI — PASS.** Same SHA-pinned checkout, `permissions: contents: read` inherited, no secrets, stdlib python3, artifacts in runner temp only.
8. **Prompt-injection/exfiltration surface — PASS.** Field inventory proves artifacts and CLI output carry only repo-relative paths, line numbers, identifiers, and raw import specifiers/schema `$id`s — all already Readable source content; no file-content field exists; output line-capped. No channel beyond what Read already allows.

## Defects

None blocking. Severity-tagged advisories (non-blocking):

1. **LOW — cache artifact integrity not self-verified.** `query.py:52-72` (`load_graph`) validates only `meta.source_fingerprint` against the recomputed source fingerprint; `graph.json` bytes are not bound to any hash, so a same-user actor (or corruption) tampering the cache dir can have altered navigation results served while "fresh". Mitigated by the same-privilege-domain threat model, the advisory-only trust model (README mandates source verification), bounded output, and no content emission. Remediation: record `sha256(graph.json)` in `graph.meta.json` and verify on load, regenerating on mismatch. Repro: edit `graph.json` in the cache without touching sources; query serves the edit silently.
2. **INFO — cache key is repo basename, not full root.** `generate.py:802-816` keys the default cache by `basename(repo_root)`; the packet note says "keyed by repo root + source fingerprint". Two same-named checkouts share a dir → regeneration churn only; the fingerprint gate prevents any stale/cross-checkout answer. Optional remediation: include a hash of the absolute repo path in the key.
3. **INFO — symlinked files (not dirs) inside include roots would be read** for fingerprint/parsing; only identifiers could surface, never contents, and zero symlinks exist in indexed roots at the frozen head (verified via `git ls-tree`). No action required.
4. **INFO — `load_graph` catches `ValueError` but not `OSError`** on the meta read (query.py:59-64); a racing/permission-denied cache read yields a traceback rather than a regeneration. Robustness nit only.

## Required rework

None for G5. Advisory 1 (artifact hash in meta) is recommended for a follow-up hardening task, not a gate condition.

## Reviewer conclusion

**PASS.** At frozen head baa09f87 the M0-T030 diff is additive-only across exactly the allowed paths, stdlib-only, network-free, execution-free over scanned code, writes strictly outside the repository with a symlink-safe guard, excludes and never touches the `.claude/worktrees` husks, adds a least-privilege SHA-pinned CI job without modifying existing jobs, embeds no secrets or absolute paths in artifacts, and its query CLI is injection-inert and structurally incapable of emitting file contents. All 26 tests and the live determinism self-proof pass; the worktree remained byte-clean throughout. Four non-blocking advisories recorded (1 LOW, 3 INFO).
