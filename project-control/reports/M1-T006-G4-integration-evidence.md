# M1-T006 — G4 integration and regression evidence (orchestrator-captured)

- **Task:** M1-T006 property-profile contract v1.1 (additive)
- **Date:** 2026-07-16
- **Merge commit:** `9c16597` (no-ff merge of `task/M1-T006-contract-v1-1` = producer `32f0159` + orchestrator pairing `82d43ef`); ledger commit `fb5594a` (CI ran at this head)
- **Recorded by:** orchestrator (evidence-capture per ADR-005 / .claude/rules/project-control.md)

## CI evidence (authoritative — GitHub Actions runner ships jsonschema 4.10.3, the legacy resolver path is LIVE here)

| Workflow | Run | Commit | Result |
| --- | --- | --- | --- |
| CI (4 jobs incl. contracts validator + api suite) | [29543679819](https://github.com/martin10101/nyc-buildability/actions/runs/29543679819) | `fb5594a` | completed / **success** |
| secret-scan | [29543679714](https://github.com/martin10101/nyc-buildability/actions/runs/29543679714) | `fb5594a` | completed / **success** |

Command: `gh run list --commit fb5594a2118417c9622b61002fd383f033a65886 --json databaseId,name,status,conclusion,url` → both `completed/success`.

The CI contracts job re-ran `validate_contracts.py` over the v1.1 schema and all fixtures **on the real jsonschema 4.10.3 runner** — this is the authoritative legacy-path evidence the G3 reviewer deferred to (its local environment had 4.26). The api job re-ran the 142-test suite including the S1 contract-validation test with the corrected 4-document registry.

## Local integration checks (orchestrator, main checkout at merge)

- Full validator: exit 0, `Checked 6 schema file(s); 0 failure(s)`, all 7 valid fixtures OK, all invalid fixtures rejected for intended reasons (run pre-merge in the worktree at identical tree).
- Validator pytest suite: 24 passed.
- Full API suite: 142 passed (post-pairing).
- Backward compatibility: `full_example.json` and the three sibling schemas byte-identical to base; every pre-existing v1.0.0 fixture passes against v1.1.
- No duplicate/contradictory implementations: the only `services/` change is the one-line test-registry pairing.
- Low-storage: ~90 KB new repo content, no installs, no datasets, no temp artifacts left (pytest caches are git-ignored).

## Result

**G4 PASS.** Contract compatibility, full suite, regression, and low-storage checks all green; CI green at `fb5594a` on both workflows.

## Non-blocking carry-forwards (from G3, recorded for the backlog)

- D1 (Low): wire `.github/scripts/tests` into a CI job at the next workflows touch (hygiene batch — workflows were a forbidden path for this task).
- D2/D5 (Info): `uniqueItems` for provenance_ref_list and the partial-linkage default — next contract minor.
- D4 (Info): when the M2 builder task emits district maps, bump `PROFILE_CONTRACT_VERSION` to "1.1.0" and extend `_assert_provenance_integrity` with both map rules.
