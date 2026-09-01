# D-024 Amendment 32 — read-only CLI-update investigation ordered; conditional admission-target rule (owner instruction 2026-09-01)

Captured: 2026-09-01 UTC by the orchestrator (Fable 5), verbatim. The message ordered a
STRICTLY READ-ONLY investigation and said "Take no action", so durable capture was
deferred (blocked-directive rule) until the owner's next message authorized handoff/
control-plane records; the investigation itself ran with ZERO mutations and its
findings were reported in-session (now preserved in `docs/SESSION_HANDOFF.md` seq 47
section 4 and the campaign seq-64 record). Base identity at capture: HEAD `43036041`
(campaign seq 63). Amends: `source-001.md`. Requirement IDs: D-024-R433..D-024-R434.

Reconciliation: R433 — the eight-question investigation was performed read-only
(process/user/machine env scopes; running-session image identity vs on-disk identity;
fresh `--version`; staging dirs; updater cause; restart effect); the conditional rule
"if anything newer than 2.1.252 is installed or staged, do not propose admitting
2.1.252" RESOLVED: nothing newer exists (versions dir holds 2.1.248/2.1.251/2.1.252
only; downloads empty), so 2.1.252 (`e713c5a6`, 217,406,624 B) remains the settled
admission target, SUBJECT to re-verification of the installed identity at M0-T132
start (if moved: stop and re-report, propose the then-current settled identity
instead). R434 — the settled safest procedure: (1) owner-typed fresh-terminal settle
(quit all Claude Code sessions AND exit WindowsTerminal entirely; relaunch; verify
`$env:DISABLE_AUTOUPDATER` prints 1 in the new shell BEFORE launching claude; launch
from the ctl24 root; verify `claude --version` = 2.1.252, no update banner, versions
dir unchanged); (2) only then the owner may authorize M0-T132 (one admission +
single combined R247 recert); (3) then the owner-typed restart sequence. Never
DISABLE_UPDATES, never downgrade (R280 unchanged); the diagnostic message itself
authorized NOTHING.

Forward trace: numbered questions 1-8 + "investigate ... read-only" + "Take no
action" -> R433; question 8's "exact safest procedure" + "If anything newer than
2.1.252 ... do not propose admitting 2.1.252" -> R433 (conditional) and R434
(procedure). Anchors: #readonly-investigation (R433), #settled-procedure (R434).

---VERBATIM-BEGIN---
Before we authorize any CLI admission or recertification, investigate the visible "Update installed · Restart to update" status read-only.

Do not restart Claude, apply an update, change environment variables, admit or repin an executable, begin recertification, modify the supervisor journal, or start the loop.

Determine and report:

1. The Claude Code version used by this running session.
2. The version and executable identity currently on disk at C:/Users/MLFLL/.local/bin/claude.exe.
3. The version reported by a fresh read-only `claude --version` process.
4. Whether another version is staged and waiting for this terminal to restart.
5. The process, user and machine values of DISABLE_AUTOUPDATER and DISABLE_UPDATES, and whether this session inherited them.
6. Why the updater still downloaded an update.
7. Whether restarting now would change the executable identity.
8. The exact safest procedure to settle on one final current version, disable further automatic updates effectively, and then perform one combined admission and one R247 recertification covering both the final Claude identity and accepted M0-T131.

If anything newer than 2.1.252 is installed or staged, do not propose admitting 2.1.252. Return only the findings and proposed next steps. Take no action.
---VERBATIM-END---
