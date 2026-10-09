# D-024 Amendment 34 — owner authorization of the bounded M0-T132 combined admission + recertification lane (owner instruction 2026-08-31/09-01)

Captured: 2026-09-01 UTC by the successor orchestrator (Fable 5), verbatim, BEFORE acting.
Base identity at capture: HEAD `1d4a6212` (campaign seq 64). Amends: `source-001.md`.
Requirement IDs: D-024-R437..D-024-R445.

Reconciliation: this is the "separate owner authorization" contemplated by R436 — once the
R437/R438 preflight passes, the R436 seam prohibitions are lifted ONLY for the bounded
M0-T132 lane defined here (admission, fixture recapture, repin, ONE combined R247 recert);
the R429 deferral of the admission lane ends by this authorization. Everything else in R436
(no journal writes beyond what preservation permits, no loop start) and every other owner
gate remains in force via R443/R444. R438 implements the R433 re-verification condition and
R434 step (1); R445 implements R434 step (3) as PRESENT-ONLY — the owner types the commands.

Forward trace: para 1 ("Work from durable repository evidence only ... before making any
change") + para 2 ("Verify root ... campaign seq-64 NEXT") -> R437; para 3 ("Before
beginning any task, verify ... stop and report without changing anything") -> R438; para 4
sentence 1 ("If all checks pass, I authorize the bounded M0-T132 combined admission and
recertification lane") -> R439; para 4 sentence 2, admission scope ("admit the settled
Claude Code 2.1.252 identity, recapture the three affected live capability fixtures, repin
the CLI capability manifest") -> R440; para 4 sentence 2, recert clause ("perform one
combined R247 recertification covering both accepted M0-T131 and the admitted 2.1.252
runtime") -> R441; para 4 sentence 3 ("Run all required gates, independent reviews and DCV
at one final frozen identity") -> R442; para 5 sentence 1 ("Preserve the HALTED supervisor
journal ... every existing owner gate") -> R443; para 5 sentence 2 ("Do not start the
supervisor ... or execute commissioning commands") -> R444; para 6 ("After everything
passes, stop and present ... Do not execute those commands yourself") -> R445.
Anchors: #preflight-reconcile (R437), #fresh-process-verification (R438),
#m0t132-authorization (R439), #admission-scope (R440), #combined-recert (R441),
#gates-one-identity (R442), #preservation (R443), #prohibitions (R444), #final-report (R445).

---VERBATIM-BEGIN---
Work from durable repository evidence only. Complete Bootstrap Gate 0 and reconcile live git, the project-control ledger, campaign record, supervisor journal and docs/SESSION_HANDOFF.md before making any change.

Verify root = C:\Users\MLFLL\Downloads\nyc-zoning\ctl24, branch = control/D-024-fable-codex-loop, HEAD equals origin, the tree is clean, and /mcp reports no servers. Read CLAUDE.md, docs/SESSION_HANDOFF.md, .claude/session-handoff-profile.md, and the campaign seq-64 NEXT.

Before beginning any task, verify that this fresh process inherited DISABLE_AUTOUPDATER=1, DISABLE_UPDATES remains unset, `claude --version` reports exactly 2.1.252, the on-disk supervisor-native executable identity is exactly e713c5a6, and no newer update or update banner is present. If anything differs, stop and report without changing anything.

If all checks pass, I authorize the bounded M0-T132 combined admission and recertification lane. Create and execute M0-T132 under the standard project-control process: admit the settled Claude Code 2.1.252 identity, recapture the three affected live capability fixtures, repin the CLI capability manifest, and perform one combined R247 recertification covering both accepted M0-T131 and the admitted 2.1.252 runtime. Run all required gates, independent reviews and DCV at one final frozen identity.

Preserve the HALTED supervisor journal, audit chain, worktrees, budgets, owner-touch history, worker drafts and every existing owner gate. Do not start the supervisor, clear or restart the journal, merge PR #241, reset anything, or execute commissioning commands.

After everything passes, stop and present the complete fresh preflight and the exact mechanically validated owner-typed `owner-restart` and certified start commands for the next commissioning journey. Do not execute those commands yourself.
---VERBATIM-END---
