# M5-T032 orchestrator seam evidence (AS-11 live smoke + integration attribution)

Captured by: orchestrator (main session, ADR-005 sole git/evidence runner)
Date: 2026-09-17T07:14:30Z
Task branch head: cbc10397 (material) on `task/M5-T032-address-search-links`
Prior commit 0e6f7b37 = orchestrator packet-repair sync (byte-identical to the ctl24
packet after the 40f8a/1d907 repairs; only `updated_at` ms drift removed). The material
commit is the cherry-target; the packet-sync commit carries no producer content.

## AS-11 dated live smoke (orchestrator-captured, separate from deterministic tests)

All three captured live from this workstation at 2026-09-17T07:14:30Z with curl
(15–20 s deadlines); raw status lines below are verbatim from the transcript.

1. GeoSearch v2 autocomplete — typing simulation `350 Fifth Ave`
   `https://geosearch.planninglabs.nyc/v2/autocomplete?text=350%20Fifth%20Ave`
   → HTTP 200 in 0.25 s, 2 features, both carrying PAD BBLs:
   `350 FIFTH AVENUE, Brooklyn (bbl 3009810111)`, `350 FIFTH AVENUE, Manhattan (bbl 1008350041)`.

2. GeoSearch v2 /search — complete pasted address `350 Fifth Avenue, Manhattan, NY`
   `https://geosearch.planninglabs.nyc/v2/search?text=350%20Fifth%20Avenue%2C%20Manhattan%2C%20NY`
   → HTTP 200 in 0.15 s, 10 features, first = `350 FIFTH AVENUE, New York (bbl 1008350041)`.

3. ZoLa lot page — `https://zola.planning.nyc.gov/bbl/3052960043`
   → HTTP 200 in 0.15 s, no redirect (FINAL_URL identical). Matches the module's
   `ZOLA_LOT_PREFIX = "https://zola.planning.nyc.gov/bbl/"` + validated-BBL construction.

Deterministic web tests do NOT depend on these live results (packet AS-11 wording);
their authority is the web/web-e2e CI on head cbc10397 (recorded separately below when
CI completes).

## Attribution of the working-tree material (Codex REVISE items, closed)

- The 14 web implementation/test files and the producer report were authored by the loop
  worker (claude-opus-4-8) under supervised runs `persistent-local-auto` and
  `persistent-local-36-m5t032`: every file matches S4.1/in_scope_edit APPROVE_ONCE
  entries in the supervisor audit journal (runtime `9aca7075…`, 2026-09-17 05:0x–06:2x UTC).
  The worker's own `git add` attempts were ASK-queued by policy (git writes are never
  AUTO), which is why the tree was uncommitted at review time; the orchestrator captured
  the attributed material as commit cbc10397 per the reviewer's requested route.
- The `project-control/tasks/M5-T032.json` delta the reviewer flagged was the
  orchestrator's run-36 packet repair synced into the worktree copy (field-by-field equal
  to the committed ctl24 packet except a 14 ms `updated_at` drift) — never a producer
  edit. Committed separately as 0e6f7b37 with that attribution.
- The producer report's "worker-reported, uncaptured" background validator run is
  superseded by an orchestrator-run foreground
  `python tools/validate_directive_compliance.py --check` with a captured transcript
  (appended below on completion). The supervisor's earlier 300 s validator timeout stays
  recorded as its own distinct outcome (known contention: the full validator starves
  against a live loop worker on this box; the loop was down for the orchestrator run).

## CI evidence (appended at completion)

- Final verdict, task-branch head **2b440f41** (material cbc10397 + ORCH corrections
  71d4abb3 + e2e-copy correction 2b440f41): workflows **CI -> success, context-budget ->
  success, secret-scan -> success** (GitHub Actions, 2026-09-17 ~08:0x UTC). All 18 CI jobs
  green, including web (lint+typecheck+build), web-e2e (vitest 971/971; Playwright journeys
  113/113 after the typed-copy update), api, control-plane, modularity, dependency gates.
- Convergence record for the intermediate reds (defect inventory before fixes, D-064-era
  method): cluster A control-plane (D-067 manifest amendment shape; fixed on candidate
  d7188b2f, registry validate() 0 errors in 113 s), cluster B web typecheck (3 strict-TS
  test-file errors; [ORCH-CORRECTED] 71d4abb3), cluster C behavior-contract consumers
  (S4 focus-after-remount defect fixed with the file's own nonce-effect pattern; legacy
  provenance-disclosure test and the e2e journey updated to the intended ZoLa-first /
  typed-outcome contracts, with allowed_paths expanded per the producer's routing request).
- Orchestrator foreground validator run: superseded by the control-plane CI job at
  2b440f41 (same validator, clean runner) - green above; the local foreground attempt was
  stopped mid-run and is recorded only as a distinct non-outcome, consistent with the
  producer report's honesty section.
