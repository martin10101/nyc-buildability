# M0-T147 producer report — review-contract convergence (deficit-convergence closure)

- **Task:** M0-T147 (governance; qualifying evidence: **provider CLI drift** codex-cli
  0.146.0 → 0.153.4, supervisor-freeze §2, + owner directive D-032 R001/R005 / D-024
  source-054-amendment).
- **Producer:** orchestrator (owner-authorized, M0-T146 precedent).
- **Date:** 2026-09-06.

## 1. The defect (reproduced 4×, then root-caused by a minimal probe)

Every live gpt-6-astra review in runs persistent-local-01/02/03 returned ROTATE_SESSION.
Journal transitions 79/91 record the reviewer's own reason verbatim: *"Execution policy
rejected both bare git commands and local file reads … this is an environment failure, not a
demonstrated worker safety violation."*

Rule-7 probe at the reviewer's exact argv (`codex exec -C <repo> --ephemeral
--ignore-user-config --strict-config --sandbox read-only …`) on codex-cli **0.153.4**/Windows:

- `git status --porcelain` → `rejected: blocked by policy` (PowerShell-wrapped by the CLI's
  shell adapter; the trust matcher cannot see through the wrapper)
- relative file read → `rejected: blocked by policy`
- raw-argv exec → tool schema is string-only (no argv form); no dedicated file-read tool
- `sandbox_permissions` config key → does not exist on 0.153.4 (strict-config refuses)

Conclusion: the M0-T131-era measured boundary ("cwd-relative reads are ALLOWED", measured on
0.146.0) is FALSE on the installed CLI. The contract mandated live verification the reviewer
can never perform; an honest high-effort reviewer therefore refused to approve, forever.

## 2. The bounded cluster (exactly two code changes + tests)

| Path | Change |
|---|---|
| `tools/agent_supervisor/evidence.py` | Added the `diff_content` git fact (`git diff HEAD`) to `GIT_FACT_COMMANDS` — the ONLY item of the contract's live-verify list the packet did not already carry (branch/head/porcelain_status/changed_files/diff_summary/ahead_behind already collected). Digest-bound and truncation-bounded by the existing machinery; `assert_read_only_git` admits it (bare `diff` already enumerated). |
| `tools/agent_supervisor/codex_reviewer.py` | `REVIEW_INSTRUCTIONS` rewritten (+ its provenance comment): measured access is now stated as **NONE** (no command execution, no file reads; a rejected attempt is expected, by design, and NEVER grounds for ROTATE_SESSION/HALT_UNSAFE); verification is fully **packet-based**, cross-checking checkpoint claims against the digest-bound `git.*` sections including the new `git.diff_content` patch text; truncated/failed collections are weighed honestly (REVISE for material worker-evidence gaps); HALT_UNSAFE reserved for genuine safety findings; checkpoint stays UNTRUSTED. |
| `tools/test_agent_supervisor_reviewer.py` | Anchors updated to the new load-bearing phrases; NEW negative test (the false 0.146-era promises may never reappear); NEW packet test proving `diff_content` is enumerated with tail `("diff","HEAD")`, admitted by the read-only guard, and flows value+digest into `packet.sections["git"]` (mutation tooth: removing the collector entry turns it RED). |

No schema change; no provider-facing constraint added; loop/broker/policy untouched.

## 3. Validation

- `python -m pytest tools/test_agent_supervisor_reviewer.py -q` → **94 passed** (exit 0).
- `ruff check` on all three files → clean.
- `python tools/modularity_check.py --check` → 0 failures.
- Full `test_agent_supervisor_*` freeze-baseline suite at the frozen candidate: run recorded
  in the gate evidence (rule 17; result appended by the orchestrator at recert).

## 4. Producer self-checks (G2)

1. Scope: exactly the three allowed code/test paths (+ this report). PASS.
2. The reviewer remains execution-free (trust-zone invariant 10 untouched; argv unchanged —
   only stdin instructions + packet content changed). PASS.
3. All prior denials/validators preserved (suite 94/94; no argv or schema change). PASS.
4. The new fact is bounded (existing truncation + packet-size refusal machinery) and
   digest-bound like every section. PASS.
5. Contract text is deterministic pure-ASCII (stdin determinism test still green). PASS.

## 5. Closure status (deficit-convergence rule 20)

Matrix complete except the single authorized live rerun: after G3/G5 + full-suite recert +
re-pin + reinstall, ONE loop relaunch serves as the closure verification (expected: reviews
return content verdicts — CONTINUE/REVISE/COMPLETE — instead of environment-failure
ROTATE_SESSION). Recorded there → VERIFIED_CLOSED or consolidated blocker.
