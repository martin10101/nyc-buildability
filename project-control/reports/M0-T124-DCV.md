# M0-T124 — Directive-compliance verification (VERBATIM verifier return; saved by the orchestrator, transport entity-decoding only)

All evidence confirmed. CI on the freshly-pushed tip fa9b38c is 17/20 success with 3 slower jobs still running (no failures); the G4 reviewer independently ran the full suite a third time this window (2889/2/0, 216.81s). Here is my final DCV report.

---

# DCV REPORT — M0-T124 (fifth recert + R347 live-start presentation), D-024 Amendment 19

**Reviewed head:** `fa9b38c` (confirmed `git rev-parse HEAD` = fa9b38cc4a45f1c75f2d5acd7b48ce5758fac63f; branch `control/D-024-fable-codex-loop`). M0-T123 now `accepted` (a573d6f) — not re-verified.
**Content identity:** Producer = orchestrator; no code changed (governance packet). Deliverables `M0-T124-recertification.md` + `M0-T096-activation-package.md` are byte-identical from the gate-reviewed `70fb379` to HEAD `fa9b38c` (`git diff --stat` empty). Certified supervisor identity: material `16e1b3b`, tree `a72a53b8c4f560c90dabbf65cb75478fef37ce43` (both reproduced).
**CI on pushed tip fa9b38c:** 17/20 `success`, 3 `in_progress` (`supervisor-bridge`, `control-plane`, `web-e2e` — the slower jobs on the just-pushed tip), **zero failures**. Prior identity a71bd65 was 20/20 (DCV-confirmed); the tip re-runs the same checks. [Orchestrator addendum at accept time: the three concluded `success` — final poll 20/20 at fa9b38c, recorded before acceptance per this report's condition.]

## Per-requirement verdicts (5/5)

**R328 — PASS.** Nothing dispositioned was exercised: I re-hashed the preserved sources READ-ONLY at `…/33dfa57d…/` → journal `a4acb370f3a23fd5…` and audit `e80c057cabc24478…`, both **byte-identical** to the G0 baselines. No restart/clear-recovery/budget change occurred (any would have grown the journal); the doctor readback is PAUSED_RECOVERY / transitions 18 / audit 43 (the post-cycle-2 preserved state), and recert §4 presents commands only.

**R330 — PASS.** Ledger check: only `M0-T123` (status `accepted`) and `M0-T124` (status `awaiting_gate`) were created since the window opened (05:53:54 / 05:53:55). No other work started under the authorization.

**R345 — PASS.** No live-loop restart / clear-recovery / journal edit / budget reset: the preserved journal is byte-identical (`a4acb370…`, re-hashed) — proof nothing executed. PR #241 untouched (`gh pr view 241` → state `OPEN`). Both deliverables are text that presents commands and executes nothing (the `!`-prefixed lines are for a separate owner decision).

**R346 — PASS.** Standard process fully reproduced on primary evidence:
- Gates: G0/G2 PASS (orchestrator, 3cb9e31); **G3/G4/G5 PASS (code-reviewer / qa-engineer / security-reviewer, all @70fb379)** — producer (orchestrator) ≠ reviewers.
- Certification sample I ran: `golden_run + launch_seam + restart_channel` → **140 passed** (42+64+34); drift tooth `test_s8_live_version_matches_catalog_fixture` → **1 passed**.
- CLI identity recomputed via `process.executable_identity('C:/Users/MLFLL/.local/bin/claude.exe')` → `digest=d6f6c29a8ac6b3cf…`, `size=217360032` — exact, no drift/repin.
- Git anchors reproduced: material `16e1b3b`, tree `a72a53b8…`, golden blob `c54fd0d2…` (carried un-weakened), launch-seam blob `1a77b904…`.
- Whole-suite **2889 passed / 2 skipped / 0 failed** is triple-sourced: the orchestrator (625.3s) plus the G4 reviewer's TWO independent runs — the T123-window run and a fresh third run this window (216.81s, exit 0, read in `M0-T124-G4-qa-review.md` §1). Far above the ≥1165 floor.
- Manifest verification: doctor `overall PASS` with the `controller_manifest` row verifying **121 files against `47293127…`**, config-bound, verify-controller PASS — independently reproduced by the G4 reviewer's read-only doctor run (§3); I confirmed the journal byte-identity that bounds it. I judged a self re-run of doctor unnecessary given the independent reproduction + byte-identity.
- R276-pattern preflight commitment recorded in recert §4 (re-run at the then-current tip before any owner-typed attempt). CI on fa9b38c 17/20 green + 3 running (no failures); a71bd65 was 20/20. M0-T123 provenance (G0/G2/G3/G4/G5 + 3 delta attestations + 20-row DCV ALL PASS) stands.

**R347 — PASS.** The STOP is honored: recert §4 PRESENTS the two-command live-start package for a SEPARATE owner decision and executes nothing. Load-bearing correctness verified against primary evidence: the journal at rest is **PAUSED_RECOVERY** (transitions 18), and `state_machine.py:283` defines `PAUSED_RECOVERY → PREFLIGHT` on `owner_cleared_pause` — so §4 correctly uses **`clear-recovery`** (the PAUSED_RECOVERY exit), explicitly "NOT owner-restart, which is the HALTED surface" (owner-restart would refuse `wrong_state`). The second command is the certified item-3 start (`--mode limited-auto --owner-enable-bounded-auto`, **no `--repin-cli-identity`**, forward-slash paths — byte-identical to the T122-certified shape). R316 one-attempt consumption restated (§3 "CONSUMED"). Nothing executed — the byte-identical journal is the proof.

## Discrepancies between claims and evidence
None material. Every hash, count, git anchor, CLI digest, and the recovery-verb correctness I reproduced matched the recert report and evidence map exactly (journal/audit byte-identity, 140-sample, drift tooth, d6f6c29a, tree a72a53b8, golden c54fd0d2, launch 1a77b904, clear-recovery↔PAUSED_RECOVERY). One honest live-state note (not a defect): CI on the just-pushed tip fa9b38c has 3 slower checks still `in_progress` (supervisor-bridge, control-plane, web-e2e), zero failures — the substance is independently green via my 140-test sample, the G4 reviewer's fresh 2889/2/0 run, and the prior-identity 20/20; the orchestrator should confirm the three conclude `success` before recording acceptance, consistent with the T121/T122/T123 tips which all finished green.

DCV VERDICT: ALL PASS
