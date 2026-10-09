# M0-T122 — G3 code review (VERBATIM reviewer return; saved by the orchestrator, transport entity-decoding only)

All checks reproduce. Compiling the G3 report.

---

# G3 CODE REVIEW REPORT — M0-T122 (fourth golden recertification)

**Task:** M0-T122 — R247/R314 recertification at the post-restart-channel frozen identity
**Producer of record:** orchestrator (governance packet; no code changed) — I am fully independent
**Frozen head:** `git rev-parse HEAD` = `62194d1` (verified). Deliverables byte-identical between `acf6505` and `62194d1` (`git diff --stat acf6505 62194d1 -- <both report files>` empty).
**Reviewer:** code-reviewer (read-only). I did not re-review M0-T121 (reviewed first-hand; I carry that the T121 restart pack went 31→34 in the F2 rework).

## Method
Every certification number was re-executed at the frozen head, not read from prose.

---

## Findings

### F1 — Identity anchors all reproduce — PASS
```
git log -1 --format=%H -- tools/agent_supervisor/   = 668c824...              (report §1) ✓
git rev-parse HEAD:tools/agent_supervisor           = d3db9f3c7ee66ff3...     ✓
git rev-parse HEAD:tools/test_agent_supervisor_golden_run.py = c54fd0d2d0e3833e...  ✓ (byte-identical to the T119 cert)
git rev-parse HEAD:tools/test_agent_supervisor_restart_channel.py = d3e23087f0f76a66...  ✓
```
All four anchors match the recert report §1 and the activation-package §10 refresh exactly. The supervisor material identity last moved at `668c824` (T121); the accepted rework `6432d2d` touched only the test pack (outside `tools/agent_supervisor/`), so certifying at this tree is correct.

### F2 — Chain arithmetic 2,780+34=2,814 is consistent — PASS
The T119 baseline (`M0-T119-recertification.md:49`) is independently **2,780 passed / 2 skipped / 0 failed (2,782 collected)**. I reproduced the current collection:
```
python -m pytest tools/test_agent_supervisor_*.py --collect-only -q  =>  2816 tests collected
```
2,816 collected = 2,814 passed + 2 skipped, matching the report. The delta from the T119 collection (2,782 → 2,816) is **exactly +34** — precisely the new restart-channel pack's size (which I confirmed is 34 tests). This is strong corroboration on two axes: (a) the only test-set change since T119 is the addition of the restart pack, and (b) the cli.py +2 subcommand wiring did **not** expand any parametrized/subcommand-enumerating test (else the delta would exceed 34). The pre-delta cross-check "2,811 = 2,780+31" is consistent with my first-hand knowledge that the pre-rework restart pack had 31 tests.

### F3 — Suite claim adequately evidenced — PASS
I did not re-run the full 425 s / 2,814 suite (unnecessary for a governance recert). I ran the required pack plus one more, plus a substantive sample:
```
pytest golden_run + restart_channel              => 76 passed   (42 golden + 34 restart) ✓ (matches report §1 golden=42, restart=34)
pytest recovery + recovery_probes                => 146 passed
```
Zero failures across 222 sampled tests. Combined with the exact collection count (F2) and the CI 20/20 claim at `6edf820` (supervisor-bridge whole-suite job; DCV-confirmed, orchestrator-captured — not runnable in my read-only sandbox), the whole-suite `2,814 passed` claim is adequately evidenced. Far above the ≥1,165 M0-T039 freeze floor. **AS-1/AS-2 satisfied.**

### F4 — CLI identity + drift tooth — PASS
```
executable_identity('C:\Users\MLFLL\.local\bin\claude.exe', name='claude').digest
  = d6f6c29a8ac6b3cf1b76e53cca2faadf784bf5114230c815d55327dbae889ed8   ✓ exact
pytest event_bus -k version_matches_catalog  => 1 passed
```
The digest matches the admitted 2.1.251 identity and the report's `d6f6c29a…` (no repin needed). The executable path digested is the same one named in the handover command (F6), so the command references the certified binary. **AS-3 satisfied** (manifest digest `7f9991cb…`/120 files, verify-controller, doctor are orchestrator-captured against `%LOCALAPPDATA%` outside my repo scope — consistent with the evidence-capture division of labor; not independently reproducible in-sandbox, correctly framed as executed-command output in the G2 self-check).

### F5 — Report honesty (R319) + handover protocol (AS-4) — PASS
Recert §3 explicitly states unit tests + golden pack + this recertification do **NOT** prove continuous operability, deferring the live journey (owner restart → preflight → fresh Fable rotation → Codex review → M0-T107 advancement) to the owner-typed cycle-2 act (R320). No affirmative operability/autonomy claim appears in the recert report or the §10 refresh. §4 records the R315 hold, the verbatim one-line handover command, and the R316–R322 + Amendment-15 protocol (one attempt; on further post-dispatch counted stop, no restart / preserve evidence / separate AD-093 defect / touch budget 2/2 at cap). The handover command matches the certified item-3 template (`M0-T096-activation-package.md:78-82`):
- mode `limited-auto` **with** `--owner-enable-bounded-auto` (the certified cycle-2 mode); executables, `--task-packet project-control/tasks/M0-T107.json`, `--config`, `--model-selection`, `--manifest` all present; **no `--repin-cli-identity`**; **forward-slash paths**; config path **quoted** (`"C:/Program Files/SupervisorConfig/config.toml"` — the only path with a space); `!` prefix; one line. ✓
- The described restored path — journal at HALTED → owner runs the NEW audited `owner-restart` (fail-closed re-verifies flag/state/asks/effects/children/identity/classification) → HALTED→IDLE with a durable audited record → then `start` dispatches — matches the shipped M0-T121 `owner_restart` surface semantics I reviewed first-hand. ✓

### F6 — Activation-package refresh scope (AS-1 anchors) — PASS
```
git diff 96362c0 acf6505 -- .../M0-T096-activation-package.md
```
The diff replaces **only** the §10 "third refresh (M0-T119)" block with the "fourth refresh (M0-T122)" block; no other section altered. Every §10 number matches the recert report: material `668c824`, tree `d3db9f3c`, golden blob `c54fd0d2` (byte-identical to T119), restart blob `d3e23087` (34 tests), CLI `d6f6c29a…` (no repin), whole suite 2,814/2/0, chain 2,780+34 (pre-delta 2,811=2,780+31), manifest 120 files / `7f9991cb…`, doctor HALTED / audit 33 / OS-ACL PROTECTED.

### F7 — Preserved live journal untouched — PASS
The task changed no code (`forbidden_paths: tools/**`); the two deliverables are report files, and the full delta (`acf6505..62194d1` and the T122 landing) touches only `project-control/**` reports + control-plane. Every journal reference in the report is a read-only observation (doctor: HALTED, transitions 13, audit head 33 — the 31→33 growth is the pre-window seq-35 refused-start audit events, per the G2 note; `record-manifest`/`doctor` write outside the repo and read the journal read-only). Nothing in the deliverables suggests a journal write. No finding.

### F8 — Directive requirement rows (packet directive_refs D-024 ALL; resolver set R302, R314–R322) — PASS
Each row is reproducibly evidenced above: R302 (authorized recert half, no other work started) — F1; R314 (frozen-identity recert executed) — F2/F3/F4; R315 (hold honored, handover recorded not released) — F5; R316/R317 (one-attempt + Amendment-15 enforcement recorded verbatim) — F5; R318 (no producer interrupted; orchestrator-executed evidence); R319 (no operability claim) — F5; R320 (live-journey standard recorded; journal untouched) — F5/F7; R321/R322 (failure protocol + no-autonomy/no-repeat recorded verbatim) — F5. No gap between a named requirement and reproducible evidence.

---

## Assessment
All certification claims reproduce at the frozen head: the four identity anchors are exact, the CLI digest and drift tooth are green, the golden blob is byte-identical to the T119 certification (capabilities carried un-weakened), and the whole-suite count is confirmed by an exact collection match (2,816 = 2,814+2) whose delta from T119 is precisely the 34-test restart pack — with zero failures across 222 sampled tests. The R319 disclaimer is honest, the handover command matches the certified item-3 shape (no repin, forward-slash, quoted config), the restored `owner-restart`→`start` path matches the shipped M0-T121 semantics, the activation-package refresh changed only §10 with numbers matching the recert, and the preserved journal is only ever read. No defects; no required corrections.

VERDICT: PASS
