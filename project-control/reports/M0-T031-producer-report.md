# M0-T031 producer report — code-graph hardening + selective routing guidance

- Task: M0-T031 (D-005 amendment 2, GO WITH CONDITIONS)
- Producer: backend-engineer (worktree agent-a4389b40579d83c13, branched from main cc273b5)
- Date: 2026-07-29 (session local)
- Base commit: `cc273b503b83831310c0a924defd5663b6d654bf`

## 1. Design notes

### 1.1 Hash-bind graph.json in meta, verify on every load (AS-1, G5 LOW advisory)

`tools/code_graph/generate.py::generate_into` now writes in a fixed order:
serialize graph -> write `graph.json` -> compute `sha256` over the exact bytes
written -> record it as `meta["graph_sha256"]` -> write `graph.meta.json`.
The hash is a pure function of the graph bytes, so determinism is unaffected
(no timestamps, no absolute paths; `--check` still passes byte-identically).

`tools/code_graph/query.py::load_graph` now delegates every cache read to
`_read_cache_attempt(meta_path, graph_path, fingerprint)`, which returns the
parsed graph only when the cache is BOTH fresh (fingerprint match) AND intact
(sha256 of the actual cached `graph.json` bytes equals `meta.graph_sha256`,
both files parse). Failure classification:

| condition | reason string | behavior |
|---|---|---|
| meta or graph file cleanly absent (cold cache) | `stale fingerprint` | regenerate / exit 3 (preserves the pre-M0-T031 message contract asserted by the existing tests) |
| `source_fingerprint` mismatch | `stale fingerprint` | regenerate / exit 3 (unchanged) |
| meta unreadable (OSError) or unparseable (ValueError) or not a JSON object | `cache integrity` | regenerate / exit 3 |
| graph unreadable (OSError) | `cache integrity` | regenerate / exit 3 |
| `graph_sha256` missing (e.g. a 1.0.1-era cache) or mismatched | `cache integrity` | regenerate / exit 3 |
| graph bytes unparseable / not a JSON object | `cache integrity` | regenerate / exit 3 |

On regeneration one line is printed: `regenerated (stale fingerprint)` or
`regenerated (cache integrity)`. Under `--no-regen` the CLI prints exactly one
line — `STALE (<reason>): refusing to serve the cached graph` — and exits 3
(the line still contains the historical `STALE` token, so the pre-existing
`test_stale_with_no_regen_exits_3` stays green unmodified). Two defensive
tails: if `generate_into` itself raises `OSError` during the rebuild (e.g. the
cache path is blocked by a same-named directory) the CLI prints one line
`cache regeneration failed (<reason>): <oserror>` and exits 3; if the cache
fails re-verification even after a successful rebuild it prints one line and
exits 3. An altered or unreadable cache is NEVER served and none of these
paths leaks a traceback.

### 1.2 Cache identity beyond basename (AS-3, G5 INFO advisory)

`default_out_dir` key changed from `<basename>` to
`sha256(os.path.realpath(repo_root).encode("utf-8")).hexdigest()[:12] + "-" + <basename>`.
Same-named checkouts at different paths now get distinct namespaces in all
three fallback locations (`CODEGRAPH_CACHE_DIR`, `%LOCALAPPDATA%`, `~/.cache`);
the basename suffix is kept purely for human readability. `realpath` also
collapses symlinked duplicates of the SAME checkout into one namespace. The
fingerprint gate continues to prevent any stale serve regardless of keying.

### 1.3 Version bump and fingerprint algorithm

`GENERATOR_VERSION` 1.0.1 -> 1.1.0 (meta semantics changed: new
`graph_sha256` field; cache-dir keying changed). `SCHEMA_VERSION`,
`CONFIG_INPUTS`, `FINGERPRINT_ALGORITHM`, and all fingerprint logic are
byte-untouched — the fingerprint ALGORITHM is unchanged. The repo-level
fingerprint VALUE differs from the M0-T030 report value only because
`tools/*.py` sources (which are fingerprint inputs) changed in this task.
New repo-level value at this worktree state:

```
21aa77fb90376adc3d11ad88e87b43bdde6f7703a3621a883ce549ae7da275b5
```

### 1.4 --limit in both positions (AS-4, G3/G4 INFO advisory)

The global pre-subcommand `--limit` (dest `limit`, default 40) is unchanged.
Every subparser additionally accepts `--limit` with a DISTINCT dest
(`limit_sub`, default `None`) — the distinct dest avoids the argparse
behavior where a subparser default clobbers an already-parsed global value.
Effective limit = `limit_sub` when given, else the global value; when both
are given the subcommand-level value wins. Default 40 / hard cap 200
(enforced in `emit`) are unchanged.

### 1.5 Selective routing guidance (owner clarification 2, D-005-R092/R096/R101)

Three guidance surfaces, exactly the ones the accepted M0-T030 packet
section H contemplated, adjusted to SELECTIVE routing:

- `tools/code_graph/README.md`: new section "Selective routing (owner
  decision, D-005 amendment 2)" encoding the decision model verbatim-faithfully
  (materially-useful? YES -> graph query -> narrow candidates -> authoritative
  source verification; NO -> normal direct navigation), the owner's full
  SHOULD-prefer list (9 items) and NOT-mandatory list (5 items), the "NEVER
  required on every task" statement, advisory-only + mandatory source
  verification for material conclusions, and the explicit no-token/time-savings
  statement (proven benefit = correctness / completeness / fewer false
  dependency claims; any later savings claim requires evidence).
- `CLAUDE.md`: exactly ONE additive routing-table row (see section 3;
  context budget check PASS below).
- `.claude/skills/start-controlled-task/SKILL.md`: exactly ONE additive
  paragraph (indented continuation of item 3, the packet-completeness item,
  so no other line changed) with the selective decision model, the graph-useful
  cases, the direct-navigation cases, "never required on every task",
  advisory-only, and mandatory source verification. No mandatory-use language.

No hooks, no watchers, no CI changes, no dependencies (stdlib only), no
product-code changes, no reserved expansion surfaces.

## 2. File inventory (complete diff surface)

| file | change |
|---|---|
| `tools/code_graph/generate.py` | `GENERATOR_VERSION` 1.1.0; `default_out_dir` path-hash + basename key; `generate_into` write-order + `graph_sha256` in meta; docstrings for the two changed functions only |
| `tools/code_graph/query.py` | `_read_cache_attempt` integrity verification (new); `load_graph` regenerate/refuse flow; per-subparser `--limit`; module docstring updated to describe the new behavior; `import hashlib`, `import json` (stdlib) |
| `tools/test_code_graph.py` | 7 new tests (section 4 below); `cache_out_dir` helper; `import hashlib`; docstring updated. All 29 pre-existing tests unmodified |
| `tools/code_graph/README.md` | new "Selective routing (owner decision, D-005 amendment 2)" section; freshness section: cache-key description updated to the new `<pathhash12>-<basename>` key, `STALE (...)` message wording, new "Cache integrity" paragraph documenting `graph_sha256` verify-on-load |
| `CLAUDE.md` | exactly one additive routing-table row (verbatim as contracted) |
| `.claude/skills/start-controlled-task/SKILL.md` | exactly one additive paragraph (+ two surrounding blank lines; no other line touched) |
| `project-control/reports/M0-T031-producer-report.md` | this report |

`git diff --stat` (before this report file existed):

```
 .claude/skills/start-controlled-task/SKILL.md |   3 +
 CLAUDE.md                                     |   1 +
 tools/code_graph/README.md                    |  73 ++++++++++++-
 tools/code_graph/generate.py                  |  26 +++--
 tools/code_graph/query.py                     | 146 ++++++++++++++++++-------
 tools/test_code_graph.py                      | 147 +++++++++++++++++++++++++-
 6 files changed, 344 insertions(+), 52 deletions(-)
```

## 3. CLAUDE.md row (AS-7)

Added verbatim as the last row of the existing "On-demand routing" table:

```
| Code navigation (dependency/impact, who-consumes, traces) — selective, advisory | tools/code_graph/README.md |
```

## 4. New tests (all fixture/temp-cache only; 29 existing kept green)

1. `test_meta_records_graph_sha256_of_written_bytes` — meta hash equals sha256 of the actual written `graph.json` bytes.
2. `test_tampered_graph_regenerated_altered_bytes_never_served` (AS-1) — warm temp cache, flip one byte mid-file (`^= 0xFF`), query with UNCHANGED sources: exit 0, `regenerated (cache integrity)`, no `Traceback` in stderr, and the cache again holds the byte-identical ORIGINAL bytes (deterministic rebuild), proving the tampered content cannot appear.
3. `test_tampered_graph_with_no_regen_exits_3` (AS-1) — same tamper + `--no-regen`: exit 3, `STALE (cache integrity)` one-liner, no traceback, no result line served.
4. `test_corrupt_meta_treated_as_stale_no_traceback` (AS-2) — truncate `graph.meta.json` mid-file: `--no-regen` exit 3 with the one-line message; without it, `regenerated (cache integrity)` and a correct answer; stderr traceback-free in both.
5. `test_unreadable_graph_oserror_handled_no_traceback` (AS-2) — replace `graph.json` with a same-named DIRECTORY (raises OSError on read on Windows and POSIX): `--no-regen` exit 3 one-liner; without it the rebuild cannot write over the directory either, so the CLI refuses with the one-line `cache regeneration failed (cache integrity)` and exit 3 — never a traceback.
6. `test_same_basename_checkouts_get_distinct_cache_dirs` (AS-3) — two fixture repos both named `samename` at different temp paths: `default_out_dir` returns DISTINCT dirs (both suffixed `-samename`), and an end-to-end query on each populates its own namespace.
7. `test_limit_accepted_before_and_after_subcommand` (AS-4) — `--limit 2` before and after `find` produce byte-identical stdout (2 results + truncation notice); when both are given the subcommand-level value wins; hard cap 200 still enforced in the post-subcommand position.

## 5. Self-check outputs (pasted verbatim)

### (a) `python tools/test_code_graph.py` — 36 tests (29 existing + 7 new), exit 0

```
test_absolute_py_import_resolves_exact (__main__.CodeGraphTests.test_absolute_py_import_resolves_exact) ... ok
test_artifacts_contain_no_absolute_paths (__main__.CodeGraphTests.test_artifacts_contain_no_absolute_paths) ... ok
test_check_flag_self_proof (__main__.CodeGraphTests.test_check_flag_self_proof) ... ok
test_contract_ref_derived_and_schema_node (__main__.CodeGraphTests.test_contract_ref_derived_and_schema_node) ... ok
test_corrupt_meta_treated_as_stale_no_traceback (__main__.CodeGraphTests.test_corrupt_meta_treated_as_stale_no_traceback) ... ok
test_determinism_two_generations_byte_identical (__main__.CodeGraphTests.test_determinism_two_generations_byte_identical) ... ok
test_every_edge_labeled_and_no_caller_callee (__main__.CodeGraphTests.test_every_edge_labeled_and_no_caller_callee) ... ok
test_external_imports_labeled_external (__main__.CodeGraphTests.test_external_imports_labeled_external) ... ok
test_fingerprint_changes_when_input_changes (__main__.CodeGraphTests.test_fingerprint_changes_when_input_changes) ... ok
test_fingerprint_changes_when_tsconfig_changes (__main__.CodeGraphTests.test_fingerprint_changes_when_tsconfig_changes) ... ok
test_fingerprint_ignores_excluded_dirs_artifacts_and_reports (__main__.CodeGraphTests.test_fingerprint_ignores_excluded_dirs_artifacts_and_reports) ... ok
test_fingerprint_is_crlf_invariant (__main__.CodeGraphTests.test_fingerprint_is_crlf_invariant) ... ok
test_generator_query_tests_import_stdlib_only (__main__.CodeGraphTests.test_generator_query_tests_import_stdlib_only) ... ok
test_is_test_flags (__main__.CodeGraphTests.test_is_test_flags) ... ok
test_limit_accepted_before_and_after_subcommand (__main__.CodeGraphTests.test_limit_accepted_before_and_after_subcommand) ... ok
test_meta_records_graph_sha256_of_written_bytes (__main__.CodeGraphTests.test_meta_records_graph_sha256_of_written_bytes) ... ok
test_query_limit_and_hard_cap (__main__.CodeGraphTests.test_query_limit_and_hard_cap) ... ok
test_query_output_lines_start_with_relpath (__main__.CodeGraphTests.test_query_output_lines_start_with_relpath) ... ok
test_query_upstream_downstream_contracts_path_impact (__main__.CodeGraphTests.test_query_upstream_downstream_contracts_path_impact) ... ok
test_refuses_to_write_inside_repo (__main__.CodeGraphTests.test_refuses_to_write_inside_repo) ... ok
test_relative_py_imports_resolve_exact (__main__.CodeGraphTests.test_relative_py_imports_resolve_exact) ... ok
test_repo_without_tsconfig_deterministic_and_invariants_hold (__main__.CodeGraphTests.test_repo_without_tsconfig_deterministic_and_invariants_hold) ... ok
test_same_basename_checkouts_get_distinct_cache_dirs (__main__.CodeGraphTests.test_same_basename_checkouts_get_distinct_cache_dirs) ... ok
test_sentinel_files_never_indexed_and_exclusions_recorded (__main__.CodeGraphTests.test_sentinel_files_never_indexed_and_exclusions_recorded) ... ok
test_sibling_script_import_resolves (__main__.CodeGraphTests.test_sibling_script_import_resolves) ... ok
test_stale_fingerprint_auto_regenerates (__main__.CodeGraphTests.test_stale_fingerprint_auto_regenerates) ... ok
test_stale_with_no_regen_exits_3 (__main__.CodeGraphTests.test_stale_with_no_regen_exits_3) ... ok
test_symbols_extracted_with_lines (__main__.CodeGraphTests.test_symbols_extracted_with_lines) ... ok
test_tampered_graph_regenerated_altered_bytes_never_served (__main__.CodeGraphTests.test_tampered_graph_regenerated_altered_bytes_never_served) ... ok
test_tampered_graph_with_no_regen_exits_3 (__main__.CodeGraphTests.test_tampered_graph_with_no_regen_exits_3) ... ok
test_ts_alias_resolves_exact (__main__.CodeGraphTests.test_ts_alias_resolves_exact) ... ok
test_ts_dynamic_import_partial (__main__.CodeGraphTests.test_ts_dynamic_import_partial) ... ok
test_ts_star_reexport_partial_named_reexport_exact (__main__.CodeGraphTests.test_ts_star_reexport_partial_named_reexport_exact) ... ok
test_unparseable_tsconfig_falls_back_to_default_no_crash (__main__.CodeGraphTests.test_unparseable_tsconfig_falls_back_to_default_no_crash) ... ok
test_unreadable_graph_oserror_handled_no_traceback (__main__.CodeGraphTests.test_unreadable_graph_oserror_handled_no_traceback) ... ok
test_unresolved_imports_labeled_never_guessed (__main__.CodeGraphTests.test_unresolved_imports_labeled_never_guessed) ... ok

----------------------------------------------------------------------
Ran 36 tests in 6.494s

OK
exit code: 0
```

### (b) `python tools/code_graph/generate.py --repo . --check`

```
determinism check PASS: 2 generations byte-identical (235 input files, fingerprint 21aa77fb90376adc)
```

Full repo-level fingerprint (`generate.compute_source_fingerprint('.')`):

```
21aa77fb90376adc3d11ad88e87b43bdde6f7703a3621a883ce549ae7da275b5
```

The fingerprint ALGORITHM is unchanged (CONFIG_INPUTS / fingerprint logic
byte-untouched); the VALUE differs from M0-T030-era values because
`tools/code_graph/generate.py`, `tools/code_graph/query.py`, and
`tools/test_code_graph.py` — all fingerprint inputs under the `tools` include
root — changed in this task. That is the designed behavior.

### (c) `python tools/context_budget_check.py` — with the CLAUDE.md row added

```
# Context-budget check

## Eager (auto-loaded) project instructions
     7425B   102L  ~ 1824 tok  CLAUDE.md
     1868B    31L  ~  458 tok  .claude/rules/expansion-agent-dispatch-hold.md
  ---- eager total: 9293B  133L  ~2282 tok  (budget 6000 tok)

## Session handoff
  ~1295 tok  docs/SESSION_HANDOFF.md  (budget 4000 tok)

## Historical markers on known stale status docs
  OK   docs/IMPLEMENTATION_STATUS.md
  OK   docs/MASTER_EXECUTION_PLAN.md
  OK   CONTINUE_FROM_CURRENT_STATE_PROMPT.md

## Retired/superseded sections in unconditional rules
  OK - none (no retired/superseded section in an unconditional rule)

## Duplicate current-status task boards
  docs/GENERATIVE_STRATEGY_INTEGRATION_PLAN.md: allowlisted
  docs/LEGAL_CORPUS_COVERAGE_MATRIX.md: allowlisted
  docs/MASTER_EXECUTION_PLAN.md: HISTORICAL-labelled

## Result
PASS - automatic context budget within limits; no stale/duplicate/retired regressions.
```

### (d) Manual live tamper transcript (AS-1, run against THIS repo, scratchpad cache dir)

Step 1 — warm the cache (`CODEGRAPH_CACHE_DIR` pointed at a scratchpad dir):

```
$ CODEGRAPH_CACHE_DIR=<scratchpad>/tamper-demo python tools/code_graph/query.py --repo . find load_graph
regenerated (stale fingerprint)
tools/code_graph/query.py:103 function load_graph
```

Step 2 — flip one byte mid-file in the cached graph.json (helper script;
note the new two-part cache dir key):

```
cache dir key: 4488274a149f-agent-a4389b40579d83c13
flipping byte at offset 585284 (of 1170568): b'i'
tampered graph.json written
```

Step 3 — query again, sources UNCHANGED (fingerprint alone cannot catch
this) -> regenerates, answers from the rebuilt graph:

```
$ CODEGRAPH_CACHE_DIR=<scratchpad>/tamper-demo python tools/code_graph/query.py --repo . find load_graph
regenerated (cache integrity)
tools/code_graph/query.py:103 function load_graph
```

Step 4 — tamper again (same helper output as step 2), then `--no-regen` ->
one-line refusal, exit 3:

```
$ CODEGRAPH_CACHE_DIR=<scratchpad>/tamper-demo python tools/code_graph/query.py --repo . --no-regen find load_graph
STALE (cache integrity): refusing to serve the cached graph
exit code: 3
```

### (e) `git status --porcelain` (before this report file was written)

```
 M .claude/skills/start-controlled-task/SKILL.md
 M CLAUDE.md
 M tools/code_graph/README.md
 M tools/code_graph/generate.py
 M tools/code_graph/query.py
 M tools/test_code_graph.py
?? .claude/settings.local.json
```

`.claude/settings.local.json` is a pre-existing untracked local harness file
already present at session start — NOT part of this task's change set; do not
stage it.

### (f) AS-8 wording grep

`git diff -U0 | grep -i -E "graph-first|graph first|always (use|run|query)|must (use|run|query) the graph|required on every"` matched ONLY the explicit negations required by the owner decision:

```
+   **Code-graph navigation (selective — owner decision, D-005 amendment 2).** ... Graph use is never required on every task; graph output is advisory only, and material conclusions must be verified in the actual source.
+**Graph use is NEVER required on every task.** The owner decision on the
+navigation infrastructure with *selective* use — not universal graph-first.
```

No "graph-first for every task" style wording exists anywhere in the diff.

## 6. Deviations, assumptions, limitations

1. **README received three small accuracy corrections in addition to the new
   selective-routing section** (freshness section: cache path key
   `<repo-root-basename>` -> `<pathhash12>-<basename>`; `STALE` ->
   `STALE (...)` message wording; new "Cache integrity" paragraph). Reason:
   these passages document exactly the behavior this task changed — leaving
   them would ship documentation that contradicts the shipped code. The packet
   lists the whole file as an allowed path with no additive-only constraint
   (that constraint applies to CLAUDE.md and SKILL.md only). Flagging for the
   gate reviewers regardless.
2. **Cold cache keeps the historical `stale fingerprint` classification.** A
   cleanly ABSENT artifact regenerates with `regenerated (stale fingerprint)`
   (a never-generated cache was always "stale"); only a PRESENT but
   unreadable/corrupt/hash-mismatched artifact reports `cache integrity`.
   This preserves the pre-existing message contract asserted by the untouched
   M0-T030 tests while meeting the new integrity semantics.
3. **One-line error messages print to stdout, not stderr**, matching the
   pre-existing `STALE` convention (`test_stale_with_no_regen_exits_3`
   asserts stdout). The new tests assert the one-line message is present on
   stdout AND that stderr contains no `Traceback`.
4. **SKILL.md paragraph placement**: inserted as an indented continuation of
   item 3 (the packet-completeness item) rather than a new numbered item, so
   items 4-7 keep their numbers and the diff is purely additive (3 added
   lines: paragraph + two blank separators).
5. **CLAUDE.md row added verbatim as contracted** — the `tools/code_graph/README.md`
   cell intentionally has no backticks (the contracted row text has none),
   which differs cosmetically from the other rows in that table.
6. **`.encode("utf-8")`** is used for the realpath cache key (identical
   behavior to the contracted bare `.encode()`, whose default is utf-8).
7. Windows-only self-checks: the OSError fixture (same-named directory) is
   asserted by design to raise OSError on both Windows and POSIX
   (`PermissionError` / `IsADirectoryError`, both OSError subclasses), but this
   session executed on Windows only; POSIX execution happens in the existing
   `code-graph` CI job (byte-untouched by this task).
8. LF-only discipline: all edited files were modified in place with the Edit
   tool (no rewrites); artifact writers still emit LF-only bytes (`serialize`
   unchanged; determinism test asserts no CRLF).

## 7. NOT RUN

- `python tools/project_control.py` (any subcommand) — orchestrator authority (ADR-005).
- `git commit` / `git push` / `gh` — orchestrator integrates.
- CI workflows — no CI change was made or needed; the existing `code-graph`
  job runs the same two commands pasted above.

## 8. Requested status

`awaiting_gate` — all AS-1..AS-9 producer-side evidence above; gates
G0/G3/G4/G5 to be run by independent reviewers.
