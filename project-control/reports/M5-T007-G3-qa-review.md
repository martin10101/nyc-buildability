# M5-T007 — G3 QA Review (independent)

- **Gate:** G3 (QA / test adequacy / regression / mutation)
- **Verdict:** PASS
- **Reviewer:** qa-engineer (independent; ≠ producer scenario-optimization-engineer)
- **Reviewed SHA:** `1f938f4a7b174c0338c0ecdb2ef0c6b14bdba436`

## Identity
Reviewer auto-isolated into its own worktree (Write-capable); the worktree-isolation guard refused `git -C ctl24` commands. Identity resolved read-only via git ref files: `ctl24/.git`→worktree gitdir→HEAD ref `candidate/D-024-mrl-option-b`→`1f938f4a…` (matches). Reproduced the suite against the ctl24 files by absolute path. (Non-blocking limitation: could not run `git status --porcelain` on ctl24 to confirm cleanliness — orchestrator confirmed the ctl24 tree is clean at 1f938f4a apart from two unrelated qa-memory untracked files, so committed blobs == reviewed files.)

## Reproduction & regression — PASS
`pytest services/api/tests/scenario` → 173 passed (Python 3.11.9, pytest 8.4.2). Per-file: ranking 49 passed; suite minus ranking 124 passed (0 regression). `--collect-only`: contract 23 + derive 70 + foundation 31 + ranking 49 = 173 (matches producer claim exactly). `modularity_check --check` → failures 0, ranking.py not in the 14 warnings.

## Boundary adequacy (7 hard boundaries)
1 explicit-only/never-fabricates — Covered (AS-3). 2 named objective on ranking AND every candidate — Covered (AS-2). 3 score = surfaced numbers only, no recompute — Strong (AS-2/AS-6/AS-7 assert candidate["derived"] == derive_practical_usable_range(...)). 4 total/stable/input-order-independent — Strong (AS-1 byte-identical forward/reversed/shuffled with a genuine tie; sort_keys-pitfall regression). 5 fail-closed + strict-JSON-safe — Strong (10 AS-4 functions; `_strict_json_safe` on every path). 6 never up-labels/never Verified — Covered (AS-5). 7 contract-free/read-only/offline — Covered (AS-6 inputs byte-unchanged/not-aliased; offline structural); "contract-free" asserted indirectly (thin but non-blocking; the real risk store/present-as-Verified is covered by boundary 6).

## Mutation sense-check — both caught by non-vacuous tests
- A: drop content_key tie-break (order becomes input-dependent) → caught by `test_as1_equal_score_reordered_key_dicts_are_input_order_independent` + byte-identical AS-1.
- B: remove `_json_safe` sanitizer → caught by AS-4 (reproduced independently: json.dumps NaN allow_nan=False → ValueError; raw negative fails ≥0; 10**5000/raw object → ValueError/TypeError).

## Rev-2 RED evidence (reasoned, not recorded) — acceptable / non-blocking
Verified the pre-fix failure modes are deterministic language-level facts (repr(10**5000)→ValueError int_max_str_digits=4300; object repr contains ` at 0x…`), post-fix suite reproduced green, assertions non-vacuous. A captured pre-fix red transcript would be gold-standard but its absence does not block PASS.

## Findings
Blocking: none. Non-blocking: (1) rev-2 RED reasoned not recorded (acceptable, independently verified); (2) boundary-7 contract-free asserted only indirectly (low value).
