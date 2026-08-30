# M0-T124 — Fifth golden recertification at the post-resume-path frozen identity + the R347 live-start package (presentation only)

Recorded by the orchestrator (producer of record) 2026-08-30. Every number is an
executed-command output from this session at the identity being certified. Per D-024-R347
this task ENDS AT A STOP: section 4 presents the live-start package for a SEPARATE owner
decision; nothing here starts, resumes, or clears anything.

## 1. The ONE final identity being certified

* Branch `control/D-024-fable-codex-loop`. **Supervisor material identity last moved at
  `16e1b3b`** (M0-T123 hardening: the unconditional seam; the base fix `6aada29` added
  `launch_seam.py` + the five wired seams). `git log -1 -- tools/agent_supervisor/` = `16e1b3b`.
* `tools/agent_supervisor` tree hash at HEAD: **`a72a53b8c4f560c90dabbf65cb75478fef37ce43`**.
* Golden pack blob **UNCHANGED through both windows**: `c54fd0d2d0e3833e54ba2ec9745ee6e7d9fdb550`
  (42 tests, carried un-weakened since the T119 certification). Launch-seam pack blob:
  `1a77b904c26935f1cb1bded87498dffa2a42230d` (64 tests). Restart-channel pack unchanged (34).
* **Provider CLI identity (R282 admission carried, NO drift):** recomputed via
  `executable_identity` — digest **`d6f6c29a8ac6b3cf…`** (`sha256_head+size`, 217,360,032
  bytes) — byte-equal to the admitted Claude Code 2.1.251 identity and the journal's pinned
  identity. NOT a new admission event. Drift tooth run explicitly: **1 passed**.

## 2. Certification evidence at this identity (all executed this session)

| Check | Result |
|---|---|
| **WHOLE supervisor suite** | **2,889 passed, 2 skipped, 0 failed** — TWO independent full runs at this identity (orchestrator 625.3 s; the G4 reviewer's own regression run, exit 0). Chain: 2,814 (T122) + 56 (T123 base: 45+7+4) + 19 (hardening) = 2,889; collect-only 2,891 = 2,889+2. Far above the ≥1,165 freeze baseline. |
| Golden-run pack | Green inside both full runs; blob byte-identical to the T119-certified `c54fd0d2` — certified scenarios carried, not re-authored. |
| Controller manifest re-recorded at the final tree | **121 files** (120 + `launch_seam.py`), digest **`472931279090cd68…`**, external `config.toml` bound, round-trip verification passed; stored outside the repo. |
| `verify-controller` | PASS — "controller verified, including the external config.toml binding." |
| `doctor` (full, non-live) | **overall PASS** — journal integrity ok (**PAUSED_RECOVERY at rest: transitions 18**, the post-cycle-2 preserved state), audit chain **43 records verified**, manifest row verifies 121 files against `47293127…`, allowlists coherent, recovery classification ok, loop modes ok, OS-ACL **PROTECTED**, limited-auto OFF by default. |
| CI | 20/20 success at `a71bd65` (DCV-confirmed); the pushed certification tip re-runs the same 20 checks. |
| M0-T123 gate provenance | G0/G2/G3/G4/G5 PASS + 3 delta attestations + 20-row DCV ALL PASS at accepted identity `21c79191…`. |
| Preserved evidence | Journal/audit/transcripts byte-identical to the G0 baselines throughout both windows (re-hashed by G5 and the DCV independently). |

**Certification verdict: the R247 window is CLOSED at this identity.** The resume-path fix
is certified; the golden capabilities carry; the preserved live journal was never written.

## 3. What this does NOT claim (R319 discipline carried; R316 stands)

Unit tests + the golden pack + this recertification do NOT prove continuous operability.
The R316 one-attempt authorization is **CONSUMED** (the cycle-2 counted stop). **No start
of any kind is authorized by this document** — the next live attempt, if any, is a NEW
owner decision (R347). The certified fix changes what would happen on such an attempt:
the over-ceiling session `798d2f00` would be SHED pre-first-dispatch (fresh Fable worker,
fresh context) and the worker would launch in `wt-m0t107`, not the primary checkout.

## 4. THE R347 LIVE-START PACKAGE (presented for a separate owner decision — nothing executes)

**State at rest:** journal **PAUSED_RECOVERY** (from the certified S14 stop; transitions
18, audit 43, 0 open asks, 0 pending effects); worktree `wt-m0t107` clean at `796e18f`;
M0-T107 claimed with checkpoint 1 delivered; owner-touch history preserved (S16.7 excess
dispositioned as a measurement only).

**If the owner decides to attempt again**, the exact certified sequence is (each `!`-prefixed,
forward-slash paths, in order):

1. **Exit the recovery pause** (the documented PAUSED_RECOVERY exit — NOT owner-restart,
   which is the HALTED surface):
   `! python -m tools.agent_supervisor clear-recovery --checkout C:/Users/MLFLL/Downloads/nyc-zoning/ctl24`
2. **The same certified item-3 start** (unchanged shape; no repin flag — §1 proves the CLI
   identity undrifted):
   `! python -m tools.agent_supervisor start --mode limited-auto --owner-enable-bounded-auto --claude-executable C:/Users/MLFLL/.local/bin/claude.exe --codex-executable C:/Users/MLFLL/AppData/Roaming/npm/codex.cmd --task-packet project-control/tasks/M0-T107.json --config "C:/Program Files/SupervisorConfig/config.toml" --model-selection C:/SupervisorController/model_selection.toml --manifest C:/Users/MLFLL/AppData/Local/NYCBuildabilitySupervisor/ctl24-activation/controller_manifest.json`

**Expected behavior on such an attempt (certified, not promised):** the pre-first-dispatch
seam sheds the over-ceiling session (`over_ceiling_session_shed` audit event, budgets and
touch history untouched), a FRESH Fable 5 worker launches in `wt-m0t107` with fresh
context, the checkpoint contract is appended, and the run proceeds to the independent
Codex review (codex_reviews 1/3 used) and — on success — actual M0-T107 advancement. On
any counted stop, the standing protocol binds: no restart, preserve everything, report,
separate bounded defect diagnosis; the owner-touch situation (cap already dispositioned
at excess) makes ANY further counted stop an immediate owner matter.

**What remains owner-only and is NOT requested here:** the decision to attempt; both
commands above; and every standing gate (PR #241 never merged; autostart, C1 canary,
Telegram live send, natural-event graduation, OS-ACL unchanged). Before any owner-typed
attempt, the orchestrator will re-run the R276-pattern preflight at the then-current tip
(clean synced tree, CI green, anchors intact, executables re-hashed, journal readback)
and report it — the presentation of this package does not skip that step.
