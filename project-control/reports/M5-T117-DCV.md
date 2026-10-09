# M5-T117 — directive-compliance verification (directive-compliance-verifier "dcv-t117", read-only)

> Transmission history: pinned at ca007dcf, delivered as five SendMessage parts (1/N..5/5) ending with END-OF-REPORT;
> no truncation. Joined verbatim by the orchestrator (transport wrapper tags removed only). Part 1 carries the
> blob-level restamp predicate (seven blobs + identity 4b04fb33) with broad disjoint-peer tolerance.

---

M5-T117 DCV — Part 1/N: RESTAMP PRE-AUTHORIZATION (up front)

PINNED HEAD at start: ca007dcf. All 7 reviewed blobs confirmed present at HEAD via `git ls-tree HEAD`.

BLOB-LEVEL RESTAMP PREDICATE (approved): this verification remains valid at any later HEAD provided the following 7 blobs are byte-identical to what I reviewed (format: name blob-sha, no equals sign):
- rate_limit.py 1091627158f7073bf6e781f998fc014470c3749d
- test_rate_limit.py 2efb09a2f5770ebad645c629e457d5fec2938f0f
- scene_api.py fa6a1181481fce431aa5a2e617f6aa1d4e9d83bb
- test_scene_api.py d0851eab5d87522c768423124a6852a17e5bcba4
- test_dxf_import_api.py fccbf3348b4716e70e59be2f40d928cdc5a9af6e
- test_export_api.py d5500e8d1894a95e3ed2f5164cc03a5286b4d0f1
- M5-T117-producer-report.md 8dd9dc70dd8deb0883a8e2b38dde54cd73ecf6ba
- plus frozen identity content_manifest_sha256 4b04fb33 (reports/M5-T117.json).

DISJOINT-PEER TOLERANCE (broad, explicit): a later HEAD may freely differ from ca007dcf in ALL of: other tasks' files/gates/reports/material (M5-T116 rework, M5-T118, M5-T119, and any new packets); other directives' registry binds and digest resyncs; the orchestrator appending MY verification rows to D-066/D-087 verification.json with digest resyncs + audit entries; DISCOVERY_BACKLOG rows and contract-seam sweep lines; lifecycle-only packet changes (status/progress/gate-record fields) to M5-T117 that do not alter the 7 blobs or the frozen identity above. Any change to one of the 8 pinned identities voids this stamp and requires a fresh review.

Verification of requirement rows follows in subsequent parts.

---

M5-T117 DCV — Part 2/5: IDENTITY, GATES, APPLICABILITY, HARNESS (all reproduced by me)

FROZEN IDENTITY (independently computed via project_control._task_git_identity at HEAD ca007dcf):
identity = 4b04fb332d1e1cee9b609321f48fac89c1862c45baf2801a18d2086cf26923cd, resolved_sha ca007dcf, err=None (all 7 allowed_paths tracked + clean). This EQUALS reports/M5-T117.json content_manifest_sha256 (4b04fb33) AND the G2/G3/G4/G5 gate stamps (each 4b04fb33). MATCH.

APPLICABILITY (directive_registry.load_registry().evaluate_task_refs(task), run by me):
ok=true; applicable_ids == cited_ids == [D-066-R001, D-087-R001, D-087-R002, D-087-R003, D-087-R004, D-087-R006, D-087-R009]; missing_ids=[], invalid_refs=[], unresolved=[]. Applicability EXACTLY equals cited (R005/R007/R011 correctly excluded — their task_ids lists omit M5-T117).

GATES (project-control/gates/M5-T117-*.json) — all PASS, all reviewers independent of producer backend-engineer:
- G0 PASS reviewer orchestrator (administrative) reviewed_sha 920452df
- G2 PASS reviewer orchestrator (self_check) reviewed_sha cf6526e3, manifest 4b04fb33
- G3 PASS reviewer code-reviewer reviewed_sha a120220e, manifest 4b04fb33
- G4 PASS reviewer qa-engineer reviewed_sha a120220e, manifest 4b04fb33
- G5 PASS reviewer security-reviewer reviewed_sha a120220e, manifest 4b04fb33
Required gates {G0,G2,G3,G4,G5} all present + PASS. G2 self-check correctly recorded under orchestrator (CLI rejects producer name).

HARNESS (reproduced locally, cwd services/api):
- `python -m ruff check .` -> All checks passed!
- `python -m pytest tests/resilience tests/scenario/test_scene_api.py tests/drawings/test_dxf_import_api.py tests/cad/test_export_api.py -q` -> 190 passed (matches the cited claim).
- `python tools/test_directive_reminder.py` -> 12 tests OK.
CI at the EXACT reviewed HEAD ca007dcf (run 36107082334): control-plane job (ADR-005; runs test_project_control.py + validate_directive_compliance.py --check + test_directive_reminder.py per ci.yml:432/442/446) = GREEN 3m33s; api/modularity/code-graph/web all GREEN; workflow success; head pushed to origin.
I SKIPPED the local 12-min validate_directive_compliance.py --check: rows settled by green CI control-plane at the verified head + my direct evaluate_task_refs and _task_git_identity. (A local test_project_control.py run produced no output within 300s — grown-registry slowness — so I defer that one to green CI at head.)

Requirement rows follow in Parts 3-4.

---

M5-T117 DCV — Part 3/5: REQUIREMENT ROWS (primary evidence reproduced by me)

D-066-R001 (obligation, navigation block) — SATISFIED. Primary: M5-T117.json inputs[10] carries the CODE-GRAPH NAVIGATION BLOCK naming rate_limit.py's consumers (the 3 route modules + tests/resilience/test_rate_limit.py), the READ-ONLY forbidden neighbors (export_service.py + every app/resilience module), and the instruction `python tools/code_graph/query.py --no-regen impact <path>` before sweeps, graph ADVISORY. G0 report (M5-T117-G0.md:28-29) attests regeneration 844 files/18356 nodes/7841 edges. Per-packet obligation met.

D-087-R001 (obligation, use capacity via normal gated packets) — SATISFIED. Primary: M5-T117 is a fully contracted/claimed/gated ledger packet — G0 PASS at contract seam 920452df ("D-089 wave-3 contract seam: M5-T117", verified ancestor of HEAD); claimed (progress_log claim @920452df, worktree wt-m5t117); required gates G0/G2/G3/G4/G5 all PASS; run as orchestrator-dispatched subagent producer (backend-engineer). No state or gate skipped — capacity added by a disjoint concurrent packet, exactly as the requirement directs.

D-087-R002 (prohibition, no interference / pairwise-disjoint paths, own worktree) — SATISFIED. Primary: G0 report Disjointness table = EMPTY overlap against ALL 19 state.json active_tasks (no filter, DB-057(p)). task.worktree = one isolated worktree C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t117. allowed_paths = exactly 7 files; `git show --stat cf6526e3` touches EXACTLY those 7 (rate_limit.py, test_rate_limit.py, scene_api.py, test_scene_api.py, test_dxf_import_api.py, test_export_api.py, M5-T117-producer-report.md), zero forbidden paths. G3/G4/G5 each independently re-confirm "exactly the 7 allowed_paths, no forbidden path".

Continued in Part 4 (R003/R004/R006/R009).

---

M5-T117 DCV — Part 4/5: REQUIREMENT ROWS (cont.)

D-087-R003 (authorization, 3D scene route) — SATISFIED as scoped. This packet hardens the shared limiter for the 3D scene route and closes its test gaps while the route stays UNMOUNTED. Primary: `git show cf6526e3 -- scene_api.py` = DOCSTRING-ONLY (import refs app.resilience.run_in_job_slot -> app.resilience.rate_limit.run_in_job_slot; SlidingWindowRateLimiter likewise), no code change; test_scene_api.py:200 adds HEAD/OPTIONS to the every-method-404 loop; AST guard test_route_uses_the_shared_limiter_and_slots_only present. app/main.py absent from commit -> route absent from OpenAPI. Built as a normal gated M5 packet (July pack = reference only).

D-087-R004 (authorization, AutoCAD/DXF-import route) — SATISFIED as scoped. Primary: the DXF-import route shares the hardened limiter; tests/drawings/test_dxf_import_api.py:160 adds HEAD/OPTIONS; ast.parse guard at :207. dxf_import_api.py is a forbidden_path and is untouched by cf6526e3; main.py untouched -> route UNMOUNTED.

D-087-R006 (authorization, CAD write/edit/export route) — SATISFIED as scoped. Primary: the CAD-export route shares the hardened limiter; tests/cad/test_export_api.py:122 adds HEAD/OPTIONS; ast.parse guard at :159. export_api.py forbidden_path untouched; main.py untouched -> route UNMOUNTED.

D-087-R009 (prohibition, unchanged boundaries) — SATISFIED. Primary, each reproduced:
- Zero new deps: rate_limit.py import set byte-identical (G5 part 3); requirements.txt/.in ABSENT from cf6526e3 (`git show --stat` empty); CI api-lock-verify + exact-production-install GREEN at head.
- Routes UNMOUNTED: app/main.py absent from commit, imports none of the 3 routers (G5); route tests assert OpenAPI-absence + generic 404.
- Limits/429 shape/deadlines/correlation ids UNCHANGED: scene_api.py docstring-only; SCENE_RATE_LIMIT_MAX=30 untouched; changes live only in the shared limiter's slot-release/sweep/principal logic; G3/G4/G5 confirm behaviour unchanged.
- Existing app/resilience modules untouched: only rate_limit.py edited; breaker/budget/cache/config/fetcher/metrics/retry/transport/__init__ (all forbidden_paths) absent from commit.
- PR #241 never merged: `gh pr view 241` -> state OPEN, mergedAt null (a different task, M5-T002).
- Gates G0-G7 discipline + D-051 fail-closed intact (limiter refuses fail-closed; sweep-skip preserves fail-closed).

Advisories + sweep + findings + verdict in Part 5.

---

M5-T117 DCV — Part 5/5: ADVISORIES, PROHIBITED-ACTION SWEEP, FINDINGS, VERDICT

REVIEWER ADVISORIES — none undercuts a cited requirement:
- G3 (1) strict AST guard fail-closed, (2) 0.05s post-start timing dep, (3) duplicated test helper — all non-blocking, cosmetic/robustness.
- G4 (1) contention tests are positive-guards (GIL), (2) AST blind spot for list/set/Counter — non-blocking; the behavioural 429/shared-limiter tests are the real enforcement.
- G5 A1 whitespace-only principal, A2 50ms timing — INFO.
- PKT-H carry-forwards (48>40 slot sizing, non-empty auth principal, per-route body ceilings = M5-T111 Finding 4): explicitly DEFERRED to the mount packet. These reinforce D-087-R009 (routes stay UNMOUNTED; mounting is PKT-H) rather than weaken it. G5 independently reproduced Findings 1-3 CLOSED with its own harness incl. the old-code leak; G4 reproduced all 5 named mutants + 2 own mutants RED.

PROHIBITED-ACTION SWEEP (all clear):
- Not accepted: task status awaiting_gate.
- No verification row yet: grep M5-T117 in D-087 verification.json = 0, D-066 verification.json = 0.
- Not on main: branch candidate/D-024-mrl-option-b.
- PR #241 untouched: OPEN, unmerged, headRef task/M5-T002-scenario-endpoint (different task).
- No blocker references M5-T117 (grep across project-control/blockers = NONE; open-blocker affects/detail scan = none).

FINDINGS (both observations, non-blocking, no compliance impact):
- F1: your brief said "claimed at ba48acad", but primary evidence (G0 reviewed_sha + progress_log) shows the M5-T117 contract/claim seam is 920452df ("D-089 wave-3 contract seam"); ba48acad is the M5-T115 review-record seam / worktree base, an ancestor of HEAD. G0 recorded at the true contract seam; identity byte-stable; no impact.
- F2: the navigation block says graph "REGENERATED at the wave-1 seam" while G0 says "at this seam" — both cite identical stats 844/18356/7841 (one consistent graph). D-066-R001 packet obligation (embedded block + query.py instruction) satisfied; regeneration attested in G0.

RESULT: every applicable requirement SATISFIED on reproduced primary evidence; zero VIOLATED / UNVERIFIABLE / BLOCKED. Restamp predicate + broad disjoint-peer tolerance stated in Part 1 (8 pinned identities: the 7 blobs + content_manifest 4b04fb33).

M5-T117 DCV VERDICT: PASS 7/7

END-OF-REPORT
