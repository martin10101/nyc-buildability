# Session Handoff — NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume, read it live —
`python tools/project_control.py status` and `python tools/current_state.py` — and reconcile against
the remote: **origin/main may have advanced, so do not trust any SHA written here as still-current.**
This file is orientation only. Operating rules, gates, and workflow routes live in `CLAUDE.md`.

Refreshed **2026-08-08 (session 7 close, CP-0045)**. **The block below supersedes the older
sections** (pruned per the context-budget guard); the ledger wins on any conflict.

## SESSION 7 CLOSE — M0-T048 ACCEPTED + MERGED; activation package is the live item

**M0-T048 ACCEPTED and MERGED (accepted count 68).** PR #180 → main `0a7cc4c`. The full unit:

- **Owner am.15 captured (source-015, R144–R154):** close G3 MAJOR-1 (cross-process resume-window
  `approved_digest` trust anchor) BEFORE acceptance. Fix delivered (task commit `9c450a5`):
  `verify_approved_digest_against_audit` cross-checks the journal `approved_digest` against the
  sealed hash-chained `operator_resume_pending_prompt` approve event BEFORE any forward — six
  distinct fail-closed reason codes, durable sealed `cross_process_resume_refused`, zero provider
  calls. Owner 8-step adversarial harness implemented exactly; RED-on-pre-fix proven (always-on
  test + two independent reviewer mutation probes). Suite **1380/2** (six independent
  reproductions).
- **Owner am.16 captured (source-016, R155–R156):** both suite skips named + adjudicated
  legitimately environment-conditional (`M0-T048-skipped-tests-evidence.md`); no follow-up task.
- **Rerun G3/G4/G5 all PASS, zero corrections** (`M0-T048-g{3,4,5}-rework-review.md`): G3 MAJOR-1
  CLOSED per its own remedy + MINOR-1 resolved; G4 all 8 owner properties independently
  reproduced, setup edit ruled faithful; G5 (original C2 finder) ruled the forgery class CLOSED,
  N-1 re-ruled CLOSED.
- **DCV final: all 20 applicable D-010 rows SATISFIED** (`M0-T048-dcv-final-rework.md`), R152
  deferred at accept then **DISCHARGED** post-merge (`M0-T048-r152-discharge.md`; verification.json
  row PASS at identity `84cf814..`/`c31043d`).

**Disclosures carried to the activation record (verbatim in the gate reports):** G5 **N-4**
(full-local-write chain-rewrite residual — the standing trust-domain limit; closing it needs
signing/external anchoring, R140-excluded, deferred to Phase 3 Option A per audit_log.py); G5
**N-5** (same-run replay of operator-approved content — pre-existing, strictly narrowed by the
fix); G3 **MINOR-2** (ambiguity rule can false-refuse a same-run byte-identical-instruction flow —
fail-closed, availability-only); G5 N-6 / G4 advisories (cosmetic). The former G5-C2 residual
decision is **RESOLVED** (owner ordered the fix; delivered, gated, accepted, merged).

## THE ACTIVATION PACKAGE (owner-held; R131/R132, am.14 R142, am.15 R153)

Every mechanically reconcilable checklist blocker is SATISFIED (see the RECONCILIATION section of
`M0-T036-ACTIVATION-CHECKLIST.md` + this close block). Remaining, in order:

1. **Elevated OS-ACL apply + live PROTECTED proof.** Owner runs, from an ELEVATED PowerShell, with
   the live controller config path substituted:
   `powershell -ExecutionPolicy Bypass -File tools\agent_supervisor\harden_controller_config.ps1 -ConfigPath "<ABSOLUTE PATH TO config.toml>"`
   Then the orchestrator captures `python -m tools.agent_supervisor doctor --config "<path>" --json`
   → `controller_config_acl.protected: true` into a committed report BEFORE any activation step.
2. **Owner-typed supervised-auto activation decision line (R131/R132).** ⛔ NO activation without
   it. The decision is taken with the N-4/N-5/MINOR-2 residuals disclosed (above).
3. **M2-T015 + M2-T016** = the two supervised-auto product proof tasks, dispatched only per the
   owner's activation decision. ⛔ HELD until then (R133/R143).

## OTHER OPEN ITEMS

- **M0-T047 (nanoid GHSA-2v37-7h3g-55p8):** age-eligible **2026-08-10T10:39:22Z** — at/after that
  instant re-verify 3.3.17 advisory-free, execute the contracted packet (CI-bot lock regeneration,
  NO local npm), gate, merge. Until then the NON-required `web-dependency-security` context stays
  red repo-wide (does not block Tier A merges; PR #178/#179/#180 precedent).
- **Housekeeping (classifier-denied, owner may run):** stale merged branch deletion —
  `! git push origin --delete task/M0-T048-c2-close` and `! git branch -D task/M0-T048-c2-close`
  (content fully merged: `9c450a5` is an ancestor of main). The orch worktree
  (`C:/Users/MLFLL/Downloads/nyc-zoning/orch`) still sits on that branch; re-point it at the next
  task claim.
- Rework queue (M0-T021/M0-T034) and the M3 chain under its blockers remain available if the owner
  pauses the activation package.

## Carried rules (unchanged)

- Task branches from origin/main in the orch worktree; spawn PRODUCERS UNNAMED; classifier denial
  ⇒ exact-path staging first, else STOP and surface the `!` line; `project-control/directives/**`
  explicit LF; commits stage exact paths; ADR-006 Tier A merges after green required checks.
- **Reviewer models:** gate reviewers run `claude-opus-4-8` + `xhigh` (standing fallback; the 5
  flipped agent files remain uncommitted in the PRIMARY checkout — revert to `claude-fable-5` pins
  when the owner says "Fable is back"). Orchestrator runs `claude-fable-5`.
- Standing holds unchanged: deployment/G6/Graphify/expansion; SHADOW-ONLY posture intact until the
  owner's typed activation decision (R131); M2-T015/T016 held (R133/R143).

---

_History: superseded session blocks (sessions 1–6 = CP-0037..CP-0044) are pruned per the
context-budget guard — recover with `git log -p docs/SESSION_HANDOFF.md`; the ledger remains
authoritative._
