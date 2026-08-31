# D-024 Amendment 23 — producer rotate-at-seam, never run to exhaustion (owner instruction 2026-08-31)

Captured: 2026-08-31 UTC by the orchestrator (Fable 5), verbatim from the owner's typed
message, BEFORE acting on it (D-001). Base identity at capture: branch
`control/D-024-fable-codex-loop`, HEAD `f69b088` (local == origin; tree clean; M0-T126
in_progress 55% — the producer's return 1 disclosed a 12/17 correction set and an R385
continuation directive was already in flight in the producer's SAME agent context).
Amends: `source-001.md` (owner directive v4). Context: the orchestrator reported that the
resumed M0-T126 producer had ~429k cumulative tokens and proposed rotating to a fresh
producer at the producer's next natural seam instead of resuming it again; the owner
confirmed that plan and added the exhaustion prohibition. Requirement IDs assigned:
D-024-R395, D-024-R396.

Reconciliation: at the M0-T126 producer's next natural seam (its next return-channel
report, or a stall requiring intervention), the orchestrator captures the producer's
uncommitted worktree work as a durable patch immediately and does NOT resume that agent
context again; any remaining production continues via a FRESH unnamed roster-typed
producer in a new isolated worktree (control-tip reset + captured patch applied),
oriented from durable artifacts — the design record, producer report, and register —
not from the prior agent's transcript (R395). No producer sub-agent in this window may
be run toward context exhaustion: assignments stay bounded, and a producer facing
context risk mid-assignment must checkpoint durably (reports updated, remaining items
listed) and return early for rotation rather than continue (R396).

Forward trace: s1 clause 1 ("ok rotate at the seam then") → R395; s1 clause 2 ("dont
let it run to exhaustion") → R396.

Anchors: #rotate-at-seam (clause 1), #no-exhaustion (clause 2).

---VERBATIM-BEGIN---
ok rotate at the seam then, dont let it run to exhaustion
---VERBATIM-END---
