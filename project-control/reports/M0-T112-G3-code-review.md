# G3 Independent Code Review — M0-T112 (D-024 Amendment 8, unit M: final golden re-certification)

**Verdict: PASS**

**Frozen review identity:** `14d204363c3ad44dff9a96333a9fe0e5662541ca` — confirmed equal to `git rev-parse HEAD`. All judgments below are at this SHA.

**Reviewer:** code-reviewer (independent, read-only). No write-producing commands were run.

**Nature of the unit:** governance/certification. It claims ZERO source/test/config changes — only re-running certification suites at the frozen post-addition identity and refreshing the activation package. The "code" under review is therefore the control-plane deliverables plus the accuracy of every identity/evidence claim against git and CI.

---

## Commands run (all read-only)

```
git rev-parse HEAD
git diff --stat a2aec114..14d20436
git diff a2aec114..14d20436 -- ':!project-control'          # non-control paths
git diff a2aec114..14d20436 -- project-control/reports/M0-T096-activation-package.md
git diff a2aec114..14d20436 -- project-control/tasks/M0-T112.json
git diff a2aec114..14d20436 -- tools/test_agent_supervisor_golden_run.py
git log -1 --format=%H -- tools/agent_supervisor
git rev-parse HEAD:tools/agent_supervisor
git rev-parse HEAD:tools/test_agent_supervisor_golden_run.py
git log -1 --format=%H -- tools/test_agent_supervisor_golden_run.py
git rev-parse a4f94b7:tools/agent_supervisor  615f661:tools/agent_supervisor  a4f94b7:tools/test_agent_supervisor_golden_run.py
git show 8574c58 --stat
git merge-base --is-ancestor 615f661a... HEAD
git log --oneline 615f661a...14d20436 ; git log --oneline -3 615f661a...
gh api repos/martin10101/nyc-buildability/commits/615f661a1ad30883469c72932970dd1ae64dc317/check-runs
# Reads: tasks/M0-T112.json, reports/M0-T112-recertification.md, reports/M0-T112-evidence-map.json,
#        reports/M0-T112-G2-self-check.md, gates/M0-T112-G0.json, gates/M0-T112-G2.json
```

---

## Scope-safety verification (central claim: only project-control/** touched)

`git diff --stat a2aec114..14d20436` lists 9 files, all under `project-control/`:
```
gates/M0-T112-G0.json | gates/M0-T112-G2.json |
reports/M0-T096-activation-package.md | reports/M0-T112-G0-readiness.md |
reports/M0-T112-G2-self-check.md | reports/M0-T112-evidence-map.json |
reports/M0-T112-recertification.md | state.json | tasks/M0-T112.json
```
`git diff --stat a2aec114..14d20436 -- ':!project-control'` returns **empty** — nothing outside `project-control/**` was touched. The central safety claim holds. **PASS.**

`git diff a2aec114..14d20436 -- tools/test_agent_supervisor_golden_run.py` is **empty**: the golden pack was re-run only, not edited, as claimed (recertification.md §2 line 28). **PASS.**

Of the two allowed_paths report files, both were touched (`M0-T112-recertification.md`, `M0-T096-activation-package.md`); the third allowed path (`tools/test_agent_supervisor_golden_run.py`) was deliberately not used. An unused allowed path is not a violation and is explained in the report. The remaining changed control-plane files (G0/G2 gate JSONs, G0-readiness, G2-self-check, evidence-map, state.json, tasks/M0-T112.json) are standard orchestrator-written gate/lifecycle artifacts, consistent with prior units. **No finding.**

---

## Identity claims verified against git

Every identity assertion in `reports/M0-T112-recertification.md` §2 and the evidence map was checked against git and matches:

| Claim (report) | Independent git result | Match |
|---|---|---|
| Supervisor material identity last moved at `8574c58` | `git log -1 -- tools/agent_supervisor` → `8574c58b3425…` | ✓ |
| `tools/agent_supervisor` tree at HEAD = `132e698c15a9f9412d53905e45ce0ae0724abe15` | `git rev-parse HEAD:tools/agent_supervisor` → `132e698c…` | ✓ |
| Golden pack blob = `d2946392f1c14ba086d63c60f2e125db6863bc10` | `git rev-parse HEAD:tools/test_agent_supervisor_golden_run.py` → `d2946392…` | ✓ |
| Golden pack last moved at `635fac5` | `git log -1 -- …golden_run.py` → `635fac5a…` | ✓ |
| Golden pack unchanged by this unit | diff empty (above) | ✓ |

**Identity stability across the certification window** (this is what makes a re-run at `a4f94b7` valid at HEAD): the supervisor tree is byte-identical at the run head, the certification tip, and HEAD, and the golden blob is identical at the run head:
```
a4f94b7:tools/agent_supervisor  = 132e698c…   615f661:tools/agent_supervisor = 132e698c…   (HEAD = 132e698c…)
a4f94b7:tools/test_agent_supervisor_golden_run.py = d2946392…
```
So the tests ran at exactly the code identity being certified; the two follow-on commits (`c2518d4`, `14d2043`) add only control-plane records. **PASS.**

---

## Activation-package edits — refresh-only verification

`git diff a2aec114..14d20436 -- project-control/reports/M0-T096-activation-package.md` shows changes confined to exactly three hunks:

1. **Amendment-8 sequencing banner** (top of file): rewritten to state both capabilities are ACCEPTED and that re-certification has run, while explicitly preserving the gate: *"This package becomes presentable for the R187/R595 activation decision ONLY once M0-T112 itself is ACCEPTED through its gates; presentation and activation remain owner-gated."* It does **not** claim presentability before acceptance and does **not** state or imply activation. **Correct.**
2. **Item 10 (Identity and evidence)**: refreshed to the certified post-addition identity (`8574c58`, tree `132e698c…`, golden blob `d2946392…`, 40 tests, re-run only) and the re-cert figures (40/40; 493/493; 2,694 passed/2 skipped/0 failed). All values match the recertification report. **Correct.**
3. **Item 11 (review verdicts)** and **Item 12 (golden-run evidence)**: item 11 refreshed to describe the per-unit 4-reviewer waves (I/K/L + this unit, whose acceptance presentability waits on); item 12 appends a "Refreshed at M0-T112" paragraph noting the 40/40 re-run. Both are descriptive refreshes, no substantive change to what was implemented.

No hunk touches any other item (1–9, 13). No item's substance changed beyond identity/evidence refresh. **PASS — refresh-only confirmed.**

---

## Internal-consistency checks

- **Whole-suite arithmetic:** 677 + 724 + 683 + 610 = **2,694** passed; + 2 skipped = **2,696** collected. Consistent across recertification.md §3, the evidence map (R247), the G2 self-check, and both progress_log entries.
- **+4 baseline delta attribution:** the report attributes +4 (2,692 → 2,696 collected) to the four L-pack correction tests from commit `8574c58`. `git show 8574c58 --stat` confirms this is the M0-T111 consolidated correction round; its message names exactly four new L-pack tests (authorized-canary-no-env, task_id dedup, queue-growth, identifier redaction+cap) and shows `tools/test_agent_supervisor_telegram_sink.py` +129 lines. `8574c58` also touches `tools/agent_supervisor/telegram_sink.py` and `telegram_sink_cli.py`, which independently confirms it as the last commit moving supervisor material identity. Attribution is sound; no unexplained drift, nothing removed. **PASS.**
- **Evidence map completeness:** `reports/M0-T112-evidence-map.json` carries all 6 applicable rows R231/R232/R246/R247/R248/R249 (the resolver-confirmed set in the packet and progress_log). No selective citation. R231/R246/R249 marked discharged-at-capture; R232/R247/R248 verified in this unit. **PASS.**
- **Gate records:** `gates/M0-T112-G0.json` = PASS (reviewed_sha `a4f94b7`, claim seam); `gates/M0-T112-G2.json` = PASS self-check (reviewed_sha `c2518d4`, submit seam). Both sensible. **PASS.**

---

## CI verification

`gh api …/commits/615f661a…/check-runs` → `{"conclusions":{"success":20},"total":20,"names_not_success":[]}` — **20/20 success**, matching the progress_log pin and recertification.md §3. `615f661a` is an ancestor of HEAD (`git merge-base --is-ancestor` → yes); it is the certification tip carrying the recert report + activation-package refresh, and the two commits after it (`c2518d4`, `14d2043`) are control-plane-only (evidence map, G2 self-check, submit), which do not alter code identity (verified above). **PASS.**

---

## Findings

**BLOCKER:** none.
**MAJOR:** none.
**MINOR:** none.

**INFO-1 — Pack-level counts are producer-attested, not reviewer-re-executable.** The per-pack figures (golden 40/40; affected 493/493; chunks 677/724/683/610) are foreground runs captured by the orchestrator-producer. As a read-only reviewer I cannot re-execute them; the CI 20-check run on `615f661` (verified 20/20, includes the supervisor-bridge whole-suite job) independently confirms the supervisor suite passes at the certified identity in aggregate, but CI does not expose the individual chunk breakdown. This is inherent to a certification unit and consistent with the recorded evidence-capture division of labor (project-control rule, 2026-07-15). Not a defect.

**INFO-2 — Task-packet diff is inflated by a JSON reindent.** `tasks/M0-T112.json` shows 143 changed lines, but `git diff` confirms this is a content-preserving 1-space→2-space reindent plus the expected CLI lifecycle fields only: `producer_agent` null→`fable-orchestrator-session`, `status` backlog→awaiting_gate, `progress_percent` 0→85, `updated_at` bump, added `worktree`, added 2-entry `progress_log`. **`allowed_paths`, `forbidden_paths`, `objective`, `outputs`, `dependencies`, `required_gates`, and `directive_refs` are unchanged** — no post-hoc scope widening. (`project-control/tasks` appearing in the packet's own forbidden_paths does not conflict: that governs producer file edits; the task's own packet is written by the orchestrator CLI during claim/progress/submit.)

**INFO-3 — One ancillary CI claim not independently re-checked.** recertification.md §3 also states "Prior tip `a2aec11` was 20/20 green at this seam's start." I verified the load-bearing tip (`615f661`) only; the `a2aec11` seam-start figure is non-load-bearing to this certification and was not re-queried.

---

## Conclusion

M0-T112 is a clean governance/certification unit. Its central safety claim (only `project-control/**` touched, golden pack re-run not edited) is confirmed by git. Every identity, tree, and blob assertion matches git; the supervisor identity is byte-stable across the run head, certification tip, and HEAD; the activation-package edits are genuinely refresh-only and preserve the owner-gated presentability/activation boundary; the whole-suite arithmetic and the +4 delta reconcile exactly to the four accepted L-pack tests in `8574c58`; the evidence map covers all six applicable rows; and CI is 20/20 green on the certification tip. No BLOCKER/MAJOR/MINOR findings.

**G3 VERDICT: PASS** at frozen identity `14d204363c3ad44dff9a96333a9fe0e5662541ca`.
