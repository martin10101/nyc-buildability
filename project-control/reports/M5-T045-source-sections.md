# M5-T045 — digest-bound source-section index (orchestrator-captured)

Per the producer's binding note (the producer cannot hash; ADR-005 division): each source
section is one FILE at the material identity, digest = sha256 over LF-normalized bytes
(CRLF smudge stripped). Material commit `39d1d3ab` (task branch), cherry-picked to
candidate as `28082288`; CI-proven at `21ee7379` (run 35431367744 success — the first head
whose CI covers this material; the T045 surface is byte-identical from the cherry-pick
through the submission head). Reviewers read the files at the pinned head and MAY verify
any digest; never rely on a bundled diff.

| LF-sha256 | file | role |
|---|---|---|
| `9a816c040f38e52f317a5de12ef6a61e7261014cad72c058f3d48e9624f2ed0e` | `services/api/app/connectors/condo_base_lot.py` | seam-policy module (271 SLOC) |
| `041ee640cc61822d4ae5ad7a91a585c7b40e84cc2fe513cd44020b5c4aa3f158` | `services/api/app/connectors/dtm_condo_soda.py` | leaf resolver + T044 riders |
| `1dc3aacaaa56ae5dee383c54a54fa983cba632a1622b8801050a5c1ae09229a0` | `services/api/app/spatial/live_provider.py` | live consumer seam (pre-lookup condo step) |
| `0f30967b42979cb76998c6b1f525dae1560b4e6096ea1d9c180c59e83a03c984` | `services/api/app/profile/zoning_crosscheck.py` | profile producer helper (existing channels) |
| `cf9d9195b9851781fd182b1e3179fef006abb8862e22df5bebda52a67f386d50` | `services/api/tests/connectors/test_condo_base_lot.py` | seam-policy tests |
| `a59b5c82ac772e08526b0d8709b667472e4a3d831631a010a1b891c312727a0a` | `services/api/tests/connectors/test_dtm_condo_soda.py` | real key-absence fixture + rider tests |
| `90ddd1fac29d90565365eed6a38cbd8f6477f6dc770fcbcd32c8f2c2d18d9737` | `services/api/tests/spatial/test_live_provider.py` | provider condo-step tests |
| `953b4f8c9e4ba38a32e52e9c46273fc1802a57a8787e3f20602b4184f5551b3c` | `services/api/tests/profile/test_ztldb_crosscheck.py` | condo_resolution_report tests |
| `0fd9f1f73ec5a93b7a5d60b6c6cc8c67ed6971b20589ec385509f09535d17fd5` | `services/api/tests/profile/test_wave_integration.py` | consumer sweep tests |
| `5fe69e09fd27b0f45bf242f7d72227f56fd8aff16ccb4d33d2524625e9ac7507` | `docs/research/source-registry-drafts/dtm-condo.json` | registry draft, BOTH datasets |
| `649f870456c7252ee7bab2b371d99ce80e311d50eed939ea5c118af37ee1371d` | `apps/web/src/components/architect/PropertyOverview.tsx` | CondoResolutionRecords + condoWithholdsAllowances allow-list |
| `0a5c85c4894f304f3946d260525d0498b56dd95a285a80b908ca846fbe31a8e4` | `apps/web/src/components/architect/ReportView.tsx` | printed-brief parity (same guard) |
| `97b0f0ef30162768c444c6fd7c34f98316561580a11b636d561a3bfc414a9561` | `apps/web/src/components/architect/AnalysisIdentityNotice.tsx` | neutral entered-vs-analysed identity record |
| `251416ce628f8cb937058d3a960aba35871eea0d7ef655816852907fc2affc8f` | `apps/web/src/components/architect/__tests__/condo-resolution-display.test.tsx` | screen-surface probes incl. missing/malformed/unknown-token withholds |
| `9df2ca32fd1e5a04e26aa3974345d55ff9b63561776720287f33e06cb7712e5a` | `apps/web/src/components/architect/__tests__/report-view.test.tsx` | printed-brief withhold probes + displayable control |
| `782be93c604b258dfe84829922f5c14b65fc0407f409c001a464aa279d79f9e6` | `project-control/reports/M5-T045-producer-report.md` | producer report (evidence carrier) |

Digest provenance: computed by the orchestrator over LF-normalized bytes at the material
identity and pasted from tool output without retyping; a reviewer-recomputed mismatch is
blocking. Not changed this packet (in allowed_paths, untouched): the api test files
`test_rule_evaluation_api.py` (route consumers unbroken — CI green is the proof).

Orchestrator-reproduced documented commands at the material identity (wt-m5t045):
ruff clean; 81 passed (condo focused); 58 passed (seam trio); 1494 passed
(connectors+spatial+profile+api full regression); modularity exit 0 (dtm_condo_soda.py
stays a justify-band warning with the cohesion justification in producer report §4 —
0 failures).
