# M1-T001 G0 definition-of-ready check (orchestrator)

- Objective unambiguous: research + documentation of official PLUTO/MapPLUTO sources; pattern = accepted M0-T002. YES.
- Dependencies: M0 control plane accepted through M0-T009; no code dependency — research-only. YES.
- File scope exclusive: docs/research/pluto-mappluto-*, docs/research/source-registry-drafts/pluto-mappluto*, project-control/reports/M1-T001-* — no other active task touches these. YES.
- Inputs/outputs defined in packet. YES.
- Acceptance scenarios S1-S5 exist in packet. YES.
- Source documentation available: public official sites (NYC Open Data, DCP); no credentials required for research (bulk pages and dataset metadata are public; Geoclient key NOT needed for this task). YES.
- Required gates assigned: G0, G1 (data-contract-verifier), G3. YES.
- Execution location: producer runs in main session context with web tools (official-source-researcher has WebSearch/WebFetch); writes only small markdown/JSON files. Local disk impact: < 1 MB text. Cleanup: none needed beyond normal git hygiene; no datasets downloaded (explicitly forbidden by low-storage policy — the producer documents download URLs, never downloads citywide files). PASS.
- Low-storage budget: unaffected (≥ 4 GB free preserved). PASS.

G0 result: PASS — task may start.
