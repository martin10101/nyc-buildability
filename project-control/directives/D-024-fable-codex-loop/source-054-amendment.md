# D-024 source-054 — amendment 54 (owner trigger of R781; activation authority; 2026-09-05)

Cross-reference amendment. The full verbatim owner message of 2026-09-05 is captured as
**D-032 source-001.md** (digest a6e70f9926305f996d937849c8fe93a2cdce28ad0b6fd0ffe9701343d11652d0);
this file records its effect on D-024. The operative verbatim sentence:

> i need you to have 1 role get codex up and running as full time loop no more monkey busnnes also
> coedex has a new model calld astra or something like that (it also has difrint setting like high
> extra high etc i want to set it at high and use that for main codex agent for the loop but i ned
> you to ucheck if the cli has already that modle or codex might need to be update in th ecli if
> yes update it but the goel is to get this done asap u dont have to run 5 millon checks you just
> have to get this done and power up the loop for the run

Effects on D-024 (recorded, requirement rows live in D-032 R001–R005 on the D-032-BOOTSTRAP
sentinel; no new D-024 rows, no rebinding of gated tasks):

1. **R781 trigger FIRED.** The anticipated owner instruction "switch the main reviewer to
   gpt-6-astra" has been given. Execution uses the R776 config-driven swap
   (`model_selection.toml review_model = "gpt-6-astra"`), subject to account availability.
2. **Effort = `high`** for the main reviewer (owner chose high over xhigh/max). The runtime value
   `review_reasoning_effort = "high"` narrows the M0-T146 xhigh-default at the config layer only;
   code default (xhigh-when-unset) and the effort ladder are unchanged.
3. **Codex CLI update authorized** if needed for the new model (installed 0.146.0 predates
   gpt-6-astra).
4. **Activation authority (narrow supersession, this activation only):** the owner-typed-only
   execution posture of R754 / R772 / R780 and terminal BLOCKER-1 (first live limited-auto run,
   controller reinstall, live confirm) is superseded FOR THIS ACTIVATION: the orchestrator is
   directed to execute the R247 recert transaction, accept M0-T146 on its existing PASS gates at
   unchanged content identity, re-pin `source_binding.json`, run the controller update script
   (backup + install), apply the runtime model/effort config, live-confirm the model, and launch
   the first live limited-auto loop. Redundant re-review waves are owner-waived ("u dont have to
   run 5 millon checks"). Permanent CLAUDE.md gates are NOT waived; R595/Option-A and R603–R605
   (GitHub lifecycle) remain owner-only and undecided; PR #241 untouched.
