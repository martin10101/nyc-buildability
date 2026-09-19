# M5-T047 — digest-bound source-section index (orchestrator-captured)

Per the producer's §0 collection coordination: each source section is one FILE at the
material identity, digest = sha256 over LF-normalized bytes (CRLF smudge stripped).
Material commit `196c6ec3` (task branch), cherry-picked to candidate as `7ecdcbf4`.
Reviewers read the files directly at the pinned head and MAY verify any digest below;
never rely on a bundled diff (the prior in-run round failed exactly on an aggregate
diff cap — every file below is individually inspectable at the head).

| LF-sha256 | file | role |
|---|---|---|
| `10046e290a35de6a197df27da9e9d9bfb83cc23eeb6fc7b4daf0e7ceab06dc97` | `services/api/app/api/v1/lot_geometry.py` | additive record-address sibling route (PRIORITY) |
| `cf78fb7ec52d0a7e64d23b400a4f102d15403ec5a4bb3bc07428536fc238bae4` | `services/api/tests/api/test_lot_geometry_api.py` | RA-1..RA-6 offline route coverage |
| `c9a15f8256e5d3b0aea1cfe8a6f1de1187579dc6d3fbdf9a8cf92d6fd2eeb589` | `apps/web/src/lib/record-address.ts` | typed client + differ + hook (PRIORITY) |
| `6530512334ea8b939219b97b34b6b95d79ab2408150f8c4c262612f84d847e11` | `apps/web/src/lib/__tests__/record-address.test.ts` | typed-outcome + differ unit coverage |
| `b76d0a76ddd8c4d4242ab6250c8d89966f02535e1ace98dc316daed4aee7b575` | `apps/web/src/components/address/AddressConfirmCard.tsx` | record-address line + HJ A2/A3a polish |
| `bc1948eed0e4f543d4d8990ecc331594338876f89e092b2e3ea434b7b323039e` | `apps/web/src/components/address/__tests__/address-confirm.test.tsx` | S10 + strengthened negatives; S9 updated with A3a |
| `2d3b6ecf256723d8eefdde09a5b8592498ceb3ba197f55c2009f5fd02b9ab678` | `apps/web/src/lib/address-search.ts` | G5-A1 length bound rider |
| `c3cc716142b8c33df796aed708f9535437cbe9b592b6d635b5f44d5195adfdd8` | `apps/web/src/lib/__tests__/address-search.test.ts` | G4-A1 + G5-A1 rider fixtures |
| `8af8c4068483de3d5c4490b737bb4e1d5e3f6c35114a90ae6f47d751a4ef15bf` | `project-control/reports/M5-T047-producer-report.md` | producer report (evidence carrier) |

Digest provenance: computed by the orchestrator over LF-normalized bytes at the material
identity and pasted from the tool output without retyping; reviewers MAY recompute any row
(`git show <head>:<path>` piped LF-normalized into sha256) and must treat a mismatch as blocking.

Read-only bases (unchanged): `services/api/app/connectors/pluto_soda.py`,
`services/api/app/resilience/fetcher.py`, `services/api/app/connectors/bbl.py`,
`docs/research/db026-address-to-lot-fixture-capture.md` §6, `apps/web/src/lib/lot-geometry-api.ts`,
`apps/web/src/components/address/AddressResolutionScreen.tsx` (in allowed_paths, UNCHANGED this run).

Orchestrator-reproduced local checks at the material identity (in-worktree wt-m5t047):
`python -m ruff check .` clean; `pytest tests/api/test_lot_geometry_api.py -q` = 33 passed;
`pytest tests/api -q` = 439 passed; `python tools/modularity_check.py --check` exit 0
(warnings all pre-existing). CI on the pushed head: run 35430668528 — conclusion recorded in
`M5-T047-ci-evidence.md` when complete (secret-scan + context-budget already green at 7ecdcbf4).
