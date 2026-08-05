# D-009 — source-002 (owner amendment 1, VERBATIM): M0-T019 age decision = Option B (6-day verified path); scoped, owner-authorized, auto-expiring FE-S9 exception

Captured per `.claude/skills/directive-compliance` §1. Channel: owner_message (typed directly to the
orchestrator on 2026-08-05). Amends `source-001.md` (it exercises and re-realizes the emergency-exception
provision of D-009-R006 / policy §6). Frozen baseline unchanged: `d5d9b506c8be63eafd00ad92bd2d3dab2012d067`
(origin/main). Head at capture time: `control/D-009-depsec-and-m0t019-dispatch` = `eb80a4dc…` (batch branch).

Requirement IDs added by this amendment start at `D-009-R008`; no existing source file or requirement
row (D-009-R001..R007) is edited.

## Provenance / context (owner orientation line, verbatim — not itself a directive)

> run python tools/project_control.py status, read that handoff, and pick up either thread once you've
> done the corresponding owner step. Everything's committed, pushed (bar this last handoff commit), and
> nothing's accepted/merged/activated.

This resolves the deferred A/B age decision recorded in
`project-control/reports/M0-T019-transitive-advisory-blocker-2026-08-05.md` §6b and blocker B-017: the
owner selects **Option B**.

## THE DIRECTIVE (verbatim from the owner message, 2026-08-05)

> B — take the 6-day verified path for M0-T019. I've confirmed I only care about the age gate as
> infection protection, and brace-expansion 1.1.18 + sharp 0.35.3 are already deep-search-verified clean
> (maintainer GPG-signed, genuine fixes, published before the Aug-4 npm incident window). Add a SCOPED,
> owner-authorized, auto-expiring FE-S9 exception for ONLY those specific verified versions — do not lower
> the global 7-day threshold, and do not exempt anything else. Then re-run G3 and G5 over that exception
> change (it's a deliberate, reviewed weakening, not a silent one), regenerate the lockfile via CI, and
> run M0-T019's remaining gates. Capture the exception and my authorization verbatim. Report the
> accept-readiness when the gates pass.

## What this amendment changes about D-009's realization (visible reversal, not silent)

D-009-R006 / policy §6 already reserve an owner-authorized, age-only, auto-expiring emergency exception.
The EXISTING implementation realized that provision as an **owner action OUTSIDE the tool** — the
machine gate `apps/web/scripts/dependency_age_gate.mjs` (FE-S9) was hard-set to 7 days (604800 s) with
"no allowlist / suppression / --ignore / exception path in this tool", so "a paper exception cannot make
the gate pass" (gate header; `docs/DEPENDENCY_SECURITY_POLICY.md` §1/§2(b)/§6; M0-T019 FE-S5/FE-S8/FE-S9).
This owner directive **reverses that specific design choice**: it authorizes an actual code-level,
narrowly-scoped, auto-expiring exception path IN the gate, for exactly two owner-verified version pins.
The owner labels this "a deliberate, reviewed weakening, not a silent one" and mandates re-running G3 + G5
precisely because a previously-reviewed security control is being changed. It also supersedes, for these
two versions only, the prior WAIT default (B-017) and the earlier owner DECLINE of age exceptions for
M0-T019 (B-013). Every in-repo assertion that FE-S9 has "no exception path" must be updated in lockstep so
no committed text contradicts the shipped gate behavior.

Timing note (recorded, does not alter the directive): at capture (2026-08-05T22:33Z) brace-expansion
1.1.18 is ~6.5 days old and clears 7 complete days on real registry age at 2026-08-06T10:17:06.961Z;
sharp 0.35.3 (published 2026-07-01) is already ~35 days old and passes the unchanged age gate on real age,
so of the two named pins only brace-expansion@1.1.18 actually requires the exception.

## Redaction

No secrets/keys/credentials present. Verified by scan before commit.
