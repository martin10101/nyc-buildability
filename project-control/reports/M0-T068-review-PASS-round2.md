# M0-T068 independent review — round 2 — PASS

> Saved VERBATIM by the orchestrator from the independent read-only reviewer's
> agent-return channel (transport entity-decoding only). Same reviewer as
> round 1 (producer = orchestrator ≠ reviewer); delta re-review of the
> two-finding rework at reviewed HEAD 4cd7274. Round-1 FAIL report:
> `M0-T068-review-FAIL-round1.md`.

Reviewed HEAD: `4cd7274097e5df108420d8e93afd2aaf5d1f4bc3` ("M0-T068 E rework: R024 change_set carrier + about_task task-id validation"), worktree confirmed. Pre-existing uncommitted entries (`state.json`, `tasks/M0-T068.json`, `reports/M0-T068.json`) are orchestrator submit-cycle records, present before my first command and unchanged by my runs.

## (a) Round-1 probes re-executed at the new HEAD

**Finding 2 (traversal) — FIXED.** `ask about_task "../../../probe_outside_secret"` against a REAL out-of-repo JSON (canary tokens only in file content): **exit 2, `invalid_task_id`, content-leak = False** (my first probe's "leak=True" was an artifact — the canary word was in the task-id string I passed, which the error detail rightly echoes; a content-only canary shows zero leak). Backslash variant also refused. The regex guard (`^M\d+-T\d+$`, `repo_views_query.py:89–98`) runs BEFORE any filesystem access. Residual regex nuance: `"M0-T001\n"` passes Python's `$`-before-trailing-newline, then fails closed as `task_packet_unreadable` with a **repo-relative** detail (no absolute path, verified) — charset makes escape impossible; `\Z` would be marginally stricter (observation only). Valid id `M0-T001` still answers correctly.

**Finding 1 (R024 carrier) — FIXED.** Live probe: **all five views** (census/changed/neighborhood/card/deep) carry `change_set` with `deleted` (= files removed), `added`, `content_modified`, `metadata_modified`, `renamed`, `global_invalidators` inside the section labeled `cache_state_non_identity`; `change_set` appears in **no** deterministic coverage section. Cold-vs-warm byte identity re-proven live with the new key: deterministic sections byte-identical while `cache_result` flipped `miss → hit`. CLI `check` → exit 0, `{"check": "PASS", "bytes": 6684}`.

**Observation fix.** `deep 99 120` on a 3-line file now refuses `excerpt_out_of_range` at module and CLI level (exit 2). Inverted in-range request still returns an honest empty excerpt (`returned: 0`) — acceptable.

## (b) Test commands — exact counts

| Command | Result |
|---|---|
| `python tools/test_repo_views.py` | **Ran 26 tests, OK, exit 0** |
| `python -m pytest tools/test_repo_views.py -q` | **26 passed, exit 0** |
| `python tools/modularity_check.py --check` | **selected 259 files; failures 0; warnings 4 (pre-existing), exit 0** |
| `ruff check` (0.13.0) on the three files | **All checks passed, exit 0** |
| `python tools/test_subsystem_resolver.py` | **21 tests, OK, exit 0** |
| `python tools/test_memory_graph.py` | **31 tests, OK, exit 0** |

The 3 new tests are faithful reproductions of my probes: real out-of-repo file with module- AND CLI-level refusal asserting no leak (`assertNotIn("LEAK", stdout)`), repo-relative error detail (`assertNotIn(self.root, detail)`), and the deep out-of-range refusal; AS-2 now asserts `change_set`/`deleted` per view.

## (c) Delta scope and regressions

`git diff 319078b..4cd7274`: the three tool files, `docs/REPO_VIEWS.md`, both producer reports, the evidence map, plus control-plane records of the packet's own lifecycle (`gates/M0-T068-G3.json` — the recorded round-1 FAIL, `reports/M0-T068-review-FAIL-round1.md`, `reports/M0-T068.json`, `state.json`, `tasks/M0-T068.json`) — all within allowed_paths or the packet's control-plane convention. Forbidden-path diff vs main: **empty (0 lines)**, R082 intact. No round-1 PASS item regressed: full suite (all original tests included) green, doc now lists the complete error-code set including `invalid_task_id`/`excerpt_out_of_range`/`missing_question_value`/`nondeterministic_views`/`view_failed`, evidence map re-verified — **27 rows == 27 mechanically applicable IDs, missing []**, R024 row now honestly describes the change_set carrier, producer report modularity count corrected to 259.

## (d) Remaining observations — none blocking

Trailing-newline regex nuance (fails closed anyway); inverted-range empty excerpt (honest marker); `errors="replace"` decode and in-tree symlink following in deep view (Windows-rare, defense-in-depth); potential `view_failed` on non-cp1252 Windows pipes (fail-closed, honest). All cosmetic or defense-in-depth; none violates a directive requirement or acceptance scenario.

## Overall verdict: PASS

Both round-1 blocking findings are genuinely fixed at the reviewed HEAD, verified by independent live probes and by regression tests that encode the exploits; all documented commands pass with the exact counts above; scope is clean and no prior PASS item regressed.
