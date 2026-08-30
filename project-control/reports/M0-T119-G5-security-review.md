<!-- Saved VERBATIM by the orchestrator from the G5 security-reviewer agent-return channel
     (transport entity-decoding only). Review head 357bb50, deliverable 882966b, certified
     material identity 7d8195b. -->

All checks complete. Every load-bearing claim independently reproduced at the frozen identity. Here is the complete G5 security review report to return to the orchestrator.

---

# Gate Report

- Gate ID: G5 (security)
- Task ID: M0-T119 (D-024 Amendment 13 unit S — third golden re-certification + R282 admission record)
- Reviewer: security-reviewer (independent, read-only)
- Producer: orchestrator (orchestrator-recert-runner) — report-only unit; verified independently
- Result: **PASS**
- Clean environment/worktree used: reviewed at frozen control head `357bb50` (deliverable `882966b`; certified material identity `7d8195b`) in the primary checkout `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24`; all git-object, binary-hash, registry, manifest, and pytest evidence reproduced from that state.

## Acceptance criteria reviewed

- AS-1 (whole-suite exact reconciliation 2712→2782) — reproduced PASS
- AS-2 (golden + affected packs pass; certified anchors pinned) — reproduced PASS
- AS-3 (DISABLE_AUTOUPDATER active; `claude --version` identical, 2.1.251) — reproduced PASS
- AS-4 (R282 admission line appears only after every pass-list item recorded PASS) — reproduced PASS

## Security review scope (6 assigned checks)

All six assigned checks reproduced independently from primary evidence. Cross-tenant isolation, service-role secrecy, private storage, SSRF/injection, and upload controls are N/A for this report-only unit (no production code changed — proven in Check 2); the security-relevant act is the R282 admission that authorizes the one-time repin, which I verified in depth.

### Check 1 — Admission-record integrity (R282): the security-critical act — PASS, NOT STALE
- Independently re-hashed the installed binary via the project's own identity function:
  `python -c "from tools.agent_supervisor.process import executable_identity; ..."` on `C:/Users/MLFLL/.local/bin/claude.exe`
  → `d6f6c29a8ac6b3cf1b76e53cca2faadf784bf5114230c815d55327dbae889ed8` (`digest_kind=sha256_head+size`, size 217360032). **This STILL equals the recorded admission digest `d6f6c29a8ac6b3cf…`.** The CLI has NOT drifted since certification — the admission is not stale, and the pending `--repin-cli-identity` will pin the correct executable. (Corroborated: the M0-T120 DCV independently re-hashed the same binary to the same digest.)
- `claude --version` → `2.1.251 (Claude Code)`. Matches the certified/admitted version and the window start/end stamps in report §2.
- `reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v DISABLE_AUTOUPDATER` → `REG_SZ 1`. Machine-scope belt is active, so the CLI cannot silently change again while the loop runs.

### Check 2 — Unit scope — PASS (report-only, no production change)
- `git show 882966b --name-only` → touches ONLY `project-control/reports/M0-T096-activation-package.md` and `project-control/reports/M0-T119-recertification.md`. No source, no schema, no config.
- `git diff --name-only 7d8195b..882966b -- tools/ docs/ apps/ services/` → **empty** (no production change anywhere in the certification window). The full `7d8195b..882966b` diff is entirely `project-control/**` (M0-T120 gate/DCV records, state.json, the two M0-T119 deliverables). `882966b..357bb50` adds only M0-T119 control-plane records (G2 self-check, evidence-map, task/state). The `docs/`-touched-earlier caveat did not materialize in this window — nothing under `docs/` moved.
- Confirmed the supervisor material identity is frozen: `git rev-parse HEAD:tools/agent_supervisor` = `8d34ea53575f2cdf5b2d99029111c9e174339596` (matches report §2 tree); `git rev-parse HEAD:tools/test_agent_supervisor_golden_run.py` = `c54fd0d2d0e3833e54ba2ec9745ee6e7d9fdb550` (matches golden blob); last commit touching `tools/agent_supervisor` = `7d8195b` (M0-T120). `git log f89aa29..HEAD -- tools/agent_supervisor` = exactly {fa16560+d6a2ac8 (T117), d1b05bb (T118), 7d8195b (T120)} — the composition claim "nothing else touched supervisor code since f89aa29" is TRUE.

### Check 3 — Claim-evidence binding (report §3/§4 pass list) — PASS
- Golden pack: `pytest tools/test_agent_supervisor_golden_run.py` → **42 collected, 42 passed** (incl. `test_the_routing_tooth_bites_a_certified_start_without_evidence`). Matches "42/42".
- Whole suite: `pytest tools/test_agent_supervisor_*.py --collect-only` → **2782 collected**; full run → **2780 passed, 2 skipped, 0 failed** (217.89s). Exactly matches report §3 and the 2712+14+0+56=2782 reconciliation. The 3 version-drift teeth are GREEN at 2.1.251 (0 failures), confirming the fixture re-point.
- Fixtures exist at named paths: `hook_event_catalog_2_1_251.json` (independently counted **33 events**), `loop_interception_detection_2_1_251.json`, `shell_routing_2026-08-29_m0t120_2_1_251.json`; plus `routing_probe.py` and `prompts/claude_native_tools.md`.
- Gate records: all PASS — T117 G0/G2/G3/G4/G5; T118 G0/G2/G3/G4/G5; T120 G0/G2/G3/G4/G5.
- DCV row counts reproduced against the DCV reports: T117 = **7/7** (R277,R278,R279,R280,R286,R287,R288), T118 = **5/5** (R277,R279,R280,R281,R282), T120 = **8/8** (R289–R296). Matches "7/7, 5/5, 8/8".
- Manifest binding: inspected the stored `%LOCALAPPDATA%\NYCBuildabilitySupervisor\ctl24-activation\controller_manifest.json` → **119 files**, digest `774f91984bd75c955d5a45bebbea3d26a7eda9c8a4b215b17536fdf5017ff022` — exact match to report §3/§4.

### Check 4 — No premature or duplicate admission — PASS
`grep -rniE "2\.1\.251" project-control/ ... | grep -i admit`: the ONLY affirmative admission record is `M0-T119-recertification.md` §4 (lines 71, 87), plus the package item-10 pointer (`M0-T096-activation-package.md:175`) and the item-12 descriptive reference (line 249), both citing the recert report §4. Every earlier occurrence is an explicit deferral/negation (T118 evidence-map "NOT recorded…", T118 producer/G0/G5 "admission deferred to M0-T119", T117/T118/T119 packet objectives "only after…", directive/manifest/requirements text). No premature or duplicate admission exists. See SEC-INFO-2 for one loose-wording note.

### Check 5 — Resume gating language + R257 exclusions — PASS
- Report §6: "the R276 rerun (R284), which starts only after THIS unit is accepted through its gates." Package banner: "only once M0-T119 is ACCEPTED through its gates AND the complete activation preflight passes again does the certified start re-run." Both gate on **acceptance**, not on the report's existence.
- R257 exclusion list (D-024-R257: autostart, PR #241, production, credentials, payments, legal, OS-ACL, C1 canary, Telegram live-send, natural-event graduation / 4.8-bridge live actuation, three residuals) survives intact. The deliverable diff did NOT touch package item 8 (4.8 bridge shadow-only, double-gated by `assert_actuation_permitted` — R595 + measured-live corpus, both absent) or item 14 (remaining owner-only steps: R187/R595 activation, install-autostart, C1 canary, natural-event graduation, OS-ACL hardening). Report §6 confirms "no PR #241 touch." All other owner gates untouched.

### Check 6 — No secrets/PII in the two deliverables — PASS
`grep -rniE "password|secret|api_key|token|bearer|sk-ant|ghp_|AKIA…"` over both files: the only hit is `M0-T096:127` "receive token **quotas**" — operator-channel log-redaction design language (operators never receive token budgets/countdowns), a redaction control, not a secret. No credentials, keys, or PII; no owner email present.

## Expected versus actual

| Claim | Expected | Actual (reproduced) | Verdict |
|---|---|---|---|
| Admission executable digest | `d6f6c29a8ac6b3cf…` | `d6f6c29a8ac6b3cf1b76…889ed8` (live re-hash) | PASS — not stale |
| `claude --version` | 2.1.251 | `2.1.251 (Claude Code)` | PASS |
| DISABLE_AUTOUPDATER (HKLM) | 1 | `REG_SZ 1` | PASS |
| Deliverable files touched | 2 report files only | exactly the 2 report files | PASS |
| Production change in window | none | none (tools/docs/apps/services empty) | PASS |
| Golden pack | 42/42 | 42 collected, 42 passed | PASS |
| Whole suite | 2782 / 2780p / 2s / 0f | 2782 / 2780p / 2s / 0f | PASS |
| Manifest | 119 files, 774f9198… | 119 files, 774f9198…7ff022 | PASS |
| Tree / golden blob | 8d34ea53… / c54fd0d2… | exact match | PASS |
| DCV counts | 7/7, 5/5, 8/8 | 7/7, 5/5, 8/8 | PASS |
| codex-cli | 0.146.0 unchanged | 0.146.0 | PASS |

## Regression/security/provenance findings

1. **SEC-INFO-1** — Live-probe provenance for the R282 "Live probes" row cites `doctor --live … seq-30`, which predates Amendments 13/14. This is not stale: the binary digest is byte-stable from seq-30 through this review (re-hashed, identical), and the item is additionally backed by M0-T118 live capability/native probes and M0-T120's live bounded routing probe, all at the same 2.1.251 executable. No action required.
2. **SEC-INFO-2** — `M0-T120-G0-readiness.md:8` uses the shorthand "the admitted 2.1.251" before the M0-T119 admission was recorded. It is a readiness-gate descriptor in an already-accepted unit (outside these two deliverables), carries no `ADMITTED:` declaration or pass-list, and the M0-T120 DCV independently confirmed no admission occurs in M0-T120. Wording imprecision only; not a premature admission record.
3. **SEC-INFO-3 / carried SEC-MINOR (disclosed, non-blocking)** — Report §5 honestly carries prior-review residuals: F2/F1 (wrapper-form `powershell -Command "Remove-Item …"` and pipe-to-interpreter classify ASK not HARD_DENY — still gated, never AUTO), F-LIVE-1 (2.1.251 reports `permissionMode=default` despite `--permission-mode manual`; mutating tools remain brokered+denied, verified live), and the routing-gate `== MODE_LIMITED_AUTO` hardcode. These originate in M0-T117/T120 (already adjudicated non-blocking by those units' G5/DCV) and touch no code in this unit. No new security exposure introduced by M0-T119.

Least-privilege / prompt-injection posture: report §6's byte-untouched claim for the broker/classifier/owner gates is consistent with Check 2 (zero production change); the routing/broker teeth (M0-T120) are already gated. The admission narrowly unpins only the CLI-drift refusal via an owner-authorized (R285), digest-verified one-time repin, with future drift re-armed as a fresh admission event (R286/R287 preserved in the package). No privilege broadening.

## Defects
None.

## Required rework
None.

## Reviewer conclusion
The M0-T119 deliverable is a clean, report-only certification: it edits only its two report files, introduces no production change, and its every load-bearing claim reproduces at the frozen identity `7d8195b`. The security-critical act — recording Claude Code 2.1.251 as the admitted provider CLI — is sound: the cited executable digest still equals a live re-hash of the installed binary (admission is NOT stale), the version is 2.1.251, the machine-scope DISABLE_AUTOUPDATER belt is active, the admission line appears only after a complete and independently-verified R282 pass list, no earlier affirmative admission exists, the R276 rerun is gated on this unit's acceptance, and all R257 owner-gate exclusions (autostart, PR #241, C1 canary, Telegram live-send, natural-event graduation, OS-ACL, 4.8-bridge shadow-only) survive untouched. No secrets or PII. All findings are INFO-level and non-blocking.

## Read-only commands executed
- `git log --oneline -5`; `git rev-parse HEAD`
- `git show 882966b --name-only`; `git diff --name-only 7d8195b..882966b [-- tools/ docs/ apps/ services/]`; `git diff --name-only 882966b..357bb50`
- `git show 882966b -- project-control/reports/M0-T096-activation-package.md`
- `git rev-parse HEAD:tools/agent_supervisor`; `git rev-parse HEAD:tools/test_agent_supervisor_golden_run.py`; `git log f89aa29..HEAD -- tools/agent_supervisor`
- `python -c "from tools.agent_supervisor.process import executable_identity; ... 'C:/Users/MLFLL/.local/bin/claude.exe'"`
- `claude --version`; `codex --version`
- `reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v DISABLE_AUTOUPDATER` (and HKCU)
- `python -m pytest tools/test_agent_supervisor_golden_run.py --collect-only -q` and full run
- `python -m pytest tools/test_agent_supervisor_*.py --collect-only -q` and full run
- `ls`/`python -c json.load` on the three fixtures, `hook_event_catalog_2_1_251.json` event count, and `%LOCALAPPDATA%\NYCBuildabilitySupervisor\ctl24-activation\controller_manifest.json`
- `grep` over `project-control/gates/` and DCV reports for verdicts/row counts; `grep` over the two deliverables for secrets/PII/admission/exclusion language; reads of the M0-T119 packet, both deliverables, and D-024 source-013/014 + requirements.json (R257/R282).

Relevant file paths (all absolute):
- `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24/project-control/reports/M0-T119-recertification.md`
- `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24/project-control/reports/M0-T096-activation-package.md`
- `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24/project-control/tasks/M0-T119.json`
- `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24/project-control/directives/D-024-fable-codex-loop/source-013-amendment.md`
- `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24/project-control/directives/D-024-fable-codex-loop/source-014-amendment.md`
- `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24/project-control/directives/D-024-fable-codex-loop/requirements.json` (R257 line 9222, R282 line 9986)
- `C:/Users/MLFLL/.local/bin/claude.exe`
- `C:/Users/MLFLL/AppData/Local/NYCBuildabilitySupervisor/ctl24-activation/controller_manifest.json`

G5 VERDICT: PASS
