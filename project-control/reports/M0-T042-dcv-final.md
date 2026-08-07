# Directive-Compliance Verification — M0-T042 (D-010 regime) — FINAL

## Overall verdict: **PASS** — ACCEPT-READY: **YES**

All 13 bound requirements are **SATISFIED** on primary evidence the verifier reproduced itself (source files, tests executed, git objects). Code identity is frozen and provably invariant across all gates; scope is clean; SHADOW-ONLY and R595-blocking posture are intact; nothing is merged/accepted/deployed. The one open item (G5 L-1 robustness defect in `parse_usage_telemetry`) is a shadow-only, no-live-path robustness gap correctly deferred to the R595 activation checklist — it does not violate any of the 13 bound rows.

Verifier: directive-compliance-verifier (independent; read-only; producer ≠ verifier).

## Frozen target verified
- **HEAD at verification** = `ea34c3b92d1b6b32b284651275032049f6bc64f9` (branch `task/M0-T042-codex-review`), a successor of `4004be2`.
- **Producer code froze at `9a1c7e1`**: `git diff 9a1c7e1..HEAD -- tools/ AGENTS.md` is **empty**. Also proved empty for the intervening review commits `e6a1b51` and `ba1d045`. Post-`9a1c7e1` commits touch only `project-control/`.
- Dependency M0-T041 is **accepted** (`state.json:38`), making M0-T042 the first dependency-valid wave-1 unit; M0-T042 was in `active_tasks` (not yet accepted) at verification — correct pre-acceptance posture.

## Observed test results (verifier's own runs, orch worktree)
| Command | Result |
|---|---|
| `python -m unittest discover -s tools -p "test_agent_supervisor_*.py"` | **Ran 1216 in 70.6s — OK (skipped=2)** ⇒ **1216 / 1214 / 0 / 2** |
| `python -m unittest tools.test_agent_supervisor_ephemeral_review` | **Ran 27 — OK** |

Matches the producer/reviewer claims (1216/1214/0/2 and 27) exactly.

## Identity statement (independently reproduced)
- **Frozen code SHA:** `9a1c7e1`. Byte-identical to HEAD on `tools/` and `AGENTS.md` (empty diffs).
- **`content_manifest_sha256` = `2db3109265d55ab3cf7b5c1b22eaea87fa3b752f7d951f4ea3b29b69a8f3fb17`**, invariant across **G2, G3, G4, G5** (read from each gate record). G0 differs (`5e56ef61…`) because G0 is the pre-code readiness gate at base `0ed2cdb` — expected.
- **Independent recomputation:** the work-product manifest component (via `directive_registry.git_tree_manifest` over the non-control allowed paths) = `5725cafb8b3b9cd6…`, **identical (55 entries) across `e6a1b51`, `9a1c7e1`, `ba1d045`** — the reviewed code content is one frozen identity. The invariant combined manifest holds despite lifecycle-bookkeeping edits because the control-plane component uses the material-digest boundary (status/progress/timestamps/reports excluded by design).

## Scope discipline — CONFIRMED
`git diff 0ed2cdb..9a1c7e1 --name-only` touches only: `AGENTS.md`; `tools/agent_supervisor/{README.md,__init__.py,codex_reviewer.py,ephemeral_review.py,review_cadence.py,review_packet.py}`; `tools/test_agent_supervisor_ephemeral_review.py`; and orchestrator control-plane files (`project-control/gates/`, `reports/`, `state.json`, `tasks/M0-T042.json`). **No forbidden path** (`.claude/`, `apps/`, `services/`, `.github/`, `project-control/directives/`, any dependency manifest/lockfile) — grep returns NONE; the `project-control/directives/` diff over `0ed2cdb..HEAD` is empty.

## Prohibition & posture evidence
- **R082 (no persistent controller):** grep for persistent-controller/session-resume in the new modules returns only negative references ("never activated"); `conduct_ephemeral_review` raises `role_not_activatable` for any non-reviewer role.
- **R042 (no CLAUDE.md duplication):** AGENTS.md (79 lines / 3893 B) < CLAUDE.md; explicit non-duplication statement (L3-5); test asserts ≤2 shared ≥40-char lines — passes.
- **AD-083 (no prohibited inclusion by default):** `guard_packet` fails closed (rejects, `packet=None`) and runs FIRST in the loop before any process.
- **SHADOW-ONLY / R595:** new modules imported nowhere in `loop.py`/`cli.py` (G3/G5 grep-confirmed); no activation path. Pre-R595 items **L-1, I-1, I-3** registered on `project-control/reports/M0-T036-ACTIVATION-CHECKLIST.md` (lines 45-58) as MUST-RESOLVE-before-activation. R595 remains mandatory-blocking.
- **Prohibited actions:** M0-T042 **not** in `accepted_tasks` at verification; HEAD **not merged** into `origin/main` (`origin/main` == merge-base `0ed2cdb`); no dependency install/deploy/purchase/PR-close. Clean.

## Process / continuity (R116)
Lifecycle ran the proven workflow with an honest FAIL+rework: G0 PASS+claim (`23ae610`) → producer (`f9d1390`) → evidence map (`6b4b909`) → submit (`fa69f9e`) → independent **G3 PASS** (`556a38f`) + **G4 FAIL** (`ac9d89b`, manifest `feb84dc5`, AS-3/R083 coverage gap) → rework (`dc9e961`) → resubmit (`9a1c7e1`) → **G3/G4 re-review PASS** (`4004be2`) → **G5 PASS** (`ea34c3b`) → this DCV. The G4 FAIL is genuinely in git history at a different (pre-rework) manifest. No new obligations (directives untouched); holds/SHADOW-ONLY/R595 unchanged. Gate reviewers (code-reviewer, qa-engineer, security-reviewer) are independent of the producer.

## 13-row verdict table

| ID | Verdict | Method | Primary evidence |
|---|---|---|---|
| D-010-R027 | PASS | DEEP | `ephemeral_review.py:225-317` fresh process per call; `_independence_proof` L130-143; test `test_a_second_review_shares_no_state_with_the_first` L173-190 (distinct packet_digests + distinct `verified_facts.packet_bytes` from real subprocesses) — executed OK. |
| D-010-R041 | PASS | DEEP | `AGENTS.md` (79 lines) covers all 13 §11.1 items (mission L7, state L12, session L17, never-guess L23, deterministic L28, boroughs L33, path L37, evidence L41, autonomy L46, hard-stops L53, routing L58, code-graph/context L65, checkpoint L73); referenced `schemas/codex_decision.schema.json` + `tools/code_graph/query.py` exist; AS5 topic test passes. |
| D-010-R042 | PASS | DEEP | `AGENTS.md:3-5` explicit non-duplication; `test_agents_md_does_not_duplicate_claude_md_wholesale` (bytes<CLAUDE, <120 lines, ≤2 shared ≥40-char lines) passes; both files read — distinct Codex-specific prose. |
| D-010-R081 | PASS | DEEP | `conduct_ephemeral_review` is sole loop entry, runs only the fresh read-only reviewer; no persistent-default path (grep empty); AS-1 green. |
| D-010-R082 | PASS | DEEP | grep for persistent-controller/session-resume → none (only "never activated"); role guard `role_not_activatable` L248-253; no controller thread created; G3/G5 concur. |
| D-010-R083 | PASS | DEEP | `guard_packet` L380-403 fails closed on all 0A.1 categories (transcript, directive_registry, all_reports, whole_repository, all_logs, full_code_graph, unrelated packets, completeness flags); loop step 1 refuses before any process; tests L294-375 incl. rework-added `all_logs`/`full_code_graph`/completeness fixtures — all pass. |
| D-010-R084 | PASS | DEEP | `review_cadence.decide_review` L114-128: trigger→review, deterministic-pass-only→reasoned refusal, no-signal→no-review; `REVIEW_TRIGGERS` maps to 0A.3 list; 5 AS-4 tests pass. |
| D-010-R085 | PASS | DEEP | `ReviewBudget` defaults = 0A.4 (32k/64k/20%); `effective_ceiling` L113-135 returns lower-of; re-derived None→64000, 400k→64000, 200k→40000; tests pass. |
| D-010-R086 | PASS | DEEP | `SPLIT_SUMMARIZE_GUIDANCE` L141-148 incl. "never…giant persistent Codex conversation"; loop step 2 returns durable refusal, reviewer never called (`calls==0` test); no persistent escape. |
| D-010-R087 | PASS | DEEP | `_reopened_sources` L146-167 records cited-but-not-supplied sources with reason; AS-1 asserts `engine.py` reopened, `tasks/M0-T042.json` not — bounded packet, no full re-investigation. |
| D-010-R088 | PASS | DEEP | non-reviewer role raises `role_not_activatable` L248-253; `record_worker_fallback` L320-350 builds record, launches nothing, grants no write; both tests pass. |
| D-010-R093 | PASS | DEEP | Enumerated all 30 public surfaces in the 3 new modules + `parse_usage_telemetry`; each traces to a cited requirement (ephemeral_review→0A.1 items1-7/AD-027/087/088; review_cadence→0A.3/AD-084; review_packet→0A.4/AD-085/086+AD-083; usage telemetry→0A.1 item7/0A.7/AD-022). Qualifying evidence: 0A.8 item 4 (blocking min-autonomy capability). No speculative surface; additive bounded diff. |
| D-010-R116 | PASS | Continuity | M0-T041 accepted (`state.json:38`)→M0-T042 first dependency-valid unit per `source-006-amendment.md:28`; full G0→producer→submit→G3 PASS/G4 FAIL→rework→G3/G4/G5 PASS→DCV lifecycle in git log; directives untouched (no new obligations); SHADOW-ONLY/R595/holds unchanged; nothing merged/accepted. |

## Rows not PASS

None. (Advisory note, not a downgrade: G5 **L-1** — `parse_usage_telemetry` raises an uncaught `ValueError` on a >4300-digit integer in untrusted `--json` stdout. Real but reachable only against a live untrusted Codex process, which cannot occur under SHADOW-ONLY; usage telemetry is correctly recorded for all normal/tested inputs. Correctly pinned to the R595 activation checklist as must-fix-before-activation. Does not violate any bound row and does not block acceptance of this shadow-only task, since R595 — where L-1 must be fixed — remains mandatory-blocking.)

## Machine-readable rows

```json
{"rows": [
{"id": "D-010-R027", "state": "PASS", "evidence": ["tools/agent_supervisor/ephemeral_review.py:225-317 fresh process per call", "_independence_proof L130-143", "test_a_second_review_shares_no_state_with_the_first L173-190 executed OK (distinct packet_digests + packet_bytes)"]},
{"id": "D-010-R041", "state": "PASS", "evidence": ["AGENTS.md covers all 13 Section 11.1 items (lines 7,12,17,23,28,33,37,41,46,53,58,65,73)", "referenced schemas/codex_decision.schema.json and tools/code_graph/query.py exist", "test_agents_md_exists_and_covers_the_11_1_topics OK"]},
{"id": "D-010-R042", "state": "PASS", "evidence": ["AGENTS.md:3-5 explicit non-duplication", "test_agents_md_does_not_duplicate_claude_md_wholesale OK (bytes<CLAUDE, <120 lines, <=2 shared >=40char lines)"]},
{"id": "D-010-R081", "state": "PASS", "evidence": ["conduct_ephemeral_review sole loop entry runs only fresh read-only reviewer", "no persistent-default path (grep empty)", "AS-1 green"]},
{"id": "D-010-R082", "state": "PASS", "evidence": ["grep persistent-controller/session-resume in new modules returns none", "role_not_activatable guard ephemeral_review.py:248-253", "G3/G5 concur no persistent session"]},
{"id": "D-010-R083", "state": "PASS", "evidence": ["guard_packet review_packet.py:380-403 fails closed on all 0A.1 categories", "conduct_ephemeral_review step1 refuses before process", "test file L294-375 incl rework all_logs/full_code_graph/completeness fixtures pass"]},
{"id": "D-010-R084", "state": "PASS", "evidence": ["review_cadence.decide_review L114-128 both-directions", "REVIEW_TRIGGERS maps to 0A.3 list", "AS4 tests OK"]},
{"id": "D-010-R085", "state": "PASS", "evidence": ["ReviewBudget defaults 32k/64k/20%", "effective_ceiling L113-135 lower-of; re-derived None->64000,400k->64000,200k->40000", "AS2 tests OK"]},
{"id": "D-010-R086", "state": "PASS", "evidence": ["SPLIT_SUMMARIZE_GUIDANCE review_packet.py:141-148 incl no-giant-persistent-conversation", "durable refusal record, reviewer.calls==0 test"]},
{"id": "D-010-R087", "state": "PASS", "evidence": ["_reopened_sources ephemeral_review.py:146-167 records cited-not-supplied with reason", "AS-1 asserts engine.py reopened, tasks json not"]},
{"id": "D-010-R088", "state": "PASS", "evidence": ["role_not_activatable ephemeral_review.py:248-253", "record_worker_fallback L320-350 launches nothing/no write", "test_worker_role_is_never_activated + test_worker_fallback_is_a_recorded_exception OK"]},
{"id": "D-010-R093", "state": "PASS", "evidence": ["all 30 public surfaces in 3 new modules + parse_usage_telemetry trace to cited reqs (0A.1/0A.3/0A.4/AD-083/AD-085/AD-086/AD-087/AD-088/0A.7/AD-022)", "qualifying evidence 0A.8 item 4 blocking capability", "additive bounded diff, no forbidden path"]},
{"id": "D-010-R116", "state": "PASS", "evidence": ["M0-T041 accepted state.json:38 -> M0-T042 first dependency-valid unit per source-006-amendment.md:28", "git log G0->producer->submit->G3 PASS/G4 FAIL(ac9d89b)->rework(dc9e961)->resubmit(9a1c7e1)->G3/G4/G5 PASS->DCV", "project-control/directives/ diff 0ed2cdb..HEAD empty (no new obligations)", "SHADOW-ONLY/R595 unchanged; L-1/I-1/I-3 on M0-T036-ACTIVATION-CHECKLIST.md:45-58; HEAD not merged to origin/main; M0-T042 not accepted"]}
]}
```

Every requirement ID is SATISFIED on reproduced primary evidence; no VIOLATED or UNVERIFIABLE rows. This directive task is verifiably complete at the frozen head and **ACCEPT-READY**. Recommended orchestrator record: write the verification row (applicable set = the 13 rows) at accept-time HEAD with `reviewed_sha == HEAD` and material identity `2db3109265d55ab3cf7b5c1b22eaea87fa3b752f7d951f4ea3b29b69a8f3fb17`, then accept.
