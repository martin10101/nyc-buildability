# M0-T088 — D-024 B1: telemetry core + primary-session ingestion (shadow mode)

Producer: orchestrator. Date: 2026-08-25. Directive: D-024 (Phase B items 1, 2, 6 of §15-B;
requirements R038/R039/R042/R044/R045/R100/R107 core; full applicable set = 34 ids, evidence map
`M0-T088-evidence-map.json`). Supervisor-freeze qualifying evidence: **D-024-R100** (Phase B,
explicitly listed in D-024) — cited here, in the task packet, and in the commit message.

## What was built

Four new focused modules under `tools/agent_supervisor/` (modularity-checked, 3.11-compatible,
stdlib-only — no dependency change), plus the carried M0-T086 hardening bundle:

1. **`telemetry_records.py`** — typed telemetry records. Every number is a `Measurement` carrying a
   **source/confidence label** (the eight-label §5.2 vocabulary verbatim) AND a **category**
   (`occupancy` / `cumulative` / `estimate` — §5's three kinds, R038). A canonical-name registry
   makes cross-labelling a hard error (an occupancy fact cannot be recorded as cumulative and vice
   versa). Missing usage is `unknown`, **never zero**: a `None` value must carry the `unknown`
   label, and a number may never claim `unknown` (R042). Bools/negatives rejected.
2. **`telemetry_redaction.py`** — the Phase B redaction subsystem, composing the existing D-007
   secret pass (`redaction.py`) with: terminal-escape/control-char stripping; **home-directory
   prefix masking** (`C:\Users\name`, `/home/name`, `/Users/name` → `[HOME]`; repo is PUBLIC —
   G5-S1); prompt-like keys withheld as sha256 digest references (never stored verbatim); free
   text bounded to excerpt + digest (§5.3: summaries and references, not prompts/transcripts).
   Order is deliberate: escapes → paths → secrets → bounding, so truncation can never cut a
   secret in half and leak its head.
3. **`telemetry_journal.py`** — persistence, sanitize-first on every write path:
   - `TelemetrySidecar`: latest-snapshot document; atomic unique-temp + `os.replace` writes
     (interrupted-before-rename leaves the previous complete document; after-rename the new one —
     never a torn file); in-process writer lock + bounded backoff retry for Windows
     `os.replace` contention; 256 KiB bound (fail, don't grow); unreadable snapshot reads as
     `None` (unknown), never as zero.
   - `TelemetryJournal`: bounded JSONL with numbered-generation rotation (`.1`…`.N`, oldest
     dropped); torn final line on read-back is skipped and counted, never invented into a record.
   Distinct from `audit_log.py` by design: the audit log keeps the tamper-evident hash chain;
   the telemetry journal is bounded/rotated/compactable runtime evidence (§5.3).
4. **`telemetry_ingest.py`** — the two B1 ingestion paths (both passive; no model-context
   injection, no `additionalContext`, no worker messages — R037/R044, structurally tested):
   - `ingest_status_line` (§5.1 item 3): primary-session status-line JSON per the official schema
     captured in `capability_matrix_v1.json` (`claude.statusline.primary_payload` +
     `.nullable_fields`). `context_window.*` ingests as **occupancy** ("live context from the most
     recent API response — never lifetime spend"), `cost.*` as **cumulative**; every field
     nullable/feature-detected (null `current_usage` at startup and after compaction → `unknown`;
     a provider-REPORTED 0 stays 0 — reported-zero vs missing kept distinct); session id,
     transcript path, model, version, `exceeds_200k_tokens`, rate-limit payloads preserved as
     attributes (sanitized at write).
   - `UsageAccumulator` (§5.1 item 4): main-loop structured provider usage. Per-step assistant
     usage (label `provider-exact`) and platform-reported cumulative totals (label
     `sdk-cumulative`) live in **separate structures and separate measurement-name families,
     never merged**; assistant messages deduplicate by message ID (bounded LRU, duplicates
     counted); a reported counter that goes backwards is a **counter regression** — counted,
     high-water totals retained, so a reset can never make the run look fresh (16.1); no
     observation → all-`unknown` snapshot; malformed steps → unknown + explicit lower-bound
     detail on the sums.

### Carried hardening bundle (M0-T086 gate round — all four items closed)

- **G4-F1** `capability_probe.classify_flags` now uses word-boundary/token-split matching:
  `--print` no longer matches inside `--print-format`; bare `exec` no longer matches inside
  `execute`; `-`/word chars both terminate a token so hyphenated flags stay atomic. A fresh
  probe body was verified **byte-identical** to the committed fixture (no live classification
  changed — the fix removes future over-claim risk only).
- **G4-F2** `_run` failure branches now unit-tested via monkeypatch: `TimeoutExpired` → unknown,
  `OSError` → unknown, non-zero exit → unknown (+ exit_code/first_line preserved).
- **G4-F3** `main --out` / stdout and `resolve_binaries` dual-install (PATH-scan, case-insensitive
  dedup) now unit-tested.
- **G3-minor** the matrix↔live cross-check is now **generic**: every `measured-live` matrix entry
  (all 11, incl. the two previously uncovered ids) derives its live-fixture verdict and asserts
  `matrix == live` equality; an unmapped measured-live id fails the test with instructions.
- **G5-S1** `probe_meta` now passes through the Phase B redaction subsystem
  (`redact_probe_meta`): resolved binary paths lose their home prefix. The committed live fixture
  was regenerated — **body byte-identical**, `probe_meta` paths now `[HOME]`-masked, zero
  username/home occurrences (regression-tested against the committed artifact).

## What was deliberately NOT built (scope honesty)

`subagentStatusLine` ingestion, Agent SDK event ingestion, lifecycle-hook ingestion, and
transcript-derived fallback are Phase B items 3–5/7 (M0-T089+). The Agent SDK remains
absent-by-policy (R040) — nothing here installs, imports, or requires it; the suite installs
nothing. Actuation stays OFF: no controller consumes these records yet (shadow mode, §15-B item 8
read-only status is a later B task). No live wiring into Claude Code settings/status-line
configuration was added (that is operator/Phase F surface); these modules are the pure
measurement core with its contracts proven by fixtures derived from the official documented
schema (capability_matrix_v1.json, official-docs confidence, fetched 2026-08-25).

## Acceptance scenarios (all reproduced by `tools/test_agent_supervisor_telemetry_core.py`)

- AS-1 label/category typing: eight-label vocabulary verbatim; unknown-never-zero both directions;
  occupancy/cumulative cross-labelling is a hard error; round-trip serialization.
- AS-2 status-line ingestion: complete documented payload; startup shape (null `current_usage`,
  null percentages, reported zeros preserved); post-compaction null; non-dict payload; malformed
  values (string/bool/negative) — all fail to `unknown`, never invent.
- AS-3 provider usage: per-step vs reported-cumulative distinct names/labels/structures; message-ID
  dedup; regression high-water ("never fresh"); empty accumulator all-unknown; malformed/
  unidentified steps counted with lower-bound detail.
- AS-4 atomicity: interrupted before rename → previous snapshot intact; after rename → new
  complete snapshot; 32 overlapping writers → parseable final snapshot equal to one writer's
  payload; oversized snapshot refused with nothing written; unreadable sidecar → `None`.
- AS-5 journal: rotation with bounded generations and byte ceiling; oldest-first read-back;
  torn final line skipped+counted; single over-bound record refused; redact-first proven
  (sensitive key masked, `sk-ant` pattern gone, redaction_count carried).
- AS-6 redaction: ANSI CSI/OSC/control chars stripped; credential patterns + `KEY=value`
  assignments masked; Windows/POSIX home prefixes masked; prompt-like keys digest-withheld;
  5000-char text bounded with digest reference; status-record transcript path `[HOME]`-masked at
  journal write; probe_meta shape-preserving redaction.
- AS-7 structural no-injection: AST scan of all four telemetry modules — no non-docstring string
  contains `additionalContext`/`hookSpecificOutput`; no worker-facing quota/countdown text exists
  anywhere in the telemetry surface (R045: these records are controller-private).
- AS-8 carried bundle: word-boundary positives AND negatives; `_run` three failure branches;
  `--out`/stdout; dual-install resolution; generic all-measured-live matrix==live equality;
  committed-fixture probe_meta redaction.

## Self-check evidence (producer runs, this checkout)

- `python -m pytest tools/test_agent_supervisor_telemetry_core.py tools/test_agent_supervisor_capability_probe.py -q`
  → **65 passed** (49 new + 16 existing probe tests, none modified).
- Full suite `python -m pytest tools/test_agent_supervisor_*.py -q` → **1969 passed, 2 skipped,
  0 failed** (baseline 1920/2/0 + 49 new; freeze §4 ≥1165/0 duty re-established).
- `ruff check` (0.13.0, CI-matched) on all five touched modules + test file → clean.
- `python tools/modularity_check.py --check` → failures 0 (new modules 219/171/216/292 SLOC).
- Fresh probe body vs committed fixture: byte-identical (verified before regenerating the
  fixture; regeneration changed only `probe_meta` — 6 lines).
- Python 3.11.9 local; modules use no 3.12-only syntax.

## Files changed

- `tools/agent_supervisor/telemetry_records.py` (new)
- `tools/agent_supervisor/telemetry_redaction.py` (new)
- `tools/agent_supervisor/telemetry_journal.py` (new)
- `tools/agent_supervisor/telemetry_ingest.py` (new)
- `tools/agent_supervisor/capability_probe.py` (hardened: word-boundary classify_flags,
  probe_meta redaction wiring; body semantics unchanged)
- `tools/agent_supervisor/fixtures/capability_probe_live_2026-08-25.json` (probe_meta redacted;
  body byte-identical)
- `tools/test_agent_supervisor_telemetry_core.py` (new, 49 tests)
- `project-control/reports/M0-T088-telemetry-core.md` (this report)
