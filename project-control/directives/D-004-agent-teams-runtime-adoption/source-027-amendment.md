# D-004 amendment 27 — owner message (verbatim capture)

- Captured: 2026-08-04T21:45:00+00:00 (approx; session-local)
- Channel: owner chat message (this session), delivered as three consecutive parts in one turn
- Base SHA at capture: cb9a9995da213f33d70e467773d595b3dfea0b57 (origin/main); task branch 1d5e50f
- Amends: source-026-amendment.md (evening authorization; orchestrator-role quota substitution)
- Cross-registry note: the same owner message is captured verbatim as D-007 amendment 12
  (D-007-codex-claude-supervisor-bridge/source-013-amendment.md). Supervisor-unit, sequencing, and
  hold requirement IDs live there (D-007-R603..R609); model-governance IDs live here
  (D-004-R751..R760).

## INTERNAL SUPERSESSION NOTICE (orchestrator note, not owner text)

The three parts arrived in one turn and part B REVERSES part A item (2) on the central design
point. All three are preserved verbatim below in arrival order. The EFFECTIVE spec is
**part B as extended by part C** (detect-and-SWITCH, fully automatic, along a fixed
config-defined preference chain). Part A item (2)'s "detect-and-hold / notify / proceed only on
my reply" design is **SUPERSEDED and must NOT be built**. Part A items (1) and (3) stand except
where (3) says "re-scoped to detect-and-hold actuation" — per part B that re-scope target becomes
detect-and-switch actuation. Part A's Fable-5 re-review hold and the "keep claude-opus-4-8 exact"
instruction are restated in parts B/C and stand.

## The owner message — PART A (first, item (2) SUPERSEDED by part B)

Three-part instruction. (1) Model availability: Opus 4.8 disappeared from the picker because Claude Code updated past the Opus 5 release — it is a build/label change, not our config and not related to the Fable limit. Opus 4.8 stays selectable via the explicit string. In .claude/settings.json and every Opus-pinned agent file, keep the exact id claude-opus-4-8; do not let anything resolve to opus-5. Confirm on disk that all 19 producer pins and the settings default still read claude-opus-4-8 verbatim, and report the claude --version and whether /model claude-opus-4-8 resolves. (2) Correct the V1.2.2 scope: the quota-exhaustion fallback is NOT the same mechanism as the 400k context-rotation, and it must NOT silently auto-switch models. Build it as detect-and-hold: on a Fable-5 quota-exhaustion launch failure for an orchestrator-role session, the supervisor dispatches nothing new, lets in-flight units finish bounded, refreshes SESSION_HANDOFF, and NOTIFIES me (phone bridge) with an explicit 'Fable exhausted — reply to continue on claude-opus-4-8' prompt; it proceeds only on my reply. No silent substitution. Fully-automatic switch is deferred to a later unit, authorized by me only after detect-and-hold has a clean supervised record. This supersedes any part of the earlier substitution spec that implied silent auto-switch. (3) The record-only substitution defect G4 caught stays in rework, but its fix is re-scoped to detect-and-hold actuation, not silent-switch actuation. Capture this message verbatim. Do not dispatch the Fable-5 re-review of any of this until I say my window is reset — it resets Thursday.

## The owner message — PART B (supersedes part A item (2))

Correcting V1.2.2 scope — build the Fable-exhaustion auto-switch as fully automatic, no owner tap: when an orchestrator-role session hits the Fable-5 account-quota-exhausted pause, the supervisor immediately relaunches the SAME session's continuation on claude-opus-4-8 and proceeds — detect-and-switch, not detect-and-hold, because Opus 4.8 is the pre-authorized destination and there is nothing for me to decide at that moment. This is a DISTINCT trigger from the 400k context-rotation (already built) and from a mid-task security downgrade — do not conflate them. The one hard requirement: fix the record-only defect G4 caught — the relaunch must ACTUALLY launch the worker/continuation on claude-opus-4-8 (effective launched model, not just the audit record), and the acceptance test must prove a real process came up on 4.8 after a simulated Fable-exhaustion, not merely that a switch event was written. Reviewer pins stay Fable-5 and still wait for reset; only the orchestrator-role auto-switches. Keep the exact id claude-opus-4-8 everywhere (the picker now hides it behind Opus 5 after the Claude Code update — build/label change, not our config). Capture verbatim. Hold the Fable-5 re-review until I say my window reset (Thursday).

## The owner message — PART C (extends part B)

Add to the Fable-exhaustion auto-switch spec: the orchestrator does NOT choose a model by judgment. It walks a fixed, config-defined preference chain, first-available-wins, tried by actual launch: claude-fable-5 → claude-opus-4-8 → claude-opus-4-7 → STOP+notify-me. Opus 5 (or any id not in the chain) is never selectable, regardless of what the picker shows. Availability is determined by PROBING the exact model id — attempt the launch and confirm a real process comes up on that id — never by reading the model picker/menu (tonight proved the menu can hide a model that is still usable by string). If no chain entry actually launches, the supervisor stops, refreshes SESSION_HANDOFF, and notifies me — it NEVER silently continues on an unlisted/substitute model. This chain governs orchestrator-role sessions only; reviewer Fable-5 pins do not fall back and instead wait for reset. The chain and its order live in the immutable supervisor config, owner-editable only. Capture verbatim.
