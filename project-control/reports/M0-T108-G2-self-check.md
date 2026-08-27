# M0-T108 G2 self-check (producer; recorded by the orchestrator)

Recorded 2026-08-27 UTC at content freeze. Producer = Fable 5 orchestrator session.

1. **Scope discipline:** `git status` delta = exactly the four packet paths
   (`.claude/hooks/readonly_agent_guard.py`, `.claude/settings.json` single matcher line,
   `tools/test_readonly_agent_guard_powershell.py`, `project-control/reports/M0-T108-guard-powershell-fix.md`)
   plus this self-check + gate/ledger records. No forbidden path touched.
2. **Tests:** new pack 95/95 PASS (incl. 4 RED-on-mutant); pre-existing Bash pack **unmodified**
   and 136/136 PASS (proves no removed denial/allow); ruff clean on both changed Python files;
   `modularity_check --check` — guard 589 SLOC, under threshold, no new warnings.
3. **Objective coverage:** (i) matcher extended to PowerShell; (ii) PowerShell
   mutation/redirection denylist with backtick normalization + reuse of the shell-agnostic
   passes + fail-closed envelope unchanged; (iii) scripting class treated generally
   (best-effort `_SCRIPT_WRITE` on both shells) with the residual documented honestly in the
   guard docstring; (iv) quote-aware redirect scan removes the observed read-only false
   positives (pure-read `open(` asserted ALLOWED).
4. **Behavior invariants:** lead pass-through, roster-producer pass-through, named-spawn
   fail-closed — all asserted in the pack.
5. **Known limitations (disclosed):** alias tokens (`sc`, `del`, `md`, …) and mutating tokens
   inside quoted strings can false-positive a PowerShell read command that embeds them — the
   same quoted-text posture the Bash `_MUTATING` pass has always had (fail-closed by design);
   dynamically composed scripting writes remain a documented residual (§2 of the producer
   report). Python version note: all checks run on the local Python; the pack is stdlib-only
   and version-agnostic (no PEP 695 syntax).
6. **Self-verdict:** ready for independent G3/G4/G5 at the frozen identity below (producer does
   not self-approve; gates decide).
