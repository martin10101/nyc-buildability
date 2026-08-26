# M0-T102 G5 security review (VERBATIM save)

Reviewer: independent read-only `security-reviewer` (unnamed spawn); reviewed at HEAD
`b69600f45d967887b16eaa68d9d19d5c2265e211` (deliverable identity `146918f`, manifest
`4ec1f5cb...`); returned through the agent-return channel 2026-08-26 UTC and saved verbatim
below (transport entity-decoding only — the harness neutralizes `<` in transit; restored here).

---

G5 security review complete. All evidence gathered and cross-checked. Returning the full report.

---

# G5 Security Review — M0-T102 (D-024 Amendment 3 unit A: native capability re-baseline)

**Verdict:** `G5: PASS`

**Reviewed identity:** HEAD `b69600f45d967887b16eaa68d9d19d5c2265e211`, branch `control/D-024-fable-codex-loop`, deliverable content identity `146918f`. Confirmed control-plane-only interval `146918f..b69600f` (deliverable files — capability-rebaseline.md, native-reuse-matrix.json, docs-snapshot/, fixtures — are byte-frozen; only G2 gate record, report status, state.json, and task status advanced). Material identity stable.

**Scope reviewed:** all 40 files in `git diff 05d03a0..b69600f` (amendment source + requirement/manifest/verification rows, D-030 records, M0-T102/M0-T103 packets, 16-file docs snapshot, probe fixture, native-reuse matrix, owner report + capture-verification + evidence-map, G0/G2 gate records, state/campaign records). Read-only review; no write commands run.

---

## Summary of the six mandated checks

| # | Check | Result |
|---|---|---|
| 1 | Public-repo leak scan | PASS with LOW advisory (pre-existing home-path/username/session-id convention in control-plane files; fixtures + docs are masked) |
| 2 | Probe fixture masking | PASS — identical `[HOME]` masking to the 2026-08-25 predecessor |
| 3 | Guard-gap finding | CONFIRMED real; MEDIUM advisory; out-of-scope for this task; remediation path (M0-T108) is adequately scoped; nothing malicious/out-of-scope was written this round |
| 4 | Prohibition compliance (D-024-R146) | PASS — no MCP/config, no SDK, no dependency/lockfile, no bypass flags, no protected-PR modification |
| 5 | Amendment security posture | PASS — deferrals are sound; preconditions enumerated below |
| 6 | Statusline/telemetry leak posture | PASS — no telemetry/statusline config modified |

---

## Findings

### BLOCKING
None.

### ADVISORY — MEDIUM: `readonly_agent_guard.py` does not intercept PowerShell / scripting-language writes (CONFIRMED)

- **What / where:** `.claude/hooks/readonly_agent_guard.py` is wired in `.claude/settings.json` as a `PreToolUse` hook with matcher `"Bash|Write|Edit|MultiEdit|NotebookEdit"` (settings.json:45). The code enforces only `tool in {Write,Edit,MultiEdit,NotebookEdit}` and a `tool == "Bash"` command scan (`_MUTATING`/`_REDIRECT`/`_git_argv_mutates`, guard lines 365-377). There is **no matcher entry and no code branch for a PowerShell tool**, and the module docstring itself acknowledges the broader residual (a scripting-language write such as `python -c` opening a file is not sandboxed). PowerShell cmdlet writes (`Set-Content`, `Out-File`, `Add-Content`, `New-Item`, `Move-Item`, `Remove-Item`, `Tee-Object`) and a PowerShell-tool invocation whose tool name isn't `Bash` therefore reach the filesystem with no deny. The producer's disclosure (task progress_log; owner report §11 item 1) is accurate.
- **Evidence it was exercised benignly this round:** Two read-only-typed agents wrote docs-snapshot files this way (disclosed + orchestrator-ratified). I verified the write set: the snapshot directory contains **exactly the 16 assigned doc pages** (agent-view, changelog, checkpointing, cli-reference, commands, cross-session-messaging, goal, hooks, plugins-reference, remote-control, sessions, skills, statusline, sub-agents, workflows, worktrees) and nothing else. Every write landed inside `allowed_paths` (`project-control/reports/M0-T102-docs-snapshot`, `tools/agent_supervisor/fixtures`). **Nothing malicious or out-of-scope was written.**
- **Severity rationale (MEDIUM, not blocking):** This is a genuine bypass of an advertised defense-in-depth control (read-only reviewer isolation) — a reviewer agent could mutate the working tree. It is mitigated, not eliminated, by the orchestrator-only integration model (only the lead stages/commits/pushes; a reviewer's local write reaches no branch/PR/ledger unless the orchestrator stages it — reinforcing the standing "no broad `git add`" discipline). It is **not blocking for M0-T102** because: (a) `.claude/hooks` and `.claude/settings.json` are in this task's `forbidden_paths` — the task correctly does not touch the guard; (b) the gap is pre-existing; (c) the round's writes were all in-scope and ratified; (d) remediation is tracked.
- **Remediation path adequacy (M0-T108):** The proposed follow-up (owner report §4/§8: "control-plane fix: close the readonly-guard PowerShell write gap") is **adequately scoped as a direction**. To actually close the gap, M0-T108 must: (i) extend the `PreToolUse` matcher to cover every write-capable shell tool the harness exposes on Windows (not only `Bash`); (ii) add a PowerShell mutation/redirection denylist mirroring the Bash pass (cmdlets above, `>`/`>>`, `git` invoked via PowerShell) with the same fail-closed-on-unparseable envelope; (iii) treat the class generally (the `python -c` residual is the same failure mode); (iv) add regression tests analogous to the existing Bash tests. Until it lands, the interim mitigation ("orchestrator treats PowerShell as a write surface in dispatch prompts") is a reasonable **procedural** stopgap but is not machine-enforced. **Recommendation:** land M0-T108 before any unit (C-I) that dispatches read-only reviewer agents into the working tree.

### ADVISORY — LOW: public-repo exposure of local home path, Windows username, and session id in committed control-plane files

- **What / where:** Newly-added control-plane files carry the literal absolute home path and username, e.g. `project-control/tasks/M0-T102.json` `"worktree": "C:/Users/MLFLL/Downloads/nyc-zoning/ctl24"`; `source-003-amendment.md` capture header/annex (`C:\Users\MLFLL\...`, and `C:\Users\MLFLL\.local\bin\claude.exe`); `M0-T102-capability-rebaseline.md` §1; `M0-T102-capture-verification.md`; verification.json notes. The Claude session id `session_01HfptKuEs3RDxaxsSHJjc7t` appears in the amendment, owner report, capture-verification, and verification records.
- **Assessment:** No secrets, tokens, API keys, credentials, or email addresses are exposed (the git grep for `@gmail`/`Bearer`/`ghp_`/`sk-`/private-key markers returned only official-docs placeholders and legitimate SHA-256 provenance digests). The exposed items are a local OS username, a home directory layout, and an opaque session correlation id with no standalone auth value. This is a **pre-existing, repo-wide convention** — `MLFLL` already appears in 313 tracked files (e.g. `M0-T101.json` already carries the same `worktree` path), and the session id in 14 files. The masked artifacts this round (probe fixture and all 16 docs snapshots) are correctly scrubbed (0 `MLFLL` hits; generic `~/.claude`, `/Users/username`, `myhost` placeholders).
- **Severity rationale (LOW, not blocking):** Username/home-path disclosure in a public repo is informational (usernames also appear in git author metadata). It is not introduced as a new class by M0-T102, and the un-masked `worktree` field is written automatically by `project_control.py`, which is outside this task's file scope to change. **Recommendation (separate repo-wide hygiene task):** mask the `worktree` field and capture-annex paths to a `[REPO]`/`[HOME]` token consistent with the fixtures, and stop recording the raw session id in durable control-plane files.

---

## Positive confirmations (per mandated check)

1. **Fixture masking (check 2):** `capability_probe_live_2026-08-26.json` masks the home prefix exactly as its 2026-08-25 predecessor — `probe_meta.claude_binaries`/`codex_binaries` use `[HOME]\.local\bin\claude.EXE`, `[HOME]\AppData\Roaming\npm\...`. No `MLFLL`, no absolute user path, no token. Masking approach is byte-consistent with the predecessor. `grep MLFLL` over the fixtures dir and the docs-snapshot dir = 0 hits.
2. **Prohibition compliance (check 4, D-024-R146):**
   - No MCP servers/config: every `mcpServers` / `--strict-mcp-config` / `mcp-config` occurrence is inside the official docs snapshots (documentation text). No `.mcp.json`, no `.claude/settings.json` change in the diff.
   - No Agent SDK admission: all `agent-sdk` / `CLAUDE_AGENT_SDK` occurrences are docs-snapshot text; no dependency admits the SDK. The matrix explicitly REJECTS the SDK as top-level authority.
   - No dependency/lockfile changes: no `package.json`, lockfile, `requirements`, `poetry`, or `pyproject` in the diff.
   - No permission-bypass flags in committed config: every `--dangerously-skip-permissions` / `bypassPermissions` occurrence is docs-snapshot text (cli-reference, sub-agents, worktrees, remote-control); no committed config applies them.
   - No protected-PR modification: `git log 05d03a0..b69600f` is five control-plane commits (capture + evidence + G2 + submit-snapshot); no `gh`/merge, no PR #241 touch, no `.github/` change. PR #241 non-merge standing item is restated in the owner report §11.3.
3. **Telemetry/statusline posture (check 6):** No telemetry or statusline config modified — `.claude/settings.json`, otel/env config are absent from the diff. The only `statusline` matches are a docs snapshot (`statusline.md`) and requirement text; the accepted statusLine integration is explicitly RETAINED (R162), not altered.
4. **Matrix security posture (check 5):** Sound. Messaging + Remote Control are `REJECTED_OR_DEFERRED` (matrix `messaging-and-remote-control`) with explicit reasoning — messaging delivery is not guaranteed → advisory-only, never authority/ledger replacement; Remote Control stores the transcript on Anthropic servers while connected + carries MCP surface implications → **owner security review + owner decision required before any offering (Tier-B/D routing)**. `fallbackModel` is rejected as a refusal/quota substitute (R165). Top-level-loop mechanisms remain prohibited as campaign authority. These decisions do not create a regression; they correctly gate the risky surfaces behind future security review.

---

## Security preconditions the conversion packets (units B–I) MUST carry

These are the security invariants that later implementation packets must encode as acceptance evidence so the deferred/wrapped native surfaces do not become a regression when built.

**Cross-cutting (all units):**
- Every new fixture/report uses the `[HOME]` masking (no `MLFLL`, no absolute path, no session id, no token). No worker-visible token/context quotas in any dispatched prompt (R045/R150).
- Land M0-T108 (guard PowerShell/scripting fix) before dispatching read-only reviewer agents into a write-capable working tree; until then, keep the procedural PowerShell-as-write-surface mitigation and strict staging (no broad `git add`).

**Unit B (M0-T103 — upgrade 2.1.220→2.1.246 + dual-version probes):**
- Re-prove MCP default-deny on the upgraded binary (Bootstrap Gate 0 + `/mcp` clean + `--strict-mcp-config` clean child launch).
- Re-run statusLine/subagentStatusLine no-leak proofs post-upgrade (no user paths, secrets, masked session data, or credentials) — R183/R185.
- Masked dual-version fixtures only.
- Post-upgrade default permission mode stays `default` — never persist `--dangerously-skip-permissions`/`bypassPermissions` (docs: the flag persists across `--bg` supervisor restart; the `--dangerously-skip-permissions daemon` routing must not be triggered). Rollback (`claude install 2.1.220`) must not introduce a bypass flag.

**Unit C (M0-T104 — native runtime adapter / background sessions):**
- Confirm the background-session daemon opens no inbound network port; the cross-session inbox is a per-session OS-user-restricted socket/named-pipe. On native Windows verify the `CLAUDE_CODE_MESSAGING_TOKEN` auth-line requirement is intact and the token is never logged/committed.
- Background sessions must NOT auto-enable Remote Control (`remoteControlAtStartup` unset/false; rely on the checked-in-project-file-can-only-turn-off semantics; `disableRemoteControl` available as hard off).
- Deterministic session names must not embed the machine hostname (RC auto-names default to hostname) or any secret in committed fixtures.
- Exactly one runtime backend per session; fail-closed to the existing controller (no dual process-management).

**Unit D (M0-T105 — native event integration / hooks event bus):**
- Hook recorders redact user paths/secrets/tokens/masked-session data; atomic persistence; restart-safe replay; unknown-event/version-drift handled safely (R155). Security/authority-relevant hooks (completion gates, seam detection) fail closed, mirroring the guard's fail-closed envelope.
- If any HTTP hook is used, it is the SSRF/exfil surface: it MUST be constrained by `allowedHttpHookUrls` and `httpHookAllowedEnvVars`; no real `Authorization: Bearer` token committed; env substitution only for allowlisted vars. Prefer command hooks over HTTP hooks to avoid the surface.
- UserPromptExpansion/UserPromptSubmit interception must sanitize and bound input and must not insert unbounded transcript/status into Fable context. Leverage the native "instruction-shaped subagent output" marker (sub-agents.md) as an additional prompt-injection signal, but keep the repo's own sanitizer/`boundedEvidenceId` discipline as the primary defense.

**Unit E (M0-T106 — bounded `/goal`):**
- No worker-visible token/quota pressure in goal prompts; completion condition leaks no internal secret; the four goal-clearing error classes are handled fail-safe; no silent runtime activation on version success.

**Unit F (M0-T092 — controller / seams / succession):**
- Successor handoff must be bounded and reconstructable from durable state alone (ledger/reports/git) — never from Claude session state or cross-session messages. Enforce at the ledger boundary that an incoming cross-session message is advisory only (never authority, approval, or config change). Recommend `isolatePeerMachines: true` if messaging is ever enabled. Retain frozen-identity review, writer-lease/overlap detection on top of native worktrees; pin the worktree `baseRef` to `head` (documented default-branch hazard).

**Unit G (M0-T094 — operator skills + UserPromptExpansion):**
- Control skills carry `disable-model-invocation: true` (owner-only invocation, R159). Status/control commands call the external supervisor directly and prove zero-model-context insertion (else honest second-terminal fallback). Must not collide with built-in `/loop`. Ensure sensitive controls are not unintentionally advertised to Remote Control/SDK command lists.

**Unit H (M0-T093/M0-T095 — refusal bridge, repair gate, GitHub exact-once):**
- `fallbackModel` must not silently replace guardrail-refusal/quota policies (R165); refusal vs quota vs availability-fallback stay distinct (16.4 matrix). GitHub/external effects remain custom, exactly-once/idempotent — not delegated to any native cross-session/remote mechanism. MCP default-deny + security controls remain custom (R164).

**Unit I (M0-T096 — shadow/supervised/crash + golden run):**
- Golden run re-proves: MCP default-deny effective; statusLine/telemetry leak-freedom; no token quotas in worker prompts; no routine polling into Fable context; both crash windows (commit-before-push, push-before-ack) recover exactly-once; **no protected owner gate crossed and continuous mode stays disabled after the golden run until explicit owner activation (R187, R595).**

---

**Verdict:** `G5: PASS` — no BLOCKING security defects. Two non-blocking advisories (MEDIUM guard PowerShell gap, correctly out-of-scope and tracked as M0-T108; LOW pre-existing public-repo home-path/session-id convention, recommend a separate hygiene task). All D-024-R146 prohibitions honored, fixture correctly masked, telemetry config untouched, and the amendment's deferral of Remote Control / cross-session messaging is security-sound with the preconditions above required of the conversion packets.

Report files of record (absolute paths):
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\reports\M0-T102-capability-rebaseline.md`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\reports\M0-T102-native-reuse-matrix.json`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\fixtures\capability_probe_live_2026-08-26.json`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\.claude\hooks\readonly_agent_guard.py`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\.claude\settings.json` (guard wiring, matcher line 45)
