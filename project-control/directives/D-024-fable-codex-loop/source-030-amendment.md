# D-024 Amendment 30 — CC-update admission lane DEFERRED; focus stays on the codex loop (owner instruction 2026-09-01)

Captured: 2026-09-01 UTC by the orchestrator (Fable 5), verbatim from the owner's typed
message, BEFORE acting on it (D-001). Base identity at capture: branch
`control/D-024-fable-codex-loop`, HEAD `57f1b70d` (local == origin; campaign seq 62).
Delivery context: the owner returned online mid-session ("go on ia am b ack online",
non-substantive continuation) while M0-T131's independent G3/G4 reviews were in flight;
the orchestrator had just presented the open 2.1.252 CLI-drift admission decision
(R286/R287 admission event: installed claude.exe auto-updated 2.1.251 -> 2.1.252;
Option A = bounded recapture->recertify->repin task, Option B = defer, supervisor
stays fail-closed unstartable). The owner's reply defers the Claude Code ("cc") update
lane and directs focus to the codex loop. Amends: `source-001.md` (owner directive
v4). Requirement IDs assigned: D-024-R429..D-024-R430.

Reconciliation: "dont worry on cc update" = the 2.1.252 admission lane is DEFERRED by
owner decision — no admission task now, no effort on the CC-update lane; the
fail-closed refusal at `cli_capability_manifest` is accepted as the standing state.
This is a deferral, NOT a waiver: R286/R287 stand in full (silent drift acceptance
remains prohibited; the recapture -> recertify -> repin discipline applies whenever the
owner later reopens the lane; the three live-fixture drift tests stay honestly red
locally and skip on CI). "focuse on codex loop" = continue the codex-loop lane
exactly as sequenced: M0-T131 through gates/DCV/accept under the standard process;
the single R247 recertification (R428) runs at the post-accept frozen identity binding
the M0-T131 supervisor tree move with the provider pin UNCHANGED at the certified
2.1.251 and the deferred 2.1.252 drift disclosed as an open admission event; the
restart sequence stays presented owner-typed only (R409/R414/R419), with the honest
caveat that a live start at installed 2.1.252 will refuse fail-closed at
`cli_capability_manifest` until the admission lane is executed.

Forward trace: "dont worry on cc update" -> deferral of the admission lane, no waiver
of R286/R287 -> R429; "focuse on codex loop" -> codex-loop sequencing (gates/accept,
recert at pin-unchanged identity with drift disclosed, owner-typed restart
presentation with the fail-closed caveat) -> R430.

Anchors: #cc-update-deferral (R429), #codex-loop-focus (R430).

---VERBATIM-BEGIN---
dont worry on cc update focuse on codex loop
---VERBATIM-END---
