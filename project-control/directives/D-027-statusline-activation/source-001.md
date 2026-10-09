# D-027 source-001 — owner authorization (verbatim)

- **Received:** 2026-08-26 (UTC), owner mid-turn terminal message in session
  `session_01HfptKuEs3RDxaxsSHJjc7t` (branch `control/D-024-fable-codex-loop`, HEAD `8bb829c`).
- **Channel:** owner terminal prompt (mid-turn user message).
- **Capture rule:** text below the marker is the owner's message, verbatim and complete.
  IMMUTABLE once D-027 is active (append-only amendments).

---VERBATIM-BEGIN---
Owner authorization:

Activate owner step (1) from the accepted M0-T099 report. Wire the accepted project statusLine handler exactly according to report §4.

Requirements:
- Keep M0-T099’s frozen accepted identity unchanged.
- If activation requires a separate project-control record or bounded task, create and validate that record instead of modifying the accepted task.
- Activate telemetry in passive shadow/read-only mode only. It may display information and write the sanitized telemetry sidecar, but it must not stop agents, rotate sessions, change models, or take any other supervisory action yet.
- Verify that the project statusLine takes precedence only inside this repository and does not compete with or damage my global personal statusLine fallback.
- Prove with a real live check that both outputs work from the same feed:
  1. the human-readable terminal row;
  2. the sanitized machine-readable sidecar for future Codex monitoring.
- Confirm that no personal paths, usernames, session identifiers, credentials, or other sensitive information are written unmasked.
- Record, test, commit, and push the activation according to existing project-control requirements.
- Do not purge the three external leftover agent worktrees during this step.
- Do not activate the continuous Codex loop.

After the wiring is safely verified and durably recorded, continue from the campaign’s NEXT action and claim M0-T090: bounded subagent contracts plus structural workload sizing, carrying forward all named advisories. Do not repeat completed work or broaden scope. Stop for any additional owner-only decision.
---VERBATIM-END---
