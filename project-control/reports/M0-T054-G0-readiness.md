# M0-T054 — G0 readiness (administrative)

Recorded by the orchestrator 2026-08-09, at main `89c4e30` (turnover code integrated via PR #211).

- **Qualifying evidence (reliability defect):** D-010 source-026 fallback test observed
  **R289 = DID-NOT-SWITCH** — when Fable 5 hit its weekly limit the built-in `fallbackModel` did NOT
  auto-move the main orchestrator to `claude-opus-4-8`; the session hard-stopped and required a manual
  owner `/model`. Root cause (R294 finding 3): no process outside the exhausted Claude session existed to
  detect the hard stop and launch an Opus successor. Owner order: D-010 source-027/028 (R300–R302,
  R304–R319).
- **Scope (narrow, defect-lane):** a small independently-live turnover mechanism (detection + exactly-once
  actuation + real adapters + one gated worker-loop seam + live-signal plumbing). No supervisor redesign;
  protected immutable config, `default_mode=shadow`, supervised runtime, and LIMITED-AUTO-off untouched.
- **Gates:** G0 (this), G2 self-check, G3 code-reviewer, G5 security-reviewer; independent DCV
  (directive-compliance-verifier) for the 16 applicable D-010 requirements.
- **Reviewers ≠ producer:** producer = orchestrator/backend-engineer; reviewers = code-reviewer,
  security-reviewer, directive-compliance-verifier (read-only, independent).
- **Readiness:** contracted with full source-028 spec; worktree isolated; deterministic tests + one bounded
  live proof required and delivered. READY for the evidence gates.
