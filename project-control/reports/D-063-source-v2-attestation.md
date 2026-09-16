Final content attestation — remote SHA **`5b832c8420e28d19bc4da45bfa4e92fbd234e18a`**

**M4-T022 G1/G3/G4: PASS remains applicable within the previously stated audit scope.**

The helper, tests, expectation fixture and all three operative source captures match their reviewed V2 SHA-256 hashes. In particular:

```text
helper: 5d4e0ae84c1f554e4b13ffe96e1f5b6299b018f4fb2712dc3e26ded08ef4f170
tests:  4323c72255f357478f7013bb0887f773c65c0a0970dc7d746655c0f03cfe07c0
```

Using the orchestrator’s remote-to-content mapping and unchanged task identity **`d25fc207bef4f94f93eb96d397112e6e7c2d3d0ea13c0b8f4fec99b0d4fba0fd`**, the report `M4-T022-G1-G3-G4-v2.md` applies to this final remote SHA. No retest was necessary: the reviewed audit content is unchanged. The reproduced **26 passing tests, 467 passing audit checks and 80 explicit gaps** retain their original scope.

**M5-T031 G1 source-semantic review: PASS.**

Reviewed task identity: **`634be631d1665c53ecae1a4b0f34a8e87283d835780d2cc5264b17462b51fedf`**, supplied by the orchestrator.

Independently inspected the current selectors, shared summary, Overview/Zoning/Report compositions, `ArchitectEntry`, `ScenarioWorkspace`, comparison presentation and producer addendum. Verified:

- **Residential FAR · city record** selects the matching PLUTO `residfar` provenance record. Built FAR remains separately available in the collapsed existing-building facts.
- **Evaluated residential FAR** requires a supported, uniquely identified residential trace. Conflicting, invalid, ambiguous or mismatched records cannot supply the headline value.
- **Draft zoning floor-area cap** requires matching analysis identity and the canonical `max_residential_floor_area_sq_ft` output. The frontend performs no PLUTO-FAR multiplication or replacement calculation.
- Height, yards and coverage summaries return status text without promoting arbitrary numeric trace values. A FAR value cannot become a height allowance.
- Supplied constraints and unusable records remain accessible as evidence. Unassociated scenario figures are explicitly disclosed as records whose association is unconfirmed.
- “Draft,” calculation limits and “Buildable envelope not assessed” remain visible. These distinctions agree with the previously checked [PLUTO field definitions](https://s-media.nyc.gov/agencies/dcp/assets/files/pdf/data-tools/bytes/pluto_datadictionary.pdf).

Current frontend content hashes:

```text
development-limits.ts:
57a6b82bdd87ea7f1247b463f613e261a616da437343e8cb9e3c42b1b3287609

DevelopmentLimits.tsx:
4d727fcf0062dd1645ad0a745dc615ba726c81c2436400f072e52b57cdf86718
```

No source-semantic defect was found in this bounded delta. This attestation does not renew frontend G3/G4/browser gates, approve legal interpretations, establish complete bulk coverage or authorize production deployment. No files or git/control state were changed.
