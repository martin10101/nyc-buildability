# Lane B — Data and site facts: status

Updated by lane B only, after every task (lane prompts, shared rules).

| | |
|---|---|
| **State** | Working the queue (B-01, B-02, B-03 merged: PRs #254, #260, #259) |
| **Done** | B-05 (M2-07) built, awaiting review: existing zoning floor area for one tax lot from a certificate of occupancy figure, DOB BIS job filings (`ic3t-wcy2`, completed work only) or a stated assumption, else "Unknown" with the reason. DOF/PLUTO building area has no input path; it stays a reference-only value. Benchmark 215-16 Northern: 39,934 sq ft (NB 440608941), not 54,488. Code: `services/api/app/profile/existing_floor_area/`; tests: `services/api/tests/profile/test_existing_floor_area_*.py` |
| **Next** | Top unblocked item in `docs/lanes/queues/B.md` |
| **Blocked by** | — |
| **Open owner questions** | (1) B-05 order: certificate figure > DOB filing > stated assumption. Should an architect's stated assumption ever override a DOB filing? (It does not now; this ties to the open B-02 entered/assumed rank question.) (2) Should a figure the architect reads off a certificate of occupancy rank as "City records"? No certificate dataset has a floor-area column. |
