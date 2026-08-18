# M0-T067 independent review — round 2 — PASS

> Saved VERBATIM by the orchestrator from the independent read-only reviewer's
> agent-return channel (transport entity-decoding only). Same reviewer as
> round 1 (producer = orchestrator ≠ reviewer); delta re-review of the B1
> rework at reviewed HEAD a005439. Round-1 FAIL report:
> `M0-T067-review-FAIL-round1.md`.

**Reviewed HEAD:** `a00543910a01daa2fac8104c5d2246b00e3850a1` (commit "M0-T067 D rework: fix B1 path traversal (canonical files[].path, exact-match evidence grounding) + O3/O4 hardening") in worktree `C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t064`, verified via `git rev-parse --show-toplevel` / `HEAD`. Read-only review; no repository file written (the 3 dirty control-plane JSON files pre-existed this round and are orchestrator lifecycle activity outside the reviewed HEAD).

## (a) Round-1 exploit probes re-executed — all refuse

Re-ran my exact round-1 probes (temp dirs only, real out-of-repo `secret.txt`):

- **P2** (traversal `services/api/../../../secret.txt` + evidence self-claim, round 1: PROMOTED into structural_links) → **refused `file_path_not_canonical`** at schema; store untouched.
- **P2b** (same traversal with a verified content digest of the out-of-repo file, round 1: PROMOTED) → **refused `file_path_not_canonical`**.
- **P3** (absolute path) → now refused at **schema** (`file_path_not_canonical`; round 1 it only quarantined at resolution).
- **P4** schema canonicality: `'services/api/../../../secret.txt'`, absolute drive path, `'..'`, `'a//b'`, `'./a'`, `'/abs'`, `'a/./b'` — **all refuse `file_path_not_canonical`** (round 1: all ACCEPTED). One probe line showing `ACCEPTS 'a\x08'` was my own heredoc-escaping artifact (JSON layer collapsed `\\b` to a backspace char, not a backslash path); the real-backslash case `"a\\b"` is covered by the repo's own regression test `test_non_canonical_file_paths_refuse_at_schema` (8 shapes, passing), and the code check `"\\" in p` / `":" in p` / leading-`/` / empty-`.`-`..` segments is directly visible in `tools/memory_digest.py:is_canonical_repo_path`.
- **Directory-shaped allowed_paths variant** (my round-1 warning): `ground_file_link(trav, facts={"allowed_paths": ["services/api"]}, ...)` → **`{'grounded': False, 'reason': 'non_canonical_path'}`** — and likewise when the traversal is offered via `diff_files` or `approved_relations`. So even bypassing the schema, no grounding basis admits a non-canonical path (defense-in-depth confirmed independently of the upstream schema refusal).
- **P1** (substring self-grounding): `docs/OUTSIDE.md` with evidence ref `"see docs/OUTSIDE.md for details"` → now **quarantined `ungrounded_file_link`** (round 1: grounded via substring); exact-equality ref `"docs/OUTSIDE.md"` still grounds with basis `evidence_ref` (legitimate case preserved). The `p in ref` clause is gone from `tools/memory_grounding.py` (verified in the diff).

The producer's own suite also reproduces my exact end-to-end exploit (`test_reviewer_probe_traversal_digest_never_promotes`, real file outside a real fixture repo root) and asserts refusal + empty store.

## (b) Documented test commands + extras — exact counts

- `python tools/test_memory_graph.py` → **Ran 31 tests … OK**, exit 0 (25 round-1 + 6 new: 5 in `B1PathTraversalRegression`, 1 in `O4UnicodeControlTags`).
- `python -m pytest tools/test_memory_graph.py -q` → **31 passed**, exit 0.
- `python tools/modularity_check.py --check` → **selected 257 files; failures 0; warnings 4** (all pre-existing, unrelated), exit 0.
- `ruff check` (0.13.0) on the four files → **All checks passed!**, exit 0.
- `python tools/test_subsystem_resolver.py` (Unit C regression) → **Ran 21 tests … OK**, exit 0.

## (c) Scope and regression

- Delta `c13eda7..a005439` touches only: the 4 tools allowed_paths, `docs/MEMORY_GRAPH.md`, the two allowed producer reports, and control-plane records (`gates/M0-T067-G3.json`, `state.json`, `tasks/M0-T067.json`, plus `reports/M0-T067-review-FAIL-round1.md` and `reports/M0-T067.json` — orchestrator-written gate/lifecycle records of my round-1 FAIL; same control-plane class as gates/state/task JSON, noted, non-blocking).
- Forbidden paths: `git diff main...HEAD` on `subsystem_*`, `repo_index_cache.py`, `agent_supervisor/` → **empty** (R082 intact).
- No round-1 PASS item regresses: `memory_graph.py` changed only the `digest_id_conflict` message string; digest/grounding changes are purely additive validation; all 25 original tests still pass inside the 31; AS-2/AS-4/AS-5/AS-6 mechanics untouched. Doc now states the canonical-path constraint, exact-match evidence semantics, and corrected conflict wording — matching the code. Evidence map still exactly equals the mechanically applicable set (**29 applicable / 29 rows / missing [] / extra []**).

## (d) Remaining observations — none blocking

- **O1** (substring evidence): fixed — exact normalized equality, tested both directions. The evidence_ref basis remains digest-internal by design (packet-sanctioned); non-blocking.
- **O2** (digest-quarantine writes outside the writer lock): still present; benign (deterministic content, atomic tmp+replace); non-blocking.
- **O3** (conflict message wording): fixed.
- **O4** (Unicode controls in advisory tags): fixed — Unicode category-C rejection, tested with DEL and a zero-width format char (both discarded, digest promotes).
- **O5** (doc/report honesty): fixed — reports now document the round-1 FAIL and rework; counts match reality (31 tests, 257 files).
- New micro-observation: `is_canonical_repo_path` permits C0-control characters *within* a segment name (e.g. `a\x08`). Such a path cannot traverse or escape — it must still exist in-tree, match a subsystem rule, and ground by exact equality — so this is cosmetic hygiene only, non-blocking.

## Overall verdict

**PASS** — B1 is fixed at both the schema (`file_path_not_canonical`) and grounding (`non_canonical_path`, exact-match evidence) layers, my round-1 exploits and the directory-scope variant all refuse when re-executed at the frozen HEAD, all documented test commands pass (31/31, 31 passed, modularity failures 0, ruff clean, Unit C 21/21), scope is clean, forbidden paths untouched, and no round-1 PASS item regressed.
