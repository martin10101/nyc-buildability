# D-024 Amendment 13 — Option A authorized: 2.1.251 admission (autoupdater control → fixture recapture → third recertification → R276 rerun with one-time repin) (owner instruction 2026-08-29)

Captured: 2026-08-29 UTC by the orchestrator (Fable 5), verbatim from the owner's interactive
message (typed in response to the seq-30 R276-stop report: provider CLI drift, installed claude
2.1.251 vs certified 2.1.248; options A/B presented in
`project-control/reports/M0-T113-activation-preflight.md` §6). Base identity at capture: branch
`control/D-024-fable-codex-loop`, HEAD `e958b64cbc8f10ec0af5d58eef4db0aeb9a0012b` (local ==
origin; tree clean except the pending `project-control/state.json` timestamp from the seq-30
progress record, folded into this capture commit). Amends: `source-001.md` (owner directive v4).
Requirement IDs assigned: D-024-R277..D-024-R288.

Reconciliation: this selects and authorizes Option A exactly as reported at the seq-30 stop —
a deliberate admission of installed Claude Code 2.1.251 following the M0-T092 precedent
(2.1.247→2.1.248), instantiated as three new bounded ledger units plus the already-open
activation task: **M0-T117** (establish + verify the DISABLE_AUTOUPDATER=1 control for
controller-launched Claude processes and the certification window — BEFORE any recapture),
**M0-T118** (bounded fixture recapture at 2.1.251), **M0-T119** (the resulting R247 full
recertification window at one frozen final identity, M0-T112/T116 pattern), then the full
R276 rerun on **M0-T113** with the one-time `--repin-cli-identity` and digest verification at
the certified start. It adds standing admission-event discipline for all future Claude Code
upgrades and an explicit owner-side stop for any Windows-level environment change. No owner
gate is loosened; R257 exclusions, R270/R273 (no restart loops, no journal edits), and every
Amendment-9..12 condition remain unchanged.

Forward trace: paragraph 1 ("I authorize Option A … rerun R276 in full.") → R277 (umbrella
authorization; the four named acts are individually instantiated by R281 recapture, R283
recertification, R284 rerun, R285 repin); paragraph 2 sentence 1 ("Before recapturing the
fixture, establish and verify the supported DISABLE_AUTOUPDATER=1 control …") → R278
(establish+verify, both scopes) + R279 (strictly before recapture); sentence 2 ("Do not use
DISABLE_UPDATES, downgrade Claude, or make unrelated global configuration changes.") → R280;
paragraph 3 ("Record 2.1.251 as the admitted version only after … all pass.") → R282;
paragraph 4 sentence 1 ("After certification, rerun R276 from the beginning.") → R284;
sentence 2 ("On the certified start, apply the authorized one-time --repin-cli-identity,
verify the new executable digest, and resume M0-T107 …") → R285; paragraph 5 sentence 1
("Going forward, keep background updates disabled for controller-launched workers.") → R286;
sentences 2–3 ("Treat future Claude Code upgrades as deliberate admission events … Do not
silently accept version drift.") → R287; paragraph 6 ("If applying DISABLE_AUTOUPDATER=1
requires an owner-side Windows action, stop before changing it and give me the exact
administrator PowerShell command plus a verification command.") → R288.

Anchors: #option-a-authorization (¶1), #autoupdater-control (¶2 s1), #prohibited-means
(¶2 s2), #admission-hold (¶3), #resume-mechanics (¶4), #standing-admission-discipline (¶5),
#owner-side-action (¶6).

---VERBATIM-BEGIN---
I authorize Option A: perform a bounded fixture recapture at Claude Code 2.1.251, use --repin-cli-identity on the next certified start, complete the resulting R247 full recertification window, and then rerun R276 in full.
Before recapturing the fixture, establish and verify the supported DISABLE_AUTOUPDATER=1 control for the controller-launched Claude processes and the certification window so the CLI cannot change again while certification is running. Do not use DISABLE_UPDATES, downgrade Claude, or make unrelated global configuration changes.
Record 2.1.251 as the admitted version only after its fixtures, drift teeth, live probes, golden suites, gates, independent reviews, manifest binding, and frozen-identity certification all pass.
After certification, rerun R276 from the beginning. On the certified start, apply the authorized one-time --repin-cli-identity, verify the new executable digest, and resume M0-T107 in the already-authorized limited-auto mode.
Going forward, keep background updates disabled for controller-launched workers. Treat future Claude Code upgrades as deliberate admission events: update intentionally, recapture fixtures, recertify, and only then repin. Do not silently accept version drift.
If applying DISABLE_AUTOUPDATER=1 requires an owner-side Windows action, stop before changing it and give me the exact administrator PowerShell command plus a verification command.
---VERBATIM-END---
