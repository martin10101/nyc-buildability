# M0-T127 — G4 report (independent qa-engineer, read-only + read-only pytest) — VERBATIM agent return (transport entity-decoding only)

Orchestrator capture note: returned 2026-08-31 by the same independent qa-engineer identity.
VERDICT: PASS — recert numbers reproduced (golden 42/42 in 16.16s; whole suite 2990/2/0);
the excl-golden labeling correction ADJUDICATED with root cause (pytest --ignore does not
prune explicitly-globbed positional files; true excl-golden = 2948 passed / 2950 collected);
the 3h13m anomaly ACCEPTED as environmental by the reviewer who originally recorded it (four
clustered datapoints 14.46/15.00/16.16/52.20s); seven R391 contents verified; >=10 citations
traced; both commissioning commands parse-validated; ASCII clean; no new findings.

---VERBATIM-BEGIN---
All duties complete. Here is my M0-T127 G4 gate report.

---

# G4 (QA) Gate Report — M0-T127 (Amendment-22 recertification + stop-and-present)

**Task:** M0-T127 — single full R247 recertification at the final frozen identity + consolidated stabilization/commissioning report (D-024-R389..R392)
**Reviewed identity:** branch tip `361c8d1b3e3c580b99a14b19c95bc4eee23a89f7`. **Material stability verified:** `git diff 2d46fb0 HEAD -- tools/agent_supervisor/ tools/test_agent_supervisor_*.py tools/supervisor_command_doc_check.py .github/ docs/CONTROLLER_UPDATE_RUNBOOK.md` is **empty** — certified supervisor material is byte-identical to `2d46fb0`; M0-T127 adds only the recert reports.
**Reviewer:** qa-engineer (independent, read-only + read-only pytest). Producer label `orchestrator-recert-runner`, so my own runs are primary evidence. No writes outside `.claude/agent-memory/qa-engineer/`; the live PAUSED_RECOVERY journal was never opened (R374).
**Environment:** Python 3.11.9, pytest 8.4.2, ruff 0.13.0.

## VERDICT: PASS — recert numbers reproduce; the 3h13m anomaly is resolved; the excl-golden labeling correction is confirmed exactly. No new defects.

## (1) Reproduced numbers table (my own runs at the certified material)

| Measurement | Recert claim | My reproduction | Result |
|---|---|---|---|
| Golden pack, single process (`pytest tools/test_agent_supervisor_golden_run.py -q`) | 42 passed, 52.20s | **42 passed, 0 failed, 16.16s** | MATCH (count); timing sub-minute |
| Whole suite INCL golden, one process (`pytest tools/test_agent_supervisor_*.py -q`) | 2990 passed, 2 skipped | **2990 passed, 2 skipped, 0 failed** (220.63s) | MATCH |
| Whole glob collection | — | 2992 collected (=2990 pass + 2 skip) | consistent |
| Whole glob + `--ignore=golden` collection | (labeling claim) | 2992 collected — **`--ignore` did NOT bite** | confirms mislabel |
| Whole suite EXCL golden, provably (`pytest tools/ --ignore=<golden> -k agent_supervisor --co`) | (2990 was mislabeled) | **2950 collected = 2948 pass + 2 skip** | 2992 − 42 = 2950 ✓ |
| 8 defect packs per-pack (collection at this identity) | next_task 18, command_docs 17, orientation 13, checkpoint_journey 25, recovery 63, launch_seam 69, loop 122, runner 74 = 401 | all match; all pass within the 2990 | MATCH |
| Golden fast-27 subset (M0-T126 regression) | 27 | 27 passed (earlier at 2d46fb0) | MATCH |

## Excl-golden reconciliation (adjudicated)

The recert's **labeling correction is CORRECT**. Root cause: `pytest tools/test_agent_supervisor_*.py --ignore=tools/test_agent_supervisor_golden_run.py` does **not** exclude golden — the shell glob passes `golden_run.py` as an explicit positional argument, and pytest's `--ignore` only prunes during directory recursion, not explicitly-named paths. Proof: the glob collects **2992** and the glob-plus-`--ignore` **also** collects 2992 (identical). Therefore the M0-T126-era "full suite excl. golden = 2990" (producer return 3 / my own G4 delta phrasing) was mislabeled — **2990 is the whole suite INCLUDING golden**. The true excl-golden count, via a provably-biting directory-recursion exclusion, is **2948 passed** (2950 collected). No pass/fail conclusion changes: golden passes both standalone (42/42) and inside the suite; the same tests ran under both labels. I carry my share of this labeling error from the M0-T126 delta gate — corrected here.

## 3h13m anomaly — RESOLVED; I accept the environmental-artifact explanation

I produced the original outlier (`42 passed in 11616.50s` at M0-T125). My fresh single-process re-measurement now is **16.16s**. Independent corroboration I reproduced from the ledger: `M0-T119-G2-self-check.md` records golden **15.00s** and `M0-T119-G4-qa-review.md` records **14.46s** for the identical pack; the M0-T119 whole-suite run (incl golden, 206.84s) also ran golden fast. Producer's M0-T127 measure was 52.20s. Four independent datapoints (14.46 / 15.00 / 16.16 / 52.20 s) cluster sub-minute; the 11616s figure is **not reproducible**. I plainly **accept** that the 3h13m was a one-off environmental artifact of that single M0-T125 reviewer session, not intrinsic test time. The pack is intrinsically sub-minute.

## (2) Baseline reconciliation

`2889` (M0-T124 whole-suite baseline) `+ 101 = 2990` — arithmetic confirmed. The four **new** packs sum to **73**: command_docs 17 + orientation 13 + checkpoint_journey 25 + next_task 18 (all created in M0-T126; independently collected here). The remaining **+28** is net additions across pre-existing packs (launch_seam D2, recovery D6/D16, runner D4, loop D5/D8/D10/D11/D12 + G3 remediation; golden net 0 — one row rewritten by the disclosed D10 correction). No test was removed (suite grew monotonically). **Limitation, not a defect:** I cannot pin each of the 28 to a specific test without checking out the M0-T124 identity per-pack; the top-line 2990 and the 73-new-pack figure reproduce and no unexplained delta surfaces.

## (3) Battery evidence

- `modularity_check.py --check`: **failures 0** (335 files) — reproduced.
- `supervisor_command_doc_check.py`: **exit 0, 12 commands, 0 drift** — reproduced.
- `verify-controller` (section-6 shape, read-only): **EXIT 0, "controller verified, including the external config.toml binding"** — independently reproduced, corroborates §4.
- `doctor`: **not independently re-run** — it reads the live PAUSED_RECOVERY journal, which I deliberately do not open (R374 preservation posture, consistent with M0-T125/T126). Its quoted readback (PAUSED_RECOVERY / 22 / 53 / 0) is internally consistent with the preservation section and with the preserved audit copy (**53 records**, verified). `record-manifest` correctly **not** re-run (writes the activation store). Manifest 125-files / `a43f133b...` is consistent across both reports.

## (4) Stabilization report QA

- **Seven R391 contents all present:** §1 what changed, §2 end-to-end proof, §3 defects found proactively, §4 remaining limitations, §5 exact frozen identity, §6 complete preflight, §7 commissioning commands.
- **≥10 numbers/citations traced:** golden 42 ✓; whole suite 2990/2 ✓; live-vs-cumulative 72,546/694,251 ✓ (traced to preserved artifacts at M0-T126); 2889+101=2990 ✓; four new packs 73 ✓; modularity 0 ✓; tooth 12/0 ✓; transcript 97 ✓; audit 53 ✓; wt-m0t107 clean `796e18f` ✓; tools/agent_supervisor tree `46722aa1af8f92f063d74b638a5a04e996a1f52d` ✓ (git rev-parse); golden blob `deeca07b...` ✓; launch-seam blob `0aed4902...` ✓; M0-T119 golden 15.00s citation ✓; producer 395-vs-391 drift (my own G4-1 finding) ✓.
- **Preflight §6 dry-checks:** row 2 `git rev-parse HEAD:tools/agent_supervisor` == `46722aa1...` executes and matches; row 6 `supervisor_command_doc_check.py` exit 0. Rows are executable as written.
- **Commissioning commands parse-validate** via `command_docs.validate_command(build_parser())`: Step 1 `clear-recovery` → **ok**; Step 2 `start` → **ok** (all five pinned flags present, `dispatch_inputs_missing` empty). No execution performed.

## (5) Preservation (read-only)

Audit **53 records** (preserved copy) ✓; worker transcript **97 lines** ✓; `wt-m0t107` **clean at `796e18f`** (rev-parse + empty `status --porcelain`) ✓. Live journal `PAUSED_RECOVERY / transitions 22 / effects 0` — accepted from the producer's read-only doctor readback and internally consistent; I did not open the live sqlite journal (R374).

## (6) ASCII
Both reports: **0 non-ASCII bytes** (recertification.md 6246 B; stabilization-report.md 11219 B).

## New findings
None. All recert claims reproduce; the labeling correction is accurate and exactly reconciled; the timing anomaly is resolved with my own fresh measurement. The recert's carried non-blocking observations (DCV obs 2 owner-machine-local digest; DCV obs 5 runbook `wt-m0t063` EXAMPLES outside D15 scope; G3 O1 tooth scans runbook only; G4 O2 exact-at-ceiling unit naming) remain honestly disclosed and non-blocking. The two structural limitations in §4 (property-3 softness; D9 autonomous tail simulation-proven only, live dispatch reserved to the R393 owner journey) are correctly scoped and match what I independently verified at M0-T126.

**Requested gate result:** **PASS** at the final frozen identity (material `2d46fb0`, reviewed at branch tip `361c8d1`). All commands reproduce read-only. Full report captured verbatim by the orchestrator as the M0-T127 G4 gate.

Note for the orchestrator: I reviewed via `git checkout --detach 361c8d1` in my own isolated worktree (I restored a clean tree first — my earlier untracked memory index and a local edit were set aside and re-applied afterward). The orchestrator owns this worktree's post-review lifecycle.
---VERBATIM-END---
