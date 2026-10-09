# M0-T107 DCV re-attestation — D-024-R748 / R749

> Orchestrator note: verifier return saved verbatim (transport entity-decoding only). Verifier: fresh independent directive-compliance-verifier agent (read-only), returned 2026-09-03 (UTC).

Independent read-only re-verification of the two previously-UNVERIFIABLE rows, now that the durable return-report artifact exists at HEAD.

**ctl24 HEAD reviewed:** `e783369e080c807e2e3c6371ef0ef38bcf867b64` (branch `candidate/D-024-mrl-option-b`)
**Artifact:** `project-control/reports/M0-T107-return-report.md` — added in commit e783369e (only commit touching the path; `git log --name-status` shows `A`).

| Req | Result | Evidence (reproduced) |
|---|---|---|
| D-024-R748 | PASS | Artifact presents all four required elements, each cross-checked: (a) Codex findings §1 — the five asks F1–F5 faithfully mirror the real `codex_decision.json` REVISE rationale (diff-summary-only, untrusted worker checkpoint / no acceptance commands, truncated material, no directive refs, claims not independently verifiable) — nothing invented; (b) corrections §2 — commit `4047c79c` name-status = both files (docs/D024_PORTABILITY_PLAN.md + portability-plan.md, provenance/status), commit `777ef5e4` name-status = report only, matching the artifact's claims exactly; (c) gate results §3 — G0 PASS/orchestrator, G2 PASS/orchestrator, G3 PASS/code-reviewer, G4 PASS/code-reviewer confirmed against `project-control/gates/M0-T107-G0/G2/G3/G4.json` (`result=PASS`, reviewers match); (d) final task status §4 = ACCEPTED. Matches requirement text line 24541. |
| D-024-R749 | PASS | Committed artifact's last non-empty line is byte-exact `M0_T107_ACCEPTED` (verified: `last==b'M0_T107_ACCEPTED'` True; `cat -A` shows `M0_T107_ACCEPTED$`, no trailing decoration or whitespace), one of the two tokens required by requirement text line 24576. |

**VERDICT: PASS**
