# M0-T113 — G2 self-check (orchestrator, producer-side verification before independent review)

Recorded 2026-08-30 after the seq-33 live proof. The unit spans four working sessions and
seven amendments (9–15); its deliverables are the two allowed_paths reports
(`M0-T113-activation-preflight.md` with sections 1–6; `M0-T113-activation-evidence.md`
with the R260 report + addenda 1–2) plus the control-plane record trail.

| # | Check | Result |
|---|---|---|
| 1 | Scope | PASS — the unit's file deliverables are exactly its two allowed_paths reports; every other change in its arc was control-plane records (captures, gates, campaign, task packets) or separately-gated units (T114–T120) |
| 2 | The activation act (R250–R254) | PASS — owner-typed authorization captured before acting; complete preflights before every start; the exact certified command shape every time; dispatch only at clean/certified/green states (four non-matching states stopped, never bypassed) |
| 3 | The operation proof (R255/R256/R260/R269) | PASS — full loop traversal live: select → dispatch Fable 5 (`observed_models: claude-fable-5`) → structured checkpoint `M0-T107-ready-2026-08-29-01` parsed/validated/correlated → 46KB evidence packet → Codex review → policy check; every fail-closed seam hit behaved as certified (ASK never AUTO; S14; pre-dispatch refusals; UNSAFE_OR_DRIFTED on corrupt inputs; HALT_UNSAFE on the untrusted checkpoint; rotation deferred to the seam) |
| 4 | Zero ask-stops on routine discovery (the R276 proof goal) | PASS — the seq-33 run completed with `permission_decisions: []`: no brokered command requests at all; the original shell-first stall did not recur |
| 5 | The repin (R277/R285) | PASS — one-time, on the certified start only, recorded with provenance; pinned digest = the R282-admitted 2.1.251 binary; drift detection re-armed |
| 6 | Prohibitions (R257/R273/R280) | PASS — every exclusion untouched (PR #241 unmerged, no autostart/C1/Telegram-live/OS-ACL/production/credentials); the runtime journal never hand-edited (reconciliation only via the reviewed read-time path, proven end-to-end); no DISABLE_UPDATES, no downgrade |
| 7 | Stop-and-report discipline (R259/R267/R270/R271/R276) | PASS — four distinct mismatch stops each reported exactly with owner options; zero restart loops; both certification invalidations ran the full R247 cycle before resume |
| 8 | Amendment-15 protocol (R298–R301) | RECORDED — this gate chain is R298's execution; the R299 report is delivered at acceptance with a fresh status readback; the cycle-2 no-restart + separate-defect protocol is captured, bound, and in the campaign NEXT |
| 9 | Evidence integrity | PASS — the 32-row evidence map cites only committed artifacts (preflight §1–6, evidence report + addenda, fable-probe report, amendment captures, progress logs, audit chain); the audit chain (31 events) and journal are intact and unedited |
| 10 | Honest characterization | PASS — the cycle-1 HALT_UNSAFE is reported as the certified independent-review refusal (a design success), NOT as task failure; the `native_tools_guidance_appended: false` resume nuance is disclosed with its digest-binding cause; the bash-mangled attempt is disclosed as an orchestrator formatting error |

**VERDICT: G2 PASS — ready for the independent G3/G4/G5 wave.**
