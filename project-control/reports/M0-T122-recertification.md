# M0-T122 — Fourth golden recertification at the post-restart-channel frozen identity (R247/R314)

Recorded by the orchestrator (producer of record for this governance packet) 2026-08-30.
Every number below is from a command executed this session at the identity being certified;
nothing is carried forward as prose. Reviewers reproduce each at the frozen head.

## 1. The ONE final identity being certified

* Branch `control/D-024-fable-codex-loop`. **Supervisor material identity last moved at
  `668c824`** (M0-T121: `tools/agent_supervisor/restart_channel.py` NEW + `cli.py` +2
  wiring lines; the accepted rework `6432d2d` touched ONLY the test pack outside the
  supervisor tree). `git log -1 -- tools/agent_supervisor/` = `668c824`.
* `tools/agent_supervisor` tree hash at HEAD: **`d3db9f3c7ee66ff36c44d518e6177c5a39378e4a`**.
* Golden pack blob **UNCHANGED from the M0-T119 certification**:
  `tools/test_agent_supervisor_golden_run.py` = `c54fd0d2d0e3833e54ba2ec9745ee6e7d9fdb550`
  (42 tests, carried un-weakened). New restart-channel pack blob:
  `tools/test_agent_supervisor_restart_channel.py` = `d3e23087f0f76a6660b5c19e605fd818fe940b47`
  (34 tests, edge-granular reachability + AS-1..AS-8).
* **Provider CLI identity (R282 admission carried, NO repin needed):** recomputed via the
  supervisor's own `executable_identity` — digest
  **`d6f6c29a8ac6b3cf1b76e53cca2faadf784bf5114230c815d55327dbae889ed8`**
  (`sha256_head+size`, size 217,360,032) — byte-equal to the admitted Claude Code 2.1.251
  identity and to the journal's pinned identity from the live-proof repin. Drift tooth run
  explicitly: `test_s8_live_version_matches_catalog_fixture` → **1 passed**.

## 2. Certification evidence at this identity (all executed this session)

| Check | Result |
|---|---|
| **WHOLE supervisor suite** (every `tools/test_agent_supervisor*.py`) | **2,814 passed, 2 skipped, 0 failed** (425.8 s). Exact chain: 2,780 (M0-T119 baseline) + 34 (M0-T121 restart-channel pack) = 2,814. Pre-delta cross-check: 2,811 at the pre-rework identity (2,780+31), measured this session — the +3 delta = the rework's added tests. Far above the ≥1,165 freeze baseline (M0-T039 duty). |
| Golden-run pack | Included green in the whole-suite run (blob byte-identical to the T119-certified `c54fd0d2` — the certified scenarios are carried, not re-authored). |
| Controller manifest re-recorded at the final tree | **120 files** (119 + `restart_channel.py`), digest **`7f9991cbb5a22a40…`**, external `config.toml` bound, round-trip verification passed; stored outside the repo (`%LOCALAPPDATA%\NYCBuildabilitySupervisor\ctl24-activation\controller_manifest.json`). |
| `verify-controller` at the new manifest | PASS — "controller verified, including the external config.toml binding." |
| `doctor` (full, non-live) at the new manifest/config | **overall PASS** — journal integrity ok (still HALTED at rest, transitions 13), audit chain **33 records verified**, controller-config allowlists coherent (`claude ['claude-fable-5','claude-opus-4-8']`), `approved_models ['claude-fable-5','claude-opus-4-8']`, OS-ACL posture **PROTECTED**, limited-auto IMPLEMENTED and OFF by default. |
| Config digests | Protected config + model_selection unchanged (doctor-verified binding; `model_selection` `[claude] model = ""` = Fable 5 account default). |
| CI | 20/20 success at `6edf820` (DCV-confirmed, incl. the supervisor-bridge whole-suite job); the pushed certification tip re-runs the same 20 checks. |
| M0-T121 gate provenance | G0/G2/G3/G4/G5 all PASS + 19-row DCV ALL PASS at accepted identity `7cadcc70…` (producer ≠ reviewers throughout). |

**Certification verdict: the R247 window is CLOSED at this identity.** The M0-T121 change
is certified; the golden capabilities carry; the preserved live journal was never touched
(all evidence above is read-only against it — `record-manifest`/`doctor` write outside the
repo and read the journal read-only).

## 3. What this certification does NOT claim (R319, binding)

Unit tests, the golden pack, and this recertification do **NOT** prove continuous
operability. Per Amendment 17 (R320), the final live evidence is the REAL preserved
journal exercised end-to-end through: **owner restart → preflight → fresh Fable rotation →
independent Codex repository review → actual M0-T107 advancement.** That journey is the
owner-typed cycle-2 act below, and nothing here pre-claims its outcome.

## 4. The R315 sequencing hold and the cycle-2 handover (AS-4, recorded verbatim)

**R315:** only after THIS task is accepted may the orchestrator rerun the R276 preflight
and hand the owner the cycle-2 start command. The command (same certified item-3 shape,
NO `--repin-cli-identity` — the one-time repin is consumed and §1 proves the identity
undrifted; forward-slash paths; `!` prefix; one line):

```
! python -m tools.agent_supervisor start --mode limited-auto --owner-enable-bounded-auto --claude-executable C:/Users/MLFLL/.local/bin/claude.exe --codex-executable C:/Users/MLFLL/AppData/Roaming/npm/codex.cmd --task-packet project-control/tasks/M0-T107.json --config "C:/Program Files/SupervisorConfig/config.toml" --model-selection C:/SupervisorController/model_selection.toml --manifest C:/Users/MLFLL/AppData/Local/NYCBuildabilitySupervisor/ctl24-activation/controller_manifest.json
```

Before the handover the orchestrator re-runs the R276-pattern preflight (clean synced
tree, CI green at tip, anchors intact, executables/digests re-checked, packet staged,
journal readback). The restored restart path: the journal rests at **HALTED**; the owner
(or orchestrator, per the certified operator surface) first runs the NEW audited
`owner-restart` command — which fail-closed re-verifies flag/state/asks/effects/children/
identity/classification — moving HALTED → IDLE with a durable audited owner-restart
record; THEN the certified start dispatches.

**Cycle-2 protocol (R316–R322 + Amendment 15, recorded for the owner act):**
* **ONE attempt** (R316). Expected on success: the live rotation crossing at the seam
  (worker at 604,772 tokens), then the independent Codex re-review of checkpoint
  `M0-T107-ready-2026-08-29-01` (codex_reviews 1/3 used), then actual M0-T107 advancement.
* On ANY further post-dispatch counted stop: **Amendment 15 binds** (R317/R300/R301) — NO
  restart, preserve ALL evidence untouched, diagnose the independent-review failure as a
  separate bounded AD-093 defect task citing D-024-R301; the owner-touch budget is 2/2 AT
  CAP, so a further counted stop is also an S16.7 excess needing disposition.
* On a live-journey failure of any other shape: preserve everything, report the new seam,
  NO repeated restarts, NO full-autonomy claim (R321/R322).
* Continuous operability is declared ONLY from the completed live journey (R319/R320).
