# M4-T022 residential verification coverage

Source retrieval and tests: 2026-09-15 UTC. This is engineering evidence, not legal approval.

- 49 official table rows cover 45 district identifiers across R1–R12; all 98 standard/qualifying parameter values match the fresh official tables.
- The existing draft engine produced the expected base FAR and arithmetic floor area in 45 synthetic district cases: 90 numeric outputs. These use a supplied district and 2,500 sq ft input, so they do not establish a real property's governing district, zoning-lot area, eligibility or complete bulk.
- 21 distinct official property records span all five boroughs. Twenty have matching ZTLDB district sets; the condominium billing lot has no ZTLDB match.
- Five actual live browser observations, performed by the orchestrator, show matching city residential-FAR references. All five return no calculated cap because `spatial_intersection_absent`; this is a calculation gap, not five successful buildability results. Built-FAR displays were not captured in those five observations.
- R11/R12 were absent in the primary R-prefixed district inventory, but broader queries found mixed assignments. Examples below retain their complete district sets.

| Borough | Address | BBL | City zoning | PLUTO residential FAR | Live display | Calculated allowance |
|---|---|---|---|---|---|---|
| SI | 196 HENDERSON AVENUE | 5000920001 | R1-2 | 0.75 | Matches | Unavailable: spatial evidence absent |
| QN | 69-02 KESSEL STREET | 4032110010 | R2 | 0.75 | Matches | Unavailable: spatial evidence absent |
| BK | 946 EAST 7 STREET | 3065090024 | R2X | 1.00 | Not observed | Not observed |
| BX | 925 HARDING PARK | 2034300037 | R3-2; R3A | 0.75 | Not observed | Not observed |
| QN | 50-01 39 AVENUE | 4001170001 | R4 | 1.00 | Not observed | Not observed |
| BK | 401 COLUMBIA STREET | 3005250001 | R5 | 1.50 | Matches | Unavailable: spatial evidence absent |
| BX | 3104 DECATUR AVENUE | 2033310040 | R5D | 2.00 | Matches | Unavailable: spatial evidence absent |
| MN | 40 CHARLTON STREET | 1005060012 | R6 | 2.43 | Matches | Unavailable: spatial evidence absent |
| BX | 2531 BELMONT AVENUE | 2032730231 | R6B | 2.00 | Not observed | Not observed |
| MN | 80 ATTORNEY STREET | 1003430001 | R7A; R8A | 4.00 | Not observed | Not observed |
| MN | 150 WEST 225 STREET | 1022150042 | R7-1 | 3.44 | Not observed | Not observed |
| MN | 80 GOLD STREET | 1000940001 | R8; C6-4 | 6.02 | Not observed | Not observed |
| MN | 278 EAST 3 STREET | 1003720012 | R8B | 4.00 | Not observed | Not observed |
| MN | 633 2 AVENUE | 1009150032 | R9 | 7.52 | Not observed | Not observed |
| MN | 1 5 AVENUE | 1005500022 | R10 | 10.00 | Not observed | Not observed |
| MN | 919 7 AVENUE | 1010110001 | R10H; C5-1 | 10.00 | Not observed | Not observed |
| MN | 142 HENRY STREET | 1002737501 | R7-2 | 3.44 | Not observed | Not observed |
| BK | 3622 13 AVENUE | 3052960043 | M1-2/R6A | 3.00 | Not observed | Not observed |
| BK | 260 HAMILTON AVENUE | 3005270001 | R5 | 1.50 | Not observed | Not observed |
| MN | 165 WEST 23 STREET | 1007990008 | C6-3X; M1-8A/R11 | 9.00 | Not observed | Not observed |
| MN | 501 8 AVENUE | 1007590037 | M1-9A/R12; C6-4M | 15.00 | Not observed | Not observed |

## Explicit gaps

1. Real-property calculation coverage remains unproven where spatial evidence is absent. The deployed cause and the connection from property evidence to the rule engine need a separate backend task.
2. Wide-street alternatives are stored and disclosed; the FAR rule does not select a higher value from a measured 100-foot geometry. Neither exact-threshold eligibility nor split portions are certified by this audit.
3. Qualifying residential-site, affordable/senior housing, UAP and MIH eligibility are not decided. The R8 8.64 footnote requires its compound conditions.
4. The R1/R2/R3 first-row per-unit 0.60 limit at 4,000 sq ft and above is retained as a limitation, not calculated from dwelling-unit data.
5. Special districts, mixed districts, split lots, overlays and R10H require their applicable legal logic. Refusing a number is a successful safeguard, not completed numerical coverage.
6. Height, yards, lot coverage, street wall and a full buildable envelope were not established by this FAR audit. Existing code modules do not prove the normal property flow calculates these.
7. PLUTO BuiltFAR and total building area describe existing records; subtracting gross existing area from an allowable zoning floor-area reference does not establish legally unused floor area.
8. Representative engineering tests are reusable but this new module is not automatically invoked by current CI. A separate scoped CI wiring change is needed for that claim.

The initial `splitzone='Y'` source request returned HTTP400 because the current SODA field is boolean. Its error is retained; the corrected `splitzone=true` capture succeeds. The failed research request is not hidden as a passing app test.
