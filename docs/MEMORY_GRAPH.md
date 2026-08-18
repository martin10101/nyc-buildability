# Session/task memory graph — closed-schema digests + promotion (M0-T067 Unit D, D-013)

The memory layer of the context-intelligence pipeline: bounded session/task
facts enter as CLOSED-schema digests, every structural link is derived and
grounded by deterministic code, and promotion into the graph store is atomic,
idempotent, replay-safe, and concurrency-safe. Nothing here is model-decided
(D-013-R009) and nothing memory-related is ever committed to Git (R011/R050).

## The digest (D-013-R044) — `tools/memory_digest.py`

- **Closed schema** `1.0.0`: exact allowed field set; an unknown field refuses
  (`closed_schema_violation`). Required fields: `schema_version`,
  content-derived `digest_id` (sha256 over the canonical document without the
  id; a drifted id refuses), `task_id`, `requirement_ids[]`, `files[]`
  (`{path, content_digest|null}` — `path` must be a CANONICAL repo-relative
  POSIX path: no `..`/`.` segments, no absolute/drive paths, no backslashes,
  no doubled slashes, else `file_path_not_canonical`; this is the R044
  "repo-relative canonical paths" constraint and the traversal guard from the
  G3 round-1 finding B1), `agent`, `outcome`, `repo_sha`,
  `source_manifest_fingerprint` (nullable, never fabricated — R051), `branch`,
  `task_index_digest` + `directive_index_digest` (from Unit C
  `AuthoritativeIndexes.digests()`), `resolver_version`/`map_version`/
  `map_digest` (the Unit C ontology stamp), `evidence_refs[]` (bounded),
  `unresolved_links[]`, `advisory_tags[]`; optional bounded `note`
  (≤2000 chars — no transcripts).
- **Agent allowlist** derives from existing repo facts: `.claude/agents/*.md`
  stems + `orchestrator`. **Outcome enum** reconciles with the gate/lifecycle
  vocabulary: `PASS FAIL BLOCKED ACCEPTED SUBMITTED INFO`.
- All validation fails closed with machine-readable codes (R013).

## Grounding (D-013-R047) — `tools/memory_grounding.py`

Existence alone is NEVER enough. Default-deny:

- a **file link** is grounded only by: task packet `allowed_paths`
  (whole-segment prefix), the promotion call's `diff_files`, the digest's own
  `evidence_refs` (EXACT normalized equality — a mere mention/substring never
  grounds; G3 round-1 B1/O1), or an explicit `approved_relations` entry
  (owner-approved). Otherwise `ungrounded_file_link`. A non-canonical path is
  refused here too (`non_canonical_path`, defense-in-depth under the schema
  guard).
- a **requirement link** is grounded only when its directive is cited by the
  digest's task packet `directive_refs` (`ungrounded_requirement_link`
  otherwise — even for requirements that exist in the registry).
- an unreadable task packet fails closed (`task_packet_unreadable`).

## Promotion (D-013-R045/R046/R048) — `tools/memory_graph.py`

Pipeline (pure code): validate → ontology-staleness check → pass 1 (`propose`,
Unit C) → pass 2 (`resolve_proposals`, Unit C — parents derived from the
master plan, directives registry, tree, versioned subsystem map) → grounding →
quarantine-or-promote.

- **Quarantine, never silent**: unresolved links (pass 2) and
  resolved-but-ungrounded or stale links (`stale_file_link` on a claimed
  content digest that no longer matches; `file_digest_unreadable`) are
  recorded under `quarantined_links` with machine-readable reasons and never
  enter `structural_links`. A digest whose ontology stamp is stale
  (`stale_ontology_version`) or whose task cannot be resolved
  (`digest_task_unresolved`) is quarantined WHOLE, with an external record
  under `<store>/digest-quarantine/<digest_id>.json`.
- **Advisory tags are leaves** (R045): validated per-tag at promotion; an
  invalid tag is discarded into `discarded_advisory_tags` with a reason and
  NEVER quarantines an otherwise valid digest (R048).
- **Store**: REUSES the accepted A2 generation store
  (`tools/repo_index_cache.py IndexCache`) under the external base
  `<runtime>/NYCBuildabilityContextIndex/memory-graph/<checkout_key>/` —
  single-writer lock (`concurrent_writer` when held), temp + validate +
  atomic `os.replace` promotion, recovery/quarantine of half-writes,
  in-repo locations refused (`cache_inside_repo`). A crash between the temp
  write and promotion leaves the prior valid generation; replay converges to
  the byte-identical clean-run state (tested with injected crashes).
- **Idempotent by content**: re-promoting an identical digest is
  `already_promoted` (same generation); the same `digest_id` with a different
  resulting node — whether the digest content or the promotion context (e.g.
  a different grounding outcome) changed — fails closed
  (`digest_id_conflict`).
- **Deterministic**: no wall clock anywhere; the same digest + repository
  state promotes to byte-identical generation payloads (fingerprint = sha256
  over the canonical payload).

## CLI

```
python tools/memory_graph.py promote <digest.json> [--diff-file F]...
python tools/memory_graph.py show
```

Exit 0 = promoted/already_promoted; exit 2 = quarantined or refused (a
machine-readable error document is printed).

## Boundaries

- Unit D stores and links facts; it never decides compliance, acceptance, or
  legal meaning, and it never feeds an unbounded dump into any context (the
  ONE compiler selects bounded evidence — R039/R042).
- Repository-intelligence views/status projections over this graph are
  Unit E (M0-T068). The promotion benchmark/runbook is Unit F (M0-T069).
- Tests: `python tools/test_memory_graph.py` (AS-1..AS-6 + crash/concurrency
  edge cases).


## M0-T075 corrections (D-018)

- **Transaction span**: promotion now holds the store's single-writer lock
  across load-current → idempotency/conflict check → mutation → validation →
  generation promotion. Two concurrent valid digests either both survive or
  one receives the explicit `concurrent_writer` refusal and succeeds on
  retry (`promote_digest(..., retries=N)`); a silently lost node is
  structurally impossible (two-writer regression test on file).
- **Real retention**: bounded generation retention runs inside the
  transaction (current + rollback generations preserved).
- **Containment**: memory evidence paths are read only through the shared
  rule in `tools/context_paths.py` (canonical form + real-path containment).
