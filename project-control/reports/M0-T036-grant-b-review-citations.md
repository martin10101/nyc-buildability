# M0-T036 — standing grant (b) "after a passing review" citations (D-007-R551)

- Recorded: 2026-08-03T23:15+00:00, orchestrator, on the owner's demand (D-007 amendment 2)
- Grant (b) (D-007-R537): auto-approve push to `task/M0-T036-supervisor-bridge` after a passing
  review — never main; R721 governs merges regardless.

## What review satisfied the condition, per phase push

Every push to the task branch was executed by the orchestrator only after the orchestrator's own
**phase-integration verification review** of the producer's submitted work (producer =
backend-engineer, verifier = orchestrator; producer ≠ verifier). No push occurred on producer
self-attestation: each phase's claimed file set was re-hashed file-by-file against the producer
manifest and every suite was independently re-run by the orchestrator on the ported tree before
the push. The verdicts and their preservation:

| Phase | Push commits | Passing review relied on | Verdict preserved at |
|---|---|---|---|
| 1 | `2f937c1`, `f39192f` | 26/26 per-file LF SHA-256 verification vs the producer manifest; orchestrator re-ran the suites: 139 OK (1 justified skip); zero control-plane regressions (22 groups + directive suites) | `project-control/tasks/M0-T036.json` progress_log 2026-08-03T05:00; full hashes in `project-control/reports/M0-T036-phase1-port-hashes.json`; producer checkpoint verbatim in `project-control/reports/M0-T036-producer-report.md` |
| 2 | `d1f0f74`, `6f4208f` | 17/17 full-hash verification + 10 claimed-unchanged Phase 1 modules verified byte-identical; orchestrator re-ran all eight suites: 383 OK (2 justified skips), zero Phase 1 regressions, doctor 20/20 | progress_log 2026-08-03T06:09; checkpoint appended verbatim to `M0-T036-producer-report.md` |
| 3 | `3a09aff`, `7b179ec` | orchestrator re-ran the ported tree: 735 OK; doctor 30/30; control-response wrapper VERIFIED live (one disclosed probe); restore drill passed; no §18 stop | progress_log 2026-08-03T16:30 |
| 4 | `f49ae74`, `fdca6ba` | orchestrator re-ran 19 suites: 1042 OK; replay corpus 8/8; doctor 36/36; Job-Objects default closed; four defects fixed without weakening stops; integration amendment (gitleaks-caught seeded fixture; producer patch applied verbatim, post-hash 248cf595 verified) | progress_log 2026-08-03T19:54 and 2026-08-03T20:42 |

## Honest boundary statement

These were **orchestrator verification reviews**, not the independent gate reviews. The packet's
required gates (G2, G3, G4-equivalent validation, G5) and its named independent reviewers
(code-reviewer, security-reviewer, qa-engineer, control-plane-verifier,
directive-compliance-verifier) have **not yet reviewed** the phase work — those reviews run at
submit/gate per the normal lifecycle and are among the "independent reviews" the Phase 5 decision
packet must contain (D-007-R506). If the owner intended grant (b)'s "passing review" to require an
independent reviewer-agent verdict rather than the orchestrator's producer≠verifier integration
verification, that stricter condition was not met by any phase push, and the orchestrator flags it
here rather than interpreting silently (directive-compliance rule 9).
