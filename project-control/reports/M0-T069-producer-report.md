# M0-T069 producer report — Unit F: promotion benchmark, runbook, status projection

Producer: orchestrator (single writer, wt-m0t064, branch
`task/M0-T069-benchmark-runbook`). Stacked on accepted Unit E (M0-T068,
merged to main cf65b78). This is the FINAL D-013 unit.

## What was built (allowed_paths only)

1. **`tools/context_benchmark.py`** — the promotion benchmark: a
   deterministic frozen corpus of the five directive-named task shapes; per
   shape the full R056 case matrix (cold/warm, one-file, dependency, config,
   rename, delete, corrupt cache, interrupted write, concurrent writer);
   reference = clean full rebuild by the UNMODIFIED builder vs new = warm
   incremental over the SAME snapshot at the SAME SHA (confound-removal
   method stated in the report); verdicts compare raw export BYTES. The
   committed report (`M0-T069-benchmark-report.{json,md}`) proves all six
   R059 promotion-evidence minimums over **42 cases, all byte-identical**,
   with honest measured-runtime stats (samples/median/p95, labeled),
   provider token savings **UNMEASURED**, three thresholds proposed with
   rationale, and the promotion decision explicitly **PENDING the
   owner/control-plane decision** (R060). CLI exits 2 if any evidence item
   fails.
2. **`tools/status_projection.py`** — the deterministic R061-R063 initiative
   status projection: unit set from the D-013 verification registry (never
   hand-listed); per-node R063 fields (exact requirement ids, reviewed SHA,
   G0 rollback point, review-report digest, gates, roles, implementation
   files, honest-null branch); R062 status mapping; bounded canonical JSON +
   Markdown/Mermaid rendered FROM the same JSON; generating SHA + Unit C
   index digest stamps; `check` exits 3 when stale. Committed snapshot:
   `M0-T069-status-projection.{json,md}`.
3. **`tools/test_context_benchmark.py` (15 tests) +
   `tools/test_status_projection.py` (8 tests)** — AS-1..AS-6 executable
   packs: full case-matrix presence, byte-identity, zero-reparse,
   stale-node absence, recovery/concurrency, honest-report labels,
   threshold/pending-decision discipline, R063 field census, R062 mapping,
   stale-check exit code, determinism, fail-closed codes.
4. **`docs/CONTEXT_PIPELINE_RUNBOOK.md`** — daily operation commands for
   every accepted layer, the storage map, failure recovery, the full R071
   rollback path (disable-without-delete, restore full build, quarantine
   incompatible generations, committed why-evidence), and the R060
   promotion-decision section.

## Key design decisions

- **Reference without a second builder**: a fresh-cache cold build runs the
  unmodified accepted builder — the strongest honest reference, cross-checked
  against the A1 baseline harness digest per shape.
- **Byte-level verdicts**: export BYTES compared, not digests of digests.
- **Honest non-source behavior**: the control-plane-only change triggers
  A2's documented conservative full rebuild (fingerprint moved, empty
  eligible change set) — reported as such with its fallback reason, never
  misclassified as an incremental-contract violation or hidden.
- **Projection is a view**: labeled, stamped, stale-checkable; regenerate,
  never edit.
- **No self-promotion**: Unit F produces evidence and proposals; the
  promotion decision and initiative completion remain with the
  owner/control plane (R060/R069).

## Self-check results (documented_test_commands)

- `python tools/test_context_benchmark.py` → **15 tests OK**.
- `python tools/test_status_projection.py` → **8 tests OK**.
- `python -m pytest tools/test_context_benchmark.py tools/test_status_projection.py -q` → **23 passed**.
- `python tools/modularity_check.py --check` → **failures 0**.
- `ruff check` (0.13.0, CI-matching) on the four new files → clean.
- Full benchmark: exit 0, 42/42 byte-identical, all six R059 items TRUE.

## Scope compliance

- Diff touches ONLY allowed_paths (new files + the packet's own reports).
- Every consumed accepted module is forbidden_paths and untouched (R082
  included); no behavior flag, config, or accepted artifact changed.

Evidence details: `M0-T069-coverage-evidence.md`; per-requirement map:
`M0-T069-evidence-map.json`; benchmark: `M0-T069-benchmark-report.md`;
projection: `M0-T069-status-projection.md`.
