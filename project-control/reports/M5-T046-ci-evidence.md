# M5-T046 — CI evidence (orchestrator-captured)

Branch `candidate/D-024-mrl-option-b`.

## Corrected head `fb7af67d` (the submission identity)

| run | workflow | conclusion |
|---|---|---|
| 35425516645 | CI (incl. web-e2e: vitest + Playwright vs recorded-official-fixture API) | **success** |
| 35425516655 | secret-scan | success |
| 35425516666 | context-budget | success |

Vitest on the failing-then-corrected suite: `src/lib/__tests__/address-search.test.ts` green at
this head (1038+1 tests overall green; the suite includes the corrected AS-5 and the new AS-5b).

## Prior head `c3c690f7` (pre-correction, for the record)

CI run 35425110351 FAILED with exactly ONE test of 1038: `AS-5 … expected 'no_match' to be
'resolved'` — the corpus §5 autocomplete query "1279 37 st" carries a street-TYPE abbreviation,
which is NOT the contracted digit-run ordinal fold; the packet's normalization rule fails unclear
cases closed. Correction applied as tagged `[ORCH-CORRECTED]` commit `ce4a9ed2` (task branch) /
`fb7af67d` (candidate): AS-5 now asserts shape tolerance + the fail-closed no_match; new AS-5b
proves the resolved path on the same body via the gate's explicit reference-parse parameter.
No production code changed in the correction (test file only). context-budget + secret-scan were
green at both heads.

Local documented command (orchestrator, repo root, material head): `python
tools/modularity_check.py --check` → exit 0 (all warnings pre-existing).
