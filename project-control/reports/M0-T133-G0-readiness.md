# M0-T133 — G0 definition-of-ready (administrative)

**Task:** M0-T133 — D-024 Amendment 37 AD-093 defect: controller-authoritative git-state checkpoint
enrichment (journey-5 invalid_checkpoint). **Reviewer:** orchestrator (admin G0). **Result:** PASS.
**Base identity:** HEAD `f10353ab`, branch `control/D-024-fable-codex-loop`.

## Bootstrap Gate 0 / readiness
- Primary cwd is the ctl24 worktree root; `/mcp` empty (unchanged this session). ✓
- **AD-093 qualifying evidence (supervisor-freeze §2):** the journey-5 reproduced `invalid_checkpoint`
  defect (`M0-T107-commissioning-journey-5.md`) — a failed acceptance scenario / inability to complete
  the authorized commissioning cycle. Cited in packet + will be in the commit. ✓
- **Requirement IDs:** D-024 Amendment 37 rows `D-024-R460..R471` (+ standing R394); `D-024:ALL` refs. ✓
- **Non-overlapping scope:** allowed = new `checkpoint_envelope.py`, `claude_runner.py`, `loop.py`, new
  `test_agent_supervisor_checkpoint_envelope.py` (+ optional runner-checkpoint test), own reports;
  forbidden = `models.py` (the ClaudeCheckpoint schema is NOT changed — the four fields stay required and
  the controller fills them), settings/apps/packages/services, control CLIs. ✓
- **Acceptance scenarios:** AS-1..AS-8 = the owner's eight named removal-sensitive scenarios. ✓
- **Gates + independent reviewers:** G0 (admin), G2 self-check, independent G3 code-reviewer, G4
  qa-engineer, DCV directive-compliance-verifier — all distinct from producer. Reviewers run on the
  approved fallback model (opus) per R460. ✓
- **Modularity:** the enrichment logic lands in a NEW focused module (`checkpoint_envelope.py`), keeping
  `claude_runner.py`/`loop.py` changes minimal (split extract_checkpoint; thread one envelope). ✓
- **Owner authorization + fail-closed guard:** R460 authorizes; R471 requires stop-and-report if the fix
  cannot be made without weakening fail-closed checkpoint integrity. Preservation R469 (journal
  PAUSED_RECOVERY / audit 104 / PR #241 / model pin / manifest) held throughout. ✓
