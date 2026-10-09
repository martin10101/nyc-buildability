# M0-T124 — G5 security review (VERBATIM reviewer return; saved by the orchestrator, transport entity-decoding only)

All five certification anchors verify exactly against the tree. I have completed all verification. Here is my G5 report.

---

# G5 SECURITY REVIEW — M0-T124 (Fifth recert + R347 live-start package presentation)

**Frozen head:** `70fb379` (`git rev-parse HEAD` → `70fb37991902...`) — verified. Deliverables at `3cb9e31`.
**Producer of record:** orchestrator (governance packet; no code changed).
**Deliverables:** `project-control/reports/M0-T124-recertification.md`, `project-control/reports/M0-T096-activation-package.md` (section-10 fifth refresh); evidence map `M0-T124-evidence-map.json`.
**Reviewer:** security-reviewer (read-only). I did not touch the live runtime dir / preserved journal (forbidden_paths); hashing was read-only.

## Verdict summary
No SEC-MAJOR or SEC-MINOR. The recertification's security posture is sound: identity anchors reproduce exactly, the CLI identity is undrifted, no secrets/Telegram values leak, the preserved journal is byte-identical after the whole window, and the R347 package is presentation-only — it executes nothing, requests nothing, and restates every standing gate. Two INFO notes. **VERDICT: PASS.**

## 1. No secrets / Telegram values (Q1) — PASS
- Scanned both deliverables + the evidence map for `sk-*|ghp_|xox*|BEGIN|password|secret|api_key|bearer|<botToken>|bot_token|chat_id` → **NONE**. No Telegram value appears (R242/R243 honored).
- The presented commands (recert §4) contain only executable paths, config/manifest **paths**, and flags. The secret-bearing external `config.toml` is referenced **by path only** (`"C:/Program Files/SupervisorConfig/config.toml"`), never inlined — the correct thin-client posture.
- The activation-package fifth refresh (3cb9e31 diff) adds only identity anchors/digests and renames the prior section to "10-prior" (history preserved); no secret, no path beyond digests.

## 2. Certification integrity — CLI identity undrifted (Q2) — PASS
- Re-ran `executable_identity(r'C:\Users\MLFLL\.local\bin\claude.exe', name='claude').digest` →
  `d6f6c29a8ac6b3cf1b76e53cca2faadf784bf5114230c815d55327dbae889ed8`, byte-equal to the admitted digest recorded in recert §1 and the activation refresh. Confirms the "no admission event / no repin" claim.
- Recorded certification anchors reproduce exactly (read-only git):
  - material identity `git log -1 -- tools/agent_supervisor/` = **16e1b3b** ✓ (my delta-attested T123 hardening commit)
  - supervisor tree `HEAD:tools/agent_supervisor` = **a72a53b8c4f560c90dabbf65cb75478fef37ce43** ✓
  - golden blob = **c54fd0d2d0e3833e54ba2ec9745ee6e7d9fdb550** ✓ (carried un-weakened since T119)
  - launch-seam blob = **1a77b904c26935f1cb1bded87498dffa2a42230d** ✓
  - restart-channel blob = **d3e23087f0f76a6660b5c19e605fd818fe940b47** ✓ (unchanged)
  All match recert §1 / the activation refresh.

## 3. Owner-gate discipline (Q3) — PASS
- **Section 4 executes nothing:** the report states "presentation only… nothing here starts, resumes, or clears anything"; commands are `!`-prefixed text for a SEPARATE owner decision. AS-4 (evidence map) records no start/clear-recovery/journal-edit in the window; the journal readback (PAUSED_RECOVERY, transitions 18, audit 43) is the unchanged post-cycle-2 state — independently corroborated by my byte-identical re-hash (§4 below).
- **Requests nothing / restates gates:** §4 "What remains owner-only and is NOT requested here" — the decision to attempt, both commands, and every standing gate (PR #241 never merged, autostart, C1 canary, Telegram live send, natural-event graduation, OS-ACL unchanged). §3 restates R316 CONSUMED (one-attempt authorization spent); the evidence map restates R345 (no restart/clear-recovery/journal-edit/budget-reset/PR #241) and R328 (S16.7 disposition grants nothing).
- **Documented surfaces only, no fail-closed bypass:** the presented sequence correctly uses `clear-recovery` for PAUSED_RECOVERY, explicitly distinguished from `owner-restart` (HALTED) and `acknowledge-emergency-stop` (EMERGENCY_STOPPED) — recert §4 step 1: "the documented PAUSED_RECOVERY exit — NOT owner-restart, which is the HALTED surface." `clear-recovery` clears only the recovery-pause blocker; the subsequent certified `start` still runs the S11.5 recover-boot classification + preflight probes AND the M0-T123 launch seam (worktree binding at cli._run_loop, the unconditional runner-chokepoint ceiling+cwd guard, and the pre-first-dispatch shed). The over-ceiling session `798d2f00` (640,224 > 400,000) is therefore **shed** (`over_ceiling_session_shed`, fresh Fable worker in `wt-m0t107`), never resumed — exactly the certified fail-closed geometry I reviewed in M0-T121/T123. The presentation describes this accurately ("certified, not promised") and weakens nothing.

## 4. Preserved-evidence integrity (Q4) — PASS
Re-hashed the preserved runtime dir (`33dfa57d…`) read-only after the whole window; both equal the T123 G0 baselines byte-for-byte:
- journal `a4acb370f3a23fd5193c27d16e729a6b6035c53c368a10c52673de8b5de29255` ✓
- audit `e80c057cabc24478ab67d785e2f903696f6cc1fcf7cbf782db9fd6f284430c83` ✓
This byte-identity is the definitive proof that the T124 recert window (doctor/verify-controller/record-manifest) did NOT write the preserved journal. Audit head 43 / transitions 18 (PAUSED_RECOVERY) is consistent with this preserved journal (the cycle-2 S14 stop: seq 42 unsafe_condition → PAUSED_RECOVERY, seq 43 owner_touch_recorded). record-manifest writes only the external manifest file; doctor reads. R345 "no journal edit" honored.

## 5. R345 side-effects (Q5) — PASS
The deliverables are TEXT and execute nothing (confirmed by the byte-identical preserved journal — no restart/clear/edit/reset side effect). PR #241 is untouched: the deliverables only RESTATE "PR #241 never merged" as a standing owner-only gate; the evidence map notes PR #241 gh-confirmed OPEN by the DCV. No `tools/**` or live-runtime path was written (forbidden_paths honored; the commit changed only control-plane files + the two report deliverables).

## INFO
- **INFO-1:** the presented commands include local absolute paths with the Windows username (`MLFLL`) and internal config/manifest locations. These are non-secret filesystem paths (the username is already the repo's git-author identity); the secret-bearing config is referenced by path only. Acceptable in a public repo (same posture as the M0-T122 handover); placeholder paths in owner-facing text would be optional defense-in-depth.
- **INFO-2:** journal safety is established by the byte-identical re-hash (strongest possible evidence); I deliberately did not re-run `doctor` against the preserved runtime, relying on the hash + the referenced G4 rerun to avoid any interaction with the preserved evidence.

Reproduction (read-only):
```
git rev-parse HEAD
git show 3cb9e31 --stat
python -c "from tools.agent_supervisor.process import executable_identity; print(executable_identity(r'C:\Users\MLFLL\.local\bin\claude.exe', name='claude').digest)"
git log -1 --format=%H -- tools/agent_supervisor/ ; git rev-parse HEAD:tools/agent_supervisor HEAD:tools/test_agent_supervisor_golden_run.py HEAD:tools/test_agent_supervisor_launch_seam.py
sha256sum "$RT/supervisor_journal.sqlite3" "$RT/audit.jsonl"   # RT = preserved 33dfa57d… runtime dir
grep -rniE "sk-|ghp_|bot_token|chat_id|password|secret|api_key" project-control/reports/M0-T124-recertification.md project-control/reports/M0-T124-evidence-map.json
```

Relevant files (absolute):
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\reports\M0-T124-recertification.md`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\reports\M0-T096-activation-package.md`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\reports\M0-T124-evidence-map.json`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\tasks\M0-T124.json`

VERDICT: PASS
