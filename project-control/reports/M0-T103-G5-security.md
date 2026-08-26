# M0-T103 G5 security review (VERBATIM save)

Reviewer: independent read-only `security-reviewer` (unnamed spawn); reviewed at HEAD
`702fe4a2d16e96ea84d1db9879d92aeb84c703b8` (deliverable identity `e0a867b`, manifest
`6092f93e…`); returned through the agent-return channel 2026-08-26 UTC and saved verbatim below
(transport entity-decoding only).

---

I have completed all evidence gathering. All seven preconditions verified against the frozen deliverable identity e0a867b (confirmed: the submit interval e0a867b..702fe4a advanced only control-plane records; the fixture, test, and version-upgrade report are byte-frozen).

---

# G5 Security Review — M0-T103 (D-024 Amendment 3 unit B: official-updater upgrade 2.1.220 → 2.1.246)

**Verdict:** `G5: PASS`

**Reviewed identity:** HEAD `702fe4a2d16e96ea84d1db9879d92aeb84c703b8`, branch `control/D-024-fable-codex-loop`, deliverable content identity `e0a867b`. Confirmed control-plane-only submit interval `e0a867b..702fe4a` (only `M0-T103-G2.json`, `M0-T103.json` report-json, `state.json`, and `tasks/M0-T103.json` status advanced; the post-update fixture, `test_agent_supervisor_capability_probe.py`, and `M0-T103-version-upgrade.md` are byte-frozen). Read-only review; no write commands run.

**Scope reviewed:** all 11 files in `git diff c6a495f..702fe4a` (G0/G2 gate records, G0-readiness + G2-self-check reports, evidence-map, version-upgrade report, report-json, state, task packet, post-update probe fixture, capability-probe test). Baseline cross-checked against `project-control/reports/M0-T102-G5-security.md` unit-B preconditions.

---

## Result per mandated precondition

| # | Precondition | Result |
|---|---|---|
| 1 | Leak scan (NEW artifacts; fixture+report `[HOME]`-masked) | PASS — deliverables masked; one new within-convention session-id (LOW) |
| 2 | MCP default-deny re-proof (no MCP config; settings.json untouched) | PASS |
| 3 | No bypass flags outside quoted docs; canaries carry none | PASS |
| 4 | Updater provenance (`claude update` only; global→native auto-correction) | PASS — auto-correction benign |
| 5 | npm-shim advisory (broken leftover on PATH pos.2) | PASS with LOW advisory |
| 6 | Statusline/telemetry (no config; deferred live re-proof honest+bounded) | PASS |
| 7 | Session integrity (parked 777b09da untouched) | PASS |

---

## Findings

### BLOCKING
None.

### ADVISORY — LOW: broken npm global `claude` shim left on PATH (second position)
- **What/where:** `M0-T103-version-upgrade.md` §1–§3. A leftover `@anthropic-ai/claude-code` npm global install sits second on PATH (`[HOME]/AppData/Roaming/npm/claude`), reported broken pre-update ("not compatible with the version of Windows you're running"); `claude doctor` records it as its 1 warning; `claude update` emitted the fix `npm -g uninstall @anthropic-ai/claude-code`.
- **Assessment:** Low risk. The native official binary resolves FIRST on PATH, so `claude` always executes the sha256-verified native install (`9f07f1ec…` post-update); the shim only executes if the native binary is removed/renamed, and being broken it fails closed (errors) rather than running stale code — this is an availability edge, not an integrity/exec-substitution exposure. It is not a repo-governed dependency (the age-gate / lockfile policy covers `package.json`/`requirements`, not the owner's global CLI harness), so no dependency-policy conflict. The updater and doctor warnings are faithfully recorded, and the uninstall is correctly scoped as owner-machine hygiene not performed by the task (owner-only action). **Recommendation:** owner runs `npm -g uninstall @anthropic-ai/claude-code` to remove the PATH-shadowing surface entirely before unit C dispatches native background sessions. Recommending owner uninstall suffices; nothing more is required of this task.

### ADVISORY — LOW: new parked-session id recorded in durable control-plane reports (within recorded convention)
- **What/where:** Owner's parked review session id `777b09da` (8-hex-char UUID prefix) newly appears in `M0-T103-G0-readiness.md`, `M0-T103-G2-self-check.md`, and `M0-T103-version-upgrade.md` (§1, §6). Confirmed genuinely new (0 hits at base `c6a495f`).
- **Assessment:** Same class as the recorded LOW session-id convention (the orchestrator's own `session_01HfptKuEs3RDxaxsSHJjc7t` already sits in 15 files at base). It is an opaque, local-only display/correlation id with no standalone auth value; sessions are local to the owner's machine and cannot be attached from a public-repo reader. Sibling project names (`nyc-ami-calculator-*`) are not new (present at base in `B-002`). No tokens/keys/credentials/emails appear in any added line. Flagged for reviewer transparency because the precondition asks for NEW instances; classified within the recorded convention, non-blocking. **Recommendation:** fold session-id scrubbing (this value included) into the repo-wide hygiene task M0-T102 already recommended.

---

## Positive confirmations (per precondition)

1. **LEAKS (PASS):** The two deliverables are `[HOME]`-masked — the post-update fixture has 0 `MLFLL` hits and uses `[HOME]\AppData\Roaming\npm\…` binary paths; the version-upgrade report uses `[HOME]/.local/bin/claude.exe` and `[HOME]/AppData/Roaming/npm/claude`. The re-baselined test adds a machine-enforced masking tooth (`test_post_update_fixture_masked_and_shaped`: asserts `"MLFLL" not in body` and every `claude_binaries` entry `startswith("[HOME]")`). The only unmasked identifiers in the diff are the auto-written `worktree` field in `tasks/M0-T103.json` (recorded convention, `project_control.py`-generated, outside task scope) and the two session-id items above. No secrets/tokens/keys.
2. **MCP default-deny (PASS):** `.claude/settings.json`, `.claude/hooks`, and `.mcp.json` are absent from `git diff --name-only c6a495f..702fe4a` — untouched. No `mcpServers` block or `.mcp.json` anywhere. Every MCP marker in added lines is either the `--strict-mcp-config` default-deny flag (report canaries lines), a capability-probe flag-detection entry (`"--mcp-config": "supported"`, `"--strict-mcp-config": "supported"` — recording that the flag exists in `--help`, not a config), or report prose. G0 report records Bootstrap Gate 0 `/mcp` = no MCP servers, none added since.
3. **Bypass flags (PASS):** Zero `--dangerously-skip-permissions` / `bypassPermissions` / `--allow-dangerously-skip-permissions` occurrences in any added line across the whole diff. The two recorded canary commands carry only `--strict-mcp-config` (+`--output-format json`). Report §9 attests no bypass flag persisted; the hook-execution canary (real Read tool call through the PreToolUse chain, `is_error:false`) demonstrates guarded default mode is active on 2.1.246 rather than a bypass daemon.
4. **Updater provenance (PASS):** `claude update` (official updater) only; report §2/§9 attest no third-party build, SDK, or wrapper. The config install-method auto-correction (`global`→`native`) is recorded (§2). Security assessment: **benign, arguably an improvement** — it reconciles the updater's own self-metadata to the native official install (sha256-verified `9f07f1ec…`) rather than the dead npm global channel, so future `claude update` flows through the native official path. It does not touch the repo's committed `.claude/settings.json` (confirmed untouched); it mutates only the owner's `~/.claude` home install-method setting (out of repo). No security concern.
5. **npm-shim (PASS w/ LOW advisory):** see finding above; warnings faithfully recorded; owner-uninstall recommendation suffices.
6. **Statusline/telemetry (PASS):** No telemetry/statusline config modified (settings.json untouched). The deferred live 2.1.246 statusLine-payload re-proof (report §8, evidence-map R162 row) is **honest and bounded**: explicitly scheduled for the FIRST fresh interactive session on the new binary (successor session or unit-C canary), matching the accepted M0-T091 next-session discharge precedent, and tracked in the campaign record. The deferral is technically necessary (this orchestrator session still runs 2.1.220 — running processes keep their binary — so it cannot emit a 2.1.246 statusLine payload). Handler tests are green within the 228-passed suite; the no-leak contract is unchanged. Not dropped.
7. **Session integrity (PASS):** The task did **not** touch parked session `777b09da`. The report cites `claude attach 777b09da` / `claude respawn 777b09da` only as the recovery path explicitly left to the owner — not executed — and states "nothing was killed." Process verified alive (pid 21448, tasklist, 189 MB). The observed display-state change (`blocked`→`failed`) is correctly attributed to a passive artifact of the official-updater-triggered daemon restart (new pid 10124) not reconnecting to a session parked mid-permission-prompt for ~7 days — an expected, documented, non-destructive side effect, not a task action. Correct restraint (attaching could answer/disturb the owner's pending permission decision). Nothing in the diff implies any interaction with the session.

**Supervisor-freeze note:** the only production-adjacent change is the test file `tools/test_agent_supervisor_capability_probe.py` (drift-tooth re-baseline + two new invariant tests). It cites qualifying evidence D-024-R148/R149/R168 in both the packet (allowed_paths widening recorded) and commit `e0a867b`, satisfying the defect-lane evidence-citation duty; no supervisor runtime activated (SHADOW-ONLY preserved, R168 step 10). No modularity concern (test-only, additive).

---

## Security preconditions this round adds/reinforces for unit C (M0-T104)

1. **Discharge the deferred statusLine no-leak proof, do not let it slip past unit C:** capture the live 2.1.246 statusLine/subagentStatusLine payload in the first fresh interactive session — masked, no user paths/secrets/session data/credentials (R162/R183/R185). This round only partially discharged R183/R185 (handler tests green; live payload deferred).
2. **Explicitly capture default permission mode = `default` (not bypass) on the auto-restarted 2.1.246 daemon** in the first live session. This round proved hooks fire and no bypass flag persisted, but printed no explicit permission-mode line for the new daemon (pid 10124).
3. **Carry the M0-T102 unit-C daemon preconditions against the now-2.1.246 background daemon:** confirm no inbound network port; cross-session inbox is an OS-user-restricted socket/named-pipe; `CLAUDE_CODE_MESSAGING_TOKEN` never logged/committed; background sessions do not auto-enable Remote Control.
4. **Recommend owner uninstall the broken npm global `@anthropic-ai/claude-code` before unit C dispatches native background sessions**, to eliminate PATH-shadowing ambiguity.
5. **Continue `[HOME]`/session-id masking** on every new fixture/report; scrub session-id values (incl. the `777b09da` class) from durable control-plane reports going forward (fold into the M0-T102 repo-wide hygiene task).

---

**Verdict:** `G5: PASS` — no BLOCKING security defects. Two non-blocking LOW advisories (broken npm shim — owner-uninstall recommendation suffices; new parked-session id within the recorded session-id convention). Deliverable fixture and report are `[HOME]`-masked, `.claude/settings.json`/hooks/`.mcp.json` untouched, MCP default-deny and hook chain re-proven on 2.1.246 with `--strict-mcp-config` canaries carrying no bypass flags, the official `claude update` provenance and its benign global→native config auto-correction are recorded, telemetry/statusline config is untouched with an honest bounded next-session deferral, and the owner's parked session `777b09da` was observed but not touched.

Report files of record (absolute paths):
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\reports\M0-T103-version-upgrade.md`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\reports\M0-T103-evidence-map.json`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\reports\M0-T103-G0-readiness.md`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\reports\M0-T103-G2-self-check.md`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\fixtures\capability_probe_live_2026-08-26_m0t103_post_update.json`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\test_agent_supervisor_capability_probe.py`
