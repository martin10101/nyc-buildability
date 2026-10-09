# D-090 source-029 (amendment): owner messages 65-66, 2026-10-05 - give this machine a browser to test what it builds; "is it safe? if yes go"

Captured 2026-10-05 by the orchestrator (Claude Code session 013RaGmCmULdpmjCy58qBeMY, model claude-opus-5-5) from the saved session transcript `~/.claude/projects/-root-project-nyc-buildability/4d3637bc-346a-4b44-a0e7-b9688bc4f91a.jsonl`: message 65 (line 2728, uuid `434b8717-8fa4-450c-b675-e2ba919fe496`, 2026-10-05T19:02:55.663Z) and message 66 (line 2777, uuid `35db7cbd-a3ca-4445-9a63-3ce42c51f25e`, 2026-10-05T19:06:01.149Z). A script copied the raw text; nothing was retyped; each is complete and byte-identical to the transcript except for the blockquote prefix. Raw-text SHA-256: 65 `6e4ba0168b39bf3400648a1281a66a3c724a00615a10992ff9e1752daa73f4a8`; 66 `9cdaae349ad7e6216df2d7abca5c7aba8893eae2cf94e4d54616ca4b4cd87631`. Message numbers continue from source-028 (message 64). This branch is stacked on the source-028 capture (R167-R169), which is still an open PR.

Context: between the two messages the orchestrator checked the options online and proposed, in plain words: step 1 = let this machine run the browser tests the project already has (Playwright with a hidden Chromium, the exact locked packages, the same commands the GitHub checks run), with the rule "no Node on this machine, website tests only on GitHub" changed to "run the website tests here first, GitHub stays the final word"; step 2, later = a browser tool for the agent (a new package, through the package safety check). It ended: "Say 'go' and I set up step 1 and record the rule change."

## Owner message 65 (verbatim)

> i want this pc to have eccsues to browser to run test on what it builds tell me how we do it best easy way check online befor you answer becuse i know there is alot of ways for cc

## Owner message 66 (verbatim)

> is it safe ? if yes go

## Reading

| Owner words | Requirement |
|---|---|
| Message 65: "i want this pc to have eccsues to browser to run test on what it builds" | R170 (obligation) |
| Message 65: "tell me how we do it best easy way check online befor you answer becuse i know there is alot of ways for cc" | answered in chat with sources (no row) |
| Message 66: "is it safe ? if yes go" | R171 (authorization, conditional on safety) |

- **Orchestrator's readings (not owner wording):** (1) "this pc" is the Linux development server the sessions run on (Ubuntu 24.04, 4 CPUs, 8 GB memory, 116 GB free, no screen), not the owner's own low-storage PC that CLAUDE.md principle 14 and `docs/LOW_STORAGE_CLOUD_DEVELOPMENT_POLICY.md` protect; that policy is unchanged for the owner's PC. (2) R171's condition was assessed as met: `npm ci` installs only the versions already locked with integrity hashes in `apps/web/package-lock.json` (the same tree the GitHub checks install; blockers B-022 and B-028 on web advisories are resolved); the browser is the Chromium build Playwright 1.61.1 (already pinned) downloads from its publisher, as the CI job does; the browser has no window and loads only this project's own pages on 127.0.0.1 served from recorded fixtures; nothing touches production, secrets or the live site; removal is deleting `apps/web/node_modules` and the Playwright browser cache. One disclosed caveat: run as root, Chromium runs without its inner sandbox, which is acceptable only because it never browses outside sites. (3) "go" authorizes step 1 and the rule change the orchestrator named: the `.claude/rules/CODING_RULES.md` line "DON'T run or document npm/npx/node locally (thin client) - web tests prove ONLY in CI" is amended for the development server; CI on the pushed head stays the final word. It does not authorize a new package: step 2 (a browser tool for the agent) still goes through the dependency-security admission (principle 15), and the MCP-clean start rule is unchanged.
