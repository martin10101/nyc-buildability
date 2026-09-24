# M5-T074 — Directive-compliance verification (directive-compliance-verifier, read-only)

> Transmission history: returned as five SendMessage transmissions from the fresh seq-128 DCV
> (t074-dcv2, dispatched at pinned head ed49b2d8): the up-front restamp pre-authorization,
> then Parts 1/4-4/4 ending with END-OF-REPORT. No truncation; nothing re-requested. Joined
> verbatim in delivery order by the orchestrator (transport only; the "— PART n/4" labels are
> the verifier's own). The verifier ran validate_directive_compliance.py --check ONCE (direct
> exit 0) and did NOT run tools/test_directive_compliance.py (prohibited; CI covers it).

---

M5-T074 DCV — RESTAMP PRE-AUTHORIZATION (up front, as requested). Full per-requirement report follows shortly (local validator + PC regression finishing; CI control-plane already green at the pinned head).

Predicate (blob-level). My forthcoming PASS carries to any later head H' with NO re-review iff at H': (1) `_task_git_identity(M5-T074)` still stamps b98125f1639bfce2ad1b19426a923cfd23f3e9c4cca3f92e2550004758473b5f, AND (2) every blob below is byte-identical:
- services/api/tests/api/test_outline_bridge.py = 55d2b3654a5b840ac76b957d30bde0f3bc6edf57
- project-control/reports/M5-T074-producer-report.md = 747f201b975c1495331e751a9ed05d99fe924604
- project-control/tasks/M5-T074.json = 389a34b3ea77b54ab1928c4f24e9f75300287350
- project-control/reports/M5-T074-evidence-map.json = f3961092d664fb24ab890d7a86f4aec074662d65
- project-control/reports/M5-T074.json = e91fe712ff7994b8b5700e7b7e9291133d38cb49
- gates M5-T074-G0/G2/G3/G4.json = b01bcf8e / e205710c / 0c0bf015 / 25a77aeb
- D-084 requirements.json = e79cea21… ; manifest.json = 98ca27a4… ; source-001.md = f221d36b…

Disjoint-peer tolerance (broad): any number of peer commits may land between this head and the restamp target without voiding the PASS — other tasks' reports/gates/maps/ledger files under project-control/**, other tasks' material under services/** or apps/**, other directives' capture files, handoff docs, and accept seams for other tasks. I do NOT require product dirs empty, and I do NOT require D-084/verification.json unchanged: the orchestrator adding MY M5-T074 verification row there is expected and does not void the predicate. Only a change to a listed blob, or a different identity stamp, voids it (delta re-attestation then).

---

M5-T074 DCV report — PART 1/4: identity, applicability, registry, frozen identity, harness (verdict at Part 4).

HEAD: `git rev-parse HEAD` = ed49b2d8af5fb4783cc3e456e29f78152e921baf (== pin); worktree toplevel C:/Users/MLFLL/Downloads/nyc-zoning/ctl24. Allowed paths clean at HEAD (identity computed require_clean and succeeded).

Applicability (computed by me, not read from packet): DirectiveRegistry('project-control/directives').load().evaluate_task_refs(M5-T074) → {ok:True, applicable_ids:['D-084-R003'], cited_ids:['D-084-R003'], missing:[], invalid:[], unresolved:[]}. Applicable == cited == [D-084-R003]. Packet tasks/M5-T074.json directive_refs=[{D-084:[D-084-R003]}], regime 1.0. M5-T074 is in R003.applicability.task_ids and in NEITHER R001 nor R002 — single-requirement task, correctly cited.

Registry integrity (recomputed):
- source-001.md sha256 = f95ee41169ff90ae7b96a112448c580048a2ebb0bad247e40322d559ca5e8084 (raw == LF-normalized; no CRLF) == manifest.sources[0].content_digest_sha256.
- sha256_text_artifact(requirements.json) = d2baddf50bab601d750e8dc6cbdf9b6b4e91504e90199fb5a1e671b280e85752 == manifest.requirements_content_digest_sha256.
- D-084 in index.json status "active"; manifest.amendments=[] (single source — none to reflect/miss); locked_requirement_ids [R001,R002,R003] all present. The 3 requirements decompose the single owner line "run 3 codex loops" into lane-1/lane-2/lane-3 obligations — no missing/weakened/combined/invented row; R003 is the distinct lane-3 obligation.

Frozen identity (CLI's own fn): project_control._task_git_identity(M5-T074) @HEAD = b98125f1639bfce2ad1b19426a923cfd23f3e9c4cca3f92e2550004758473b5f (err None). Byte-equal to reports/M5-T074.json content_manifest_sha256 (submitted @ reviewed_sha f4a8cbef) AND to content_manifest_sha256 in gates M5-T074-G2/G3/G4.json. Submission identity intact at the pin → accept here won't hit frozen-evidence mismatch.

Harness (mine): validate_directive_compliance.py --check → EXIT 0 (direct exit code, no pipe, ONE run). test_project_control.py → EXIT 0 (all 23 groups incl. S9 claim-enforcement/git-canonical-identity/independent per-task verification, S11 lifecycle acceptance, S12 empty-identity guard). test_directive_reminder.py → EXIT 0 (12). CI control-plane run 35963219466 @ headSha ed49b2d8 (== pin): conclusion success; job control-plane success incl. steps project-control regression, directive-compliance registry validation, validator+adversarial, reminder-hook, reviewer-guard, MCP default-deny — all success; api/web-e2e/modularity all success. Did NOT run test_directive_compliance.py (hard-prohibited; CI covers it).

---

M5-T074 DCV report — PART 2/4: D-084-R003 primary evidence (lane-3 journal) + requirement row.

R003 (KEEP LANE 3 RUNNING): lane 3 stays live on its M5-T070 increment-2 run (persistent3-local-17), not restarted/displaced; on natural close, harvest + re-feed. Sentinel-bound operational lane-occupancy (producer: orchestrator; required_evidence: run journal + harvest/re-feed seam commits). Grounded in PRIMARY evidence, not the evidence map:

Lane identity: C:\SupervisorController3\autostart-launch.ps1 $CheckoutKey=9df5e3ba4671… (distinct from lane-1 9aca7075…/lane-2 cfdedc11… per M5-T072-DCV). Journal …\NYCBuildabilitySupervisor\9df5e3ba4671…\supervisor_journal.sqlite3 opened mode=ro&immutable=1, table `transitions`:
- run-17 (persistent3-local-17-m5t070): 43 transitions (seq 326-368); TAIL seq 368 POLICY_CHECK→PREFLIGHT trigger cycle_closed @2026-09-23T04:47:33.374Z (cycle 6). Directive captured 04:10Z (manifest.captured_at) — run-17 ran UNDISTURBED to natural close; not restarted/displaced; exactly one cycle_closed. Corroborated by ledger harvest seam 075e9149 "M5-T070 increment 2 (loop-3 run persistent3-local-17, cycle_closed harvest)".
- run-18 (persistent3-local-18-m5t074): 43 transitions (seq 369-411), contiguous after run-17, appears exactly ONCE (fresh/never reused). HEAD seq 369 PREFLIGHT→START_CLAUDE preflight_pass @04:56:03.481Z (~9 min after run-17 close = the between-harvest-and-re-feed seam R003 permits). Checkpoints reference M5-T074 (M5-T074-claimed-producer-cp1…). TAIL seq 411 cycle_closed @06:07:23.048Z (cycle 6) — natural close, unit delivered.
- audit.jsonl run-18: 106 lines; task_id {M5-T074}; branch {task/M5-T074-bridge-500-proof}; target_paths = EXACTLY the two allowed paths (wt-m5t074\services\api\tests\api\test_outline_bridge.py + \project-control\reports\M5-T074-producer-report.md), nothing else; 0 denied events; approval_auto S4.1/in_scope_edit; claude_unit_completed expected_model claude-opus-4-8, model_mismatch false; owner_touch_recorded S13.8 consecutive_revision_loops synchronous_stop (natural cycle-cap close). 11 approval_deferred = S4.3 unclassified-command deferrals, target_paths [] (no writes).
- Launcher: $RunId=persistent3-local-18-m5t074, $TaskPacket=…M5-T074.json, $Repo=wt-m5t074; comment "RE-FEED seq-126 (D-084 lane-3): run-17 cycle_closed … harvested ALL-MATCH at 075e9149; claim seam 419c967a".
- Ledger re-feed seam: claim 419c967a (ancestor of HEAD); unit ea2cdb65; harvest/evidence f4a8cbef.

REQUIREMENT ROW — D-084-R003: SATISFIED. Lane 3 stayed on run-17 undisturbed to its natural close, harvested, re-fed fresh as run-18 on M5-T074 and closed with the unit delivered; frozen identity b98125f1 intact; gates PASS. Evidence is primary (journal + audit + seams), independently reproduced.

---

M5-T074 DCV report — PART 3/4: rulings, gates, prohibited-action sweep.

RULING 1 (G3 F6 — evidence-map R003 row is work-content prose, cites no journal path): The row's LEADING clause ("Lane-3 re-fed and ran after the T070 increment-2 harvest exactly per the directive") DOES argue R003's operative clause (lane-occupancy/re-feed); the remainder describes the DB-045(c) unit that occupied the lane (vehicle/context, not a substitute). G3's critique is FAIR but NON-BLOCKING: R003 is sentinel-bound (status_reason "never a work-content obligation"; producer orchestrator), so its truth is judged on the run journal, which I located and reproduced (Part 2). Test content can neither satisfy nor violate R003 (G3 correct). RESOLVED by DCV grounding; not a gate blocker, does not block acceptance.

RULING 2 ([ORCH-CORRECTED per M5-T074-G3 F5] material_commit → literal ea2cdb65): ACCURATE. `git show ea2cdb65`: subject "M5-T074 unit (loop-3 run persistent3-local-18, cycle_closed)…", name-only = exactly the two allowed paths (report 270/4, test 111/0). It is the CHERRY-PICK material commit; f4a8cbef is the follow-up seam (evidence map + harvest append) — labeling ea2cdb65 (not f4a8cbef) is correct per the material_commit rule. Commits touching allowed paths since claim seam 419c967a = exactly {ea2cdb65, f4a8cbef} (complete/bounded). test_outline_bridge.py blob byte-identical ea2cdb65→HEAD = 55d2b3654a5b840ac76b957d30bde0f3bc6edf57 (== G4's stated blob). Replaced prose "+381/-4, 2 files" = ea2cdb65's two-file aggregate (270+111 add, 4 del) — consistent. Map is OUTSIDE allowed_paths → edit moved NO material identity: _task_git_identity == b98125f1 == all gate/submit stamps. Map now binds the true material identity. RESOLVED, non-blocking. reports/M5-T074-G4-mutant-capture.md (baseline 42; +detail field → 4 live-500 fails via set(body)==_GENERIC_500_KEYS; restore 42) is consistent with the G4 record — the reviewer independently reproduced with a novel field name ("debug_context"→4 failed) + message-tampering mutant, verdict PASS.

GATES: G0 PASS (orchestrator/administrative); G2 PASS (reviewer orchestrator, role self_check — producer qa-engineer, ≠ producer); G3 PASS (code-reviewer, independent); G4 PASS (backend-engineer, independent). Both independent reviewers ≠ producer and ≠ each other; code-reviewer+backend-engineer+directive-compliance-verifier all in packet reviewer_agents. All three records carry content_manifest b98125f1 (== live stamp). Gate reviewed_sha (G2 490c3413; G3/G4 eef20d2c) are HEAD ancestors; reviewers physically reviewed at 9bc68dc7 (G3)/7c6ea4f0→dc5a763e (G4) and attested review-surface blob-stability — binding identity invariant. Standard disjoint-peer-during-wave; not a defect.

PROHIBITED-ACTION SWEEP (each checked by me): NOT accepted — state.json accepted_tasks=256 (last6 T068/069/070/071/072/076), M5-T074 absent. NO verification row — D-084/verification.json has M5-T072+M5-T076 only; mine is first for M5-T074. NOT merged — main=origin/main=d8b3899f; branches containing ea2cdb65 AND ed49b2d8 = only origin/candidate/D-024-mrl-option-b. PR — #241 OPEN (base main, head M5-T002 "DO NOT MERGE", unrelated, untouched); no PR references M5-T074; none on candidate branch. Blockers — none reference M5-T074 (affects/detail); 0 open mention it (_blocker_references won't trip). Nothing deployed/installed/purchased — diff = one test file + one report; zero dependency/lockfile/deploy/config path. I wrote no repo/ledger file; journal read-only.

---

M5-T074 DCV report — PART 4/4: findings, restamp, verdict.

Findings (mine):
- F1 (INFO, affirming; closes G3 F6, non-blocking): R003 run journal exists outside the repo and corroborates run-17 natural close + run-18 fresh re-feed on M5-T074 row-by-row (Part 2).
- F2 (INFO, affirming; resolves G3 F5, non-blocking): material_commit ea2cdb65 accurate; identity motion nil; frozen manifest b98125f1 intact across submit/G2/G3/G4/HEAD.
- F3 (LOW, advisory, non-blocking): the evidence-map R003 row would read cleaner citing the run-id/journal path; documentation-only — the requirement is satisfied on primary evidence.
- F4 (LOW, advisory, non-blocking): packet required_gates G0,G2,G3,G4 vs config.json required_gates_by_task_type["backend"]=G0,G2,G3,G4,G5; explicit --gates honored over the default, and G5 (provenance/new-package) is N/A for a test-only additions change with zero production/dependency paths (allowed_paths = a test file + a report). Same class as the accepted M5-T072 F2 — one line in the accept record.

No VIOLATED, UNVERIFIABLE, or BLOCKED result. The single applicable requirement is SATISFIED on primary evidence reproduced by me (file/field/values in Parts 1-3).

RESTAMP: predicate + broad disjoint-peer tolerance already sent UP FRONT (prior message) — blob-level over the 12 listed blobs + _task_git_identity(M5-T074)==b98125f1639bfce2ad1b19426a923cfd23f3e9c4cca3f92e2550004758473b5f; D-084/verification.json changes (adding my row) and all other peer commits tolerated; only a listed-blob change or a different identity stamp voids it. Unchanged.

Per-requirement:
- D-084-R003 → SATISFIED (lane-3 journal run-17 cycle_closed 04:47:33Z undisturbed + run-18 fresh re-feed on M5-T074 cycle_closed 06:07:23Z unit delivered; audit 2-allowed-paths/0-denied; seams 419c967a/ea2cdb65/f4a8cbef; frozen identity b98125f1; gates G2/G3/G4 PASS).

DCV VERDICT: PASS 1/1

END-OF-REPORT
