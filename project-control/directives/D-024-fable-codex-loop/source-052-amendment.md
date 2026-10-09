# D-024 Amendment 52 — Codex reviewer at MAX reasoning effort (owner directive, 2026-09-04)

- **Directive:** D-024 (fable-codex-loop campaign)
- **Kind:** amendment (append-only; amends source-001.md; follows source-051-amendment.md)
- **Issued by:** owner (interactive session, 2026-09-04, answering the orchestrator's offer to
  draft a bounded task setting the Codex reviewer's reasoning effort)
- **Context:** the orchestrator reported (from the installed config + code) that the Codex
  reviewer `gpt-5.6-sol` currently runs with NO reasoning-effort tier set — `build_argv`
  (`codex_reviewer.py:93`) passes no effort; `--ignore-user-config` strips any personal effort;
  and `--effort`/`--effort=high`/`--reasoning-effort` are hard-denied argv flags (`cli.py:429`).
  The orchestrator offered to draft a bounded task to set it to max, or leave the default.
- **Base identity at capture:** ctl24 `candidate/D-024-mrl-option-b` HEAD `b7f76755` (local only),
  tree clean; origin/main `d8b3899f`; installed controller frozen `3f4cee86`.

## Verbatim owner directive

> yes I want it at max

(In direct response to: "force `high`/`max` on the reviewer … Want me to draft that as a
bounded task, or is the default effort fine?")

## Orchestrator findings recorded at capture (D-001 rule 9; verified read-only, official sources)

1. **No literal "max" reasoning-effort value exists in codex-cli 0.146.0.** The authoritative
   codex config reference lists the `model_reasoning_effort` enum as exactly
   **minimal, low, medium, high, xhigh** (default medium); `xhigh` is the documented maximum and
   is model-dependent ("expect to test"). One secondary web result claimed gpt-5.6-sol advertises
   `max`/`ultra` tiers, but the authoritative config reference does not list them and
   `--strict-config` fails closed on an unrecognized value — so the conflicting claim is NOT
   relied on. Sources: codexinsider.com/config/model-reasoning-effort (authoritative), a web
   search summary (conflicting, not relied on).
2. **Interpretation:** "max" = the maximum available reasoning-effort tier = **`xhigh`**. This is
   set config-driven (a supervisor-owned field) so it is a one-line change if the owner later
   names a different tier or if a literal higher tier is confirmed to exist for this model.
3. **Mechanism:** there is no dedicated `codex exec` flag; effort is set via the config-override
   form `-c model_reasoning_effort=xhigh` (verified from `codex exec --help`). This is the
   SUPERVISOR-set path and is distinct from the hard-denied user-injected `--effort` /
   `--reasoning-effort` argv flags, which stay denied.
4. **Model-dependency (unverifiable offline):** whether `gpt-5.6-sol` actually honors `xhigh` can
   only be confirmed on a live review call (owner-gated). `codex doctor` does not validate the
   enum locally. The implementation therefore sets `xhigh` with a safe fallback to `high` if a
   live review rejects `xhigh` (parsed provider error), and the live confirmation is a row that
   completes only on the next owner-run live review.
5. **Consequences the owner accepted:** max effort increases Codex review latency and cost.
   The change modifies the frozen supervisor tree (`tools/agent_supervisor/**`, defect-only under
   `.claude/rules/supervisor-freeze.md`) as an OWNER-AUTHORIZED feature exception, and therefore
   TRIGGERS R247 recertification at a new frozen identity; the installed controller must be
   reinstalled for the live effect. The recert + reinstall + live `xhigh` confirmation land behind
   the same owner-gated live-run boundary as the persistent-loop activation.
