# SESSION HANDOFF — seq 135 (2026-10-03 ~00:45 UTC; owner-invoked /session-handoff, no reason given; Claude Code session 08a1e891 / 01AjePR92H83Yc5jH81uya6d, claude-opus-5-5; directives D-090, D-091)

Orientation only. The ledger (`python tools/project_control.py status`) and `project-control/` WIN
over this prose. Seq 134 is in git (#327).

## Identity (live at generation)
- **Machine:** the DigitalOcean droplet (Ubuntu, 4 CPU / 8 GB), not the owner's PC.
- **Repos:** main checkout `/root/project/nyc-buildability` = origin `candidate/D-024-mrl-option-b` @ `15b4d656` before this handoff PR
  (written in worktree `/root/project/w-handoff4`, branch `task/session-handoff-2026-10-03`).
- **CLIs:** claude **2.1.288** at `/usr/bin/claude` (certified by M0-T179). Host auto-update is **OFF** (`DISABLE_AUTOUPDATER=1` in
  `~/.claude/settings.json`, owner-requested on 2026-10-03). codex-cli **0.157.0** at `/opt/nyc-codex` (built from the admitted
  `tools/codex_cli/package-lock.json`), symlinked at `/usr/local/bin/codex`. Codex is **not signed in** yet.
- **Running:** no loop, no supervisor process, no subagent. Memory peaked at 16% (limit 70%).
- **Server venv:** `/root/project/lanes-runtime/venv/bin/{python,ruff}`; run api tests from `services/api` (stale `app` copy in site-packages).

## Owner decisions in force (new this session)
- **D-090 source-008–009** (#328, #340): resume rules (R077–R079); explain the loop steps and the open items in depth (R080, R081); **R082:
  the website says less and shows exact information, not warnings or long paragraphs.** R082 does not by itself remove the tax-lot-only
  warning (R030–R033) or the settled capacity wording (R038); whether that warning shrinks to a short "Tax lot only" tag is an open owner
  question.
- **D-091 source-002 / R009** (#343): the owner approved amending the activation PIN so that a **proved** systemd control group counts as
  containment alongside the Windows Job Object.
- Standing: Option B merges (a different agent's PASS at the exact head, all CI green, `--match-head-commit`); `LANE_A_ENABLED` off;
  zoning-math merges need the owner's yes; capacity wording settled; at most 5 robots, memory under 70%.
- Owner feedback: don't narrate the record-keeping ("word for word") in replies; just say what happens next.

## Done this session (each merged after independent review and green CI)
- **Product, all behind default-off flags:**
  - #326 D-12 hidden-issues window;
  - #329 W5 mount of the W2–W4 routes;
  - #331 D-15 parity window;
  - #332 site_fact 1.1.0 `version_check`;
  - #334 B-06 attach;
  - #335 B-3 wiring;
  - #336 D-04 slice 3 (version status in the lot panel);
  - #337 PLUTO version probe;
  - #338 B-4 probe wiring (fail-closed `version_unknown`; 1 attempt, 5 s; 60 s negative cache).
- **Records:** #328 and #340 (D-090 captures), #343 (D-091 R009), #333 and #339 (notes; DB-103, DB-104).
- **Loop, D-091:**
  - #330 M0-T175 checklist (interim; the task stays in progress);
  - #341 blocker **B-027** (the Linux loop could not start a worker: Windows-only containment gate plus a POSIX self-kill), via deficit
    convergence;
  - #342 contract;
  - **#344 M0-T177**, the systemd control-group containment proof plus the self-kill fix. Its real-unit kill test passed in CI;
  - **#345 M0-T178**, the equal-model refusal;
  - **#346 M0-T179**, the Linux recertification superseding M0-T174. It admits claude 2.1.288; the certified subtree is `019ecf1f`.

## Open PRs
- #268 E-03 DXF (draft; waits on A-04).
- #241: never merge.
- #64: old.

## Blockers and owner steps (plain words)
1. **PIN text (B-027 stays open until it is merged).**
   - The G5-approved text is at `/root/nyc-loop-drafts/PIN-amendment-draft.md` (sha256 `417e1f70…`).
   - The prepared branch is `control/D-091-R009-pin-amendment`, in worktree `/root/project/w-pin-amend`.
   - The orchestrator's edit is refused by auto-mode ("Security Weaken"), so the owner applies it in a terminal, or explicitly asks the
     orchestrator to run the one append-commit-push line.
   - Then: a reviewer confirms the text matches, merge, resolve B-027.
2. **Commissioning (M0-T175):** all of it is owner-typed, in the DigitalOcean web console, because `!` lines in the owner's app don't run.
   - Codex sign-in: `codex login --device-auth`.
   - The root config and `model_selection.toml`.
   - The orchestrator runs `record-manifest`, `verify-controller` and `doctor`.
   - Install the systemd unit, start it, and approve the first prompt digest.
   - The drafts in `/root/nyc-loop-drafts/` predate M0-T177: **refresh the unit draft from the hardened template** (KillMode, ExitType,
     SendSIGKILL, TimeoutStopSec, ProtectControlGroups; START_CMD must exec python directly), and contract a small canary ledger task
     first.
3. **OD-B, the combining model:** optional; the recommendation is Opus 5.5. The model must differ from the Claude reviewer model (now
   enforced in code) and use canonical ids only (DB-105).
4. **Product questions:**
   - Q1/Q12: the pilot lot and a licensed checker.
   - Lane A GO for the R6B math engine (merges still need the owner's yes).
   - The comparables "similar" rule.
   - Q4: the dashboard as the only entry.
   - Q8: the section view under the hold.
   - Q10: the architect mockup review.
   - R082: should the tax-lot warning become a short tag?

## NEW: dependency-security incident (found at handoff; not started)
- Since about 2026-10-03 01:00 UTC, `web-dependency-security` fails on **every** PR. The cause is the new advisory **GHSA-vfj7-8cjw-p6xm**
  (`braces`, high severity; npm audit shows the range `*`, i.e. all versions). It enters through a dev chain: `eslint-config-next` →
  `@next/eslint-plugin-next` → `fast-glob` → `micromatch` → `braces` (5 high findings). The audit suggests `eslint-config-next@14.2.35`,
  which is a breaking change. First seen on PR #347, run 37088548221.
- The policy has no waiver, so **no PR can merge until it is fixed**. That includes this handoff (#347). Never merge with a red check.

## Follow-ups recorded
- DB-104: before enabling the study read in production: B-001 sign-in and a study-route concurrency bound.
- DB-105: canonical model ids.
- DB-106: `preflight.py:126` session isolation, at the next recert.
- Requests B-1, B-3 and B-4 are done; B-2 (study-level transit/parking) is owner-decided W6.

## Standing restrictions
- Tier D / Section 20 stops.
- Never merge #241. The expansion §2 hold stands.
- Commissioning, the PIN amendment and credentials are owner-typed.
- Never pass `model:`. Dependency security: no waiver.
- No local npm or node for web (CI is the web executor).
- Never run whole RealProcess classes or the whole `test_agent_supervisor_model_chain.py` on this host.
- Any `tools/agent_supervisor/**` change voids the M0-T179 certification.
- Lessons are in `docs/WORKING_KNOWLEDGE.md`, "Cloud session 2026-10-03".

## EXACT NEXT ACTION (successor)
1. Gate 0, then READY TO RESUME or BLOCKED. Run `gh pr list`. **If #347 is still open, read this handoff from branch
   `task/session-handoff-2026-10-03`.**
1a. **The dependency-security incident comes first:**
   - invoke `/dependency-security`;
   - confirm the advisory's affected and patched ranges (GHSA, registry);
   - contract a Lane C (or orchestrator) fix that removes or replaces the vulnerable dev chain with an admitted, 7-day-old, advisory-free set
     (new packages need a G5 provenance review), or wait for an upstream patch;
   - then get #347 green and merge it, and re-run CI on any other open PR.
2. If the owner has pushed `control/D-091-R009-pin-amendment`:
   - a reviewer (security-reviewer) confirms the appended text equals the signed-off draft (sha `417e1f70…`) and that nothing else changed;
   - merge;
   - resolve B-027 in a control PR.
3. Prepare commissioning:
   - contract a tiny canary ledger task (one safe file, its own worktree);
   - refresh `/root/nyc-loop-drafts/` (the hardened unit; START_CMD with the canary packet, the manifest and `--codex-executable
     /opt/nyc-codex/node_modules/@openai/codex-linux-x64/vendor/x86_64-unknown-linux-musl/bin/codex`);
   - give the owner one numbered list for the DigitalOcean console.
4. Otherwise, lane work that is not owner-blocked: the R082 text cleanup pass (Lane D) on the hidden-issues, parity and lot-panel windows.

## COPY INTO THE NEW SESSION
Owner, before starting: `cd /root/project/nyc-buildability && git pull --ff-only && claude`. `/mcp` must list none.

Resume as the NYC Buildability orchestrator (verify the model with /model). Work only from repository
evidence. Verify: cwd IS the repo worktree root, branch candidate/D-024-mrl-option-b, HEAD == origin,
/mcp empty (Bootstrap Gate 0). Read CLAUDE.md, docs/SESSION_HANDOFF.md and `python tools/project_control.py
status` (the ledger wins); check `gh pr list`. Report READY TO RESUME or BLOCKED, then continue from EXACT NEXT
ACTION without repeating work. At most 5 robots, memory under 70%; LANE_A_ENABLED stays off; zoning-math
merges need the owner's yes; explain things to the owner in plain, simple words. Stop for Tier D, PR #241,
owner holds and owner-typed commissioning; never pass `model:`. If PR #347 (this handoff) is not merged yet, read
docs/SESSION_HANDOFF.md from branch task/session-handoff-2026-10-03.
