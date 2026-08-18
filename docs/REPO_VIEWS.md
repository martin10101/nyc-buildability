# Bounded repository-intelligence views (M0-T068 Unit E, D-013)

Deterministic, bounded retrieval views over the accepted A1/A2 index, the
code graph, the Unit C ontology, and the Unit D memory store — all consumed
read-only. Views feed the ONE context compiler (D-013-R039): they return
structured data and never assemble a prompt, budget, or capacity-filling
content of their own (R042). Advisory navigation: source files remain
authoritative for every material conclusion.

## Coverage modes (D-013-R023) — `tools/repo_views.py`

| mode | view | content |
|---|---|---|
| `census` | `census_view` | every eligible file accounted for as indexed or excluded/failed with per-reason groups (`reconciles`), plus a bounded indexed-file enumeration with a truncation marker |
| `changed` | `changed_view` | this run's deterministic change classification (`added / content_modified / metadata_modified / deleted / renamed` + global invalidators) against the **prior cache generation**; a stated base fingerprint other than the current snapshot **refuses** (`unsupported_base_fingerprint`) — a diff against an unreconstructible base is never guessed |
| `neighborhood` | `neighborhood_view`, `card_view` | bounded in/out dependency edges around a named seed; the card adds kind, module, line, `is_test`, tree existence, and the subsystem — derived ONLY by the versioned Unit C resolver (R045) |
| `deep` | `deep_view` | an exact bounded excerpt of ONE authoritative source with line provenance and a CRLF-normalized content digest; non-canonical (`..`/absolute) or out-of-tree paths refuse |

## The coverage record (D-013-R024)

One builder (`coverage_record`) used by every view emits: repository
identity, snapshot fingerprint, HEAD/branch/`head_detached`, dirty-state
digest, the census (eligible/indexed, excluded-by-reason, failed-by-reason,
stale, reconciles), indexer/schema/config versions **plus the Unit C ontology
stamp** (`resolver_version`/`map_version`/`map_digest`), generator identity,
source-manifest and export digests, graph node/edge counts, `views_version`,
and the EXACT `query_params` and result `limits`.

Cache hit/miss, mode, rebuild reason, reparse/reuse counts, and the
`change_set` counts (added / content_modified / metadata_modified / deleted
(= files removed) / renamed / global invalidators — the R024 "files
reparsed/rebound/removed/invalidated" group) live in a SEPARATE section
labeled `cache_state_non_identity`: they are relative to the prior cache
generation and legitimately differ cold vs warm, so they are excluded from
byte-identity.
The deterministic sections (content + coverage) of `census`/`card`/
`neighborhood`/`deep` are byte-identical across cold and warm runs (tested);
the `changed` view's content is base-relative by design (disclosed by its
`base` label) and is therefore excluded from the byte-identity self-proof.

## Bounds and truncation (R003/R039/R042)

Every list is capped by an explicit limit recorded in the coverage record;
over-limit output is truncated WITH a machine-readable marker
(`{limit, returned, omitted, truncated}`) — never silently.

## Question-oriented retrieval — `tools/repo_views_query.py`

Typed deterministic question forms (no LLM anywhere, R009):
`about_file` (card + advisory memory digests naming the file), `about_task`
(packet summary + advisory memory digests; unreadable packet fails closed),
`about_requirement` (directive parent via the registry + citing tasks),
`who_imports` (bounded downstream importers), `what_changed` (changed view).
Unresolvable inputs return machine-readable no-answers (`seed_not_in_graph`,
`unknown_requirement_id`). Memory-graph reads are ADVISORY and labeled: an
absent or empty store reports `store_unavailable` / `store_empty`, never a
fabricated answer (R051).

## Fail closed (R013)

`index_unavailable` (index cannot be built), `ontology_unavailable`,
`non_canonical_path`, `path_not_in_tree`, `source_unreadable`,
`excerpt_out_of_range`, `task_packet_unreadable` (detail stays
repo-relative), `invalid_task_id` (a task id is a path component: anything
but the exact `M<n>-T<n>` ledger pattern refuses BEFORE any filesystem
access), `unsupported_base_fingerprint`, `missing_question_value`,
`nondeterministic_views` (check self-proof), `view_failed` (catch-all) — all
machine-readable, CLI exit 2. No partial answer is presented as complete.

## CLI

```
python tools/repo_views_query.py census|changed [--since FP]
python tools/repo_views_query.py card SEED | neighborhood SEED
python tools/repo_views_query.py deep PATH START END
python tools/repo_views_query.py ask about_file|about_task|about_requirement|who_imports|what_changed [VALUE]
python tools/repo_views_query.py check     # two-run byte-identity self-proof
```

## Boundaries

- No benchmarks, no runbook, no initiative status projection (Unit F).
- No writes anywhere: views read the index (external cache), the tree, the
  control-plane files, and the external memory store.
- Tests: `python tools/test_repo_views.py` (AS-1..AS-6 + truncation,
  no-answer, fail-closed, cold-vs-warm determinism).


## M0-T075 correction (D-018)

Deep-view and card reads now go through the ONE shared containment rule
(`tools/context_paths.py`): canonical repo-relative form plus real-path
(symlink/junction) containment — an out-of-checkout link target refuses with
`path_escapes_repository` and no error discloses a private absolute path.
