# M5-T052 source-sections index (frozen submission identity)

Material lineage (three commits on candidate): producer material cherry-pick `365f492f`
(task-branch `171ba0b0`, runs 55–56 through six revision rounds, orchestrator-committed
at the breaker close) → tagged consumer-sweep fix `46bf1105` (task-branch `7017144e`) →
tagged timestamp fix `a6f35a0f` (task-branch `b41bf913`). The three commits, precisely:
1. Producer material (runs 55–56) — orchestrator-committed.
2. `[ORCH-CORRECTED consumer sweep per producer report §5]` — report-view.test.tsx
   updated to the shared-decision behavior exactly as the producer routed (the file is
   OUTSIDE M5-T052's allowed_paths; flagged known-red by the producer, never silent).
3. `[ORCH-CORRECTED per CI 35449971976]` — boundedTimestamp fix in condo-records.ts
   (ISO timestamps were colon-stripped by the boundedToken allowlist; 2/1151 tests bound
   the round-trip and caught it).

CI at the corrected head `a6f35a0f`: run **35451055372**, ALL jobs success (0 non-success;
the prior run 35449971976 failed exactly the 2 timestamp assertions — root-caused, fixed
tagged; the consumer-fix tests passed on their first CI run).

SHA-256 digests are LF-normalized (CRLF→LF before hashing), pasted verbatim.

| sha256 (LF-normalized) | file |
|---|---|
| `d0d134fdfafb48fc708b2f9ce6f9193c670b11187aeb9960cb019619c502a7cc` | services/api/app/api/v1/condo_records.py (per-BBL records route; resolver's own outcome literals; substitution substrate-record; unit-BBL increment) |
| `9afa159a452c57c72aafcf507dd415e22f36e047210a2baa2a7c614ba180d5a9` | services/api/app/main.py (the one mount line) |
| `670cfccbb013573f96a21813713e4c9850a9740ae760aaa8539f3bdc17093874` | services/api/tests/api/test_condo_records_api.py (15 route tests incl. token pin + unit-BBL + absence/error honesty) |
| `52e44c9fe9dedfef861fd4a049c663fda303e002c470109541d4efcae4086634` | apps/web/src/lib/condo-records.ts (typed client; credentials omit; bounded; boundedTimestamp fix) |
| `5354a3ac1dd7d6e0547efde1e1b81423d0d5195d88f64fbd2d740442df7f6904` | apps/web/src/lib/__tests__/condo-records.test.ts |
| `0c7113d4d1a0feec886bf25f72e129c7e12bb90793aaf643a287d715ee22a017` | apps/web/src/components/architect/PropertyOverview.tsx (deriveCondoSurface — the ONE shared decision; CondoRecordsChannelSection) |
| `97b0f0ef30162768c444c6fd7c34f98316561580a11b636d561a3bfc414a9561` | apps/web/src/components/architect/AnalysisIdentityNotice.tsx (UNCHANGED from the accepted state — the ruling folds the explanation into the substitution record; in the index as an allowed_path the reviewers must confirm untouched) |
| `22bf1b1264b3abf59406916a6c8879c44c826a02deb86712213fc94066ec0acc` | apps/web/src/components/architect/ReportView.tsx (the brief reads the SAME shared decision + section) |
| `acc62445493fe086662ea0569bd2f6211316ed2902d5b218ec7928164e721c5c` | apps/web/src/components/architect/__tests__/condo-resolution-display.test.tsx (channel stubs; all outcome branches; token pin; heading semantics) |
| `fa7c04127c2f17b8c1f5154e8ec51ef6bb841ef175370844c843e9e5a58a26fe` | project-control/reports/M5-T052-producer-report.md (leads with the guard-coherence ruling §1; digest updated after the tagged G3 report corrections — pre-correction digest bf225ba6…) |
| `5631bfd0603bc51963d68118bdaf777820dd7541f559b093703f3fb19c142cd5` | apps/web/src/components/architect/__tests__/report-view.test.tsx (OUTSIDE allowed_paths — the tagged consumer-sweep fix, listed for reviewer completeness) |

Orchestrator reproduced at harvest (wt-m5t052, documented cwds): ruff clean; 15 route +
454 api + 697 rules tests; modularity exit 0 ([ORCH-CORRECTED per G3 F2]: PropertyOverview GREW 210->319 and stays below the warn tier; the earlier SHRANK wording mirrored the producer report's false claim). CI web proof:
run 35451055372 at a6f35a0f (1151 vitest incl. the shared-decision suites + Playwright).
