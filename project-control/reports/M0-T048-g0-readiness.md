# M0-T048 G0 readiness (administrative)

**Task:** M0-T048 - Close G5-C2: cryptographically bind forwarded prompt content to the
operator-named approval digest (owner am.14)
**Recorded by:** orchestrator. **Date:** 2026-08-08 (UTC).

- Packet complete: objective (exactly ONE bounded security fix for the C2 two-field-forgery
  residual per am.14), allowed paths (tools/agent_supervisor/, tools/test_agent_supervisor_*.py,
  producer report, packet), acceptance scenarios AS-1..AS-6 (AS-1 is the owner's verbatim 7-step
  adversarial test, required non-vacuous - must fail on pre-fix code), directive_refs (D-010
  R134-R143, the full am.14 set), gates G0/G2/G3/G4/G5 + DCV at accept, five reviewers rostered
  (producer != reviewer, R141).
- Directive capture: am.14 recorded verbatim as source-014-amendment.md at frozen base
  `9c2ec25` (origin/main); R134-R143 appended append-only; registry validates clean
  (`validate_directive_compliance.py` OK, commit `01b20d6`).
- Dependencies: M0-T046 ACCEPTED (the fix builds directly on its park-time anchor + sealed
  refusal machinery) - dependency-valid. Base for the task branch: origin/main `9c2ec25`
  (contains the merged M0-T046 code).
- AD-093 qualifying evidence: the C2 finding is a pinned, enumerated gate finding
  (M0-T046-g5-security.md M-1/C2) whose closure the owner has now DIRECTED (R134); this is
  directive-cited defect work, not speculative feature work.
- Design boundary (R137/R140): preserve the S13.5 clock invariant; smallest correct design (owner
  names two candidate constructions); no redesign/features/infrastructure/cleanup. The producer
  must inventory build_forwarded_prompt's inputs for determinism (packet risk 1) and must not
  weaken any M0-T046 check (risk 3).
- Sequencing: after acceptance + merge, the ACTIVATION SEQUENCE RESUMES (R142: elevated ACL apply
  + live PROTECTED capture + owner-typed decision line); M2-T015/T016 remain held (R143).
  SHADOW-ONLY intact; no authority change in scope (R139d).
- Blockers: none reference M0-T048. The repo-wide red web-dependency-security context (nanoid,
  M0-T047, age-eligible 2026-08-10T10:39:22Z) is a NON-REQUIRED CI context and does not gate this
  task's merge (required 8-context ruleset unaffected); noted for R141 required-checks review.
- Producer: backend-engineer (delegated, spawned UNNAMED per the guard rule), orch worktree,
  fresh branch from origin/main.

**G0 result: PASS (ready to claim).**
