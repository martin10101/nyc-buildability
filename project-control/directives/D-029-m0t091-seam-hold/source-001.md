# D-029 source-001 — owner instruction (verbatim)

- **Received:** 2026-08-26 (UTC), owner mid-turn terminal message in session
  `session_01HfptKuEs3RDxaxsSHJjc7t` (branch `control/D-024-fable-codex-loop`), during the
  M0-T091 production run (mid composite-baseline chunk B).
- **Channel:** owner terminal prompt (mid-turn user message).
- **Capture rule:** text below the marker is the owner's message, verbatim and complete.
  IMMUTABLE once D-029 is active (append-only amendments).

---VERBATIM-BEGIN---
OWNER HOLD: Finish, review, accept, checkpoint, commit, and push M0-T091 exactly as currently scoped. Do not claim or begin M0-T092 or any later campaign task.

Allow all healthy, productive agents and validation shells to finish naturally. At the resulting clean seam, verify the working tree is clean, origin contains every material commit, no agent or shell remains active, and the ledger agrees with Git.

Then report exactly:

M0-T091 SEAM READY

Include its frozen accepted commit, checkpoint, test totals, remaining campaign NEXT action, and whether any background process remains. Wait for my instruction after reporting. Do not start new implementation work.
---VERBATIM-END---

## Orchestrator interpretation note (not owner text)

Read as: complete the in-flight M0-T091 through its normal lifecycle — producer report, G2
self-check, submit, the independent G3/G4/G5+DCV review wave at the frozen identity, accept,
checkpoint, commit, push — exactly as already scoped (the review wave IS part of "finish,
review, accept": dispatching the packet's required read-only reviewers is required, not new
work). The post-acceptance campaign-record advance (the mechanical `advance()` that repoints
NEXT) is part of the standard accept-and-checkpoint flow and does not claim or begin M0-T092;
the HOLD forbids claiming/beginning M0-T092 or any later campaign task and starting any new
implementation work after the seam. "Agents and validation shells finish naturally" — no
healthy productive agent or running validation shell is killed for the hold. Seam
verification and the exact report text/contents are as written. The hold ends only on the
owner's next instruction. D-028's unattended-continuation authorization is narrowed by this
later instruction: after the M0-T091 seam report, WAIT (do not continue the campaign chain).
