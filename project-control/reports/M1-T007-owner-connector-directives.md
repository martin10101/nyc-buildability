# M1-T007 — Owner connector directives (recorded by orchestrator, 2026-07-17)

Owner directives accompanying the M1-T007 gate run. These are BINDING inputs for every
future DOB connector task packet (M2 DOB facts, M1-T008 BIS research). Cite this file in
those packets' `inputs`.

## 1. Dataset-count mapping (verified by orchestrator 2026-07-17; G1 must re-verify live)

6 core + 5 secondary = 11 dataset identifiers, represented as 9 registry records in
`docs/research/source-registry-drafts/dob-now.json`:

| Registry record | Dataset ID(s) |
| --- | --- |
| nyc-dob-now-build-job-filings-soda | w9ak-ipjd |
| nyc-dob-now-build-approved-permits-soda | rbx6-tga4 |
| nyc-dob-now-certificate-of-occupancy-soda | pkdm-hqz6 |
| nyc-dob-now-safety-facades-soda | xubg-57si |
| nyc-dob-now-safety-boiler-soda | 52dp-yji6 |
| nyc-dob-now-elevator-safety-compliance-soda | e5aq-a4j2 |
| nyc-dob-now-build-laa-soda | xxbr-ypig |
| nyc-dob-now-electrical-permits-soda | dm9a-ab7w (parent) + xmmq-y7za (details child, join: job_filing_number only, child has no location fields) |
| nyc-dob-now-build-elevator-permits-soda | kfp4-dz4h (parent) + juyv-2jek (device details child, join: job_filing_number + device_id, child has no BIN/BBL) |

The two parent/child pairs are INTENTIONAL combined family records. Verified: each child
dataset ID, join rule, column count, per-child rowsUpdatedAt freshness observation, and
child-specific limitation is individually represented inside its combined record.

## 2. Mandatory connector model (preserve for all DOB connector implementation tasks)

```
BBL
→ resolve every associated BIN
→ query every applicable DOB NOW family using the supported key
→ normalize and validate keys
→ preserve raw values
→ deduplicate/version filings deterministically
→ retain source-family provenance
→ reconcile with BIS
→ expose incomplete or conflicting coverage honestly
```

Never assume:
- one BBL equals one BIN
- one BIN equals one building record
- one filing row equals one unique job
- a permit row means the permit is currently active
- a safety filing proves current compliance
- no DOB NOW result means no DOB activity

## 3. Required explicit parsers and fixtures (connector tasks must contract these)

- BIN aliases: `bin`, `bin_number`, `location_bin`
- BBL aliases: `bbl`, `gis_bbl`
- numeric and zero-padded identifiers
- invalid/polluted join keys (observed: "Permit is no" inside job_filing_number, rbx6-tga4)
- borough case normalization (title case vs UPPER observed across sibling datasets)
- every non-ISO date format (observed: '02/15/22 11:08:46 AM' in pkdm-hqz6; 52dp-yji6 text dates)
- parent/child relationships (electrical, elevator families)
- amendments and repeated filing versions
- empty valid results versus source failure

## 4. Staged implementation priority (do not let secondary families delay the first usable DOB property-history view)

First connector priority: Job Application Filings (w9ak-ipjd), Approved Permits (rbx6-tga4), Certificates of Occupancy (pkdm-hqz6).
Second connector priority: Façade filings, Boiler filings, Elevator safety, LAA/electrical/elevator parent-child families.

## 5. Coverage labeling

BIS-family research (M1-T008) and BIS reconciliation are mandatory before any UI may claim
complete DOB history. Until then, results must be labeled "DOB NOW channel coverage",
never "complete DOB records".
