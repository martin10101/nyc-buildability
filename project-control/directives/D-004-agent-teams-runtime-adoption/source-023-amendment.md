# D-004 amendment 22 — owner message (verbatim capture)

- Captured: 2026-08-04T16:30:00+00:00 (approx; session-local)
- Channel: owner chat message (this session)
- Base SHA at capture: cb9a9995da213f33d70e467773d595b3dfea0b57 (origin/main); task branch ae38b1b
- Scope: model-governance decision. Supersedes the effort-key prohibition R159 ONLY for the
  exact keys named here; R159 otherwise stands, including everything Codex-side (and the
  supervisor's own D-007 §3.1 config effort prohibition is untouched).

## The owner message

Model-governance decision (scoped amendment: this supersedes the effort-key prohibition R159 ONLY for the exact keys named here; R159 otherwise stands, including everything Codex-side). (1) Orchestrator sessions run Claude Fable 5: set the model key in project settings to the full Fable 5 model ID; durable effort stays high; I raise effort per-session myself with /effort — no standing xhigh or max in any settings file. (2) Subagents: set model: claude-opus-4-8 and effort: high in the frontmatter of every agent EXCEPT the gate reviewers (code-reviewer, security-reviewer, qa-engineer, control-plane-verifier, directive-compliance-verifier), which stay on Fable 5. Do not set the subagent model environment variable, so per-file exceptions hold. Show me the full frontmatter diff before committing; it lands as one commit citing this capture. (3) V1.2, authorized as the next unit after the doctor --live probe returns: model-identity discipline in the supervisor — every supervised session launches with an explicit --model from model_selection; the model field is verified on every stream-json event; on any downgrade the supervisor dispatches nothing new, lets the in-flight unit finish bounded, refreshes SESSION_HANDOFF, rotates via the existing rotation path, and relaunches pinned; if the pinned model is unavailable it pauses and notifies me — an orchestrator-role session never continues on a substitute model silently. (4) Process rule, binding: when an owner-typed gated command fails closed and is later made ready, the re-run comes back to me as a line to type; a session-executed act is never recorded as owner-typed, and the M0-T035 commit message's label is noted as inaccurate on this point. Capture this message verbatim.
