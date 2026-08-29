# D-024 Amendment 10 — Fable-availability correction: stale Opus-4.8 worker pin removal (owner instruction 2026-08-29)

Captured: 2026-08-29 UTC by the orchestrator (Fable 5), verbatim from the owner's interactive
message (channel: Claude Code interactive session, typed by the owner in response to the
M0-T113 activation-preflight STOP report, campaign seq 28). Base identity at capture: branch
`control/D-024-fable-codex-loop`, HEAD `ae2e18a30212afed21848c64757b77e0d21cf479` (local ==
origin; clean tree). Amends: `source-001.md` (owner directive v4). Requirement IDs assigned:
D-024-R261..D-024-R267.

Reconciliation (recorded before any change):

- **This corrects preflight MISMATCH 1** (`M0-T113-activation-preflight.md` §2): the owner
  states as fact that Fable 5 never went away, is currently available to the account with
  substantial usage, and powers the active main session (independently consistent: this
  session runs on `claude-fable-5`). The 2026-08-09 exhaustion-era worker pin
  (D-010-R296/R308, `model_selection.toml [claude] model = "claude-opus-4-8"`) is declared
  STALE. This owner statement is the R290-anticipated switch-back act in substance
  ("Fable is back"), given in corrected words.
- **Authorized change is NARROW (R265):** only the required model-selection setting — the
  recorded revert path in the file's own comment: `[claude] model` → `""` (account/CLI
  default, which is Fable 5). No other file changes; `model_selection.toml` is mutable by
  design and OUTSIDE the controller manifest, so this edit does not move the certified
  code identity or the manifest binding.
- **Probe-before-change sequencing (R263):** the read-only live capability probe is the
  certified bounded control-response probe (`doctor --live` — runbook §8: "the ONLY
  intentional bounded live control-response probe"), which launches the canonical Claude
  executable through the shipped adapter with NO explicit model flag, i.e. the account
  default (Fable 5): one turn, one denied tool call, throwaway directory, no repo or
  config change.
- **Launch remains held (R267):** after the model-selection update and the owner's
  administrator edit of the protected approved-model configuration, the manifest must be
  re-recorded and the COMPLETE activation preflight must pass again before any start —
  this re-affirms Amendment 9's R254/R259 and does not itself launch anything.
- Rows bind to the claimed activation-act task **M0-T113** (this correction adjusts that
  unit's preconditions; it does not broaden its contract).

Forward trace: paragraph 1 ("Correction: … Treat the August 9 exhaustion-era Opus 4.8
worker pin as stale.") → R261; paragraph 2 sentence 1 ("I explicitly authorize removing…")
→ R262, sentence 2 ("Before changing anything, perform a read-only live capability
probe…") → R263, sentence 3 ("Record the probe evidence and this owner correction
durably.") → R264; paragraph 3 sentence 1 ("If the probe passes, update only the required
model-selection setting.") → R265, sentence 2 ("Then give me exact administrator-level
instructions…") → R266, sentence 3 ("Do not launch until the manifest is re-recorded and
the complete activation preflight passes again.") → R267.

---VERBATIM-BEGIN---
Correction: Fable 5 never went away and is currently available to my account. I still have substantial Fable 5 usage available, and my active main session is using Fable 5. Treat the August 9 exhaustion-era Opus 4.8 worker pin as stale.

I explicitly authorize removing that stale worker pin and restoring Fable 5 as the primary autonomous worker. Before changing anything, perform a read-only live capability probe proving that the controller can launch Fable 5 successfully. Record the probe evidence and this owner correction durably.

If the probe passes, update only the required model-selection setting. Then give me exact administrator-level instructions for adding claude-fable-5 and claude-opus-4-8 to the protected approved-model configuration. Do not launch until the manifest is re-recorded and the complete activation preflight passes again.
---VERBATIM-END---
