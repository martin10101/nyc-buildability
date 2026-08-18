# M0-T067 independent review — FAIL

> Saved VERBATIM by the orchestrator from the independent read-only reviewer's
> agent-return channel (transport entity-decoding only). Reviewer: fresh
> general-purpose agent (producer = orchestrator ≠ reviewer). Round 1 at
> reviewed HEAD c13eda7. (The reviewer's header names the branch
> "task/M0-T067-context-compiler"; the actual branch is
> `task/M0-T067-memory-graph` — preserved as returned.)

**Reviewed HEAD:** `c13eda7411e2814a09235d82017b5c66fb3cf1d3` on `task/M0-T067-context-compiler` worktree `C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t064` (verified via `git rev-parse --show-toplevel` / `HEAD`). Reviewer is read-only and independent of the producer; no repository file was written (uncommitted `state.json` / `tasks/M0-T067.json` / untracked `reports/M0-T067.json` pre-existed this review and are orchestrator control-plane activity outside the reviewed HEAD).

## Per-item verdicts

**1. SCOPE — PASS.** `git diff --name-only main...HEAD` = 12 files: the 5 code/doc allowed_paths, the 4 allowed report paths, plus `project-control/gates/M0-T067-G0.json`, `project-control/state.json`, `project-control/tasks/M0-T067.json` (the packet's own control-plane records). `git diff main...HEAD -- tools/subsystem_resolver.py tools/subsystem_entities.py tools/subsystem_map.json tools/repo_index_cache.py tools/agent_supervisor/` is **empty**; no `repo_index_*`, `context_pack_*`, or `subsystem_*` file touched (R082 satisfied: `tools/agent_supervisor/**` untouched; it is only imported read-only via `repo_index_cache`).

**2. AS-1 closed schema (R044) — FAIL (one format gap).** The field set is genuinely closed (`closed_schema_violation` on unknown fields, tested), all fields typed, `digest_id` is enforced sha256-over-canonical-doc-minus-id (`digest_id_mismatch` tested), the agent allowlist derives from `.claude/agents/*.md` stems + orchestrator (tested against a 2-file fixture), outcome enum fixed, no silent defaults. **But R044's minimum-field text requires "files[] with repo-relative canonical paths", and `_check_files` (tools/memory_digest.py:104-115) only requires a non-empty string.** Probe (run live): the schema **ACCEPTS** `'services/api/../../../secret.txt'`, an absolute path `'C:/Users/.../secret.txt'`, `'..'`, and `'a//b'`. This is a direct gap in an explicitly named R044 format constraint, and it enables the item-4 finding.

**3. AS-2 derived parents (R045/R046) — PASS.** The digest carries no parent field anywhere (closed schema); every parent (task→milestone via packet+master plan, requirement→directive via registry, path→subsystem via the versioned Unit C map) is derived exclusively in `ents.resolve_proposals` from live authoritative indexes. The two-pass shape is real: `_proposals_from_digest` → Unit C `propose` (normalize/dedupe typed candidates) → `resolve_proposals` (existence + derivation), and unresolvables land in quarantine with reasons. Ontology stamp + index digests are stamped into the promoted node (asserted in AS-2 tests). No model-supplied value can mint a *parent*; see item 4 for the link-value hole.

**4. AS-3 grounding + quarantine (R047) — FAIL (BLOCKING defect confirmed by execution).** The packet's own scenarios hold: an existing-but-out-of-scope file quarantines (`ungrounded_file_link`), unknown requirement (`unknown_requirement_id`), uncited directive (`ungrounded_requirement_link`), stale claimed file digest (`stale_file_link`), stale ontology stamp quarantines the whole digest with an external record, unreadable packet fails closed — all verified by running the tests and reading the logic; nothing enters `structural_links` without a recorded basis. **However, an adversarial probe I executed (temp dirs only) admitted a file OUTSIDE the repository into `structural_links`:**

- Digest path `services/api/../../../secret.txt` (a real file *outside* the fixture repo root): Unit C's `resolve_path` whole-segment prefix match resolves it to subsystem `services/api` (segments `[services, api, ..]…` match prefix `[services, api]`), `(root / value).exists()` passes via OS-level `..` resolution, and grounding admits it — observed promoted node: `{"grounding_basis": "evidence_ref", "kind": "path", "parents": {"subsystem": "services/api"}, "value": "services/api/../../../secret.txt"}`, `quarantined_links: []`. With a claimed `content_digest`, `_file_digest` (tools/memory_graph.py:73-75) **read and verified the out-of-repo file's bytes** and still promoted.
- Two compounding causes, both inside Unit D's own files: (a) the schema accepts non-canonical paths (item 2); (b) `ground_file_link` (tools/memory_grounding.py:69) grounds on `p in ref` — a **substring** match against the digest's *own* `evidence_refs`, i.e. a self-claim fully controlled by the digest author. Worse, with a directory-shaped `allowed_paths` entry (common in real packets), `_prefix_match` would ground the traversal path via *task scope itself*, no evidence self-claim needed.
- Absolute paths are safely quarantined (`no_matching_subsystem_rule`), so only the `..`-embedded form escapes.

This defeats the R047 guarantee against exactly the input R046/R047 exist to police (a crafted/hallucinating extractor digest): a structural link whose value escapes the repository, carrying a derived subsystem parent, enters the graph that Unit E will project. The fix is cheap and entirely within allowed_paths (reject `..`/absolute/non-normalized segments in `_check_files` or before resolution/grounding).

**5. AS-4 promotion guarantees (R048) — PASS.** Promotion genuinely reuses the accepted A2 `IndexCache` (`memory_store` wraps `ric.IndexCache` under a separate external `memory-graph` base; zero new locking/atomicity machinery except the small atomic tmp+`replace` digest-quarantine writer). The crash test is real: `mock.patch.object(ric.os, "replace", side_effect=OSError)` interrupts the actual atomic generation promotion (`os.replace(tmp, existing)` in repo_index_cache.py:270) after the temp write; the lock releases via context manager, `load_current()` stays `None` (prior state intact — a live-pid temp is correctly left for the still-running owner), and replay converges to the byte-identical clean-run fingerprint (asserted). The promotion→pointer crash point is covered by the accepted A2 suite (tools/test_repo_index_cache.py, 13 tests). Idempotency is by content (`already_promoted` with identical generation, 1 node); same `digest_id` with different promotion context raises `digest_id_conflict` fail-closed (tested).

**6. AS-5 advisory separation (R048/R038) — PASS.** Advisory tags are stripped from the stored digest body, judged per-tag at promotion (`judge_advisory_tag`), invalid ones land in `discarded_advisory_tags` with a reason while the digest **promotes** (tested with `"bad\x00tag"`); tags can never be structural links or parents (they never enter `_proposals_from_digest`, and AS-5 asserts none appear in `structural_links`).

**7. AS-6 concurrency + storage (R048/R050/R011) — PASS.** Held `SingleWriterLock` → `concurrent_writer` refusal with store unchanged, then clean promotion after release (tested). In-repo store base → `cache_inside_repo` refusal raised in `memory_store` *before any write* (tested). Quarantine records and generations go only under `cache_base_dir()/memory-graph/<checkout_key>` (LOCALAPPDATA namespace) or explicit temp bases; every test promotes with a temp base; `git status` before/after my full test runs shows zero new repository files. Nothing memory-related is committed. Observation (non-blocking): `_quarantine_digest` writes without holding the writer lock — benign (atomic replace, deterministic identical content), but a divergence from the single-writer discipline worth noting.

**8. TESTS — PASS.** All commands run at HEAD:
- `python tools/test_memory_graph.py` → **Ran 25 tests … OK**, exit 0.
- `python -m pytest tools/test_memory_graph.py -q` → **25 passed**, exit 0.
- `python tools/modularity_check.py --check` → **selected 257 files; failures 0; warnings 4** (all 4 pre-existing, unrelated files), exit 0.
- `ruff check` (ruff **0.13.0**, CI-matching) on the four new files → **All checks passed!**, exit 0.
- `python tools/test_subsystem_resolver.py` (Unit C regression) → **Ran 21 tests … OK**, exit 0.

Tests are real, not vacuous: they assert machine-readable codes, store contents, fingerprint equality across independent stores, and the crash test interrupts the true atomic primitive. Gap: no test covers `..`/absolute/non-canonical `files[].path` — exactly where the blocking defect lives.

**9. DOC + HONESTY — PASS (observations).** `docs/MEMORY_GRAPH.md` matches the code: field list = `_FIELDS` exactly, all error codes exist in code (`closed_schema_violation`, `stale_ontology_version`, `digest_task_unresolved`, `stale_file_link`, `file_digest_unreadable`, `digest_id_conflict`, `concurrent_writer`, `cache_inside_repo`, exit-code semantics), storage path matches `cache_base_dir()+memory-graph+checkout_key`. No token-savings/whole-repo/census overclaims (grep over the five files: zero hits). Evidence map row set **equals** the mechanically applicable set: `evaluate_task_refs` → 29 applicable, 29 rows, missing=[], extra=[]. Observations: (a) producer report says modularity "254 files" vs 257 at HEAD (failures 0 either way — trivial count drift); (b) the doc says a file link is grounded by "the digest's own `evidence_refs`" without disclosing that the match is *substring*, which understates the permissiveness item 4 exploits.

**10. UNIT BOUNDARY — PASS.** No repository-intelligence views/status projections (Unit E) and no benchmark/runbook (Unit F); `show` prints only a bounded store summary (node count, digest ids, generation fingerprint, version).

## Findings

**BLOCKING**
- **B1 (R044/R047, security — path traversal):** `files[].path` is not canonicality-checked (`tools/memory_digest.py:_check_files` accepts `..`, absolute, `a//b`), and `tools/memory_grounding.py:69` grounds on a substring match against digest-author-controlled `evidence_refs`. Demonstrated at runtime: `services/api/../../../secret.txt` — a file **outside** the repository — resolved, grounded (`evidence_ref` basis), had its out-of-repo bytes hashed by `_file_digest`, and entered `structural_links` with `parents.subsystem="services/api"`. With directory-shaped `allowed_paths`, task scope itself would ground the traversal. Violates R044's "repo-relative canonical paths" minimum-field constraint and defeats the R047 quarantine guarantee for crafted extractor input. Fix is confined to allowed_paths (reject `..`/absolute/non-normalized segments at schema validation and/or before grounding; add regression tests).

**Observations (non-blocking)**
- O1: Evidence-ref grounding is self-referential by design (digest-internal strings, not verified artifacts) — packet-sanctioned, but consider exact-token matching and/or verifying refs exist once B1 is fixed.
- O2: `_quarantine_digest` writes outside the single-writer lock (benign, deterministic content, atomic replace).
- O3: Re-promoting an identical digest after control-plane index drift raises `digest_id_conflict` whose message says "different content" (context, not content, changed) — fail-closed and safe, wording slightly misleading.
- O4: `judge_advisory_tag` control-char check misses DEL/Unicode controls (`ord(c) < 32` only).
- O5: Producer-report modularity count 254 vs 257 at HEAD; doc omits the substring semantics of evidence grounding.

## Overall verdict

**FAIL** — one confirmed blocking defect (B1: non-canonical `files[].path` admits an out-of-repo structural link, R044/R047), demonstrated by execution at the reviewed HEAD; all other checklist items pass, all documented test commands pass (25/25, 25 passed, modularity failures 0, ruff clean, Unit C regression 21/21), scope is clean, and the evidence map exactly matches the 29-row mechanically applicable set. Rework is small and confined to `tools/memory_digest.py` / `tools/memory_grounding.py` / `tools/test_memory_graph.py`.
