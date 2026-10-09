# M5-T048 source-sections index (frozen submission identity)

Material: commit `8a4b3b4520b3cc193e7ce3605b48eb018f3b3f01` (task branch, runs 11–14 build,
orchestrator-committed) → cherry-pick `0c7b17f111f85636ccafb4aeff10837117311de4`; tagged
correction `607aab6b3bc9af699c7fdd9827d7cc4bc61c4fbd` ([ORCH-CORRECTED per contracts-CI]:
semantic-fixture relocation) → cherry-pick `93f194c0a52ca936c1d097777037d86f0aee6490`.
CI at the corrected head 149fab76: run 35439235554, ALL jobs success (M5-T048-ci-evidence.md).

SHA-256 digests are LF-normalized (CRLF→LF before hashing), pasted verbatim from the tool
output. Note the two schema copies hash IDENTICALLY (the byte-equality contract).

| sha256 (LF-normalized) | file |
|---|---|
| `dc41be0e356ca76b1617cbdeb1439d2d400d9e583f02afea4729ae95337ce4b9` | packages/contracts/schemas/v1/scenario.schema.json (contract 1.1.0, optional proposed_massing) |
| `dc41be0e356ca76b1617cbdeb1439d2d400d9e583f02afea4729ae95337ce4b9` | services/api/app/_contract_schemas/v1/scenario.schema.json (byte-identical copy) |
| `230392c45ae01850563e62c0b039c8e1b7acb08ec07463bc6822589d83cc92c5` | packages/contracts/generated/scenario.ts (regenerated, typegen --check byte-identical) |
| `c3adec5313d40250455685b28463d0d85688517b61f2a61b6b9e67459a38ce87` | packages/contracts/fixtures/valid/scenario/proposed_massing_preliminary.json |
| `c4a0c735cce39c70c0f335c441874385b6c4ed82f27ab380977791e25ed6fda3` | packages/contracts/fixtures/valid/scenario/proposed_massing_multilevel.json |
| `0b26601d1695e2035d952feef9420965e2b07b31d6e8c35519cb3fb1413c41cc` | packages/contracts/fixtures/invalid/scenario/proposed_massing_negative_height.json (schema-rejected: exclusiveMinimum) |
| `f43309fa7a555f6a334eb0e2d6aed97feade878948315c702cc85dcc652aa635` | packages/contracts/fixtures/semantically_invalid/scenario/proposed_massing_open_ring.json (schema-valid; proposal.py-refused) |
| `3e38aa88791044fb864d2dadc591bc7df54516d2a78d31798f55288f6cdb0dc5` | packages/contracts/fixtures/semantically_invalid/scenario/proposed_massing_self_intersecting.json (schema-valid; proposal.py-refused) |
| `4649edf0bf2915c68042bba06b73e8532c7c7df02aff04e73bbbdaf916f8c76c` | services/api/app/scenario/contract.py (admits + threads the validated optional block) |
| `8feded0224e7729392bc3bf0427e2c7cf7fc636cb619349edd49e462a0507e4e` | services/api/app/scenario/proposal.py (NEW focused validator; typed refusals, DB-013 ceilings) |
| `f27d42f07db5aa0f0f369dfb08c1e5dd6dc010c8639f96716b47aa4cbd3e1057` | services/api/tests/scenario/test_scenario_contract.py |
| `059ceac956b1766fb66f27970d1777a37d3e3ea21c8b315e749d254a976ca70e` | services/api/tests/scenario/test_scenario_proposal.py |
| `50f37a1d302dbb611f532a2959aaeabfceefe4de6dc5182615517624e9b4a195` | project-control/reports/M5-T048-producer-report.md (producer evidence + tagged orchestrator addendum) |

Orchestrator reproduced pre-commit (both at harvest and after the tagged correction): ruff
clean; pytest tests/scenario 527, tests/api 439, packages tests 29, all passed; typegen
--check all OK; modularity exit 0; the exact CI contracts script
`.github/scripts/validate_contracts.py` → "Checked 11 schema file(s); 0 failure(s)".
The one CI round lost: run 35437764489 at 0c7b17f1 failed 2/11 on the two geometry fixtures
placed under invalid/ per the packet's own SCOPE wording — root-caused as the schema-vs-
validator layering fact and corrected as tagged 607aab6b (see the producer-report addendum).
