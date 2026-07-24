# D-004 — source-005 (owner amendment 4, verbatim)

Captured verbatim per `.claude/skills/directive-compliance` §1 (amendments are new append-only
files; committed sources are never edited). Channel: owner_message. Amends `source-001.md`.
Frozen baseline unchanged: `origin/main` = `421265709f81a40e20f3d890609907ed932967dd`.
Head at capture time: `origin/main` = `b43b49886987f0b6a6804910bf0fb62672ecbb57` (post PR #108).
Requirement IDs added by this amendment start at `D-004-R129`; no existing row is edited.

---

OWNER DECISIONS on the Step-1 STOP (D-004). Capture this as the next
append-only amendment in sequence; new requirement IDs from the next
free row; recompute digests; no edits to existing rows.

1. STEP-1 EVIDENCE — ACCEPTED AS-IS. Do not re-run the reviewer wave
   now. The FAIL/FAIL/PASS verdicts, the off-policy Sonnet spawns, and
   the sentinel escape stay recorded exactly as captured; the
   UNVERIFIABLE byte-identity finding is accepted as inherent to
   flag-3 option (a), no remediation. The on-policy re-run happens
   ONLY after the B-015 fix merges, and then doubles as that fix's
   end-to-end acceptance test: same three reviewer roles, frozen SHA =
   then-current main head, EXPLICIT per-spawn model Fable 5 on every
   spawn, sentinel test repeated — and this time the denial must be
   observed and independently verified.

2. R095 — CONFIRMED: R081 was the intended row. Your verbatim-match
   resolution stands; record the confirmation in this amendment.

3. B-015 — RATIFIED as an orchestrator control action. Its diagnosis
   and fix are assigned to M0-T028, whose scope now expands to:
   (a) determine with evidence why the PreToolUse guard did not deny
   the teammate's Bash redirection (hook not firing for teammates vs
   firing without agent_type), factoring in the positive finding that
   per-spawn tool-unavailability WAS enforced by the harness;
   (b) fix so reviewer-class teammates are denied writes;
   (c) regression tests = the sentinel test itself, plus the R100
   path-quoting ride-along and the R101 settings.local.json gitignore
   entry;
   (d) the index.json affected_tasks correction if M0-T028's packet
   rules allow it, else flag where it belongs.
   Do NOT start M0-T028 yet; present its packet for my review first.

4. STEP-2 GO — granted now, before the fix, deliberately: the probe
   is read-only-instructed, disposable, and its outcome shapes
   M0-T028's design. Safeguards, since B-015 proves instructions are
   currently the only barrier: pre-create both worktrees from the
   frozen base; spawn probe teammates WITHOUT Write/Edit tools
   (tool-unavailability is proven enforceable), Bash instructed to
   pwd/git inspection only; after the second attestation, run a full
   dirt sweep (git status in the main checkout AND both worktrees),
   record it in the probe report before teardown. Any unexpected file
   anywhere: record it, tear down, STOP. The probe report lives under
   M0-T027 as planned; M0-T027 stays blocked until the item-1 re-run
   passes — collecting further pilot evidence under it is authorized.

5. EFFORT — DECIDED, hold closed: effortLevel stays xhigh,
   session-global, unchanged. MAX is rejected because the only
   existing mechanism is session-global and would force the lead to
   max as well. Revisit only if a per-spawn effort control ships.
   Still: no effort key written by you, ever.

6. MODEL MECHANISM — recorded: with teammateDefaultModel absent and
   all agent definitions model: inherit, EVERY teammate spawn must
   pass an explicit model value — Fable 5 for gate-class reviewers,
   Opus 4.8 for producers. teammateDefaultModel gets set to Opus 4.8
   via /config only at Step 5, per amendment 1.

7. R112 — acknowledged, no action: PostToolUse/Stop are intentionally
   unregistered machine-side; repo-side equivalents, if ever needed,
   arrive only through contracted tasks.

Execute: capture this amendment, then run Step 2 under item 4, then
STOP with AGENT-TEAMS-PILOT-2-PROBE.md and the M0-T028 packet
proposal. Anything ambiguous: blocker, not action.
