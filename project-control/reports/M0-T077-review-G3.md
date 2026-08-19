<!-- Orchestrator preservation note (report-preservation rule, 2026-07-16): the review
below was returned through the agent-return channel by the independent read-only
G3 reviewer and is saved VERBATIM (transport entity-decoding only). Received
2026-08-19. Verdict: FAIL. The orchestrator recorded gate G3 FAIL at the frozen
submission identity (reviewed SHA 90ea22f5, content manifest d9f9ac65) and moved
the task to rework. Everything below this line is the reviewer's text. -->

# G3 Independent Adversarial Code Review — M0-T077 (D-020 MCP default-deny)

**Reviewer:** code-reviewer (independent, read-only)
**Substantive identity reviewed:** `eb742f2eb89c64938902c898bacab86e4919288e` (enforcement artifacts unchanged since)
**HEAD at close of review:** `2d8173d8bc2b6366a362bbf33b2aee51db180312`
**Base:** `31c50a09bd1671d111f21923c6a2d739f51187dd`
**Worktree:** `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m0t077`

## VERDICT: **FAIL**

The implementation is good work — minimal, officially-supported, and I independently reproduced its effect from fresh processes. `eb742f2`'s deny-first addition is a real improvement, and I confirmed behaviorally that it does what it claims. The gate fails on one blocking finding: **an ordinary session started one directory deep inside the repository gets live Supabase production-database tools.** The committed evidence asserts the opposite.

I modified nothing in the repository; `git status` in the worktree is clean. All fixtures were created under my OS temp scratchpad plus a throwaway `C:\g3probe-outside*` pair that I deleted.

---

## Direct answer to the p8 question you raised

**Yes — p8 can be satisfied while being completely neutered, though not by gaming the deny list itself.**

The deny-list check is tight: `"mcp__*" in deny_rules` is an exact list-element match, so it cannot be satisfied by a substring, a narrowed rule (`mcp__supabase__*`), reordering, or an empty list — I tested all four and the validator correctly rejects the weakened ones. Adding `allow: ["mcp__*"]` alongside the deny, or junk sibling keys, does not weaken the outcome either.

The hole is one level up. `permissions` is a **schema-validated object**, and putting an invalid value in a *sibling* field — `permissions: {"deny": ["mcp__*"], "defaultMode": "notARealMode"}` — makes Claude Code **discard the entire settings file**. All four unrelated servers return, and `validate_mcp_policy.py` exits 0 printing *"policy intact."* So `eb742f2` did not just add a protective layer; it **widened the F-2 attack surface** by introducing a new nested enum field where a typo silently voids the whole policy with green CI.

Separately, and to `eb742f2`'s credit: I verified the deny rule is **behaviorally real**. With pencil explicitly allowlisted and connected, a headless session asked whether it had `mcp__pencil*` tools answered **NO** with the deny rule and **YES** without it — and it still answered **NO** under `defaultMode: "bypassPermissions"`. The deny-first layer genuinely removes MCP tools and survives bypass mode. The caveat text is accurate.

---

## 1. Probes executed

All `claude mcp list` / `claude -p` runs were prefixed with an environment scrub (`$STRIP`) so probes could not inherit this session's state:

```
env -u CLAUDECODE -u CLAUDE_CODE_ENTRYPOINT -u CLAUDE_CODE_SESSION_ID \
    -u CLAUDE_CODE_CHILD_SESSION -u CLAUDE_CODE_BRIDGE_SESSION_ID \
    -u CLAUDE_PID -u CLAUDE_EFFORT
```

`$PROBE` = `C:/Users/MLFLL/AppData/Local/Temp/claude/C--Users-MLFLL/a0cd3da1-a009-41dc-9f90-0e67e53f4f86/scratchpad/g3probe`; `$WT` = the worktree; CLI 2.1.220.

### Enforcement probes (fresh `claude mcp list` processes)

| # | Command (cwd) | Result |
|---|---|---|
| 1 | `$PROBE/p1-baseline`, no settings | Airtable OK, M365 needs-auth, pencil OK, supabase OK — **control reproduces the audit** |
| 2 | `$PROBE/p2-policy`, policy verbatim | `No MCP servers configured.` |
| 3 | `$PROBE/p3a-local-aggressive` — policy + `settings.local.json` with `disableClaudeAiConnectors:false`, allowlist of all four, `deniedMcpServers:[]`, `disabledMcpjsonServers:[]`, `enableAllProjectMcpServers:true` | `No MCP servers configured.` — **nothing returned** |
| 4 | `$PROBE/p3b-local-minimal` — minimal local override | `No MCP servers configured.` |
| 5 | `$PROBE/c1-localonly` — **control**: policy placed only in `settings.local.json` | `No MCP servers configured.` — file IS read, so 3–4 are real negatives |
| 6 | `$PROBE/p4-allowlist-only` — `{"allowedMcpServers": []}` alone | `No MCP servers configured.` — **empty allowlist alone is deny-all** |
| 7 | `$PROBE/p5-newserver` — policy + `.mcp.json` with unaudited `probe-brand-new` | blocked |
| 8 | `$PROBE/c2-mcpjson-nopolicy` — **control**, same `.mcp.json`, no policy | `probe-brand-new` loaded — 7 is a real negative |
| 9 | `$PROBE/p6-case` — `.mcp.json` with `SupaBase`, `PENCIL`, `Sequential-Thinking` | blocked — case variants do not bypass |
| 10 | `claude --mcp-config extra.json mcp list` | `Error: Invalid MCP configuration` (variadic flag ate the subcommand) — **not tested**, see §3 |
| 11 | `$PROBE/p11-dupkeys` — duplicate JSON keys, weakening value first | blocked — Claude and Python agree on last-wins; **no bypass** |
| 12–18 | `$PROBE/p12*`, `p13*` — type mutations, each with validator + list | see F-2; only `model` non-string and `fallbackModel` non-array discard the file; stderr = **0 bytes** |
| 19 | validator vs `$PROBE/p14-hookdecoy` (all three guard hooks deleted, names left in an inert `echo`) | exit 0, *"pre-existing settings preserved"* — see F-3 |
| 20 | `$WT` (worktree **root**) | `No MCP servers configured.` |
| 21 | `$WT/tools` | **Airtable, M365, pencil, supabase all connected** |
| 22 | `$WT/project-control` | **all four connected** |
| 23 | `$PROBE/v3-parent/sub/deeper` — plain non-git tree, policy at parent | **all four connected** |
| 24 | `$PROBE/v3-parent` — **control**, same tree at root | blocked |
| 25–26 | `$PROBE/v2-policy`, `$PROBE/v2-local-override` — blob from `git show eb742f2:.claude/settings.json` | blocked in both |
| 27–28 | `C:/g3probe-outside` (outside user profile) + control | policy blocks; control shows 3 servers, supabase absent — corroborates the audit's ancestor-pickup claim |

### p8 / `permissions` bypass hunt (new surface from `eb742f2`)

Each fixture = the `eb742f2` policy with `permissions` overridden.

| # | Fixture | Validator | `claude mcp list` |
|---|---|---|---|
| 29 | `{"deny":["mcp__*"],"allow":["mcp__*"]}` | PASS | blocked |
| 30 | `{"deny":["mcp__*"],"defaultMode":"bypassPermissions"}` | PASS | blocked |
| 31 | `{"deny":["mcp__*"],"defaultMode":"notARealMode"}` | **PASS** | **all four connected — whole file discarded** |
| 32 | `{"deny":["WebFetch","Bash","mcp__*"]}` | PASS | blocked |
| 33 | `{"deny":["mcp__*"],"additionalDirectories":[...],"ask":["mcp__supabase__*"]}` | PASS | blocked |
| 34 | `{"deny":["mcp__supabase__*"]}` (narrowed) | FAIL — correctly caught | n/a |
| 35 | `{"deny":[]}` and `permissions` removed entirely | FAIL — correctly caught | n/a |
| 36 | `allowedMcpServers:[pencil]` + `deny:["mcp__*"]` | FAIL (expected; other invariants dropped) | **pencil connected** — deny does not stop connection |

### Tool-exposure probes (headless `claude -p`, the layer `mcp list` cannot see)

Prompt: *"Do you have any tool whose name begins with `mcp__<server>`? Reply with ONLY one word: YES or NO."*

| # | cwd / fixture | Answer |
|---|---|---|
| 37 | `$PROBE/b7-control-nodeny` — pencil allowlisted, **no** deny rule | **YES** |
| 38 | `$PROBE/b6-connect-vs-tooluse` — pencil allowlisted **+** `deny:["mcp__*"]` | **NO** — deny rule genuinely removes the tools |
| 39 | `$PROBE/b8-bypassmode-live` — same **+** `defaultMode:"bypassPermissions"` | **NO** — bypass mode does **not** neuter the deny |
| 40 | `$WT` (worktree root), asking for `mcp__supabase` | **NO** |
| 41 | `$WT/tools` (subdirectory), asking for `mcp__supabase` | **YES** — live Supabase tools exposed |

### Static / contract probes

| # | Check | Result |
|---|---|---|
| 42 | `yaml.safe_load(ci.yml)` + step enumeration | Parses; 18 jobs; both new steps are the **last two steps of the existing `control-plane` job**; no new job |
| 43 | `git diff --name-status 31c50a09..HEAD` | Only `.github/workflows/ci.yml` among workflows; **no other workflow or test file touched** |
| 44 | Containment vs frozen `allowed_paths`/`forbidden_paths` | `eb742f2`: 17 files, all allowed, zero forbidden. HEAD: 20 files, **one outside** (F-4) |
| 45 | Key-by-key `31c50a09` vs `eb742f2` settings | `$schema`, `model`, `fallbackModel`, `effortLevel`, `env`, `hooks` all **value-identical**; purely additive |
| 46 | `sed -n` at every citation in the supervisor report | All accurate (F-INFO-2) |
| 47 | `grep -rn -- "--settings\|--mcp-config\|--strict-mcp-config" tools/agent_supervisor/` | No matches — claim holds |
| 48 | Regex secret sweep over the 143,761-byte diff | Clean (F-INFO-3) |
| 49 | `gh api repos/:owner/:repo/branches/main/protection` | HTTP 404 **"Branch not protected"** (F-6) |

---

## 2. Findings

### F-1 — BLOCKING: sessions started in a repository subdirectory get the full connector set, including live Supabase tools

Claude Code resolves `.claude/settings.json` from the **current working directory only**; it does not walk up to a project or git root. Probes 21–22 show a fresh process in `wt-m0t077/tools` or `wt-m0t077/project-control` connecting to Airtable, Microsoft 365, pencil, and supabase. Probe 41 escalates this from "listed" to "usable": a headless session started in `$WT/tools` reports **YES**, it has `mcp__supabase*` tools — i.e. `execute_sql`, `apply_migration`, and the rest against the program's production datastore. From the worktree root the same question returns **NO** (probe 40). Probes 23/24 reproduce the asymmetry in a plain non-git tree, so this is cwd-based settings resolution, not a git-worktree artifact.

`eb742f2`'s deny-first layer does **not** mitigate this: in a subdirectory the settings file is never read at all, so `permissions.deny` is never in effect. Probes 21, 22, and 41 were all run at `eb742f2` or later.

This falsifies, as written:

- **D-020-R024** — "The policy must apply to fresh ordinary Claude Code sessions opened from this repository and its clean worktrees." A session opened in `repo/tools` is opened from this repository.
- **D-020-R020 / AS-1** — "every ordinary Claude Code session … defaults to NO unrelated external MCP server active."
- `M0-T077-fresh-session-proof.md` §5: *"The policy governs sessions launched from THIS repository and its worktrees. Sessions launched elsewhere … are outside repository-scope authority by design."* A subdirectory of this repository is not "elsewhere," yet it is unprotected.
- `docs/MCP_DEFAULT_DENY_POLICY.md` "Honest enforcement boundary," which enumerates the boundary and omits this case.

Every run in the committed proof (A, B, C, D, E) is a worktree **root**, so the evidence set has a systematic blind spot rather than a contradicting datapoint. `grep` for "subdirector", "cwd", or "working directory" across the proof and policy doc returns only the supervisor sentence.

The implementation is not wrong — it is as strong as a project-scope setting can be. The claims and the evidence are broader than reality, and D-020 item 6 anticipates exactly this: *"If one type of MCP server cannot be blocked through a supported repository-level mechanism … Report the exact limitation and the smallest owner-gated next step."* That was done properly for the supervisor gap and not for this one.

**Correction (documentation, not code):** disclose the subdirectory case in both the policy doc's enforcement boundary and the proof's limitations, with a subdirectory probe as committed evidence; correct the §5 sentence that currently asserts the opposite; record the smallest owner-gated next step. Note the genuine mitigation established in F-INFO-2 — supervised workers launch with `cwd` set to the worktree **root**, so agent sessions are covered and the residual is human sessions started one level down. Do **not** fix this by scattering `.claude/settings.json` into subdirectories; that breaches the "smallest supported policy" constraint.

### F-2 — MAJOR: validator bypass — a type or enum error in `model`, `fallbackModel`, or `permissions.defaultMode` silently voids the entire policy while CI stays green

A settings file with all eight invariants perfectly intact, but one schema-invalid value, causes Claude Code to **discard the whole file**. All four servers return, `validate_mcp_policy.py --check` exits **0** printing *"MCP default-deny policy intact … pre-existing settings preserved,"* and **nothing is written to stderr** (probe 18: zero bytes). Three confirmed triggers:

- `model` non-string (probes 13, 16)
- `fallbackModel` a string instead of the committed array (probe 17) — the realistic one: "simplifying" `["claude-opus-4-8"]` to `"claude-opus-4-8"` is the shape most people would write
- `permissions.defaultMode` not a valid enum member (probe 31) — **new surface introduced by `eb742f2`**

I verified the exposure is specific, not open-ended: `effortLevel` as an array, `env: {}`, non-string `env` values, unknown top-level keys, and `deniedMcpServers` entries carrying an extra `toolName` key are all tolerated and do not weaken enforcement (probe 15). The gap is that `PRESERVED_KEYS` checks **presence only**, never type, and nothing checks `permissions` beyond the deny list.

This defeats the objective's "smallest durable CI validation that detects removal or weakening of the policy." AS-5 enumerates "settings file unparseable"; these files parse perfectly and are still discarded wholesale by the consumer.

Fix is a few lines in the existing p7 loop, no new dependency:

```python
if not isinstance(settings.get("model"), str): errors.append(...)
if not isinstance(settings.get("fallbackModel"), list): errors.append(...)
mode = (settings.get("permissions") or {}).get("defaultMode")
if mode is not None and mode not in {"default","acceptEdits","plan","bypassPermissions"}: errors.append(...)
```

### F-3 — MINOR: p7's hook check is a substring match, so a decoy passes as "preserved"

`validate_mcp_policy.py:117-120` does `hooks_blob = json.dumps(settings.get("hooks", {}))` then `if hook not in hooks_blob`. A file with **all three** control-plane guard hooks deleted, their filenames surviving only inside an inert `"command": "echo disabled: agent_dispatch_guard.py readonly_agent_guard.py directive_reminder.py"`, passes with exit 0 and the message "pre-existing settings preserved" (probe 19). MCP enforcement is unaffected — p2–p6 and p8 are exact-value checks — but the AS-4 backstop is weaker than it reads. Checking that each filename appears inside a `command` value of a registered entry would close it.

### F-4 — MINOR: one file at HEAD is outside the frozen `allowed_paths`

`project-control/reports/M0-T077.json` was added by `703e4dd` and is not among the 27 `allowed_paths` entries; the packet's `allowed_paths` was not amended (only `status: claimed → awaiting_gate` and `progress_percent: 10 → 85`). In fairness it is a standard control-CLI submission artifact — 96 such `M<n>-T<n>.json` files already exist — so this is contract-drafting omission, not a producer scope breach. The orchestrator should amend `allowed_paths` or record the CLI-artifact exception, since G3's containment criterion is violated exactly as written. At `eb742f2` containment was clean.

### F-5 — MINOR (process): the artifact moved during the gate

HEAD was `309e202` when I began; `eb742f2`, `90ea22f`, `703e4dd`, and `2d8173d` landed mid-review, and an uncommitted edit to `M0-T077-fresh-session-proof.md` was briefly present. I re-anchored by extracting the settings blob with `git show eb742f2:` (probes 25–26) and confirmed via `git diff --name-status eb742f2..HEAD` that `.claude/settings.json`, both tools, and `ci.yml` are **unchanged** since `eb742f2` — so every enforcement finding stands at HEAD. Flagging it because this repository has already had to correct a gate recorded against a moving target (`93c80fb M0-T076 re-accepted at corrected identity`). Whatever gate is recorded must name a frozen sha.

### F-6 — MINOR: the "blocks merge" comment in `ci.yml` is not currently true

`.github/workflows/ci.yml:451-452` says the steps were added *"so removing or weakening the policy blocks merge (connected check; no branch-protection change needed)."* Probe 49 returns HTTP 404 **"Branch not protected"** for `main`, so no status check blocks a merge today. The wording is copied verbatim from the pre-existing D-001 comment block directly above it, so it is an inherited inaccuracy rather than a new claim, and the step placement is correct.

### F-INFO-1 — What passed, verified independently

- The policy **works** at worktree root: probes 2, 20, 25, 27, 40 all clean against a control (1, 28) reproducing the audit exactly.
- `settings.local.json` **cannot** re-enable any audited server (3, 4), and probe 5 proves that file is genuinely read — real negatives, not an ignored fixture.
- `allowedMcpServers: []` is deny-all on its own (6) and blocks brand-new (7 vs 8) and case-variant (9) servers.
- **`eb742f2`'s deny-first layer is behaviorally real** (37 vs 38): it removes `mcp__*` tools from the model's toolset even while the server is connected, and it survives `defaultMode: "bypassPermissions"` (39). Its deny-list check resists narrowing, reordering, emptying, and `allow` alongside it (29–35).
- Duplicate JSON keys are not a bypass — Claude and Python agree on last-wins (11).
- Settings preservation is exact: all six base keys value-identical, diff purely additive (45). AS-4's substance is met.
- CI wiring is correct: both steps in the **existing** required `control-plane` job, no new job, valid YAML, no other workflow or test touched (42, 43). `tools/agent_supervisor/**` has zero changed lines.

### F-INFO-2 — Supervisor-compatibility citations are accurate

Verified read-only: `cli.py:2686-2689` is `RunnerConfig(executable=..., cwd=str(worktree), ...)`; `turnover_adapters.py:404-412` is `cwd=self._targets.checkout`; `preflight.py:91` is `RunnerConfig(..., cwd=cwd)`; `claude_runner.py:1085` is `subprocess.Popen(argv, shell=False, cwd=self.config.cwd or None, env=env, ...)`; `broker.evaluate_request` is at `claude_runner.py:1696`, inside the cited range; no `--settings`/`--mcp-config`/`--strict-mcp-config` anywhere in the package. The conclusion is sound and the "no live launch performed" declaration is appropriate. This is also what bounds F-1: supervised workers start at the worktree root.

### F-INFO-3 — No secret exposure; one CLI-message oddity

The diff is clean for the full Supabase project ref, `sb_`/`sbp_` tokens, JWTs, GitHub tokens, `sk-` keys, DB URIs, and `SUPABASE_ACCESS_TOKEN` values. Reports truncate the ref to `dyiv…` and say so. The only private absolute path is `"worktree": "C:/Users/MLFLL/..."`, the convention in all 96+ task packets. I deliberately keep the full project ref out of this report though my probe output displayed it.

Minor observation for future operators: when `allowedMcpServers` blocks claude.ai connectors, the CLI reports *"claude.ai MCP servers blocked by enterprise policy"* even though no managed settings exist on this machine (probes 37–39). Confirms the allowlist is enforced; the wording could mislead someone debugging later.

---

## 3. What I could not test, and why

1. **Whether a user-scope `allowedMcpServers` entry can broaden the empty project allowlist.** Requires writing to the owner's `~/.claude/settings.json`, which D-020 items 5–6 prohibit. The caveat is documented honestly and mitigated by `permissions.deny`, whose effectiveness I *did* confirm (probes 37–39) — but the broadening premise itself rests on documentation, not measurement.
2. **Managed/enterprise settings precedence.** No `managed-settings.json` exists; creating one is an owner-machine action.
3. **Command-line `--mcp-config` injection** (probe 10). The flag is variadic and consumed my subcommand; I found no working invocation. Low relevance since the supervisor demonstrably never passes it (probe 47), but it is a genuine gap.
4. **A live supervised worker launch.** Owner-present only under D-018/D-019; correctly declared as an owner-gated residual by the producer.
5. **CI actually executing the new steps on GitHub.** I read and parsed the workflow; I did not trigger or observe a run.
6. **Unicode homoglyph identifiers.** Reasoned, not executed: the validator compares against exact ASCII literals, so a homoglyph makes the check *fail* — the fail-closed direction, which cannot weaken the policy. Flagging the judgment rather than hiding it.
7. **Interactive (non-`-p`) session behavior.** My evidence is fresh processes and headless runs. Probes 40/41 differ only in cwd, so F-1 is not a medium artifact — but it is not interactive-session evidence.

---

## 4. Required corrections before G3 can pass

1. **F-1 (blocking):** disclose the subdirectory limitation in `docs/MCP_DEFAULT_DENY_POLICY.md` and `M0-T077-fresh-session-proof.md`, with a subdirectory probe as committed evidence; correct the proof's §5 sentence; record the smallest owner-gated next step; note the supervisor-root mitigation.
2. **F-2 (major):** add type/enum assertions for `model`, `fallbackModel`, and `permissions.defaultMode`, with regressions proving a schema-invalid preserved key fails the validator.
3. **F-4, F-5 (minor):** amend `allowed_paths` (or record the CLI-artifact exception) for `project-control/reports/M0-T077.json`, and record the gate against a frozen sha.
4. **F-3, F-6 (minor, orchestrator's discretion):** tighten p7's hook check to inspect registrations rather than a JSON substring; correct the "blocks merge" comment given `main` is unprotected.
