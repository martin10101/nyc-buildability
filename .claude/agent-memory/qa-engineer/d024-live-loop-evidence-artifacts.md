---
name: d024-live-loop-evidence-artifacts
description: Where the preserved D-024 live-loop audit chain + worker transcript live, and how to read them read-only
metadata:
  type: reference
---

The D-024 Amendment-20/22 live-loop evidence (byte-for-byte preserved, R374 — never
open the sqlite journal, never run any `python -m tools.agent_supervisor` subcommand
against it) is two PLAIN files, readable directly:

- Audit chain (53 records, hash-chained): `C:/Users/MLFLL/AppData/Local/NYCBuildabilitySupervisor/33dfa57d54dbc5d11d55dd8bab9248280e6568ef0e50002ba04a38543967a7ed/audit.jsonl`
- Worker transcript (97 events): `C:/Users/MLFLL/.claude/projects/C--Users-MLFLL-Downloads-nyc-zoning-wt-m0t107/0835bb80-0f2e-451f-882d-0b37df6d77d5.jsonl`

Non-obvious facts confirmed at the M0-T125 G4 gate (2026-08-30):
- `context_tokens` in `claude_unit_completed` audit rows is CUMULATIVE peak-per-event
  usage, NOT live context: seq 50 = 694,251 while the transcript's true final live
  usage is ~72.5k (cache_read 67,935 + cache_creation 3,962 + output 647). This is
  register defect D5 and it is the crux of context-ceiling mis-consumption.
- `native_tools_guidance_appended: false` (seq 50) yet the dispatched first prompt (2,176
  chars) DOES contain the `NATIVE-TOOL PREFERENCE (D-024-R294)` sentinel — the flag is
  degenerate (computed after the checkpoint-contract fold already embeds it). Register D4.
- `claude_unit_completed` is journaled BEFORE the `claude_process_started` transition for
  the same unit (seq 8/9, 21/22, 40/41, 50/51) — durable journal rests at START_CLAUDE
  for the whole unit. Register D6.
- The 12/12 counted stop: 36 assistant events, all stop_reason tool_use, exactly 12
  distinct message ids, tools Glob/Grep/Read only, no checkpoint JSON, ~2m24s.

**How to apply:** parse these with a read-only inline python (json.loads per line) to
independently verify any audit-seq or transcript claim; never mutate. See
[[golden-run-multi-hour-runtime]].
