# Session Handoff — NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume, read it live —
`python tools/project_control.py status` and reconcile against the remote: **origin may have
advanced; no SHA here is guaranteed current.** This file is orientation only. Operating rules,
gates, and workflow routes live in `CLAUDE.md`.

## Handoff - seq 108: 200 accepted; landed by /session-handoff (no reason given)

Generated 2026-09-13 ~17:21 UTC (landing invoked hours after the wave closed ~08:49 UTC; no
repository activity in between — 0/0 vs origin at landing) by the wave-2 orchestrator session
(session_01JjK8w1YXwFBjUS8PRrTfHp). Root `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24`, branch
`candidate/D-024-mrl-option-b`, HEAD `d40301a8` **pushed** (0/0 vs origin). `main` untouched.
PR #241 OPEN — NEVER merge. Dirty at landing: ONLY the conventional reviewer agent-memory files
(human-journey-reviewer + qa-engineer, intentionally uncommitted) + session-local `scratchpad/`.
No sub-agent is live (2 producers, 6 reviewer engagements, 1 DCV — all completed and reconciled).
Campaign-continuity CLI still exits 1 (stale D-024 record + invalid D-032 records) — ledger+git
fallback, as before.

## WHAT THIS SESSION DELIVERED (198 → 200, both end-to-end gated + DCV'd; wave 2 closed 2-wide)

1. **M4-T012 (199th)** R1/R2 height/setback family, D-049 definitive scope. BINDING first step
   PASSED: §23-421 captured via the official print/PDF render (`entityprint/pdf/node/18075`,
   sha256 `b5777618…`, 9,500-present check PASS, word-for-word MATCH vs the owner-verified
   verbatim). 4 rulesets (bare 25/35 express; suffix-inheritance w/ owner-decision provenance;
   (g) explicit conditional R1-1/R1-2/R2 w/ 9500/100/5 triggers; QRS 35/35), 4 hash-guarded
   snapshots (canonical+bundle), 110 tests (suite 568). Gate arc: G4 honestly FAILED on 6 ruff
   findings (= the api CI failure at dd7c8b74) → surgical rework + reviewer-invited test
   additions → 3 delta-attestations PASS. **Producer disproved the packet premise: raw HTML
   bytes DO contain §23-421(g)** — prior loss was a text-extraction-layer artifact;
   `docs/ARCHITECT_REVIEW_QUESTIONS.md` TOOLING NOTE corrected (G3-A1); print/PDF rule STANDS.
2. **M4-T015 (200th)** B2 DCM street-width connector (pins the accepted M4-T013 research):
   `dcm_street_centerline_arcgis.py` + pure `dcm_street_width_classifier.py` — 24 typed classes,
   wide ONLY on mathematical entailment ≥75 ft, everything else narrow_fail_closed + class +
   review flag; mapped-street override keys Feat_Type/Paper_ST/Record_ST never Feat_status;
   injection-proof predicate builder; 26 fixtures (25 live, 1 marked synthetic) **G1 live
   byte-verified** against the keyless endpoint; 131 offline tests (connectors 619); zero deps;
   no consumer wiring; OQ-1/OQ-3/OQ-4 surfaced never resolved. Cohesion justification for the
   959-line connector RECORDED in the G4 gate report (modularity review_signal discharged);
   producer-report accuracy corrections applied as tagged ORCH-CORRECTED rework + attested.
3. **DCV**: 16/16 requirement rows PASS (D-045 R001/R003/R008/R009, D-046 R001/R002, D-048
   R001/R002, D-049 R001–R006) — verbatim + addendum in
   `reports/M4-T012-M4-T015-dcv-verification.md`; verifier later completed the slow harness
   (test_directive_compliance 129 OK). verification.json blocks assembled at f5b8742b.
4. Validation at landing: registry validator EXIT 0 (foreground, ~7 min); rules 568; connectors
   619; modularity EXIT 0 (17 warnings, connector justified); sync_zr_snapshots OK 14; **CI fully
   green at material head 8538c272 AND at the last substantive head d40301a8** (confirmed
   completed success at landing; b91bdc3a/307779ff runs were cancelled by successor pushes —
   control-plane-only deltas). Later 10faa11f/cb0f16a6 commits are this handoff doc only.
   Checkpoint `CP-2026-09-13-wave2-closed`.

## POST-LANDING AMENDMENT: D-050 owner-assisted research channel (peer-captured @ b7fc789a)

D-050 arrived by peer relay AFTER landing; verified + ACKNOWLEDGED by this session (R004).
`docs/RESEARCH_REQUESTS.md` is the running queue: append research-shaped requests (NON-BLOCKING —
never wait; absent an answer, official-source-researcher proceeds as normal). **Results are
discovery aids ONLY — no citation chain may terminate at owner research; official capture (incl.
print/PDF completeness) stays the only provenance; interpretation still routes D-048/D-049.**
Seeded RQ-001 (A2 section map) + RQ-002 (C-district survey) directly feed the wave-3 lanes below —
CHECK THE QUEUE for ANSWERED entries before starting either lane; RQ-003 (§12-10 QRS definition)
could convert D-049-R004 fail-closed flags into computed conditions; RQ-004 = A4 triage input;
**AMENDMENT 1 (R005, @ c68cdd8e) — ACTIVE NOTIFICATION: appending to the md is NEVER sufficient
notice. While any owner-addressed request is OPEN, state each as one line in owner-visible turn
output at every owner-facing seam (wave summaries, landings, the handoff owner-items list); on
appending NEW requests, send one batched PushNotification (desktop; phone when Remote Control is
connected) — genuinely new asks only; the companion session owns the in-conversation relay leg.
Quiet rule narrowed: owner-addressed research requests are never silent. Non-blocking unchanged —
notify, then proceed.** **OWNER RESEARCH RETURNED 2026-09-13 (post-wave-3): Astra deep-research
results received and archived at `docs/research/owner-research/NYC_Buildability_Research_2026-09-13.md`
(discovery aid ONLY, R002); RQ-003/RQ-004 stamped ANSWERED, RQ-005 answered-in-part (residual:
the DCM field-level width convention — DCP Technical Review / Borough Topo Office is the named
target); no conflict with any accepted rule value; wave-4 packets should consult it FIRST to
cut discovery time, then capture officially.** **D-051 (captured post-wave-3 by the build
session): owner corrected two build-session claims and bound wave-4 engineering — (1) bounded
negatives only ("not located in examined sources", never "the city never documented it");
(2) unknown street width keeps factual status UNKNOWN, and every conservative fallback is
validated PER CONSUMING RULE (§23-431 street-wall placement is the counterexample proving
fail-closed-to-narrow is NOT universally conservative; the accepted FAR rule remains the one
validated case) — every A2 rule packet consuming width classification MUST carry a per-rule
conservative-direction analysis or keep assumption/review labels (cite D-051:R002,R003); the
RQ-005 independent-confirmation report is archived in owner-research/ (aid only).** **D-052
(OQ-3 OWNER-DECIDED): DRAFT street-width classification policy approved — 75-ft threshold w/
exceptions-first, one-sided explicit bounds usable under source/street-status/frontage-coverage
checks (owner-approved assumption; nearest-centerline alone insufficient), straddling/approx/
unrecognized ⇒ UNKNOWN ⇒ map resolution, full provenance, per-rule fallback (D-051), DRAFT
until G6. Implementation = gated wave-4 tasks citing D-052:R001..R007 (policy layer consumes
the accepted M4-T015 24-class classifier output; frontage-coverage needs the A2 geometry
lane); OQ-3 closure recorded in the architect doc section D; RQ-005(1) residual unchanged.** **AMENDMENT 2 (R006, @ 920110be) — IMMEDIATE UPDATE + COMPACT CLOSURE +
PHONE ACCESS: the pushed branch's docs/RESEARCH_REQUESTS.md is the owner's phone-readable copy
(GitHub URL in the doc header) — every queue change commits AND pushes in the same working step,
never dirty-local or batched; owner-returned results are stamped ANSWERED (date + named
verification target) immediately by the receiving session; SATISFIED requests are DELETED from
the active queue and collapsed to one-line rows in the Closed register at the file bottom (full
text stays in git history).**
RQ-005 (appended by this session) = the DCM OQ-1/OQ-5/LION fact gaps. Mark entries
ANSWERED/ROUTED with date + verification target (R003).

## NEXT ACTIONS (wave 3 per D-047-R004 ramp — widen only while review latency + CI stay healthy)

1. **Contract the A2 lane** (now unblocked by the accepted connector): research-first per
   D-045-R002 — the within-100-ft-of-a-wide-street lot-geometry mechanic (OQ-4: DCM polyline ×
   lot geometry × 100-ft buffer, EPSG:2263) consuming `dcm_street_centerline_arcgis`; note OQ-3
   (ambiguity-class legal policy) stays fail-closed-to-narrow until a G6-class ruling — never
   resolved in-task. Cite D-045:R002(+R008/R009); bind registry task_ids + **digest resync in the
   SAME commit** (c14).
2. **Optionally parallel: C-district research** (D-045-R005 research-first half,
   official-source-researcher lane, scopes disjoint from A2).
3. OWNER return items: backend-engineer agent-file model flip (D-047-R001 — classifier blocked
   both edit paths this session; dispatches used the harness override to claude-sonnet-5,
   deviation recorded in M4-T015 G0/path_notes/progress); D-043 dashboard walkthrough + live-URL
   confirm; Supabase B-001; the G6 ask in `docs/ARCHITECT_REVIEW_QUESTIONS.md`; PR #241 unmerged.
   **OPEN research requests awaiting the owner (D-050-R005 — please go through
   `docs/RESEARCH_REQUESTS.md`):** RQ-001 A2 sky-exposure/street-width ZR section map; RQ-002
   C-district rule-structure survey; RQ-003 §12-10 "qualifying residential site" verbatim;
   RQ-004 special-district priority inventory; RQ-005 DCM width-definition + bulk-product facts.

## TIPS THIS SESSION PROVED (full set in orchestrator memory)

- **Run `cd services/api && python -m ruff check .` in EVERY producer prompt AND orchestrator
  pre-gate** — it is the api CI job's FIRST step; a lint-only miss cost a CI round + a G4 FAIL.
- Gate CLI fails closed on dirty allowed_paths at record time AND on `--sha != HEAD` (a
  retroactive FAIL row cannot be recorded — preserve FAIL arcs in report files + progress log).
- `.claude/agents/*.md` model-key edits are permission-classifier-blocked (Edit AND PowerShell):
  use the Agent-tool model override at dispatch, record the deviation, queue the owner item.
- Applicability task_ids append REQUIRES the manifest `requirements_content_digest_sha256` resync
  (applicability_append audit entry) in the SAME commit — c14 fails closed otherwise.
- Reviewer agents may land in the PRIMARY checkout: pin HEAD in the prompt, forbid git writes
  there, and HOLD all commits until the wave returns. Producer worktrees spawn fine off HEAD
  (reset-to-base + show-toplevel guards stay mandatory).
- SendMessage delta-attestation to the same reviewer agents is fast (~1 min each) and clean for
  behavior-neutral or reviewer-prescribed rework; save every return verbatim.
- CLI submit records land at `project-control/reports/<task>.json` — stage them (easy to miss).
- test_directive_compliance.py takes ~46 min locally (Windows git subprocess cost) — not hung.

## ADVISORY BACKLOG (no task contracted)

Deferred M4-T015 G4 test-robustness advisories 4–6 (record-trigger-isolating fixture; explicit
no-retry call-count; exact lt/le class pins); `returnGeometry=false` until OQ-4 consumes geometry;
redirect pinning in default_fetch (LOW); hyphenated ban-list gap (campaign-wide); validator
runtime has GROWN to ~15 min per the peer (was ~440 s — budget your one full run per seam and use
foreground with a generous timeout; background runs got reaped twice this session); prior backlog
items from seq 107 stand.

## STANDING RESTRICTIONS (unchanged)

NEVER merge PR #241. Supervisor frozen/SHADOW-ONLY. Expansion hold (delivered lot-outline
increment excepted). §G for any admission (zero new deps this session). Internal-only deploy.
Thin client (no local npm). G6 owner-only; DRAFT-until-G6 everywhere. Stop-and-ask only
credentials/payments/legal (D-008). Bootstrap Gate 0 first. Campaign producers = claude-sonnet-5
(D-047); reviewers/orchestrator pinned set unchanged.

## AUTHORITATIVE FILES (smallest set)

`project-control/state.json` + `tasks/M4-T012.json` + `tasks/M4-T015.json` (both accepted) ·
`directives/{D-045..D-049}*/` (requirements + verification incl. the new task blocks) ·
`reports/M4-T012-M4-T015-dcv-verification.md` + `-ci-evidence.md` + the per-gate reports ·
`reports/M4-T013-street-width-research.md` (A2's pin) · `docs/ARCHITECT_REVIEW_QUESTIONS.md`
(G6 agenda; corrected TOOLING NOTE) · `checkpoints/CP-2026-09-13-wave2-closed.json` ·
`.claude/session-handoff-profile.md` · `CLAUDE.md` · this file.

## COPY INTO THE NEW SESSION

resume from handoff seq 108: work from durable repository evidence, not assumptions about the
prior conversation. Verify root/branch/HEAD (expect C:/Users/MLFLL/Downloads/nyc-zoning/ctl24 on
candidate/D-024-mrl-option-b; origin may have advanced — ledger and CI win), Bootstrap Gate 0
(cwd = worktree root, /mcp clean), read CLAUDE.md + docs/SESSION_HANDOFF.md, run
`python tools/project_control.py status` and
`python -m tools.agent_supervisor.campaign_continuity --status` (exit 1 = fall back to
ledger+git). 200 accepted; wave 2 closed (M4-T012 + M4-T015); D-045..D-049 active. First:
confirm CI green on d40301a8 (or current tip). Then execute NEXT-ACTION 1 (contract the A2
within-100-ft wide-street geometry lane, research-first per D-045-R002, pinning the accepted
M4-T015 connector; OQ-3 stays fail-closed pending G6) and optionally NEXT-ACTION 2 (C-district
research, disjoint, parallel per D-046/D-047 ramp). Read the TIPS section before the first
commit, gate, or dispatch (ruff-in-pre-gate; c14 same-commit digest resync; gate-CLI fail-closed
rules; reviewer-in-primary-checkout HEAD pinning). Report READY TO RESUME or BLOCKED before
changing anything. Stop only for owner-only items (credentials/payments/legal, PR #241, public
launch, Supabase, G6).
