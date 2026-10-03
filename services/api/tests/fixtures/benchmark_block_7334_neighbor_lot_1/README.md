# Block 7334, Queens, neighbour tax lot 1 — recorded existing-floor-area evidence (B-11 slice 2)

Tax lot **1** (BBL 4073340001, 215-10 Northern Blvd) is the recorded **touching neighbour** of the
subject lot **70** (215-16 Northern Blvd, BBL 4073340070). B-07 established that lots 1 and 70 share
one 99.98 ft lot line (their EPSG:2263 outline vertices coincide exactly), tested in
`services/api/tests/spatial/test_multi_lot_site_benchmark_block_7334.py`. This pack records the
neighbour's **own** existing-zoning-floor-area evidence so B-11 slice 2 can capture it through the
B-05 source order (certificate of occupancy > DOB filing > stated assumption; **never** DOF/PLUTO
building area).

Queue item B-11 slice 2 (Lane B; plan section 11b parity data; directive D-090, owner GO
D-090-R087). The subject lot 70's records are in `../benchmark_215_16_northern/` (B-01) and are not
copied here.

## Why this pack exists

The B-07 README named a gap: lot 1's evidence had only been captured *incidentally* by the subject
lot 70's BIN queries, and "no query keyed on BBL 4073340001 was recorded … no certificates of
occupancy by BBL." This pack closes that gap with a first-class, self-contained neighbour capture:
lot 1's building filings and the two certificate datasets queried **directly for the neighbour**
(the certificates by BBL, the exact query shape B-01 used for lot 70).

- **Capture:** 3 official responses on 2026-10-03 UTC. Python `urllib` GET, keyless, one request per
  file, sequential, at least 3 s apart, all HTTP 200. Each body is stored byte-for-byte as returned.
  The `ic3t-wcy2` `$select` is verbatim from the B-01 pack, so no applicant/owner name column is
  fetched (the committed body carries only property, job, zoning and flag columns).
- **Provenance:** `MANIFEST.json` lists, per file, the dataset id, exact URL, `retrieved_at` (UTC),
  HTTP `Date` and `Last-Modified`, status, byte count, sha256 and row count.
- **Integrity:** `services/api/tests/connectors/test_benchmark_neighbor_lot_1_fixtures.py` re-hashes
  every file and rebuilds the certificate URLs. `.gitattributes` (`-text`) keeps the bytes exact.

| File | Source | What it holds |
|---|---|---|
| `dob_bis_jobs_ic3t-wcy2_bin_4157401.json` | DOB BIS Job Application Filings (`ic3t-wcy2`) | 22 rows for lot 1's building BIN 4157401. The only zoning-figure rows: job **421199072** (A1, "PERMIT ISSUED - ENTIRE JOB/WORK", existing/proposed zoning 14,150 sq ft — **not signed off**) and job **421803891** (A1, "PLAN EXAM - DISAPPROVED", existing 9,100 → proposed 39,772 sq ft, text "ALTERATION -1 APPLICATION TO BE FILED UNDER TAX LOT #1 … ONE (1) ZONING LOT AND (2) TAX LOTS (LOT #1 & #70)"). All other rows are A2/A3/SI renovations with 0 zoning sq ft. |
| `dob_bis_co_bs8b-p36w_bbl_4073340001.json` | DOB BIS Certificate Of Occupancy (`bs8b-p36w`) | `[]` — no BIS certificate of occupancy keyed on lot 1's BBL. |
| `dob_now_co_pkdm-hqz6_bbl_4073340001.json` | DOB NOW: Certificate of Occupancy (`pkdm-hqz6`) | `[]` — no DOB NOW certificate of occupancy keyed on lot 1's BBL. |

## Reading on the recorded data (test: `tests/profile/test_parity_neighbor_floor_area.py`)

Resolved through B-05 (`app.profile.existing_floor_area.resolve_existing_zoning_floor_area`), the
neighbour lot 1 reads **Unknown — enter**, i.e. its existing zoning floor area is **not recorded**:

- job 421199072's 14,150 sq ft is **set aside** — the work is not shown as completed (status
  "PERMIT ISSUED - ENTIRE JOB/WORK"; no certificate of occupancy names the job);
- job 421803891's 39,772 sq ft is **set aside** — a disapproved filing whose text mentions one
  zoning lot of tax lots 1 and 70, so its figure may cover the whole zoning lot rather than this
  building (and it is not completed either); the zoning-lot mention is cited;
- no certificate of occupancy figure and no stated assumption were entered.

Both set-aside figures keep their source. DOF/PLUTO building area (lot 1 `bldgarea` 8,409; lot 70
`bldgarea` 54,488) is **never** read as existing zoning floor area and appears nowhere in the
capture. The ic3t body is not byte-identical to B-01's BIN 4157401 capture (the daily `dobrundate`
field differs); the figures and status are the same. A recorded filing does **not** verify a zoning
lot: that stays "Check needed".

The neighbour **set** itself (which lots are neighbours of the subject) is the lots on the subject's
tax block whose recorded MapPLUTO EPSG:2263 outline shares a lot line with the subject — a touching
lot. For the benchmark that is lot 1 (B-07). A block-wide neighbour set is a future capture (an open
B-11 owner question). Method recorded in `docs/research/neighbor-floor-area-2026-10-03.md`.
