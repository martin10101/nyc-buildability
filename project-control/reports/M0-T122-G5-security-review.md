# M0-T122 — G5 security review (VERBATIM reviewer return; saved by the orchestrator, transport entity-decoding only)

I have completed all verification steps. Here is my G5 security review report for M0-T122.

---

# G5 SECURITY REVIEW — M0-T122 (Fourth golden recertification)

**Frozen head:** `62194d1` (`git rev-parse HEAD` → `62194d1664eb...`) — verified. Deliverables landed at `acf6505`.
**Producer of record:** orchestrator (governance packet; no code changed).
**Deliverables reviewed:** `project-control/reports/M0-T122-recertification.md`, `project-control/reports/M0-T096-activation-package.md` (section-10 fourth refresh), `project-control/reports/M0-T122-evidence-map.json`.
**Reviewer:** security-reviewer (read-only). I did not touch the live runtime dir / preserved journal (forbidden_paths).

## Verdict summary
No SEC-MAJOR or SEC-MINOR findings. The certification's security posture is sound: the CLI identity claim reproduces exactly, no secrets/Telegram values leak, the R315 owner gate and the M0-T121 fail-closed restart discipline are honored, and no operability/autonomy claim is made. Two INFO notes. **VERDICT: PASS.**

## 1. No secrets / credentials / Telegram values (R242/R243) — PASS
- Scanned both T122 deliverables + the activation-package refresh for `telegram|bot_token|chat_id|<digits>:<b64>|xox*|ghp_|sk-*|BEGIN|password|secret|api_key|bearer`. **No credential, bot token, or chat id appears.** The only "telegram" hit is `M0-T096-activation-package.md:232` — the descriptive phrase "the accepted Codex-channel and Telegram-sink additions in place" (a feature-name reference, no value), and it is **pre-existing text (M0-T112 refresh), not part of the section-10 change** this task made.
- The section-4 handover command contains only executable paths, config/manifest **paths**, and flags. The secret-bearing external `config.toml` is referenced **by path only** (`"C:/Program Files/SupervisorConfig/config.toml"`) and never inlined — exactly the R242/R243-compliant posture (secrets live outside the public repo per the thin-client policy).
- Verification: `grep -rniE "telegram|bot[_-]?token|chat[_-]?id|[0-9]{8,10}:[A-Za-z0-9_-]{30,}|xox|ghp_|sk-|BEGIN|password|secret|api[_-]?key|bearer" <3 files>`.

## 2. Certification integrity — CLI identity undrifted — PASS
- Re-ran `python -c "from tools.agent_supervisor.process import executable_identity; print(executable_identity(r'C:\Users\MLFLL\.local\bin\claude.exe', name='claude').digest)"` →
  `d6f6c29a8ac6b3cf1b76e53cca2faadf784bf5114230c815d55327dbae889ed8`.
- This equals the admitted digest recorded in recert §1 and the activation-package refresh **byte-for-byte**. The identity is undrifted, so the NO-repin claim is sound: a repin-free certified start will pass the S11.5 pinned-identity probe. AS-3's "drift tooth green, digest unchanged, no repin" is reproduced.

## 3. Owner-gate discipline — PASS
- **R315 hold honored:** recert §4 states the cycle-2 command is released "only after THIS task is accepted"; the command is recorded verbatim **for verification behind the hold**, not handed over. Evidence-map D-024-R315 corroborates ("no R276 rerun executed, no cycle-2 command handed to the owner").
- **No gate weakened / limited-auto not broadened / no MCP or channel added:** the start command is the existing certified item-3 shape (`--mode limited-auto --owner-enable-bounded-auto`), which the doctor row confirms is "limited-auto IMPLEMENTED and OFF by default" — the `--owner-enable-bounded-auto` flag is the owner-typed R595 activation path, not a broadening. No MCP server, no new channel, no allowlist change appears in either deliverable.
- **PR #241 untouched:** no `#241`, `pull/241`, or merge instruction anywhere in the deliverables (grep clean). The only "merge/weaken/autonomy" grep hits are the prohibition statements themselves ("un-weakened tests carried", "NO full-autonomy claim").
- **Restored restart path requires M0-T121 fail-closed preconditions and does not bypass emergency-stop discipline:** recert §4 correctly routes HALTED → the NEW audited `owner-restart` verb, which "fail-closed re-verifies flag/state/asks/effects/children/identity/classification" before HALTED→IDLE, then start dispatches. The journal is at HALTED (not EMERGENCY_STOPPED), so `owner-restart` is the correct verb; the stronger token-gated `acknowledge-emergency-stop` path is not invoked and is not weakened. This matches the M0-T121 code I certified in the prior G5 (evaluate_preconditions ordering: emergency-stop flag first, then exact source state).

## 4. Journal safety — consistent read-only posture — PASS (INFO-2)
- The certification commands are read-only against the preserved journal per the report: `doctor` reads; `record-manifest` writes ONLY the manifest file under the external `…/ctl24-activation/` dir (outside the repo), not the journal. The packet forbids touching the live runtime dir, which I honored.
- **Internal consistency check of the doctor row:** journal HALTED, **transitions 13** (unchanged), **audit head 33 verified**. A refused start appends audit events without a state transition, so audit rising from 31→33 (+2 = the seq-35 refused-start events) while transitions stay flat at 13 is exactly the expected signature of refused starts — NOT of a mutation by this certification window. The window as described could not have mutated the journal (no write path to it; the two extra audit records are attributable to the separate refused-start attempts, not to doctor/record-manifest/verify-controller).
- I could not (and must not) independently re-read the live journal; this judgment rests on the described read-only posture plus the internal consistency above.

## 5. R319 / R320 — no operability/autonomy overclaim — PASS
- Recert §3 (R319, "binding") explicitly states unit tests + golden pack + this recertification do **NOT** prove continuous operability. §4 repeats: "Continuous operability is declared ONLY from the completed live journey."
- The live-journey standard (R320) is recorded accurately: the REAL preserved journal through **owner restart → preflight → fresh Fable rotation → independent Codex repository review → actual M0-T107 advancement**. No affirmative operability/autonomy claim appears in either deliverable. R321 (preserve everything / report new seam) and R322 (no repeated restarts, no full-autonomy claim) are recorded verbatim in §4.

## Scope / regression
- `acf6505` touched only the two allowed report files plus control-plane artifacts (gates, tasks, state, campaign, evidence-map, G0-readiness) written under the orchestrator's own authority. **No `tools/**` or code changed** (forbidden_paths honored); the supervisor material identity is unchanged since `668c824`, consistent with §1. Because no code changed, the M0-T121 security properties I certified (and the delta-attested test hardening) are carried intact.

## INFO
- **INFO-1:** the handover command and refresh contain local absolute paths that include the Windows username (`MLFLL`) and internal config/manifest locations. These are non-secret filesystem paths (the username is already the repo's git-author identity), and the secret-bearing `config.toml` is referenced by path only. Acceptable in a public repo; no remediation required, but the orchestrator may prefer placeholder paths in owner-facing text as defense-in-depth.
- **INFO-2:** journal-safety is judged from the report's described read-only posture and the doctor-row internal consistency (audit +2 refused-start events, transitions flat at 13); no independent live-journal read was performed (correctly out of scope).

Reproduction commands (read-only):
```
git rev-parse HEAD
git show acf6505 --stat
git show acf6505 -- project-control/reports/M0-T096-activation-package.md
python -c "from tools.agent_supervisor.process import executable_identity; print(executable_identity(r'C:\Users\MLFLL\.local\bin\claude.exe', name='claude').digest)"
grep -rniE "telegram|bot[_-]?token|chat[_-]?id|[0-9]{8,10}:[A-Za-z0-9_-]{30,}|ghp_|sk-|password|secret|api[_-]?key" project-control/reports/M0-T122-recertification.md project-control/reports/M0-T122-evidence-map.json project-control/reports/M0-T096-activation-package.md
```

Relevant files (absolute):
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\reports\M0-T122-recertification.md`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\reports\M0-T096-activation-package.md`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\reports\M0-T122-evidence-map.json`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\tasks\M0-T122.json`

VERDICT: PASS
