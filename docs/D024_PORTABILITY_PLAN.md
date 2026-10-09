# D-024 Portability Plan: Generic Claude Code Plugin (Unit J)

**Task:** M0-T107 (D-024 Amendment 3, unit J) | **Requirement:** D-024-R179 | **Status:** PLAN ONLY
**Authored:** 2026-08-31 at content identity c5c6ff777928071e3d3a7e555b659256c4d2a667 (branch `task/M0-T107-plugin-portability`)
**Revised:** 2026-09-02 from starting state ffc77bab (the Amendment-49 commit of the prior-journey
drafts); this revision re-verified every cited source and inventory row against the worktree
(see the producer report, Section 3) and changed no substantive decision.

## 0. Standing constraints (read first)

1. **This document authorizes nothing.** It is the planning deliverable ordered by D-024-R179
   ("prepare a separate portability plan ... portability work must not block the local loop's
   activation"). Every implementation step in Section 8 is a PROPOSAL that requires its own
   orchestrator-created ledger task under the standard gates before any file is created.
2. **Non-blocking is a hard property, not an intent.** No task proposed here may become a
   dependency of any D-024 activation, commissioning, stabilization, or recertification task.
   The local loop activates (or fails to activate) exactly as if this plan did not exist.
3. **The frozen supervisor is never modified for portability.** `tools/agent_supervisor/**` is
   under the defect-only maintenance lane (`.claude/rules/supervisor-freeze.md`; AD-093).
   Portability extraction COPIES source into a separate plugin workspace and generalizes the
   copies there. A portability wish is not qualifying evidence for touching the frozen tree.
4. **NYC-specific assets stay in this repository** (R179 verbatim: "Keep NYC-specific graph,
   ledger, security policy, profiles, and product rules in this repository"). Section 5
   enumerates them concretely.
5. **Replace-not-layer applies to this repository.** This repo keeps running its in-repo
   supervisor as the single active backend. The plugin is a downstream packaging for OTHER
   repositories; it is not installed here alongside the live loop, so no dual-backend state
   ever exists locally.

## 1. Authority and grounding

| Source | What it contributes |
|---|---|
| `project-control/directives/D-024-fable-codex-loop/source-003-amendment.md` (unit list, item J at line 337; official-doc list lines 80-99) | The verbatim unit-J order and the documentation baseline duty |
| `project-control/directives/D-024-fable-codex-loop/requirements.json` (D-024-R179) | The binding requirement this plan satisfies |
| `project-control/reports/M0-T102-docs-snapshot/plugins-reference.md` (fetched 2026-08-26) | The plugins-reference snapshot this plan's mechanics are grounded in |
| `project-control/reports/M0-T102-capability-rebaseline.md` Section 3 | Capability decision: "portability plugin" = OPTIONAL ENHANCEMENT, "post-golden-run only" |
| `project-control/tasks/M0-T107.json` | Task packet: deliverables, scope, gates (G0/G2/G3) |

**Snapshot-staleness duty:** the plugins-reference snapshot is dated 2026-08-26. Whichever future
task implements Phase 1 must re-fetch the live official documentation at execution time (the same
duty D-024-R147 imposed on the rebaseline) and reconcile any drift before scaffolding. Version
gates quoted below are from the snapshot and must be re-verified then.

## 2. What a Claude Code plugin can natively carry

Per the snapshot, a plugin is a self-contained directory bundling: **skills** (`skills/<name>/SKILL.md`),
**agents** (`agents/*.md`), **hooks** (`hooks/hooks.json`), **workflows**, **MCP servers**, **LSP
servers**, **monitors** (experimental), **themes** (experimental), legacy flat **commands**, plus
**`bin/`** executables and **`scripts/`** utilities, with an optional manifest at
`.claude-plugin/plugin.json` (`name` is the only required manifest field).

**There is no native "adapters" component type.** The D-024 "adapters" (unit C runtime adapter and
friends) therefore ship as ordinary plugin payload: a Python package under the plugin root invoked
through hook commands and documented skill commands (`${CLAUDE_PLUGIN_ROOT}` substitution), with
optional thin `bin/` wrappers. Note the snapshot's Windows caveat: `bin/` entries ride the Bash
tool PATH and depend on `bash` availability, so exec-form hook commands and explicit
`python -m ...` skill instructions are the primary invocation surface; `bin/` is a convenience
layer only.

Distribution starts as a **skills-directory plugin**: a folder under `~/.claude/skills/<name>/`
containing `.claude-plugin/plugin.json` loads as `<name>@skills-dir` with no marketplace or
install step. Marketplace packaging is a later, optional phase.

## 3. Reusable component inventory (built by units C-G)

Classification legend: **PORT** = generalize and include in the plugin; **PORT-LATER** = candidate
for a later plugin version; **STAYS** = remains in this repository (Section 5).

### Unit C - native runtime adapter (M0-T104)
| Artifact | Class | Notes |
|---|---|---|
| `tools/agent_supervisor/native_runtime.py` | PORT | Feature detection, native background dispatch, `claude agents --json` ingestion |
| `tools/agent_supervisor/runtime_backend.py` | PORT | Exactly-one-selected-backend seam |
| `tools/agent_supervisor/runtime_detectors.py`, `runtime_health.py`, `capability_probe.py` | PORT | Installed-version probing; generic by construction |
| `tools/agent_supervisor/claude_runner.py` | PORT | Existing controller fallback backend |

### Unit D - native event integration (M0-T105)
| Artifact | Class | Notes |
|---|---|---|
| `.claude/hooks/supervisor_event_recorder.py` | PORT | Hook-record capture; becomes a plugin hook via `hooks/hooks.json` |
| `tools/agent_supervisor/event_bus.py`, `event_stream.py`, `event_drift.py` | PORT | Dedup, atomic persistence, restart-safe replay, version-drift handling |
| `tools/agent_supervisor/redaction.py`, `replay.py` | PORT | Redaction before persistence; replay |

### Unit E - bounded /goal integration (M0-T106)
| Artifact | Class | Notes |
|---|---|---|
| `tools/agent_supervisor/goal_contract.py`, `goal_checkins.py`, `goal_outcomes.py` | PORT | One-bounded-assignment goal contract; generic |

### Unit F - safe-seam session succession (M0-T092)
| Artifact | Class | Notes |
|---|---|---|
| `tools/agent_supervisor/state_machine.py`, `epoch_lease.py`, `durable_state.py` | PORT | Loop state machine, lease/epoch, durable state |
| `tools/agent_supervisor/turnover_seam.py`, `turnover_controller.py`, `worker_turnover.py`, `rotation.py`, `handoff.py`, `child_handoff.py`, `launch_seam.py` | PORT | Seam/rotation/handoff machinery (rotation CEILING VALUES are policy and stay configurable, not hardcoded) |
| `tools/agent_supervisor/stop_intent.py`, `outage_policy.py`, `bootstrap_gate.py`, `circuit_breakers.py`, `loop_breakers.py` | PORT | Stop intents, outage policy, bootstrap gate, breakers |

### Unit G - thin operator interface (M0-T094)
| Artifact | Class | Notes |
|---|---|---|
| `.claude/skills/loop-start`, `loop-stop`, `loop-status`, `loop-pause`, `loop-resume`, `loop-tasks`, `loop-ask`, `loop-codex`, `loop-emergency-stop` (9 skills) | PORT | Zero-model-context operator surface; `disable-model-invocation: true` retained; repo-specific wording generalized |
| `.claude/hooks/loop_command_interceptor.py` | PORT | Pre-model interception of `/loop-*`; becomes a plugin hook |
| `tools/agent_supervisor/cli.py` (section-14 operator surface), `operator_status.py`, `operator_ask.py`, `operator_channel_cli.py`, `command_docs.py` | PORT | CLI the skills/hook call into |

### Cross-cutting supervisor payload
The remaining `tools/agent_supervisor/*.py` modules that the ported modules import (protocol,
models, config, locking, audit_log, telemetry_*, refusals, etc.) port with them as package
internals, EXCEPT the repo-coupled modules listed in Section 5. The extraction task must produce
an import-closure inventory and classify every module explicitly; this table is the seed, not the
final word.

### Governance hooks (partially generalizable)
| Artifact | Class | Notes |
|---|---|---|
| `.claude/hooks/readonly_agent_guard.py` | PORT-LATER | Read-only-reviewer enforcement is generically useful; needs de-NYC-ing (roster references out, config in) |
| `.claude/hooks/agent_dispatch_guard.py` | STAYS | Enforces this repo's roster/hold rules (G5-protected; expansion-hold rule) |
| `.claude/hooks/directive_reminder.py` | STAYS | D-001 directive-system coupling |

### Agents
The 25 `.claude/agents/*.md` definitions are NYC product/governance roster agents - **STAYS**.
The plugin's `agents/` directory ships at most two GENERIC archetypes written fresh for the
plugin (bounded producer, read-only independent reviewer), parameterized via plugin `userConfig`;
porting any NYC agent file is out of scope.

## 4. Proposed plugin shape

Working name `agent-loop-supervisor` (final name, license, and repo visibility are owner
decisions - Section 9).

```text
agent-loop-supervisor/
+-- .claude-plugin/plugin.json     # name, version, description; no Node deps
+-- skills/                        # 9 generalized loop-* operator skills
|   +-- loop-status/SKILL.md       #   (each keeps disable-model-invocation: true)
|   +-- ...
+-- agents/                        # 2 generic archetypes (producer, read-only reviewer)
+-- hooks/hooks.json               # UserPromptSubmit interceptor + lifecycle event recorder,
|                                  #   exec-form commands via ${CLAUDE_PLUGIN_ROOT}
+-- scripts/                       # hook entry points (python)
+-- supervisor/                    # the generalized Python package (ex tools/agent_supervisor)
+-- bin/                           # OPTIONAL thin wrappers (bash-dependent; convenience only)
+-- LICENSE, CHANGELOG.md, README.md
```

Deliberate exclusions, with reasons:

- **No MCP servers, no channels.** The D-024 amendment explicitly does not authorize enabling new
  MCP servers/channels; the generic plugin keeps that posture as its default. (The Telegram sink
  would require the MCP-based `channels` feature - PORT-LATER at most, behind its own review.)
- **No LSP servers, monitors, themes, workflows, output styles.** Nothing in units C-G needs them;
  monitors additionally run unsandboxed and are experimental.
- **No `package.json` and no lockfile.** The plugin payload is Python-stdlib-only (as the
  supervisor already is). Shipping no Node manifest keeps Claude Code's automatic
  `npm ci`/`bun install` machinery permanently inert - one less supply-chain surface, consistent
  with this repo's dependency-security posture (CLAUDE.md principle 15).
- **No state under the plugin root.** `${CLAUDE_PLUGIN_ROOT}` changes on every update and cached
  copies are ephemeral; durable loop state goes to the host project's state directory (default)
  or `${CLAUDE_PLUGIN_DATA}`, never the install directory.
- **No path traversal.** Copied plugins cannot reference `../` outside the plugin root; the
  package must be import-closed (the extraction inventory in Section 3 enforces this).

Configuration seam: `userConfig` in the manifest (repo root override, state directory, ledger
adapter command, model/rotation policy file). Snapshot caveat honored: shell-executed fields
reject `${user_config.*}`, so hook/monitor commands read `CLAUDE_PLUGIN_OPTION_<KEY>` environment
variables or a config file instead. Sensitive values (if any ever exist) ride the keychain path
and stay under its ~2 KB budget; the default plugin declares NO sensitive keys.

Version floor: the snapshot documents feature gates at v2.1.154/205/207/218/221/238/239/246. The
plugin targets the re-verified current stable at Phase-1 time and declares its floor in README;
boolean-frontmatter variants (v2.1.218+) are avoided by writing plain `true`/`false`.

## 5. What stays in this repository (R179 exclusion list, made concrete)

| R179 category | Concrete assets that never enter the plugin |
|---|---|
| NYC-specific graph | `tools/code_graph/**` and every graph artifact/index |
| Ledger | `project-control/**`, `tools/project_control.py`, `tools/validate_directive_compliance.py`, `tools/current_state.py`, directives, gates, checkpoints, blockers |
| Security policy | `docs/DEPENDENCY_SECURITY_POLICY.md`, `.claude/ORCHESTRATION_POLICY.md` (incl. section G), audit tooling, gitleaks wiring, owner-waiver machinery |
| Profiles | Owner/agent model-selection policy values, approved-model lists (`approved_models.py` VALUES), rotation-ceiling numbers, autonomy-tier assignments |
| Product rules | `CLAUDE.md`, `.claude/rules/**`, the 25 roster agents, expansion holds, PRD and all product docs |

The mechanism/policy split is the load-bearing idea: **mechanisms port, policy values stay.**
Example: rotation machinery ports; the ~400k rotate-at-seam ceiling is a configured value the NYC
repo sets locally. `approved_models.py` mechanics port as an allowlist engine; this repo's actual
allowlist remains local configuration.

## 6. Boundary design: ports the plugin defines, adapters hosts implement

The generic plugin must run without any NYC asset. Where the supervisor today touches this repo's
control plane, the plugin defines a narrow interface ("port") plus a minimal reference
implementation; each host repo supplies its own adapter.

| Port | Duty | Generic reference impl | NYC adapter (stays here) |
|---|---|---|---|
| LedgerPort | task facts, claim/progress/checkpoint records, acceptance state | flat-file JSON ledger under the state dir | `project_control.py`-backed adapter |
| PolicyPort | model allowlist, rotation ceilings, autonomy tiers, holds | TOML/JSON config file | NYC policy files + owner holds |
| ReviewPort | independent-review dispatch and verdict intake | checklist-file stub | Codex/gate reviewer wiring |
| EffectsPort | exactly-once external effects (GitHub etc.) | journal-file reference | `external_effects.py`/`github_flow.py` NYC config |

Unit H components (refusal bridge, repair gate, exact-once GitHub effects) are deliberately OUT of
the initial plugin scope: they were not named by R179 (which lists units C-G work), and they are
the most policy-entangled. They are PORT-LATER candidates behind the EffectsPort/ReviewPort seams.

## 7. Windows and portability notes

- All hook commands use exec form with `${CLAUDE_PLUGIN_ROOT}`-prefixed absolute paths (no shell
  quoting ambiguity; works with `cmd`/PowerShell/bash hosts).
- `bin/` wrappers are optional because they require `bash`; documented `python -m supervisor ...`
  invocations are the guaranteed path (mirrors today's `/loop-status` fallback wording).
- Symlink-based marketplace sharing is avoided entirely (Windows requires elevation or Developer
  Mode for `mklink /D`); the plugin is fully self-contained instead.
- Path handling in the ported package keeps the existing supervisor discipline (forward slashes
  accepted, no reliance on POSIX-only APIs); the extraction task inherits the supervisor's
  Windows-first test posture.

## 8. Proposed sequencing (all phases are proposals; none block D-024 activation)

| Phase | Content | Gate posture |
|---|---|---|
| 0 (this task) | This plan + producer report; no code | M0-T107 gates G0/G2/G3 |
| 1 | New separate private repository; copy-and-generalize extraction per Section 3 inventory; import-closure check; `claude plugin validate --strict` green; no NYC asset in payload | New ledger task(s); standard gates; owner creates the repo (ownership action) |
| 2 | Canary: install as `@skills-dir` plugin in a scratch repo; exercise the 9 skills, interceptor hook, event recorder, and a bounded goal run against the reference ports | New ledger task; standard gates |
| 3 (optional) | Marketplace packaging, versioning/tagging, `defaultEnabled: false` | Owner decision first |

Hard sequencing rules restated: Phase 1 may start only after the D-024 golden run has passed and
the activation campaign no longer competes for the same owner/orchestrator attention (R179
"after the local loop passes its golden run"); no phase is ever added as a dependency of any
D-024 activation-chain task; the frozen `tools/agent_supervisor/**` tree is read, never written.

## 9. Owner decisions required before Phase 1

1. Plugin name, license, and repository visibility (repo creation itself is an ownership action).
2. Whether `readonly_agent_guard` generalization is in the v1 payload or PORT-LATER.
3. Whether any distribution beyond `@skills-dir` (marketplace) is wanted at all.
4. Timing: which milestone slot, given portability is OPTIONAL ENHANCEMENT and must not displace
   product work.

## 10. Risks

| Risk | Mitigation |
|---|---|
| Docs drift since the 2026-08-26 snapshot | Phase-1 re-fetch duty (Section 1) |
| Hidden NYC coupling inside "generic" modules | Import-closure inventory + a payload scan gate: zero references to `project-control`, `code_graph`, NYC policy values |
| Plugin update semantics vs durable state | State lives outside `${CLAUDE_PLUGIN_ROOT}` (Section 4) |
| Supply-chain exposure via plugin auto-install | No Node manifest ever ships (Section 4) |
| Divergence between in-repo supervisor and plugin copy | Plugin CHANGELOG records the source tree-hash it was extracted from; resync is a deliberate, task-gated act |
| Scope creep into activation work | Non-blocking rules in Sections 0 and 8; any violation is a gate FAIL |

## 11. Explicit non-authorizations

This plan does NOT: create ledger tasks; modify the master plan; authorize edits to
`tools/agent_supervisor/**`, `.claude/hooks/**`, `.claude/skills/**`, or any settings file;
authorize MCP servers, channels, monitors, or the Claude Agent SDK; alter any D-024 activation,
hold, or touch-budget state; or place any new obligation on the local loop's commissioning.
