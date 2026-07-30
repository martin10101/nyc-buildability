# M2-T018 — G5 security review (D-004 Step 4 pilot; fresh-session reviewer return, captured verbatim)

Orchestrator capture note: reviewer = security-reviewer, unnamed spawn, explicit Fable 5, frozen
SHA `756f60164e5cf27c56082166047ffc119a5f3d02` (task/M2-T018-serializer-wiring). Return preserved
verbatim below (transport entity-decoding only).

---

All evidence gathered. Here is the G5 report, returned verbatim for the orchestrator.

---

# Gate Report

- Gate ID: G5 (security review)
- Task ID: M2-T018
- Reviewer: security-reviewer (independent, read-only)
- Producer: backend-engineer (per commit message; unnamed producer spawn, D-004 Step 4 pilot)
- Result: **PASS**
- Clean environment/worktree used: `.claude/worktrees/M2-T018-serializer-wiring` — `git rev-parse HEAD` = `756f60164e5cf27c56082166047ffc119a5f3d02` (exact match to the frozen SHA; `git status --porcelain` empty). Diff base `84c1bf29243bb862d344c909099c9bd9a3f6a766` confirmed as the sole parent of the frozen commit (single commit, no intermediate history).

## Acceptance criteria reviewed

AS-1 (fail-closed on undocumented key, never an invalid 200), AS-2 (four connector shapes cross the boundary, lineage keys survive, no bypass, schema copies consistent), AS-3 (tripwire pins the single import boundary), AS-4 (provenance completeness/fidelity), AS-5 (suites + drift checks green — verified for the three required suites; full-suite and drift checks are G2/G3 lane), AS-6 (attestation + no producer git writes) — all re-derived from the packet `project-control/tasks/M2-T018.json` at the frozen SHA, not taken from the producer report.

## Directive/requirement verification

The task is in-regime (`directive_refs: D-004:ALL`, 300+ requirements). The exhaustive requirement-by-requirement D-004 pass is the `directive-compliance-verifier`'s lane per `/run-quality-gate`; below are the D-004 requirements that fall inside this G5 security lane, each re-derived from `project-control/directives/D-004-agent-teams-runtime-adoption/requirements.json` at the frozen SHA and verified against artifacts (producer's map treated as claims, reproduced independently):

| Requirement ID | Reviewed SHA / content identity | Verdict | Reproduced evidence |
|---|---|---|---|
| D-004-R300 | 756f6016 | PASS | M2-T018 is the contracted lane-2 pilot task named in the requirement text; packet exists at the SHA and matches (serializer wiring + fail-closed tests). |
| D-004-R302 | 756f6016 | PASS | Producer report §0.2 records all four attestation values for the assigned worktree (path, toplevel, branch `task/M2-T018-serializer-wiring`, HEAD `84c1bf2…` = EXPECTED_BASE_SHA) captured before first write; harness deviation (work done in the harness-assigned isolated worktree) disclosed in §0.1/§0.3 with byte-identity proof of the ten in-scope files, not concealed. |
| D-004-R303 | 756f6016 | PASS | Diff file list (7 files) ⊆ `allowed_paths`; zero forbidden paths touched; frozen commit author+committer is the orchestrator identity (`martin10101 <myhappybook212@gmail.com>`), not a producer; report requests status `awaiting_gate`. |
| D-004-R023 / D-004-R024 | 756f6016 | PASS | Redaction scan of the full diff and producer report: no session IDs, no pane IDs, no absolute user paths (`C:\Users`, `MLFLL`, `/home/`, `AppData` → zero hits), agent id redacted as `agent-<id>`. See INFO-4 for a pre-existing commit-trailer note outside the reviewed tree. |
| D-004-R306 | 756f6016 | PASS | Diff touches no settings, no effort keys, no M0-T025, no expansion surfaces, no deployment files — only the 7 in-scope files. |

## Steps independently executed

All commands run read-only against the frozen worktree (absolute paths; cache/bytecode writes suppressed):

1. `git -C <worktree> rev-parse HEAD` → `756f6016…` (match); `git status --porcelain` → clean.
2. `git diff --stat` and `--name-only` base..frozen → 7 files, 1070 insertions / 26 deletions.
3. `git diff base..frozen -- serializers.py __init__.py source_fact.schema.json(x2) property_profile.ts contract.py` → **empty** (all unchanged).
4. SHA-256 of both `source_fact.schema.json` copies → both `2577d2aabe6fb9c4732dd43eeda815630fd0b804dd345366b96c4b94e5380540`, 11876 bytes (byte-identical; matches producer claim).
5. Read-only inspection: `builder.py` (`_closed_provenance`, both splice points), `serializers.py` (error classes/messages), `properties.py` (full exception path), `rule_evaluation.py` (full exception path), `wave_integration.py`, `zoning_crosscheck.py`, both new test files, tripwire amendment diff.
6. Grep enumeration: writers to `profile["provenance"]` under `app/**`; callers of `build_property_profile`; callers of `additional_provenance=`; `except` clauses in `app/profile/**`; `is_serializable` call sites.
7. Diff scans: eval/exec/subprocess/dynamic-import, network primitives, credential-shaped strings, machine paths, session ids.
8. `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/contracts tests/profile tests/api -q -p no:cacheprovider` in `<worktree>/services/api` → **243 passed in 5.74s**.
9. `git show --no-patch --format=fuller 756f6016` → orchestrator-identity commit; trailer convention checked across the prior 20 commits (7 carry the same trailer — pre-existing).

## Expected versus actual

| Check | Expected | Actual |
|---|---|---|
| Frozen SHA | 756f6016… | 756f6016… (match) |
| Test suites | 243 passed | 243 passed |
| Serializer vs base | unchanged | unchanged (empty diff) |
| Schema copies | byte-identical | identical, SHA 2577d2aa… |
| Generated TS | untouched | untouched |
| Diff containment | ⊆ allowed_paths | 7/7 files inside; 0 forbidden |

## Findings per scoped dimension

**1. Information disclosure on the failure path — PASS.** `UnknownFieldError`/`MissingFieldError` messages name offending **keys only, sorted, never values** (`serializers.py:79-97`). Both routes call the builder inside a broad `except Exception` mapping to `_internal_error_500`: `properties.py:407-408` logs `type(exc).__name__` + correlation id only (never `str(exc)`/traceback, `properties.py:172-175`) and returns the fixed generic body. The new wire test (`test_provenance_boundary_api.py:83-106`) genuinely asserts non-leakage on a real HTTP response (`raise_server_exceptions=False`): status 500, `state == "internal_error"`, correlation id in body and `X-Correlation-ID` header, `"provenance" not in body`, and — against the raw response text — neither the injected key name `_debug_stacktrace`, nor `SUPER_SECRET`, nor the full injected value. The builder-level test `test_as1_rejection_never_leaks_the_offending_value` additionally asserts the exception message itself carries the key but never the value.

**2. Injection surface — PASS.** Exhaustive enumeration under `app/**`: exactly two writers into `profile["provenance"]` — `builder.py:763` (initial splice: `result.facts` + `additional_provenance`) and `builder.py:828` (wave/spatial extend) — both wrapped in `_closed_provenance`. Exactly two production callers of `build_property_profile` (`properties.py:393`, `rule_evaluation.py:226`); neither bypasses. `additional_provenance` is spliced *before* serialization, so any future production caller of that argument inherits the boundary automatically. `zoning_crosscheck.py` emits no `source_fact` records (verified by grep, not just the docstring) — conflicts/notes only. Tests inject undocumented keys into all three feeds, including a monkeypatched wave feed proving the second call site is live, plus the optional-field-typo and missing-required cases. Key-level injection fails closed everywhere. Named gaps (both disclosed, neither a defect of this change): (a) a future assembler that never calls `build_property_profile` skips the boundary — the response path is backstopped by `validate_profile` against the closed schema (`additionalProperties:false`, `source_fact.schema.json:111`); a future storage path would need the boundary explicitly (producer R3); (b) see INFO-3 on value-level nesting.

**3. Fail-closed vs fail-open regression — PASS.** Traced the full path: zero `try/except` in `builder.py` and `wave_integration.py`; the only excepts in `app/profile/` are `contract.py:158` `(KeyError, TypeError)` and `contract.py:249` `ImportError` — neither can catch `ContractSerializationError` (a `ValueError`). `is_serializable` (which swallows exceptions into a bool) is defined but **never called** in production code. The routes' broad `except Exception` converts the error to a typed 500 — that is the designed fail-closed sink, not a swallow; no path returns 200 or a partial profile after a rejection.

**4. Hygiene — PASS.** No dependency/lockfile changes (file list is 7 files); no `eval`/`exec`/`subprocess`/`importlib.import_module`/`__import__` added (the two grep hits are doc-text describing what the tripwire *catches*); no network primitives added (fixture transports only); test "secrets" are obviously-fake canaries (`SUPER_SECRET_abc123` with `noqa: S105`) and the injected IP is TEST-NET-3 documentation space (`203.0.113.7`); no machine-specific paths or usernames anywhere in the diff.

**5. Contract integrity — PASS.** `serializers.py`, `contracts/__init__.py`, both `source_fact.schema.json` copies, `packages/contracts/generated/property_profile.ts`, and `profile/contract.py` are all byte-identical to base (empty diff). Schema copies hash-identical to each other and to the producer's stated SHA. The serializer was not weakened — it was not touched at all, exactly as the producer stated.

**6. Containment + provenance of the change — PASS.** All 7 changed files inside `allowed_paths`; no forbidden path touched. Single commit atop the exact declared base. Commit made under the orchestrator's git identity (producer ran no git — consistent with R303/ADR-005). Producer report contains the attestation values, the fully-disclosed harness worktree deviation with byte-identity proof, and is clean of session ids/user paths.

**7. Test reproduction — PASS.** `python -m pytest tests/contracts tests/profile tests/api -q` in the worktree's `services/api`: **243 passed**, matching the expected count exactly.

## Severity-ranked findings

- **INFO-1 (pre-existing, out of this diff's scope):** `rule_evaluation.py:116-119` — `_internal_error_500`'s docstring claims "Logs the type + correlation id only," but its two call sites (`rule_evaluation.py:193-197`, `285-290`) log stage + correlation id **without** the exception type. Information-reducing, not a leak; the file is a forbidden path for this task and unchanged. Worth a docstring/log fix in a future in-scope task.
- **INFO-2 (disclosed residual, producer R3):** the boundary lives in `build_property_profile`; a future profile assembler or direct-storage path bypassing the builder would skip it. Response path is backstopped by `validate_profile` + `additionalProperties:false`; any future Supabase provenance-persistence task must route through the boundary explicitly.
- **INFO-3 (accepted M2-T017 design, no regression):** `input_vintages` is a documented key whose inner map is deliberately open (`source_fact.schema.json:103`), and documented values (e.g. `original_value`) carry verbatim source content — so value-level smuggling *inside* documented keys is outside the key-level boundary by design. Defense for stored external content remains the value-layer (JSON schema) plus the standing rule that ingested source text is untrusted data, never instructions (`.claude/rules/backend-api.md`).
- **INFO-4 (orchestrator lane, outside the reviewed tree/report):** the frozen commit's message carries the harness-standard `Claude-Session` URL trailer. This is a pre-existing repo-wide convention (7 of the 20 commits preceding the base carry it) and the producer report itself is clean; noting it only because D-004-R024's broad wording ("anything written to the repository") vs. the harness commit-trailer mandate is an owner/orchestrator reconciliation question, not a defect of this task.

## Defects

None at CRITICAL, HIGH, MEDIUM, or LOW severity. The four INFO items above require no rework of this task.

## Required rework

None.

## Reviewer conclusion

The change is a textbook fail-closed boundary: one function, two call sites covering every writer into the provenance array, exceptions that name keys never values, routes that convert them to a generic typed 500 with correlation-id-only logging, non-leakage proven at the real wire, the frozen serializer and both schema copies untouched and hash-verified, a strictly stronger tripwire, clean diff hygiene, and full containment with orchestrator-only git. All seven scoped security dimensions verified independently at the frozen SHA; 243/243 tests reproduced.

VERDICT: PASS — every scoped security dimension was independently verified at the frozen SHA with no defect above INFO severity, and the 243-test evidence reproduced exactly.

---

*(Orchestrator capture notes: one absolute Windows worktree path in the reviewer's environment line
was normalized to the repo-relative form per the no-machine-specific-data rule; the reviewer's own
redaction scan of the reviewed artifacts found zero machine-specific data. No other alteration.)*
