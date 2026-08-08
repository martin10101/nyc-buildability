# Session Handoff — NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume, read it live —
`python tools/project_control.py status` and `python tools/current_state.py` — and reconcile against
the remote: **origin/main may have advanced, so do not trust any SHA written here as still-current.**
This file is orientation only. Operating rules, gates, and workflow routes live in `CLAUDE.md`.

Refreshed **2026-08-08 (session 7, post-PROTECTED-proof seam; last checkpoint CP-0045)**. **The
block below supersedes the older sections**; the ledger wins on any conflict.

## SESSION 7 STATE — ALL ACTIVATION PREREQUISITES CLOSED; waiting ONLY on the owner-typed decision

**Accepted count 71.** Main (at refresh) `1fd9983`. Full supervisor suite **1392 passed / 2
skipped** (the 2 skips adjudicated legitimately environment-conditional, R155/R156).

Units accepted + merged this session:

- **M0-T048** (PR #180/#181, count 68): C2 closure + owner-ordered G3-MAJOR-1 fix — cross-process
  resume cross-checks the journal `approved_digest` against the sealed hash-chained
  operator-approval audit event before any forward; fail-closed, zero provider calls, durable
  refusal. R152 deferred-then-DISCHARGED. Residuals carried to the activation decision: **G5 N-4**
  (full-local-write chain rewrite — R140-excluded, Phase 3 Option A external anchoring), **G5
  N-5** (same-run approved-content replay — narrowed), **G3 MINOR-2** (fail-closed ambiguity
  false-refusal edge).
- **Controller-config relocation** (source-017/018, PR #182/#183): owner-run elevated move to
  `C:\Program Files\SupervisorConfig\config.toml` (dedicated protected parent; the original
  `C:\SupervisorConfig` plan was STOPPED by the C:\ inherited-Modify preflight check).
  `model_selection.toml` stays MUTABLE at `C:\SupervisorController\model_selection.toml`.
  Config-content check ruled the shadow config exactly correct for supervised-auto (no immutable
  field change needed; claude allowlist [] = account-default posture, live-proven).
- **M0-T049/T050/T051** (PRs #184/#185/+, counts 69-71): THREE owner-demonstrated
  hardening-script defects, each caught by the owner's fail-closed inspection BEFORE privilege
  was exercised, each fixed + adversarially regression-tested + G3/G5/DCV'd + merged:
  (1) WinPS 5.1 parser failure (`$Var:` interpolation) → brace fix + whole-script parser-API test;
  (2) `$Args` automatic-variable collision dropped every command argument → `$CommandArgs` +
  full-vector dry-run tests + dry-run wording branch;
  (3) explicit `Authenticated Users:(M)` ACE survived the apply → `icacls /reset` before
  `/inheritance:r` (deterministic three-ACE DACL by construction) + poisoned-fixture tests.
  **Barred blobs (never elevate): `0f01d649`, `ca3811cd`, `9625514e`. Applied reviewed blob:
  `b6ee6589d93b4cd95283ce6d45c22f7010aba56a`.**
- **LIVE PROTECTED PROOF captured + merged** (`M0-T036-PROTECTED-live-proof.md` + raw doctor
  JSON): unelevated doctor — `controller_config_acl.protected: true`, file + parent both
  PROTECTED, config readable, SHA `29eb765e..da1cb` unchanged, model_selection unelevated-
  writable, nothing activated. Closes the last activation-checklist item.

**Directive registry:** D-010 sources 015–022 captured (R144–R213), validator green throughout;
verification rows recorded for M0-T048/T049/T050/T051 (all-PASS at their frozen identities).

## THE ONE REMAINING ITEM (R131/R212)

⛔ NO activation without the owner typing the decision line (presented 2026-08-08, with the
N-4/N-5/MINOR-2 residuals disclosed):
`ACTIVATE SUPERVISED-AUTO — I have read and accept the N-4/N-5/MINOR-2 residuals; proceed per R595/R131.`
(or `HOLD activation`). On the typed activation line: record it durably (directive capture), then
dispatch **M2-T015 + M2-T016** as the two supervised-auto product proof tasks — HELD until then
(R133/R143/R153/R167/R196/R213).

## OTHER OPEN ITEMS

- **M0-T047 (nanoid GHSA-2v37-7h3g-55p8):** age-eligible **2026-08-10T10:39:22Z**; contracted
  packet (CI-bot lock regeneration, NO local npm); until then `web-dependency-security` stays red
  repo-wide (NON-required; Tier A merges unaffected — precedent PRs #178–#185).
- **Registered follow-up candidates (reviewer-recommended, owner-optional, none contracted):**
  rollback-path dry-run wording (same class as R190, one-line branch); parent-first hardening
  order (removes the theoretical transient in the general case); MINOR-2 cycle-disambiguation;
  `-rs` on the CI pytest invocation; Phase 3 external audit-anchor (Option A) for N-4.
- **Housekeeping (classifier-denied, owner may run):** `! git push origin --delete task/M0-T048-c2-close`
  and `! git branch -D task/M0-T048-c2-close` (content fully merged). The orch worktree sits on
  the merged `task/M0-T051-explicit-ace-strip`; re-point at next claim.
- Rework queue (M0-T021/M0-T034) and the M3 chain (under its blockers) remain available.

## Carried rules (unchanged)

- Task branches from origin/main in the orch worktree; producers spawned UNNAMED; classifier
  denial ⇒ exact-path staging first, else STOP and surface the `!` line;
  `project-control/directives/**` explicit LF; commits stage exact paths; ADR-006 Tier A merges
  after green required checks; owner dry-run-first rule for any elevated script (R195).
- **Reviewer models:** gate reviewers `claude-opus-4-8` + `xhigh` (standing fallback; the 5
  flipped agent files remain uncommitted in the PRIMARY checkout — revert to `claude-fable-5`
  pins when the owner says "Fable is back"). Orchestrator `claude-fable-5`.
- Standing holds unchanged: deployment/G6/Graphify/expansion; SHADOW-ONLY until the owner's typed
  activation decision.

---

_History: superseded session blocks (sessions 1–7 pre-seam = CP-0037..CP-0045) recoverable via
`git log -p docs/SESSION_HANDOFF.md`; the ledger remains authoritative._
