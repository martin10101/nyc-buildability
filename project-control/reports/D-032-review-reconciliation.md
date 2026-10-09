# D-032 consolidated assessment — 2026-09-05 review reconciled with current local work

Produced 2026-09-06 by the orchestrator (D-032 R006–R018). Verification performed read-only by two
independent explore agents against ctl24 HEAD (candidate/D-024-mrl-option-b), the PR #241 worktree
(4174a3b2), and main (d8b3899f); full 23-page PDF extracted (evidence IDs R01–R16, G01–G08,
C01–C22). Baseline fact: between reviewed main and the candidate tree, `services/api` + `apps/web`
differ ONLY in `requirements-tools.in/.lock` — every product file cited below is blob-identical to
what the review saw, so its product findings were verified against effectively current code.

## 1. Findings classification (current file/line + commit evidence)

| # | Finding | Verdict | Key current evidence |
|---|---|---|---|
| A | Live spatial integration missing on default path | **CONFIRMED** | `services/api/app/api/v1/rule_evaluation.py:91-92` literal `return None`; `rules/integration.py:470-484` fail-safe → professional review; full real adapter EXISTS (`spatial/adapter.py:143-180` `compose_from_connectors` + 3 connectors, ~5.9k SLOC) with **zero app/ callers** (tests only); PR #241 scenario reuses the same dependency; no DB driver in `requirements.in`. Last touch 2026-07-21/22. |
| B | No persistent customer workflow | **CONFIRMED** | `main.py:6-9` "INTERNAL/DEV ONLY — authentication is NOT enabled"; `supabase/migrations/` contains only `.gitkeep`; `ReviewStore` is a bare Protocol (`review_actions.py:200`), only impl is a test double; 7 review handlers exist but NO router binds them (app has exactly 2 routers); no auth/DB package present. Tracked: B-001 chain, M0-T007/T008, M2-T019 (backlog). |
| C | Legal: 7 drafts / 6 unverified snapshots / FAR-only | **CONFIRMED** (locally checkable half) | 7 rule files all `needs_review` 0.1.0-draft; all 6 snapshots `raw_html_verified: false`; ZERO `.html` capture artifacts in tree; `integration.py:69` hardcodes `TARGET_FAMILY = "residential_far"`; height/setback families load but reach no API path. Mitigation: every result stamped conditional-ceiling disclaimer. |
| C′ | ZR 23-21 footnote/table scoping | **CONFIRMED + prepared for qualified review** | `_zr_snapshots/v1/zr-23-21.snapshot.json:23` stores the 0.60 single-dwelling-unit provision as free-standing prose; table (lines 24-53) truncated to R5A/R5B/R5/R5D rows (section title says "R1 Through R5"); `grep footnote services/api/app` → 0 hits; `0.75` appears nowhere in the corpus; **digest protects `verbatim_excerpt` only** (`rules/snapshots.py:129-139`) — the table sits outside the integrity mechanism. NO legal correction made (per directive); routed to the M3-T002/T003 capture+verification scope and the G6 qualified reviewer. |
| D | Document isolation | **PARTLY RESOLVED** (one review claim wrong; substance right) | CONTRADICTED: extraction does NOT call the decoder directly — single entry `begin_extraction_job` requires `require_isolation()` first (`extraction/routing.py:49,393-402`; `survey_pipeline.py:647-653`). CONFIRMED: probes attest capability PRESENCE only (`isolation.py:22-26`; Landlock ABI version query, `/proc` reads); nothing anywhere installs a ruleset/seccomp filter/no_new_privs/sandboxed worker → on a capable Linux host untrusted PDF bytes parse unrestricted in-process. Self-documented gap (`docs/M2-T015-SB-COVERAGE-MATRIX.md:35`). |
| E1 | PLUTO 26v1 vs 26v2 | **PARTLY RESOLVED** | No hard pin — `pluto_soda.py:112` format regex only, 26v2 passes; `fact_key` proven stable across versions (`test_data_semantics.py:283`). But source registry (`pluto-mappluto.json:53`), 10 fixtures, ~48 test refs still say 26v1 → fixture/doc refresh item (OQ-6 already open). |
| E2 | pip 26.1.2 audit failure | **ALREADY FIXED** (candidate) | `requirements-tools.lock:248` = `pip==26.2` hash-pinned, commit `d0d1129f` 2026-08-27 (PYSEC-2026-3721). Main/origin still 26.1.2 — fix lands with candidate integration; no competing fix created (per review + directive). |
| E3 | npm advisory 503 | **PARTLY RESOLVED** | Bespoke age-gate classifies outage precisely (`dependency_age_gate.mjs:61,350-354,466-471`, tested vs 503); but raw `npm audit` CI steps have no outage-vs-vuln classification, and `ci.yml:163-176` step (b) (`npm audit --json || true` → missing `metadata` → 0 vulns) is a **latent fail-open** saved only by step (a) ordering; Python side has one undifferentiated `AgeGateError`. Hardening proposal below (no gate weakening). |
| E4 | 12s browser timeout vs backend retries | **CONFIRMED** | `apps/web/src/lib/api.ts:44` `DEFAULT_TIMEOUT_MS = 12_000` (chosen for Playwright CI, not backend-aligned); backend 3 attempts × 10s (SODA) / 30s (ArcGIS) + `Retry-After` honored to 120s (`resilience/fetcher.py:359-371`, `config.py:49-52`); **no server-side overall deadline exists** (0 grep hits). No client retry storm (user-click only). |
| E5 | GitHub public vs "private" descriptions | **CONTRADICTED** (intent is PUBLIC) | Recorded owner decision 2026-07-20: `B-009-github-actions-billing.json:18` ("repository made PUBLIC… verified isPrivate=false", frees Actions minutes; also clears B-008); re-verified `M0-T034-G3-report.md:105`. Stale "private" docs: `docs/CONNECTION_AUDIT.md:10` etc. **Real tail**: `M0-T036-V1.2-G5` + `M0-T077` reviews accepted username/absolute-path disclosure on the (already-false) private-repo premise → re-examination item. No visibility change made. |
| — | Review's ledger counts (main 100 / control 147 / handoff 84) | **LAGGED — superseded by live ledger** | Live: **157 accepted** (M0-T107 `9dcbdd09`, M0-T144 `892c9fe1` reconciled); M0-T109 awaiting_gate@95 (accept coupled to R754 first live run); campaign D-024 active seq 71+, terminal BLOCKED_FOR_PERSISTENT_ACTIVATION now being discharged under D-032. Nothing reset to review snapshots. |

## 2. Dependency-ordered plan mapped to existing tasks

**Which controller work actually blocks product delivery: none beyond finishing this activation.**
After the loop is live, remaining controller items (M0-T133 re-gate, M0-T137 model-selection
decision rows, M0-T145/M0-T025 — now the loop's own first workload) are hygiene/hardening, not
product blockers. The product path below can proceed in parallel with the loop.

0. **D-032 activation (in flight)** — owner install + allowlist → first live limited-auto run over
   `[M0-T145, M0-T025]` → accept M0-T146 → accept M0-T109 (R754 satisfied by the run).
1. **Real source integration + durable revisions** — *no existing task covers the default-provider
   wiring* → **propose M2-T020** "wire `compose_from_connectors` behind
   `get_spatial_substrate_provider` + persisted run revision (run id bound to source digests,
   versions, rule version, as-of date)". Anchors: M2-T013 engine (accepted), review acceptance
   gate: one genuine R5 lot through real adapters → spatial evidence → evaluation → persisted run →
   reopen, plus one real out-of-scope and one missing/conflicting-source case.
2. **Auth, storage, review workflow** — B-001 closure (owner secure channel) → M0-T007/M0-T008
   (Supabase auth + organizations) → M2-T019 (production ReviewStore + HTTP binding + migrations).
   Also **propose** the isolated-parser-worker task (finding D) before any untrusted-upload
   exposure, and the deadline-budget task (finding E4: one overall server deadline + aligned client
   budget + resumable-job path).
3. **Exact legal evidence + qualified approval** — M3-T001→T002→T003→T004 (contracted chain;
   raw-byte capture closes the `raw_html_verified:false` gap), fold the ZR 23-21 table/footnote
   item into M3-T002/T003 scope explicitly; extend the snapshot digest to cover table structure;
   then bounded R5 package under G6 with the owner-designated qualified reviewer (B-010
   benchmarks). M4-T001..T006 stay merged-draft until G6.
4. **Constrained options, saved comparisons, evidence reports** — M5-T001/M5-T002 foundation
   (PR #241 stays open under its hold; merge is a separate owner decision and does NOT by itself
   produce a live cap — finding A); constrained footprints/floor stacks follow the coverage gate.
   3D/UI expansion planning remains under the standing owner-review hold.
5. **Benchmarks + paid pilot** — B-010 + the review's 20–30 stratified professionally-assessed
   cases; zero critical false-confident conclusions; abstention measured separately. E1 fixture
   refresh (26v2) + E3 audit-outage classification + E5 stale-doc/private-premise re-examination
   ride along as bounded hygiene items.

R5 pilot = bounded **release phase**; the all-five-borough mission is unchanged. The 30/60/90-day
schedule is treated as provisional sequencing, not a commitment.

**Differentiation (tested, not assumed):** Envelope/TitleVest already advertises citations+massing+
expert support; PropertyScout markets City of Yes broadly (its own roadmap shows pending items);
Tectmind sells supported reports (2–3 days); TestFit from $15k/yr; Forma bundles with Revit
subscriptions; Gridics $999/$1,499 per report; Deepblocks $499/mo. Our testable edge = the four
directive criteria: reproducible frozen runs, explicit coverage/abstention labels, constrained
options with binding-constraint explanations, and measured reviewer-minutes reduction — proven on
the same parcels via the benchmark set, not claimed.

## 3. Next concrete deliverable + acceptance criteria

**Deliverable:** first live limited-auto autonomous loop run (`--run-id persistent-local-01`) over
`[M0-T145, M0-T025]` with gpt-6-astra@high as main reviewer (sol@high until the allowlist lands).
**Acceptance:** run reaches its stop bound with ≥1 APPROVE and exactly-once advancement recorded in
the durable journal; live evidence for the seven local-autonomy facts (auto-REVISE loop-back,
auto-correct without owner "continue", auto-advance, controller task selection, controlled
interruption, checkpoint resume, accurate foreground view) present in `audit.jsonl` + run
artifacts; zero owner-gate violations; then M0-T146 accepted (DCV rows R772/R780 → PASS at final
HEAD) and M0-T109 acceptance unblocked (R754).
**Product deliverable after that:** the M2-T020 spatial-wiring proposal above, with the review's
real-parcel acceptance gate as its scenario pack.

## 4. Owner decisions + external dependencies (grouped)

**Now (finishes the loop activation — two commands, §2 of D-032-activation-transaction.md):**
1. Run the controller install (+ verify-manifest) command — the assistant's permission layer
   blocked exactly this call, which matches the original owner-run design.
2. Run `owner_allow_astra.ps1` elevated (admin-locked allowlist; adds gpt-6-astra).

**Queued (product path):** 3. B-001 Supabase secure credential channel; 4. designate the qualified
zoning reviewer + provide authorized benchmark material (B-010); 5. approve the exact bounded R5
pilot scope when the M3 evidence package is ready; 6. PR #241 merge decision (hold stands);
7. R595/Option-A + R603–R605 GitHub lifecycle (owner-only, undecided, untouched); 8. authorize the
stale-doc cleanup + re-examination of the two security reviews that assumed a private repo;
9. expansion-planning hold remains until the owner reviews the 3D/UI integration report.

**External:** repo remains PUBLIC by owner decision (no change made); PLUTO 26v2 upstream bump
(fixture refresh only); npm advisory-service outage was transient; gpt-6-astra account access
verified live 2026-09-06.
