# M0-T039 — Supervisor Behavior-Identity Freeze Record

**Task:** M0-T039 — Phase 1: freeze M0-T036 supervisor behavior identity + defect-only
maintenance lane (AD-065). **Directive:** D-010 (Section 18 Phase 1; AD-065; 0A.10).
**Producer:** backend-engineer. **Date computed:** 2026-08-06.
**Status of the thing being frozen:** SHADOW-ONLY (see §4). This freeze record pins an
identity; **it activates nothing.**

This record pins the behavior identity of the accepted, merged, shadow-only supervisor so
that every future defect-lane task (`.claude/rules/supervisor-freeze.md`) can diff against a
fixed baseline. Every value below was computed by the producer with the exact command shown
and is independently reproducible.

---

## 1. Merged main SHA carrying M0-T036

M0-T036 ("Codex-Claude Supervisor Bridge — ACCEPTED (shadow-only)") merged to `main` via
**PR #154**.

| Item | Value |
|---|---|
| PR #154 merge commit (full 40-char SHA) | `cec785f97ac1037df1fb2e1b114260eb106b7de0` |
| Merge commit subject | `Merge pull request #154 from martin10101/task/M0-T036-supervisor-bridge` |
| Merge commit date | `2026-08-06 20:06:56 -0400` |
| Current `origin/main` HEAD (freeze base) | `d6c84c88c321c9956c62fb78db161ebb4d2fa129` |
| Is the merge commit an ancestor of `origin/main`? | **YES** (verified) |

SHA length was verified as exactly 40 hex characters (a prior task failed G3 on a dropped
hex digit; both SHAs re-counted programmatically — `len == 40`).

Reproduce:

```bash
gh pr view 154 --json mergeCommit,state,title
# -> {"mergeCommit":{"oid":"cec785f97ac1037df1fb2e1b114260eb106b7de0"},"state":"MERGED", ...}
git rev-parse origin/main
# -> d6c84c88c321c9956c62fb78db161ebb4d2fa129
git merge-base --is-ancestor cec785f97ac1037df1fb2e1b114260eb106b7de0 origin/main && echo YES-ancestor
# -> YES-ancestor
git log -1 --format="%H%n%s%n%ci" cec785f97ac1037df1fb2e1b114260eb106b7de0
```

---

## 2. Supervisor tree identity (`tools/agent_supervisor/`)

The git tree object hash of the `tools/agent_supervisor/` directory is the content-identity
of the frozen supervisor. It is **byte-identical at the PR #154 merge commit and at the
current `origin/main`** — confirming no supervisor change has merged since M0-T036 was
accepted.

| Ref | `tools/agent_supervisor/` tree hash |
|---|---|
| PR #154 merge commit `cec785f9…` | `e8eeb4fa240013c508042654968b2a5fc25dcbeb` |
| `origin/main` `d6c84c88…` | `e8eeb4fa240013c508042654968b2a5fc25dcbeb` |
| Freeze branch HEAD `650fc6b8…` | `e8eeb4fa240013c508042654968b2a5fc25dcbeb` |
| **Identical across all three?** | **YES** |

Reproduce:

```bash
git rev-parse cec785f97ac1037df1fb2e1b114260eb106b7de0:tools/agent_supervisor
git rev-parse d6c84c88c321c9956c62fb78db161ebb4d2fa129:tools/agent_supervisor
git rev-parse HEAD:tools/agent_supervisor
# all three -> e8eeb4fa240013c508042654968b2a5fc25dcbeb
```

---

## 3. Test-suite baseline

Invocation follows the **documented convention** in `tools/agent_supervisor/README.md`
(section "Tests"): standard-library `unittest`, all 20 supervisor test modules
(`tools.test_agent_supervisor_*`). The README states no pytest dependency exists in this
package; pytest 8.4.2 is present in this environment but the documented unittest convention
was used for the frozen baseline.

Exact command (run once, in full, from the `orch` worktree root):

```bash
python -m unittest \
  tools.test_agent_supervisor_phase1 \
  tools.test_agent_supervisor_protocol \
  tools.test_agent_supervisor_audit \
  tools.test_agent_supervisor_process \
  tools.test_agent_supervisor_policy \
  tools.test_agent_supervisor_broker \
  tools.test_agent_supervisor_runner \
  tools.test_agent_supervisor_reviewer \
  tools.test_agent_supervisor_rotation \
  tools.test_agent_supervisor_scheduler \
  tools.test_agent_supervisor_recovery \
  tools.test_agent_supervisor_ipc \
  tools.test_agent_supervisor_endurance \
  tools.test_agent_supervisor_loop \
  tools.test_agent_supervisor_replay \
  tools.test_agent_supervisor_invariants \
  tools.test_agent_supervisor_adversarial \
  tools.test_agent_supervisor_crash \
  tools.test_agent_supervisor_fuzz \
  tools.test_agent_supervisor_model_chain
```

Result:

| Metric | Value |
|---|---|
| Environment | Python 3.11.9 |
| Tests run | **1165** |
| Passed | **1163** |
| Failed / errored | **0** |
| Skipped | **2** |
| Terminal status | `OK (skipped=2)` |
| Duration | **62.502 s** (`Ran 1165 tests in 62.502s`) |

The fuzz module is seeded (`SEED = 20260803` per README), so the corpus is deterministic
across machines; the replay module reported all 8 required S15 corpus cases present
(corpus digest `768eea1ec6bb9e83…`), 0 provider calls, 0 project-control writes.

---

## 4. Frozen behavior-identity summary block

```
FROZEN SUPERVISOR BEHAVIOR IDENTITY (M0-T039, 2026-08-06)
  merged main SHA (PR #154)        : cec785f97ac1037df1fb2e1b114260eb106b7de0
  freeze base origin/main HEAD     : d6c84c88c321c9956c62fb78db161ebb4d2fa129
  tools/agent_supervisor tree hash : e8eeb4fa240013c508042654968b2a5fc25dcbeb
                                     (identical @ merge, @ origin/main, @ freeze HEAD)
  test suite (python -m unittest, 20 modules, Python 3.11.9)
                                   : 1165 run / 1163 passed / 0 failed / 2 skipped
                                     duration 62.502s, terminal status OK (skipped=2)
  status                           : SHADOW-ONLY — this freeze activates nothing
```

Future defect-lane tasks (`.claude/rules/supervisor-freeze.md`) diff against this block. A
supervisor change is expected to change the tree hash; it must (a) cite AD-093 qualifying
evidence and (b) re-establish the suite baseline (>= 1165 tests, 0 failures) under the
standard gates.

---

## 5. SHADOW-ONLY status reaffirmed — this freeze does not activate anything

M0-T036 was accepted **shadow-only** (owner decision, keep-shadow-only). This freeze record
records an identity and a maintenance lane; it does **not** move the supervisor beyond
shadow mode and does **not** lift any activation prerequisite. Per
`project-control/reports/M0-T036-ACTIVATION-CHECKLIST.md`, the R595 prerequisite remains
MANDATORY BLOCKING, quoted verbatim:

> ### ⛔ R595 supervised rehearsal — MANDATORY BLOCKING (owner directive 2026-08-06, D-007-R619)
> ... A **supervised rehearsal (R595)** that actually actuates the rotation seam live and
> preserves its audit evidence is a **mandatory blocking prerequisite BEFORE any of:**
> supervised-auto activation; limited-auto activation; automatic product-task execution; any
> claim that live session rotation has been proven.

Until R595 is satisfied and independently reviewed, none of the above may proceed, and R593
must **never** be represented as fully live-proven (D-007-R621). Nothing in this freeze
record or in `.claude/rules/supervisor-freeze.md` changes that.

---

## 6. Commands run (full list, for reproduction)

```bash
git rev-parse HEAD                              # 650fc6b8a66c652109c43707c0303669ffc1eb2e
git rev-parse --abbrev-ref HEAD                 # task/M0-T039-supervisor-freeze
git rev-parse origin/main                       # d6c84c88c321c9956c62fb78db161ebb4d2fa129
gh pr view 154 --json mergeCommit,state,title   # merge oid cec785f9…, MERGED
git rev-parse d6c84c88…:tools/agent_supervisor  # e8eeb4fa…
git rev-parse cec785f9…:tools/agent_supervisor  # e8eeb4fa…
git rev-parse HEAD:tools/agent_supervisor       # e8eeb4fa…
git merge-base --is-ancestor cec785f9… origin/main  # YES-ancestor
git log -1 --format="%H%n%s%n%ci" cec785f9…
python --version                                # Python 3.11.9
python -m unittest tools.test_agent_supervisor_*(20 modules)  # 1165 run, OK (skipped=2), 62.502s
```

---

## 7. Anomalies

None. Tree hashes are identical across the merge commit, current `origin/main`, and the
freeze branch HEAD (no supervisor drift since acceptance). The suite ran clean: 0 failures,
0 errors, 2 skips. No test made a network call or touched a real runtime directory (per
README design and the replay report: 0 provider calls, 0 project-control writes).
