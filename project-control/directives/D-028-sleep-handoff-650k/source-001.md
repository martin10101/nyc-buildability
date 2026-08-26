# D-028 source-001 — owner instruction (verbatim)

- **Received:** 2026-08-26 (UTC), owner mid-turn terminal message in session
  `session_01HfptKuEs3RDxaxsSHJjc7t` (branch `control/D-024-fable-codex-loop`), during the
  M0-T090 production run.
- **Channel:** owner terminal prompt (mid-turn user message).
- **Capture rule:** text below the marker is the owner's message, verbatim and complete.
  IMMUTABLE once D-028 is active (append-only amendments).

---VERBATIM-BEGIN---
i am going to sleep at around 650k tokens on main agent (U)aprox hold for my seasen handoff token is aproxxmitly plus 50k or - is ok
---VERBATIM-END---

## Orchestrator interpretation note (not owner text)

Read as: the owner is going to sleep; the session continues its authorized campaign work
unattended; when the MAIN agent's context usage reaches approximately **650,000 tokens**
(tolerance ±50,000 — "plus 50k or -"), the orchestrator must HOLD at a clean seam and produce
the session handoff (`docs/SESSION_HANDOFF.md` conventions), reserving headroom for the
handoff itself. Measurement basis: the live project statusLine feed's main-session context
occupancy (`.claude/telemetry/statusline_sidecar.json`, `context_total_input_tokens` /
`context_used_pct` of the 1M window). Tension noted: D-010 R113–R114 records a ~400k
rotate-at-seam ceiling (owner 2026-08-07); this later owner instruction (2026-08-26) governs
THIS session's seam point at ~650k ±50k; the permanent D-010 rule is not amended by this
capture. Ambiguity resolution "650k ± 50k": treat 600k as the alert level and do not run past
~700k without the handoff written.
