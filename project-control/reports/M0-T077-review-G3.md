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


---
---

<!-- Orchestrator preservation note: RE-REVIEW below, returned through the
agent-return channel by the same independent read-only G3 reviewer after the
rework, saved VERBATIM (transport entity-decoding only). Received 2026-08-19.
Verdict: PASS with required corrections — recorded as gate G3 PASS per the
gate-verdict semantics rule; the section-4 corrections are BLOCKING for the
next gate and for acceptance. Everything below is the reviewer's text. -->

# G3 Re-Review — M0-T077 (D-020 MCP default-deny), corrected identity

**Reviewer:** code-reviewer (independent, read-only)
**Identity re-reviewed:** `9e5c8221f87f4e975bbcdb6dcf778a45a1ad2338`
**Branch head checked:** `002ffc39405ca3992831b4b0d95f3f670e990a30`
**Prior verdict:** FAIL at `90ea22f5` (1 BLOCKING, 1 MAJOR, 4 MINOR)

## VERDICT: **PASS with required corrections**

Per `.claude/rules/project-control.md` gate-verdict semantics this is recorded as **PASS**, and the corrections in §4 are **BLOCKING for acceptance and for the next gate**.

**The BLOCKING finding F-1 is fully and accurately remediated.** I re-verified the disclosure text against my own measurements rather than taking it on trust: it is precise, it does not overclaim, the old "elsewhere" sentence is gone, the mitigation is real, and the owner-gated next step is recorded. F-3 is fully closed and its documented residual is *verifiably* honest — I checked the mechanism it defers to and it does hold. F-4 is clean at both commits. F-6 is corrected in `ci.yml`.

**F-2 is not closed as a class.** The three shapes I reported are now guarded and I confirmed each of my original bypass fixtures fails. But the guard is an enumeration of the shapes I happened to find, and in one fuzzing pass I found **five more** schema-invalid shapes that pass p1–p9 while Claude Code silently discards the whole settings file — including one that defeats the newly added `fallbackModel` guard from the inside. That does not block this gate (the shipped policy artifact is byte-identical to the one I already proved works) but it must be closed before acceptance, and the fix should be structural rather than another three entries.

I modified nothing in the repository; `git status` is clean. Fixtures live only in my OS temp scratchpad.

---

## 1. Item 6 first — enforcement artifacts are unchanged, so my passing probes still stand

`.claude/settings.json` is the **same blob** at all three commits:

```
git rev-parse eb742f2:.claude/settings.json 9e5c8221:.claude/settings.json 002ffc3:.claude/settings.json
dd11cd79e01f309c524f00906ff1266de439a287   (x3, identical)
```

So probes 1–41 from the first review carry over unchanged: the policy blocks all four servers at worktree root, `settings.local.json` cannot re-enable anything, the empty allowlist is deny-all, and the deny-first `mcp__*` rule genuinely strips MCP tools from the model's toolset. Equally, my F-1 subdirectory measurements still describe the shipped artifact — which is exactly what the new disclosure now says.

`git diff --name-status 9e5c8221..002ffc3` touches only `project-control/reports/M0-T077.json`, `state.json`, and `tasks/M0-T077.json` — control-plane records only, as you described.

---

## 2. Probes executed (continuing the numbering from my first report)

`$STRIP` is the same environment scrub as before; `$WT` = the worktree; `$PROBE` = my temp scratchpad.

### F-2 regression — my original bypass fixtures against the NEW validator

| # | Fixture (unchanged from first review) | Old result | New result |
|---|---|---|---|
| 50 | `p12-badtype` (`model:12345`, `env:{}`, `effortLevel:[...]`) | PASS (bypass) | **FAIL** — `p9 model must be a string … (found: int)` |
| 51 | `p12a-model-number` | PASS (bypass) | **FAIL** — same p9 message |
| 52 | `b3-invalid-mode` (`defaultMode:"notARealMode"`) | PASS (bypass) | **FAIL** — `p9 permissions.defaultMode must be one of (...)` |
| 53 | `p13b`, `p13c` (minimal fixtures) | PASS | **FAIL** (on p2/p4 — these fixtures never carried the full policy; superseded by probe 61) |
| 54 | `p14-hookdecoy` (F-3 echo decoy) | PASS (bypass) | **FAIL** — `p7 … disappeared (no registered hook command references .claude/hooks/agent_dispatch_guard.py)` |

### F-2 completeness — is every value the validator *admits* actually safe?

`VALID_DEFAULT_MODES = ("default", "acceptEdits", "plan", "bypassPermissions")`. The source comment says these were "PROVEN accepted by the consumer (G3 probes 30-31)" — I had actually only proven `bypassPermissions`, so I tested all four:

| # | `permissions.defaultMode` | Validator | Consumer (`claude mcp list`) |
|---|---|---|---|
| 55 | `"default"` | PASS | blocked |
| 56 | `"acceptEdits"` | PASS | blocked |
| 57 | `"plan"` | PASS | blocked |
| 58 | `"bypassPermissions"` | PASS | blocked |

**No admitted mode discards the file.** The enum list is safe, and the fail-closed posture for unlisted values is the right call.

### F-2 completeness — hunting NEW discard shapes that still pass p1–p9

Each fixture is the committed `9e5c8221` settings with one key overridden.

| # | Shape | Validator | Consumer | Verdict |
|---|---|---|---|---|
| 59 | `permissions.allow: "not-a-list"` | **PASS** | **file discarded, all servers returned** | **NEW BYPASS** |
| 60 | `env: "not-an-object"` | **PASS** | **file discarded** | **NEW BYPASS** |
| 61 | `fallbackModel: [123]` (list of non-strings) | **PASS** | **file discarded** | **NEW BYPASS — defeats the new p9 guard from inside** |
| 62 | `$schema: 12345` | **PASS** | **file discarded** | **NEW BYPASS** |
| 63 | `cleanupPeriodDays: "thirty"` | **PASS** | **file discarded** | **NEW BYPASS** |
| 64 | `fallbackModel: "claude-opus-4-8"` (string) | **FAIL** (p9) | file discarded | guard works ✓ |
| 65 | `effortLevel: "ultra"` (invalid enum string) | PASS | blocked | tolerated, no issue |
| 66 | `model: "not-a-real-model-id"` | PASS | blocked | tolerated, no issue |
| 67 | `permissions.deny: ["mcp__*", 123]` | PASS | blocked | tolerated, no issue |
| 68 | `deniedMcpServers` entries with nested non-string extras | PASS | blocked | tolerated, no issue |
| 69 | `hooks: []` | FAIL (p7) | blocked | fail-closed ✓ |

### F-3 — tightened hook check and the honesty of its residual

| # | Check | Result |
|---|---|---|
| 70 | `p15-pathdecoy` — all three guards deleted, but the command string contains the literal full paths `.claude/hooks/agent_dispatch_guard.py` etc. | Validator **PASSES** — matches the residual documented in the source comment |
| 71 | Does the deferred-to mechanism actually hold? Read `tools/test_readonly_agent_guard.py:108-126` and `tools/test_directive_reminder.py:163-175` | **Yes.** `check_settings_commands()` requires *every* hook command in `.claude/settings.json` to be the canonical `python "${CLAUDE_PROJECT_DIR}/.claude/hooks/<x>.py"` form, shlex-split against a space-containing synthetic root and resolved to an existing hook file — an `echo …` decoy fails it. `test_settings_json_valid_and_hooks_wired` additionally asserts the reminder is wired on **both** `SessionStart` and `UserPromptSubmit`. Both run in the same control-plane job. |

The comment's claim — *"a command crafted to contain the exact path still satisfies it; the behavioral guarantee comes from the hook test suites the same CI job runs"* — is accurate and I verified the deferral target rather than accepting it. **F-3 closed, residual honest.**

### F-1 — disclosure accuracy

| # | Check | Result |
|---|---|---|
| 72 | `grep -rn "elsewhere"` across the policy doc and proof | **no match** — the old overclaim is gone |
| 73 | Subdirectory disclosure present | policy doc 3 hits, proof 4 hits |
| 74 | Read the "Honest enforcement boundary" section | Accurate: names cwd-only resolution, gives `<repo>/tools` as the example, states "including live Supabase tools", cites Runs F/G, states the supervisor-root mitigation, warns against scattering settings files, and records the owner-gated next step (owner-installed managed settings, deliberately not performed) |
| 75 | Read proof Runs F/G and corrected §5 | Run F (subdirectory, full ambient set) and Run G (same worktree root, control) match **exactly** what I measured in my probes 21/22 vs 20. §5 now reads "started at the ROOT … Sessions started in a SUBDIRECTORY … load no project settings at all" |
| 76 | Does the proof credit the tool-exposure evidence correctly? | Yes — cites the reviewer's probes 40/41 for the `mcp__supabase*` finding rather than restating it as its own |

The first bullet of the boundary section was also rewritten from "launched from this repository and its worktrees" to "launched **from the ROOT of** this repository or one of its worktrees" — the precise correction needed. No remaining sentence overclaims the scope.

### F-4, F-6, and general health

| # | Check | Result |
|---|---|---|
| 77 | Containment vs frozen `allowed_paths` at `9e5c8221` | 22 changed files, **outside allowed: NONE**, forbidden: NONE |
| 78 | Containment at branch head `002ffc3` | 22 changed files, **outside allowed: NONE**, forbidden: NONE |
| 79 | `python tools/test_mcp_policy.py` | OK; six new tests added: `test_hook_decoy_substring_fails`, `test_hook_names_in_noncommand_field_fail`, `test_model_wrong_type_fails`, `test_fallback_model_string_fails`, `test_invalid_default_mode_fails`, `test_valid_default_mode_passes` |
| 80 | `python tools/validate_mcp_policy.py --check` on the real committed settings | exit 0 |
| 81 | `ci.yml` MCP comment | **Corrected**: now says the steps "fail this job on every push and PR" and adds "(Failing checks gate merges only to the extent branch protection requires them — a pre-existing repository setting this task does not change; G3 F-6.)" — accurate and honest |
| 82 | `grep -rn "blocks merge"` across this task's artifacts | Still present in `docs/MCP_DEFAULT_DENY_POLICY.md:89` and `project-control/reports/M0-T077-submission.md:43` (see F-6-residual). `ci.yml:439` is the pre-existing D-001 comment, not this task's |
| 83 | G3 FAIL gate record + verbatim preservation | `gates/M0-T077-G3.json` records `result: FAIL`, reviewer `code-reviewer`; `reports/M0-T077-review-G3.md` carries a preservation header and my text below it |

---

## 3. Findings

### F-1 — RESOLVED (was BLOCKING)
Disclosed accurately in both documents, evidence committed as Runs F/G matching my independent measurements, mitigation stated correctly, owner-gated next step recorded, no surviving overclaim. Probes 72–76.

### F-2-residual — MAJOR (carried forward, not closed as a class)
The three reported shapes are guarded and verified (probes 50–52, 64), and the admitted enum values are all consumer-safe (55–58). But p9 enumerates shapes rather than asserting one, and I found five more live bypasses in a single pass (probes 59–63). The most telling is **probe 61**: `fallbackModel: [123]` passes the brand-new `isinstance(x, list)` guard because the guard never checks element types, and the consumer still discards the file. **Probe 59** (`permissions.allow: "not-a-list"`) is the most realistic in practice — writing a single allow rule as a bare string instead of a one-element list is an ordinary mistake, and it would silently void the entire MCP policy with green CI.

Enumerating five more shapes is the wrong fix; it is the same whack-a-mole with a longer stick. The settings file is small (12 top-level keys) and changes rarely, so the structurally complete and *smaller* fix is a **whole-file shape assertion**: every key present must be a known key and match its expected type — including element types for list-valued keys and a recursive type check for `env` and `permissions` sub-keys — with anything unrecognized failing closed. That converts an open-ended "which shape discards?" question into a closed "is the file still exactly the expected shape?" check, and it would have caught all eight shapes I have now demonstrated without my having to find them first.

### F-6-residual — MINOR (partially closed)
`ci.yml` is corrected and now states the boundary honestly (probe 81). Two of this task's own artifacts still assert merge-blocking that branch protection does not provide (probe 82):
- `docs/MCP_DEFAULT_DENY_POLICY.md:89` — *"so accidental removal or weakening of the policy blocks merge."* This sentence also claims the validator "asserts every invariant above", which F-2-residual shows is broader than reality.
- `project-control/reports/M0-T077-submission.md:43` — *"Runs the validator + tests on every push/PR so weakening blocks merge (R029)."*

### F-3 — RESOLVED (was MINOR)
Path-anchored registration check works, my original decoy now fails, and the documented residual defers to a mechanism I verified actually exists and would catch the stronger decoy. Probes 54, 70, 71.

### F-4 — RESOLVED (was MINOR)
`project-control/reports/M0-T077.json` is now in `allowed_paths`; containment is clean at both `9e5c8221` and `002ffc3`. Probes 77–78.

### F-5 — RESOLVED (was MINOR, process)
The re-review was performed against a stated frozen identity, the enforcement blob is provably unchanged across it, and the prior FAIL gate is recorded with the review preserved verbatim under a truthful preservation header. Probes 50, 83.

### INFO — quality of the rework
The validator's new docstring is careful: it says "Guarded shapes (each reproduced by the G3 adversarial review, F-2)" rather than claiming completeness, and the `VALID_DEFAULT_MODES` comment explicitly chooses visible failure over silent admission. The six new tests map one-to-one onto the corrections. The disclosure prose is the strongest part of this rework — it states the limitation plainly, including the Supabase consequence, instead of burying it.

---

## 4. Required corrections (BLOCKING for acceptance / next gate)

1. **F-2-residual (major):** replace the three enumerated p9 shape guards with a whole-file shape assertion over the known key set, including list element types (closing probe 61) and sub-object types for `env` and `permissions` (closing probes 59, 60). Add regressions for at least probes 59–63. Unknown keys should fail closed, since probes 62–63 show an unrecognized-or-mistyped key is exactly the discard vector.
2. **F-6-residual (minor):** correct `docs/MCP_DEFAULT_DENY_POLICY.md:89` and `project-control/reports/M0-T077-submission.md:43` to the honest phrasing already adopted in `ci.yml`, and scope the "asserts every invariant" clause to what the validator actually checks.

---

## 5. What I could not test, and why

1. **User-scope `allowedMcpServers` broadening** — still requires writing the owner's `~/.claude/settings.json`, prohibited by D-020 items 5–6. The deny-first mitigation's effectiveness I did verify behaviorally in the first review (probes 37–39).
2. **Managed settings** — the owner-gated next step the doc now proposes is untestable here for the same reason: installing `managed-settings.json` is an owner-machine action. I can confirm the proposal is the correct mechanism in principle; I cannot confirm it works on this machine.
3. **Exhaustiveness of my own shape fuzzing** — I tested 11 shapes and found 5 discards. I make no claim that 5 is the complete set; that is precisely why I recommend a whole-file assertion instead of enumerating my findings.
4. **CI actually executing on GitHub** — I parsed the workflow and ran both commands locally; I did not trigger a run. `main` remains unprotected (unchanged from the first review).
5. **Live supervised worker launch** — owner-present only; correctly declared as an owner-gated residual.
6. **Interactive (non-`-p`) sessions** — all evidence remains fresh-process and headless.


---
---

<!-- Orchestrator preservation note: CORRECTION CONFIRMATION below, returned through
the agent-return channel by the same independent read-only G3 reviewer after the
blocking corrections were committed at b0200803, saved VERBATIM (transport
entity-decoding only). Received 2026-08-19. Verdict: CORRECTIONS CLOSED — the
G3 PASS gate's blocking corrections are resolved and independently verified.
Everything below is the reviewer's text. -->

# G3 Correction Confirmation — M0-T077 at `b0200803184b37b042dc734b092bb51759a52eaf`

## VERDICT: **CORRECTIONS CLOSED**

Both §4 blocking corrections are verified closed. No new findings. Nothing in the repository was modified by me; `git status` is clean.

---

## Item 3 — enforcement artifact unchanged ✓

```
git rev-parse eb742f2:.claude/settings.json b0200803:.claude/settings.json 002ffc3:.claude/settings.json
dd11cd79e01f309c524f00906ff1266de439a287   (identical across all three)
```

Still the same blob I proved effective, so every enforcement probe from both prior reviews carries over untouched.

## Item 1 — F-2-residual CLOSED, and closed as a *class* ✓

`python tools/validate_mcp_policy.py --check` on the real committed settings: **exit 0**. `python tools/test_mcp_policy.py`: **OK, 35 tests**.

I re-ran all five fixtures from my probes 59–63 and fuzzed thirteen more shapes against the new whole-file assertion, checking specifically for the dangerous combination (validator PASS + consumer discards the file):

| Fixture | Validator | Consumer |
|---|---|---|
| `permissions.allow: "not-a-list"` (probe 59) | **FAIL** | discarded |
| `env: "not-an-object"` (probe 60) | **FAIL** | discarded |
| `fallbackModel: [123]` (probe 61) | **FAIL** | discarded |
| `$schema: 12345` (probe 62) | **FAIL** | discarded |
| `cleanupPeriodDays: "thirty"` (probe 63) | **FAIL** | discarded |
| `disabledMcpjsonServers: [...,123]` | **FAIL** | discarded |
| `hooks` entry with `hooks: "not-a-list"` | **FAIL** | discarded |
| `permissions.additionalDirectories: [123]` | **FAIL** | discarded |
| `disableClaudeAiConnectors: 1` | **FAIL** | discarded |
| `permissions.ask: "nope"` | **FAIL** | discarded |
| `$schema: null` | **FAIL** | discarded |
| `env: {"BASH_DEFAULT_TIMEOUT_MS": 300000}` | FAIL | tolerated |
| unknown top-level key | FAIL | tolerated |
| unknown `permissions` sub-key | FAIL | tolerated |
| `deniedMcpServers` with a bare string element | FAIL | tolerated |
| `effortLevel: 7` | FAIL | tolerated |
| `outputStyle: "concise"` (legitimate key) | FAIL | tolerated |
| `fallbackModel: []` | PASS | blocked ✓ |

**All eleven shapes that actually discard the file now fail the validator. Zero bypasses found** — no fixture produced validator PASS with a discarded file.

This is stronger than the correction I asked for. Six of those eleven discard shapes (`disabledMcpjsonServers` mixed types, a broken `hooks` entry, `additionalDirectories` element type, `disableClaudeAiConnectors: 1`, `permissions.ask` as a string, `$schema: null`) are ones I never reported — the assertion caught them because it validates the whole file rather than the shapes I happened to find. That was the point of the correction, and it holds.

The six over-strict rows are fail-closed and visible, which is the documented design. Worth an operational note rather than a finding: adding a legitimate new Claude Code setting (the `outputStyle` row) will fail CI until `KNOWN_KEY_SHAPES` is extended in the same reviewed change. The validator docstring states this as intended visibility, mirroring the connector-authorization procedure, and I agree it is the right trade for a 12-key policy file — but whoever next edits `.claude/settings.json` will meet it, so it belongs in the handoff.

## Item 2 — F-6-residual CLOSED ✓

`grep -rn "blocks merge\|block merge\|blocks the merge"` across `docs/MCP_DEFAULT_DENY_POLICY.md` and `project-control/reports/M0-T077-submission.md`: **no match in either file.**

Both now carry the honest phrasing, and the coverage claim is properly scoped. The policy doc's "Durable validation" section no longer says "asserts every invariant"; it enumerates what is actually asserted — exact policy-key values, merge preservation **with the string-level hook residual named and its backstop identified**, and the whole-file shape assertion with the reason ("one mistyped key makes Claude Code silently discard the entire file") — then states plainly that "Failing checks gate merges only to the extent branch protection requires them — a pre-existing repository setting this policy does not change." The submission report's `ci.yml` row matches.

Naming the hook residual in the user-facing doc, not just the source comment, is more than I asked for and is the right call.

## Incidental checks

- Containment at `b0200803`: 22 changed files, **none outside `allowed_paths`**, none in `forbidden_paths`.
- Working tree clean; `b0200803` is branch head.

---

**Bottom line:** F-1 (blocking), F-2, F-2-residual, F-3, F-4, F-5, F-6, and F-6-residual are all resolved and independently verified. I have no remaining findings against this task. The one thing I could not test remains unchanged from the first review: exhaustiveness of my own fuzzing — I tested 18 shapes here and found no bypass, which is evidence of a well-formed general assertion rather than proof that none exists. The whole-file design is what makes me comfortable saying so; enumerated guards never would have been.
