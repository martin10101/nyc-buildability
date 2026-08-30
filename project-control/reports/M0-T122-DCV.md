# M0-T122 — Directive-compliance verification (VERBATIM verifier return; saved by the orchestrator, transport entity-decoding only)

All 10 rows verified against primary evidence I reproduced. Here is my DCV report.

---

# DCV REPORT — M0-T122 (fourth golden recertification), D-024 Amendments 16/17

**Reviewed head:** `cf2f202` (confirmed `git rev-parse HEAD` = cf2f2025ce9dcd8a76c62b4f76c7adb5d09cb5b3; branch `control/D-024-fable-codex-loop`, pushed = origin tip). M0-T121 is now `accepted` (96362c0), so I did not re-verify it.
**Content identity:** Producer = orchestrator; no code changed (allowed_paths = the two report files). Deliverables `M0-T122-recertification.md` + `M0-T096-activation-package.md` are byte-identical from the gate-reviewed `62194d1` to HEAD `cf2f202` (`git diff --stat 62194d1 cf2f202 --` on both = empty; only control-plane files changed between). Certified supervisor identity = material `668c824`, `tools/agent_supervisor` tree `d3db9f3c`.
**CI on pushed tip cf2f202:** 19/20 `success`, `supervisor-bridge (pytest tools/test_agent_supervisor_*.py)` still `in_progress` (started 05:17:51Z; the whole-suite job, ~3-7 min), **zero failures**. Same pattern as the M0-T121 tip 6edf820, where the identical job concluded `success`.

## Per-requirement verdicts (10/10)

**D-024-R302 — PASS.** Ledger check: the only tasks created on/after 2026-08-30 are `M0-T121` (status `accepted`) and `M0-T122` (status `awaiting_gate`). No other work started under the authorization. `git log ef0d476..cf2f202` shows no R276-rerun/start-dispatch commit. Qualifying-evidence report `M0-T107-cycle2-start-refusal.md` present. Window = one defect task + this recert, exactly as authorized.

**D-024-R314 — PASS.** Standard process reproduced on primary evidence:
- Gates: G0 PASS (orchestrator, 96362c0), G2 PASS (orchestrator, acf6505), **G3 PASS (code-reviewer, 62194d1)**, **G4 PASS (qa-engineer, 62194d1)**, **G5 PASS (security-reviewer, 62194d1)** — the three independent reviewers differ from the producer (orchestrator); producer ≠ verifier.
- Certification sample I ran myself: `pytest golden_run + restart_channel` → **76 passed** (42+34); drift tooth `test_s8_live_version_matches_catalog_fixture` (in `test_agent_supervisor_event_bus.py`) → **1 passed**.
- CLI identity recomputed via the supervisor's own `process.executable_identity('C:/Users/MLFLL/.local/bin/claude.exe')` → `digest=d6f6c29a8ac6b3cf1b76e53cca2faadf784bf5114230c815d55327dbae889ed8`, `size_bytes=217360032`, `digest_kind=sha256_head+size` — **byte-exact** to the recorded 2.1.251 identity (no repin).
- Git anchors reproduced: material `git log -1 -- tools/agent_supervisor/` = `668c824`; tree `HEAD:tools/agent_supervisor` = `d3db9f3c7ee66ff36c44d518e6177c5a39378e4a`; golden blob `HEAD:...golden_run.py` = `c54fd0d2d0e3833e54ba2ec9745ee6e7d9fdb550` — **byte-identical to the value recorded in `M0-T119-recertification.md`** (carried un-weakened); restart blob = `d3e23087f0f76a6660b5c19e605fd818fe940b47`.
- Whole-suite 2814 passed / 2 skipped / 0 failed: independently reproduced by the G4 reviewer's OWN run (`M0-T122-G4-qa-review.md` §1: 195.66s, exit 0) in addition to the orchestrator's run (425.8s). I judge this sufficient — two independent full-suite runs agree on the count, far above the ≥1165 freeze floor, and I reproduced the sub-packs + all cryptographic anchors. I did not re-run the ~3-7 min whole suite myself.
- CI on cf2f202: 19/20 green, supervisor-bridge (whole-suite) still running, no failures. Recert executed at the ONE final identity.

**D-024-R315 — PASS.** Hold honored. No R276 rerun and no cycle-2 start executed this window: no start-dispatch commit in `ef0d476..cf2f202`; `M0-T107` `updated_at`=2026-08-30T03:06:43 (predates the window opened ~03:15) and status is the pre-window `claimed`/20 (not advanced); the preserved journal rests at HALTED/transitions 13. The handover command is recorded VERBATIM behind the hold in recert §4 with the correct certified item-3 shape: `--mode limited-auto --owner-enable-bounded-auto`, **NO `--repin-cli-identity`**, forward-slash paths — release stated to be only after this task's acceptance.

**D-024-R316 — PASS.** The one-attempt protocol is recorded verbatim in recert §4 ("ONE attempt (R316)"). The attempt itself is the post-acceptance owner-typed act; this is protocol-recording verification (R300/R301 precedent), and the recording is present and correct.

**D-024-R317 — PASS.** Amendment-15 enforcement recorded verbatim in recert §4: on any further post-dispatch counted stop → NO restart, preserve ALL evidence untouched, diagnose as a separate bounded AD-093 defect task citing D-024-R301, with the S16.7 touch-budget-2/2-at-cap note.

**D-024-R318 — PASS.** No producer was interrupted: this is an orchestrator-produced governance packet (evidence is executed-command output); the three reviewer spawns ran to natural completion (their G3/G4/G5 reports exist on file); the M0-T121 producer completed naturally before this task began (verified in the M0-T121 DCV).

**D-024-R319 — PASS.** `grep -niE` for affirmative operability/autonomy claims across BOTH deliverables returns only disclaimers/protocol lines (recert §3 line 47 "do NOT prove continuous operability"; §4 lines 80-81 "NO full-autonomy claim", "Continuous operability is declared ONLY from the completed live journey"); the activation-package §10 refresh returns no operability match. No affirmative claim anywhere.

**D-024-R320 — PASS.** The live-journey standard is recorded verbatim in recert §3-4: the REAL preserved journal exercised end-to-end through owner restart → preflight → fresh Fable rotation → independent Codex repository review → actual M0-T107 advancement; the journey is the owner-typed cycle-2 act after acceptance. Preserved journal untouched by this window: transitions 13 / audit 33 / HALTED at rest — corroborated by recert §2, the G4 reviewer's independent read-only `doctor` (§7: transitions=13, audit 33 verified), and M0-T107's pre-window `updated_at`. Audit head 33 = 31 + the pre-window seq-35 refused-start events (`M0-T107-cycle2-start-refusal.md` §4), i.e. no in-window journal write.

**D-024-R321 — PASS.** Live-journey failure protocol recorded verbatim in recert §4: preserve everything (journal/audit/packets/worktree) and report the new seam.

**D-024-R322 — PASS.** No-full-autonomy / no-repeated-restart rule recorded verbatim in recert §4 ("NO repeated restarts, NO full-autonomy claim"), reinforced by the §3 disclaimer; bounded to one attempt (R316) with Amendment-15 enforcement (R317).

## Discrepancies between claims and evidence
None material. Every numeric, cryptographic, and git anchor I reproduced matched the recert report and evidence map exactly (76-pack, drift tooth, CLI digest d6f6c29a + size 217,360,032, golden/restart blobs, tree hash, material commit, deliverable byte-stability, whole-suite count via the independent G4 run). Two honest live-state notes (neither a defect): (1) the `supervisor-bridge` CI check on cf2f202 was still `in_progress` at report time — the substance it validates is already independently green (my 76-pack + drift tooth + the G4 reviewer's full 2814/2/0 run); the orchestrator should confirm it concludes `success` before recording acceptance, as it did for the M0-T121 tip. (2) As the G4 reviewer noted, `doctor` does not print the literal "HALTED" token, but transitions=13 + `recovery_classification=safe_no_auto_resume` + the T107 record are mutually consistent with the at-rest HALTED journal — no discrepancy.

DCV VERDICT: ALL PASS
