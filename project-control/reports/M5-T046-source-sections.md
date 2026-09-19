# M5-T046 — digest-bound source-section index (orchestrator-captured)

Per the producer's §1 collection coordination: each source section is one FILE at the
material identity, digest = sha256 over LF-normalized bytes (CRLF smudge stripped —
PROGRAM_KNOWLEDGE rule). Material commit `a3d195d7` (task branch), cherry-picked to
candidate as `3182f0a2`; adjudication head `c3c690f7`; the AS-5 tagged correction
`[ORCH-CORRECTED]` landed as `ce4a9ed2` (task branch) / `fb7af67d` (candidate) — the
test-file digest below is the CORRECTED identity. Reviewers read the files directly
at the pinned head and MAY verify any digest below; never rely on a bundled diff.

| LF-sha256 | file | role |
|---|---|---|
| `0096e659a64b4bd68d4e5ea107a2d2e622698f2b8decd374e36fe55c14f55e3f` | `apps/web/src/lib/address-search.ts` | equality gate + normalization (changed) |
| `973ec3c5712e977dd1f63671f51241e39fe2973c14d88dad390ef7e102930f22` | `apps/web/src/lib/__tests__/address-search.test.ts` | byte-faithful corpus regression (changed; AS-5 corrected + AS-5b added, tagged) |
| `137e4e3adf3f29417eac79651d201f53e56d7fadc85c6f17a736c6e1004d23fc` | `docs/research/source-registry-drafts/geosearch.json` | source-registry draft (changed) |
| `018aa354ebca29dff0b7a811e4556840b47d906c07191898a5ff0cb9fdab1c2b` | `apps/web/src/components/architect/AddressAutocomplete.tsx` | raw-typed-text capture on pick (changed) |
| `45574ebcdbdf0ac4d719e4ce3368ca8c82cb4f55ac27a07c3639b8c0b2b44777` | `apps/web/src/components/architect/__tests__/autocomplete.test.tsx` | onPick raw-text test (changed) |
| `70cc76dff2bf62a43661f318100ad416a8ad8b7640e8be32759425f02b024aed` | `apps/web/src/components/address/AddressResolutionScreen.tsx` | threads typedInput (changed) |
| `dd4f02f508aac6d0dd9ed18672c387e31b5b9e06f803458c90ac59c82887be02` | `apps/web/src/components/address/AddressConfirmCard.tsx` | entered-vs-matched display (changed) |
| `8561c226dd944160e38442eb64f71c87e1f0248691ac5729c2ac11c6133c712b` | `apps/web/src/components/address/__tests__/address-confirm.test.tsx` | confirm-arc journey tests (changed) |
| `22c725a0e1dd400b41bb0e5d0ab7e59a32ab0c95531850353ad9f6809804c9e3` | `project-control/reports/M5-T046-producer-report.md` | producer report (evidence carrier) |
| `15e98b63e653dc144f15dc4a106ca09c0d5d317187f2c38104417737dc8c3f92` | `docs/research/db026-address-to-lot-fixture-capture.md` | 8-capture corpus (read-only basis) |
| `b6580dcf9368b073d972ef85239e7d40c1a9fc417390bc2b6d1a2e6fd50fe9ae` | `docs/research/source-registry-drafts/ztldb.json` | committed shape mirrored (read-only basis) |

Read anchor (unchanged consumer named in the call-path): `apps/web/src/lib/architect/use-address-suggestions.ts`.
Local documented check reproduced by the orchestrator at the material head: `python tools/modularity_check.py --check` → exit 0 (warnings all pre-existing).
CI on the pushed head: run 35425110363 (context-budget) success; 35425110354 (secret-scan) success; 35425110351 (CI) — conclusion recorded in `M5-T046-ci-evidence.md` when complete.
