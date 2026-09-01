# M0-T134 G4 — independent QA review (MRL Tranche A, D-024 Amendment 39)

**Gate:** G4 (independent QA) · **Reviewer:** qa-engineer (read-only; not the producer)
**Reviewed HEAD / identity:** `ad770ad4` / `1c3078c6…` · **Verdict: PASS.**

QA independently executed the suites and audited every test file for genuine fail-closed/mutation
coverage (a second independent read-only agent re-derived the two security-critical cases).

## Reproduced results (raw exits)
- **Tranche-A suite** (7 files, direct pytest): `77 passed`, raw exit **0**.
- **Full supervisor suite** (`tools/test_agent_supervisor_*.py` + `test_gate_runner.py`, 3146 collected):
  **3144 passed, 2 skipped, 0 failed** in 239s — behavior-neutrality of the split confirmed at the
  final tree.
- **gate_runner machine record** `M0-T134-tranche-a-evidence.json`: `repo_head 5e89175d`, `repo_tree
  f8d3bbd4` (== `git rev-parse 5e89175d^{tree}`), `returncode 0`.
- **modularity_check --check** unpiped: raw exit **0**. **ruff 0.13.0**: all checks passed (14 files).
- **validate_directive_compliance --check**: exit 0.

## Per-file negative/mutation coverage (audited, not tautological)
- **split (10):** `assertIs` facade identity across 7 names + cli path; missing/conflicting-duplicate/
  multiple-distinct/invalid checkpoint all fail closed.
- **worker_result (15):** unknown/forged (8-key loop), wrong type, bad enum, excess length, non-object,
  empty summary rejected; controller-authority positive proves facts come from the controller.
- **codex_decision (16):** dup/non-controller/over-cardinality evidence ids; provider SHA as unknown
  field; APPROVE→HOLD on failing invariants/gates; strict-`is True` (1/'yes'/[1]→HOLD); malformed SHA
  and empty ref/url fail closed.
- **remote (6):** empty url, empty ref, no-sha, non-hex sha fail closed (injectable runner; no network).
- **transport (8):** forbidden flags, no fallback model, non-positive budgets, empty prompt, single
  spawn, no re-spawn on provider continuation.
- **exec_identity (11):** load-bearing same-size(16B)+`os.utime`-restored-mtime replacement still
  rejected; reorder; missing DISABLE_AUTOUPDATER; DISABLE_UPDATES prohibited; runtime model/version
  match+mismatch+empty. Positive counterpart proves the guard is not always-raise.
- **gate_runner (11):** shell-string refused; real `powershell.exe` pipe records the child's raw exit
  (independently corroborated, value 9); large stdout does not mask exit; mutation killed→ok,
  survivor→not-ok, expect-zero pass.

## Judgement
All positive tests have negative/mutation counterparts; no fake or tautological assertions. The three
minor observations (AS-4 attribution, `&` flag, gate_runner PowerShell scope-note) are consistent with
correct Tranche-A scope and are disclosed as Tranche-B obligations in the producer report §6. No defect;
no failed acceptance scenario. **PASS.**
