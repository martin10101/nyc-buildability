# Code-navigation index (task M0-T030, D-005 V1)

A deterministic, stdlib-only, in-house code-navigation graph for this
repository: a generator (`generate.py`), a bounded query CLI (`query.py`),
and a fixture-based test suite (`tools/test_code_graph.py`). No Graphify, no
hooks, no config changes, no new dependencies, no committed artifacts.

## Trust model — read this first

**The graph is an advisory navigation index, never authoritative truth.**

The intended workflow is always:

1. graph result → 2. likely locations → 3. **read the actual source**.

**Source verification is mandatory** — a graph answer alone is never
sufficient evidence — for anything touching:

- legal semantics (zoning rules, effective dates, provenance),
- security,
- the control plane (`project-control/`, gates, ledger),
- contracts (`packages/contracts/**`),
- dependency impact,
- public interfaces,
- acceptance or gate decisions.

For those questions the graph may only tell you *where to look*; the
decision evidence must come from the source files themselves.

## Honesty labels

Every edge carries a `confidence` label. The generator never guesses: a
relationship it cannot establish syntactically is labeled, not inferred.

| confidence | meaning | examples |
|---|---|---|
| `exact` | A syntactic fact read directly from the parsed source. For imports that resolve inside the indexed tree, the target file is certain. For `resolution: external` edges the *import statement* is the exact fact; the external package itself is not indexed. | `from app.util import helper` resolved to `services/api/app/util.py`; `import react` (external); a Python `class`/`def` or exported TS declaration (symbol nodes carry `confidence: exact`). |
| `derived` | Produced by a documented heuristic, not by parsing an import. Currently only `contract_ref` edges: a file's text contains an exact substring of a contract schema's filename (`property_profile.schema.json`), its stem (`property_profile`), or its `$id`. This is deliberately noisy (a mention in a comment or docstring counts; short stems like `common` over-match — e.g. the word "commonly"); treat every `derived` edge as a *lead*, never a dependency claim. | docstring mentioning `property_profile.schema.json`; a `$ref` between schemas. |
| `partial` | The relationship is real but incompletely characterized without a compiler/runtime. | `export * from './x'` (target module known, re-exported symbol set not enumerable); `import('X')` with a literal specifier (reference certain, load runtime-conditional). |
| `unresolved` | An internal-looking specifier the generator could not resolve inside the indexed tree — including ambiguous dotted specifiers (never guessed) and imports of non-indexed file types (`.css`, `.json` fixtures). The raw specifier is preserved in `specifier` and the edge target is `unresolved:<specifier>`. | `import './globals.css'`; `from app.nonexistent import x`. |

Additional edge fields: `type` (`import`, `reexport`, `dynamic_import`,
`contract_ref`), `from`, `to`, `line` (statement location), `specifier`
(raw source text), `resolution` (`internal` / `external` / `unresolved`).

**V1 emits no caller/callee edges of any kind** (owner clarification 1 —
deferred by design, not a bug). Import/export/contract-touchpoint edges only.

### Per-language resolution semantics

- **Python** (`ast`, per-file): module/class/function/method nodes with
  qualnames and lines. Absolute imports resolve first against the importing
  file's own directory (mirroring `sys.path[0]` for scripts), then against
  the resolution roots `services/api`, `tools`, `packages/contracts`, and the
  repo root. Ambiguous keys are `unresolved`, never guessed. Relative imports
  (`ast.ImportFrom.level`) resolve path-wise against the containing package.
  A specifier whose top segment matches an indexed top-level name but fails
  to resolve is `unresolved`; anything else non-resolving is `external`.
- **TypeScript/TSX** (line-based state machine, **no compiler**): static
  `import ... from`, `export ... from`, side-effect imports, literal
  `import('X')`, and exported declarations (`export const/function/class/
  interface/enum/type/namespace/default`, `export { a as b }`). `@/x`
  resolves via the `paths` alias in `apps/web/tsconfig.json` (default
  `@/* -> apps/web/src/*`); relative specifiers resolve against the file's
  directory trying `.ts`, `.tsx`, `/index.ts`, `/index.tsx`. Bare specifiers
  are external (`@scope/pkg` keeps two segments).

## Freshness: no committed artifact, non-self-referential fingerprint

Artifacts (`graph.json`, `graph.meta.json`) are written **only outside the
repository** and are **never committed**:

1. `--out DIR` if given, else
2. `$CODEGRAPH_CACHE_DIR/<repo-root-basename>/`, else
3. `%LOCALAPPDATA%\nyc-codegraph\<repo-root-basename>\` (Windows) or
   `~/.cache/nyc-codegraph/<repo-root-basename>/` (POSIX).

Why: a committed artifact would go stale on every product commit and either
break unrelated PRs or silently lie. Here, product lanes can never fail CI
because of a stale graph, and staleness is *detected* instead of trusted:
the **source fingerprint** is `sha256` over the relpath-sorted sequence of
`relpath\0sha256(normalized_bytes)\n` for every **input** source file
(`normalized_bytes` = raw bytes with `\r\n` replaced by `\n`, so checkouts
with different line endings fingerprint identically). Generated artifacts,
excluded trees, and report files are **never** fingerprint inputs, so the
graph cannot invalidate itself (no self-referential SHA).

`query.py` recomputes the fingerprint **first on every invocation**. On
mismatch it regenerates in-process and prints `regenerated (stale
fingerprint)`; with `--no-regen` it prints `STALE` and exits 3. A stale
graph never answers silently.

`generate.py --check` proves determinism without any committed artifact: it
runs two fresh generations into temp dirs and fails on any byte divergence.

## Usage

```
# generate (artifacts go to the cache dir, never into the repo)
python tools/code_graph/generate.py --repo .

# determinism self-proof (CI job `code-graph` runs exactly this)
python tools/code_graph/generate.py --repo . --check

# queries (default --limit 40 lines, hard cap 200, never a full dump;
# every line starts with a repo-relative path and :line when known)
python tools/code_graph/query.py find CoverageBadge
python tools/code_graph/query.py file services/api/app/profile/builder.py
python tools/code_graph/query.py module app.profile.builder
python tools/code_graph/query.py upstream services/api/app/profile/builder.py
python tools/code_graph/query.py downstream services/api/app/profile/builder.py
python tools/code_graph/query.py neighbors apps/web/src/lib/api.ts
python tools/code_graph/query.py contracts property_profile
python tools/code_graph/query.py path apps/web/src/app/page.tsx apps/web/src/lib/api.ts
python tools/code_graph/query.py impact services/api/app/config.py --depth 2

# test suite (temp fixtures only)
python tools/test_code_graph.py
```

`path` searches only `exact`-confidence resolved-internal import/reexport
edges ("reliable"); it prints `no reliable path` otherwise. `impact` walks
the downstream (who-imports-it) neighborhood, max 2 hops.

## Indexed inputs and exclusions

Include roots: `services/api` (`**/*.py`), `tools` (`**/*.py`),
`apps/web/src` (`**/*.ts`, `**/*.tsx`), `packages/contracts` (`**/*.py`,
`schemas/**/*.schema.json`, `generated/*.ts`).

Directory names hard-excluded anywhere in the walk (also recorded in
`graph.meta.json`): `.git`, `.claude`, `node_modules`, `.next`, `dist`,
`build`, `coverage`, `__pycache__`, `.pytest_cache`, `.venv`, `venv`,
`.mypy_cache`, `.ruff_cache`, `_quarantine`, `graphify-out`, `.cache`.

Test files (path contains `/tests/`, or basename `test_*.py` / `*.test.ts*`)
carry `is_test: true`.

## Known blind spots (by design, labeled — never inferred)

- **Dynamic imports** with computed specifiers (`import(someVar)`) are not
  extractable; literal dynamic imports are `partial`.
- **Computed re-exports / `export *` symbol sets** are not enumerated
  (`partial`).
- **Type-only nuance**: `import type` is recorded like a normal import; type
  erasure and declaration merging are not modeled.
- **No caller/callee analysis** at all in V1 (owner prohibition).
- **Contract touchpoints are substring heuristics** (`derived`): mentions in
  comments count, short stems over-match; a missing mention proves nothing.
- **String-naive comment scrubbing** in TS: comment markers inside string
  literals can hide or truncate a statement on that line.
- Non-indexed file types (`.css`, `.json` fixtures, `.md`) are `unresolved`
  targets even when the file exists.
- Python `sys.path` manipulation, namespace packages, and import-time magic
  are not modeled; such imports appear `unresolved` or `external`.

When a blind spot matters to your question, fall back to reading source —
that is the designed behavior, not a failure mode.
