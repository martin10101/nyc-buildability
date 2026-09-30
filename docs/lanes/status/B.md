# Lane B — Data and site facts: status

Updated by lane B only, after every task (lane prompts, shared rules).

| | |
|---|---|
| **State** | Working the queue (B-01, B-02, B-03 merged: PRs #254, #260, #259) |
| **Done** | B-05 (M2-07) built, awaiting review: existing zoning floor area for one tax lot from a certificate of occupancy figure, DOB BIS job filings (`ic3t-wcy2`, completed work only) or a stated assumption, else "Unknown" with the reason. DOF/PLUTO building area has no input path; it stays a reference-only value. Review #274 rework: a filing that may carry a zoning-lot figure fails closed, and when a supplied DOB row on the block mentions a zoning lot the DOB figure is set aside. Benchmark 215-16 Northern (lot 70): "Unknown — enter", never 54,488; DOB NB 440608941's 39,934 sq ft is kept in the set-aside list with its source, and job 421803891 ("one zoning lot, tax lots 1 & 70") is cited, so the architect can confirm it as a stated assumption. Code: `services/api/app/profile/existing_floor_area/`; tests: `services/api/tests/profile/test_existing_floor_area_*.py` |
| **Next** | Top unblocked item in `docs/lanes/queues/B.md` |
| **Blocked by** | — |
| **Open owner questions** | (1) B-05 order: certificate figure > DOB filing > stated assumption. Should an architect's stated assumption ever override a DOB filing? (It does not now; this ties to the open B-02 entered/assumed rank question.) (2) Should a figure the architect reads off a certificate of occupancy rank as "City records"? No certificate dataset has a floor-area column. |
