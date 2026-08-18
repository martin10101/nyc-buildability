# Code Modularity Policy (permanent; M0-T073, D-017-R105..R113)

The detailed source of truth for the repository's permanent modularity and
code-organization rules. The concise entry points — the CLAUDE.md principle, the
AGENTS.md rule, and the auto-loading `.claude/rules/code-architecture.md` — defer
here for depth. Machine enforcement: `tools/modularity_check.py` in CI
(`modularity` job), with `tools/modularity_baseline.json` (reviewed legacy-debt
register) and `tools/modularity_exceptions.json` (explicit, expiring,
path-specific exceptions).

These rules are **permanent repository law**, not initiative-scoped: every future
source-code PR runs the modularity CI check; every future Claude session receives
the concise root instruction; every future Codex review receives the AGENTS.md
rule; the path-scoped rule loads whenever production source is touched.

## 1. First principles

- Design production code around **clear responsibilities and stable module
  boundaries**. A module earns its existence by owning one responsibility.
- **Line count is a warning signal, never by itself proof that architecture is
  bad** — and a passing line count never excuses responsibility mixing, giant
  functions, hidden coupling, or dumping grounds. Reviewers judge the diff;
  the checker only measures.
- Change-reason is the boundary test: code that changes for different reasons
  (domain rule vs storage format vs transport vs presentation) belongs in
  different modules, even when it is currently convenient to co-locate.

## 2. Responsibility and cohesion rules

Separate, whenever they change for different reasons:

| Responsibility | Belongs in |
|---|---|
| Domain logic / deterministic rule computation | pure modules with no I/O |
| Persistence / storage access | repositories or storage adapters |
| Serialization / schema mapping | codecs, (de)serializers, contract mappers |
| External I/O (HTTP, subprocess, filesystem) | clients / gateways / adapters |
| API or CLI wiring | thin route/command layers that call domain code |
| Policy (authorization, limits, gating) | dedicated policy modules |
| Presentation (rendering, formatting, React) | components / presenters |

Do **not** append unrelated behavior to a file merely because it already exists
and is convenient. Before substantially growing any file, inspect its current
size, responsibilities, and dependencies, and ask which module *should* own the
change.

## 3. Size thresholds (measured as SLOC — see §10)

| Threshold | Value | Effect |
|---|---|---|
| Warning | 600 | new modules should normally stay below this; checker reports |
| Justification | 750 | crossing it requires an explicit cohesion justification recorded in review |
| Hard | 1,000 | a NEW handwritten production file above this **fails CI** without a reviewed exception; mandatory architecture-review item |

Grandfathered files (the baseline register, §7) may exist above these values but
may not grow **materially** — more than `max(50 lines, 10%)` over their recorded
size — without a reviewed exception.

Higher-priority signals than raw size: giant functions, high fan-in/fan-out,
mixed responsibilities from §2 in one file, and frequent-change hotspots.

## 4. Function and class complexity guidance

- Prefer functions that fit on one screen and do one thing; extract when a
  function needs section comments to stay navigable.
- A class with more than a handful of public methods, or a module above ~40
  top-level symbols (checker warning), is a boundary-review signal.
- Deep nesting (> 3 levels) and long parameter lists are extraction signals.
- Rule-engine code: one rule family per module; deterministic inputs/outputs;
  no I/O inside rule evaluation.

## 5. Module-boundary examples

- **Python API (services/api)**: `routes/*.py` (wiring only) → `services/*.py`
  (domain) → `repositories/*.py` (storage) → `schemas/*.py` (serialization).
  A route handler that parses, computes, and persists in one body is mixing
  three responsibilities.
- **Deterministic rule engine**: `rules/<family>.py` pure computation;
  `rules/loader.py` sourcing; `rules/provenance.py` citation tracking. Legal
  math never lives in routes or prose-generation code.
- **React / TypeScript (apps/web/src)**: components render; hooks own state
  transitions; `lib/` owns pure domain helpers; API access lives in typed
  client modules. A `.tsx` file that fetches, transforms, and renders is a
  split candidate.
- **Storage**: one adapter per backend concern; migrations are generated
  artifacts and excluded from measurement, never hand-grown as logic.
- **Tooling (tools/)**: one operational concern per script/module; shared logic
  is promoted into a named module with tests, never copy-pasted between tools.

## 6. Public-interface preservation and safe refactoring

When splitting an existing module:

1. Add focused tests around the behavior being moved **before** moving it.
2. Extract into cohesive named modules (never `utils.py` / `helpers.py` /
   `common.ts` dumping grounds).
3. Keep the original import path working as a **thin compatibility facade**
   (re-exporting the moved names) when anything else imports it; deprecate in
   the docstring rather than breaking consumers.
4. Avoid circular dependencies: dependencies point from wiring → domain →
   primitives. If an extraction would create a cycle, the boundary is wrong —
   invert it or introduce an interface module.
5. Run the modularity checker and the module's test suite before submitting a
   checkpoint.

## 7. The reviewed baseline (legacy debt)

`tools/modularity_baseline.json` is the versioned, reviewed register of files
that already exceeded the warning threshold when the policy was adopted (or at a
later approved regeneration). Baseline entries:

- are **reported**, not failed — legacy debt is visible, not punished;
- may not grow materially (§3) without an exception;
- are integrity-protected by a recorded digest — an edited baseline fails the
  check closed;
- can only be regenerated by `--regenerate-baseline --approval-id <id>` backed
  by an unexpired `baseline-regeneration` entry in the exceptions file, and a
  regeneration **never erases live debt**: an entry whose file still exists at
  or above the warning threshold is carried forward at the smaller of its
  recorded and current size.

## 8. Exceptions (explicit, expiring, path-specific)

An exception is a **reviewed** record in `tools/modularity_exceptions.json`
with: exact file `path` (no globs, no directories), `max_lines` ceiling,
`owner`, `reason`, `review_evidence` (PR / gate report), and `expires` (ISO
date). Malformed, expired, broadened, or incorrectly targeted exceptions fail
the check closed. Exceptions are narrow and temporary: renewing one requires
fresh review evidence, not editing the date.

## 9. Exclusions

Measured: handwritten production source only — `services/**`, `tools/**`,
`packages/**` (Python) and `apps/web/src/**` (TS/TSX). Excluded: generated
code, vendored code, lockfiles, schemas, migrations, fixtures, tests, replay
corpora, prompts, and any path containing a recognized generated/vendored
segment (see `EXCLUDED_SEGMENTS` in the checker). Inherently data-driven files
belong in excluded locations, not in production module roots.

## 10. Measurement definition

- **SLOC** = physical lines that are non-blank and not comment-only
  (`#` for Python; `//` and `/* … */` for TS/TSX). Docstrings count (they are
  content); blank and comment-only lines do not.
- **Top-level symbols** = column-0 `def`/`class`/`async def` (Python; reliable)
  or `export`-ed declarations (TS/TSX; approximate) — a warning-only signal.
- Selection comes from `git ls-files` (tracked files only). Output is sorted
  and deterministic; date input for expiry is explicit (`--today`) in tests.

## 11. Avoiding meaningless over-fragmentation

Splitting is for cohesion, ownership, testability, and change isolation — never
to satisfy a number. Do not shatter a cohesive 700-line module into seven
100-line fragments that share mutable state; that trades visible size for
hidden coupling. A file crossing the justification threshold with ONE
responsibility and a recorded justification is healthier than a forced split.
(D-013-R010 states the same rule for the context-intelligence work.)

## 12. How this is measured and enforced

- CI job `modularity` runs `python tools/modularity_check.py --check` on every
  PR and push — new regressions fail; legacy debt is reported.
- `python tools/modularity_check.py --report` prints the census (largest files,
  symbol counts, warnings) without gating.
- Task integration: every production-code task packet answers the seven
  boundary questions (see `/start-controlled-task`); independent code review
  (G3, `/run-quality-gate`) checks the answers against the actual diff.
- Proof tests: `tools/test_modularity_check.py` demonstrates that a focused
  module passes; a new oversized module fails; growth of a grandfathered file
  fails; excluded generated files never fail; a valid exception is narrow and
  temporary; expired/broadened/mistargeted exceptions fail; and baseline
  regeneration cannot silently erase debt.
