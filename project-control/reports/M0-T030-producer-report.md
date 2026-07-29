# M0-T030 producer report — in-house code-navigation index (D-005 V1)

Producer: backend-engineer (worktree agent). Status requested: awaiting_gate.
Base commit: 613c4b1 (main). All work done in the producer worktree
`.claude/worktrees/agent-a912bb35ec4613e66` (branch
`worktree-agent-a912bb35ec4613e66`) — see "Deviations" for why this is not
the `M0-T030-codegraph` worktree named in the dispatch.

## File inventory (complete)

| path | change |
|---|---|
| `tools/code_graph/generate.py` | NEW — stdlib-only deterministic extractor (graph.json + graph.meta.json, `--check` determinism self-proof) |
| `tools/code_graph/query.py` | NEW — bounded deterministic query CLI, fingerprint-first freshness |
| `tools/code_graph/README.md` | NEW — trust model, honesty-label table, freshness design, exclusions, blind spots |
| `tools/test_code_graph.py` | NEW — 26 stdlib tests on temp fixture repos only |
| `.github/workflows/ci.yml` | MODIFIED — ONE additive job `code-graph` (18 inserted lines, 0 deletions; verified by `git diff`) |
| `project-control/reports/M0-T030-producer-report.md` | NEW — this report |

NOT produced: `project-control/reports/M0-T030-benchmark.md` (AS-9). Per the
dispatch instruction, the A/B benchmark is the orchestrator's job (producer
must not judge its own answers; correctness verification requires
producer != verifier).

## Design decisions

### Fingerprint algorithm (non-self-referential; AS-3)

`sha256` over the relpath-sorted sequence of
`relpath\0sha256(normalized_bytes)\n` for every INPUT source file, where
`normalized_bytes` = raw bytes with `b"\r\n"` replaced by `b"\n"`
(checkout-invariant across CRLF/LF working trees — the M0-T020 CRLF
byte-identity risk from the task packet). Inputs are exactly the files
selected by the include roots after exclusion pruning; generated artifacts,
excluded trees, and report files are structurally incapable of entering the
fingerprint (artifacts live outside the repo; reports/*.md match no include
pattern). Tests prove: edit input => changes; edit excluded/artifact/report
files => unchanged; CRLF rewrite of an input => unchanged.

### Cache location (no committed artifact; owner clarifications 2 & 9)

`--out DIR` explicit, else `$CODEGRAPH_CACHE_DIR/<repo-root-basename>/`,
else `%LOCALAPPDATA%\nyc-codegraph\<basename>\` (Windows) or
`~/.cache/nyc-codegraph/<basename>/` (POSIX). `generate_into()` refuses
(SystemExit) any out dir that resolves inside the repo root (test-enforced).
Nothing generated is ever committed, so product lanes can never break on a
stale graph and the self-referential-SHA problem cannot arise.
Interpretation note: `CODEGRAPH_CACHE_DIR` is treated as the cache ROOT with
a `<basename>` subdirectory appended (so two checkouts sharing the env var
never collide); documented in README.

### Honesty-label semantics (AS-5)

- **Python** (via `ast`): resolved-internal imports `exact`; external
  packages `exact` with `resolution: external` (the import statement is the
  exact syntactic fact); internal-looking-but-unresolvable and ambiguous
  dotted keys `unresolved` with the raw specifier — never guessed. Relative
  imports resolved path-wise from `ast.ImportFrom.level`. Absolute
  resolution order: importer's own directory (mirrors `sys.path[0]` for
  scripts), then roots `services/api`, `tools`, `packages/contracts`, repo
  root. external-vs-unresolved discrimination is version-independent (top
  segment membership in indexed top-level names, NOT
  `sys.stdlib_module_names`, which varies by interpreter version and would
  break cross-environment reproducibility).
- **TypeScript/TSX** (line-based state machine, no compiler): static
  import/re-export edges `exact` when resolved (`@/` alias from
  `apps/web/tsconfig.json` paths, relative specifiers with
  `.ts/.tsx//index.ts/index.tsx` candidates); bare specifiers `external`;
  internal-looking non-resolving `unresolved`; `export * from` `partial`
  (symbol set not enumerable); literal `import('X')` `partial`
  (runtime-conditional; the packet lists dynamic imports under
  partial/unresolved-by-design); exported declarations are `exact` symbol
  nodes.
- **Contract touchpoints**: `contract_ref` edges are `derived` only — exact
  substring of schema filename, stem, or `$id` in the file text; README
  documents this as a deliberately noisy heuristic (short stems over-match).
- **NO caller/callee edge type exists** (owner clarification 1);
  test-asserted (allowed edge types are exactly
  `import|reexport|dynamic_import|contract_ref`, and no type contains
  call/caller/callee/invoke).

### Exclusions (AS-4)

Directory names pruned anywhere in the walk and recorded in
`graph.meta.json.exclude_dirs`: `.git`, `.claude`, `node_modules`, `.next`,
`dist`, `build`, `coverage`, `__pycache__`, `.pytest_cache`, `.venv`,
`venv`, `.mypy_cache`, `.ruff_cache`, `_quarantine`, `graphify-out`,
`.cache`. Sentinel-planting test proves none are ever indexed (including
`.claude/worktrees` husks — excluded from traversal only, never touched).

### Determinism (AS-2)

All node/edge collections canonically sorted; `json.dumps(sort_keys=True,
indent=1)`; LF-only binary writes; no wall-clock, username, or absolute
path in artifacts (test scans artifacts for the fixture-repo absolute
path). `--check` generates twice into fresh temp dirs and byte-compares —
it never consults a committed or cached artifact.

## Self-check evidence (all run with shell cwd at the worktree root, Python 3.11.9, Windows)

### (a) `python tools/code_graph/generate.py --repo . --check`

```
determinism check PASS: 2 generations byte-identical (235 input files, fingerprint 18d461e2910ab476)

real    0m9.368s
```

(Two full generations in 9.4 s wall — far under the AS-1 120 s budget.)

### (b) `python tools/test_code_graph.py`

```
Ran 26 tests in 4.844s

OK
```

26/26 pass. Coverage includes: determinism byte-identity (+ `--check`
subprocess), fingerprint change/invariance/CRLF-invariance, sentinel
pollution exclusion across 11 excluded trees, every-edge-labeled +
no-caller/callee, relative py imports, absolute py imports, sibling script
imports, unresolved-never-guessed (py + ts), external labeling, `@/` alias,
star-reexport partial vs named-reexport exact, dynamic-import partial,
contract_ref derived, is_test flags, symbol lines, no-absolute-paths in
artifacts, refuse-to-write-inside-repo, query limit + 200 hard cap +
truncation notice, output lines start with relpath, stale auto-regen,
`--no-regen` exit 3 with STALE, subcommand smoke (upstream/contracts/path/
no-reliable-path/impact), stdlib-only import enumeration via AST for
generate.py + query.py + the test file itself.

### (c) Example bounded queries against the real repo

`python tools/code_graph/query.py downstream services/api/app/profile/builder.py` (exit 0):

```
services/api/app/api/v1/properties.py:61 -> services/api/app/profile/builder.py [import/exact] spec=app.profile.builder
services/api/app/api/v1/rule_evaluation.py:53 -> services/api/app/profile/builder.py [import/exact] spec=app.profile.builder
services/api/tests/api/test_properties_v1.py:34 -> services/api/app/profile/builder.py [import/exact] spec=app.profile.builder
services/api/tests/api/test_property_contract.py:45 -> services/api/app/profile/builder.py [import/exact] spec=app.profile.builder
services/api/tests/profile/test_data_semantics.py:38 -> services/api/app/profile/builder.py [import/exact] spec=app.profile.builder
services/api/tests/profile/test_wave_integration.py:46 -> services/api/app/profile/builder.py [import/exact] spec=app.profile.builder
services/api/tests/profile/test_ztldb_crosscheck.py:42 -> services/api/app/profile/builder.py [import/exact] spec=app.profile.builder
services/api/tests/resilience/test_lkg.py:13 -> services/api/app/profile/builder.py [import/exact] spec=app.profile.builder
services/api/tests/resilience/test_staleness.py:21 -> services/api/app/profile/builder.py [import/exact] spec=app.profile.builder
```

`python tools/code_graph/query.py contracts property_profile` (exit 0) —
40 result lines, no truncation (verified: `--limit 200` also returns exactly
40, so the default cap was not silently hiding results). First/last lines:

```
apps/web/src/lib/__tests__/contract-versions.test.ts:33 -> packages/contracts/schemas/v1/property_profile.schema.json [contract_ref/derived] spec=property_profile.schema.json
apps/web/src/lib/contract.ts:6 -> packages/contracts/schemas/v1/property_profile.schema.json [contract_ref/derived] spec=property_profile
apps/web/src/lib/rule-evaluation-contract.ts:10 -> packages/contracts/schemas/v1/property_profile.schema.json [contract_ref/derived] spec=property_profile
apps/web/src/lib/validate-profile.ts:5 -> packages/contracts/schemas/v1/property_profile.schema.json [contract_ref/derived] spec=property_profile
...
services/api/tests/scenario/test_scenario_foundation.py:390 -> packages/contracts/schemas/v1/property_profile.schema.json [contract_ref/derived] spec=property_profile
tools/code_graph/generate.py:631 -> packages/contracts/schemas/v1/property_profile.schema.json [contract_ref/derived] spec=property_profile.schema.json
```

Every output line starts with a repo-relative path and `:line`; all
contract edges honestly labeled `derived`.

### (d) Real-repo `graph.meta.json` counts

```
"input_file_count": 235
"node_counts": {"class": 185, "contract_schema": 9, "external": 49,
                "function": 1703, "method": 396, "py_module": 141,
                "ts_module": 85, "ts_symbol": 339}
"edge_counts": {
  "by_type": {"contract_ref": 259, "dynamic_import": 3, "import": 1229},
  "by_confidence": {"derived": 259, "exact": 1220, "partial": 3, "unresolved": 9},
  "by_language_confidence": {
    "json": {"derived": 26},
    "py":   {"derived": 181, "exact": 983},
    "ts":   {"derived": 52, "exact": 237, "partial": 3, "unresolved": 9}}}
"source_fingerprint": "18d461e2910ab47675a889721fecdb861893033f3be2ae2d6248983b92acb635"
```

The 9 unresolved edges were manually inspected and are honest blind spots,
not resolution bugs: 3 CSS imports (`./globals.css`, `./dashboard.css`) and
6 JSON fixture imports from `apps/web/src/test-support/*` into
`packages/contracts/fixtures/**` — targets genuinely outside the indexed
input set, preserved with their raw specifiers.

### Isolation evidence (AS-10)

`git status --short` after all work:

```
 M .github/workflows/ci.yml
?? .claude/settings.local.json
?? tools/code_graph/
?? tools/test_code_graph.py
```

`git diff --stat` = `.github/workflows/ci.yml | 18 ++++++ (18 insertions,
0 deletions)` — the ci.yml diff is exactly the one added `code-graph` job
(SHA-pinned checkout action copied verbatim from the existing stdlib-only
jobs; no setup-python needed, matching the control-plane/product-map
convention; PyYAML syntax check of the edited file passed locally).
`.claude/settings.local.json` is NOT mine: it pre-existed at session start
(harness-created local settings) and must not be committed with this task.
No product tree, dependency manifest, hook, or control file was touched.

## Deviations from the dispatch spec (disclosed)

1. **Worktree**: the dispatch named `.claude/worktrees/M0-T030-codegraph`,
   but the agent harness hard-confines file writes to this producer's own
   worktree (`agent-a912bb35ec4613e66`, same base commit 613c4b1). Write to
   the M0-T030-codegraph path was refused by the tool harness ("Edit the
   worktree copy of this file instead"). All deliverables therefore live on
   branch `worktree-agent-a912bb35ec4613e66`; content is exactly what the
   spec requires and can be integrated or cherry-picked onto
   `task/M0-T030-codegraph` by the orchestrator.
2. **Truncation marker**: ASCII `...truncated (N more)` instead of the
   Unicode ellipsis in the spec, to avoid Windows cp1252 console encoding
   crashes (stdout is also reconfigured to UTF-8/replace defensively).
3. **`CODEGRAPH_CACHE_DIR`** treated as cache ROOT + `<basename>` subdir
   (collision safety across checkouts); the spec wording was ambiguous.
4. **Literal dynamic imports** are labeled `partial` (not `exact`): the
   reference is syntactic but the load is runtime-conditional, and the
   packet places dynamic imports under partial/unresolved-by-design.
5. **AS-9 benchmark** deliberately not produced (orchestrator-owned per
   dispatch; producer must not self-judge).

## Known limitations (also in README)

- `derived` contract_ref edges are substring heuristics and deliberately
  noisy (e.g. `scenario`/`common` stems over-match; docstring mentions
  count). They are leads, never dependency claims.
- TS comment scrubbing is string-naive; a `//` inside a string literal on
  an import line could truncate that statement's parse.
- `export const a = 1, b = 2` records only the first declarator name.
- Python `sys.path` magic, namespace packages, and computed imports appear
  `unresolved`/`external` by design.
- `path` subcommand traverses only exact-confidence resolved-internal
  import/reexport edges ("reliable"); partial/derived edges never form
  paths.

Nothing failed; nothing else was cut.
