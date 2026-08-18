# M0-T067 producer report — Unit D: session/task memory graph

Producer: orchestrator (single writer, wt-m0t064, branch
`task/M0-T067-memory-graph`). Stacked on accepted Unit C (M0-T066, merged to
main 1ded78f).

## What was built (allowed_paths only)

1. **`tools/memory_digest.py`** (157 SLOC) — the CLOSED digest schema
   (`1.0.0`, D-013-R044): exact allowed field set (unknown fields refuse),
   content-derived `digest_id` (drifted ids refuse), agent allowlist derived
   from `.claude/agents/*.md` stems + orchestrator, outcome enum reconciled
   with the gate/lifecycle vocabulary, nullable-but-never-fabricated fields
   (R051), bounded note/evidence refs (no transcripts — R011/R050), and
   per-tag advisory judgment used at promotion (R048 separation).
2. **`tools/memory_grounding.py`** (64 SLOC) — default-deny R047 grounding:
   file links grounded only by task `allowed_paths` / promotion `diff_files` /
   digest `evidence_refs` / explicit owner-approved relations; requirement
   links only by the task packet's cited directives; unreadable packet fails
   closed. Existence alone never grounds anything.
3. **`tools/memory_graph.py`** (227 SLOC) — the two-pass promotion pipeline
   (R046): validate → ontology-staleness check → Unit C `propose` (pass 1) →
   Unit C `resolve_proposals` (pass 2, parents DERIVED from authoritative
   indexes + the versioned subsystem map — R045) → grounding → quarantine or
   promote. The store REUSES the accepted A2 `IndexCache` under the external
   `memory-graph` base: single-writer lock, temp + validate + atomic
   `os.replace`, recovery, in-repo refusal — so promotion is atomic,
   idempotent by content, replay-safe, and concurrency-safe (R048) without
   any new storage machinery (R015 Stage-0 reuse). Digest-level quarantine
   records are written externally; link-level quarantine lives in the node
   with machine-readable reasons. Bounded CLI: `promote` / `show`.
4. **`tools/test_memory_graph.py`** (315 SLOC) — 25 tests: executable
   AS-1..AS-6 packs plus crash injection (patched `os.replace`), lock
   contention, idempotency/conflict, staleness, CLI, and graph-extension
   edge cases.
5. **`docs/MEMORY_GRAPH.md`** — the memory-graph contract: schema, grounding
   rules, quarantine semantics, promotion guarantees, storage location, and
   the Unit E/F boundary.

## Key design decisions

- **Reuse over invention** (R015/R026-style): the accepted A2 generation
  store already provides exactly the R048 guarantees; Unit D adds zero new
  locking/atomicity code and inherits its recovery + quarantine behavior.
- **The task packet is the grounding authority** (R047): an unresolvable
  task quarantines the digest whole BEFORE grounding; everything else
  grounds against that packet's scope and citations, default-deny.
- **Ontology binding is mandatory** (R043/R044): every digest must carry the
  current Unit C version stamp; a stale stamp quarantines the digest whole —
  memory can never silently reference a superseded vocabulary.
- **Advisory tags are leaves** (R038/R045/R048): judged per-tag at promotion,
  discarded separately with reasons, never structural, never fatal.
- **Unit E boundary**: no views/status projections; `show` prints only a
  bounded store summary.

## G3 round-1 rework (review FAIL → fixed)

The round-1 independent review found blocking defect **B1** (path traversal:
non-canonical `files[].path` + substring evidence grounding admitted an
out-of-repo structural link). Fixed in round 2 entirely within allowed_paths:
canonical-path enforcement at the schema (`file_path_not_canonical`),
exact-match evidence grounding (substring removed), `non_canonical_path`
defense-in-depth in grounding, Unicode category-C advisory-tag rejection (O4),
clarified conflict message (O3), doc updated (O5). Six regression tests added,
including the reviewer's exact probe reproduced end-to-end. Details:
`M0-T067-coverage-evidence.md`; round-1 report:
`M0-T067-review-FAIL-round1.md`.

## Self-check results (documented_test_commands, round 2)

- `python tools/test_memory_graph.py` → **31 tests OK**.
- `python -m pytest tools/test_memory_graph.py -q` → **31 passed**.
- `python tools/modularity_check.py --check` → **failures 0**.
- `ruff check` (0.13.0, CI-matching) on the four new files → clean.
- Unit C regression: `python tools/test_subsystem_resolver.py` → **21 OK**.

## Scope compliance

- Diff touches ONLY allowed_paths (new files + the packet's own reports).
- All reused accepted modules (`repo_index_cache`, `subsystem_*`,
  `context_pack_io`, A1/A2) are forbidden_paths and untouched (R082 included).

Evidence details: `M0-T067-coverage-evidence.md`; per-requirement map:
`M0-T067-evidence-map.json`.
