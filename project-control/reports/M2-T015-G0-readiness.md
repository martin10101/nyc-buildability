# M2-T015 — G0 readiness (administrative)

Recorded by the orchestrator 2026-08-09, at main `1b3af35` (M2-T015 integrated via PR #213).
- **Scope:** secure survey/official-document ingestion, extraction, deterministic-verification pipeline
  (owner survey workstream Packet B); D-010 in-regime (directive_refs D-010 ALL; 97 applicable).
- **Acceptance scenarios:** SB-S1..SB-S9 (task file). Objective + named outputs (incl. SURVEY_FIXTURE_MATRIX.md
  + committed synthetic fixture pack with MANIFEST digests) present.
- **Dependencies:** M2-T014 (accepted), M0-T054 (accepted — Fable→Opus turnover unblocked 3k).
- **Gates:** G0 (this), G1 data-contract, G2 self-check, G3 code walkthrough, G4 integration/regression,
  G5 security; DCV directive-compliance (97 reqs). Reviewers ≠ producer (read-only, independent).
- **Readiness:** worktree isolated (wt-m2t015); deterministic tests + synthetic fixture pack; CI green on 3.12.
  READY for the evidence gates.
