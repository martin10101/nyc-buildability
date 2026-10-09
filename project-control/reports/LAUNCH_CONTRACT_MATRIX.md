> # ⚠ SUPERSEDED / HISTORICAL EVIDENCE ONLY (D-024 Amendment 39, 2026-09-01)
> This PHASE-1 launch-contract matrix is **historical evidence**, not the canonical implementation
> plan. The canonical plan is the corrected three-tranche MRL under D-024 Amendment 39
> (`source-039-amendment.md`, R489–R514). Do not treat the C1–C14 verdicts or the 15–23-day repair
> estimate here as the active plan of record; Amendment 39 revised the classification (C2/C3 REQUIRED,
> C6/C7/C10 eliminated, trust-boundary redesign) and conditionally authorized **Tranche A only**.

# LAUNCH CONTRACT MATRIX — M0-T135 (D-024 Amendment 38, PHASE 1)

**Read-only launch-contract lab.** Nothing was implemented, launched, pushed, merged, recertified, or
mutated. M0-T133 remains `awaiting_gate` (unaccepted); the loop remains `PAUSED_RECOVERY`. Structured
data: `LAUNCH_CONTRACT_RESULTS.json`. Repair sequencing + recommendation: `STABILIZATION_REPAIR_PLAN.md`.

## Freeze identity
| Fact | Value |
|---|---|
| Local HEAD | `e54e083d` (unpushed) on `control/D-024-fable-codex-loop` |
| origin/control | `6f5d12a6` (what the external audit saw) |
| origin/main | `d8b3899f` — **0 behind / 567 ahead** |
| Two unpushed local commits | `b7b203d2` (M0-T133 modularity-exception renewal), `e54e083d` (recert/present-only deliverable) → 565 (audited) + 2 = 567 |
| Live provider canaries | **0 of 8** authorized calls used (see JSON `canary_note`) |

## Verdict summary — 14 of 14 contracts, ZERO clean pass
| # | Contract | Verdict | Sev | Est (h) | Proof |
|---|---|---|---|---|---|
| C1 | Canonical controller source / stale-main | **FAIL** | P0 | 3–5 | reproduced+static |
| C2 | PowerShell command semantics + `$LASTEXITCODE` | **FAIL** (syntactic only) | P1 | 5–8 | static |
| C3 | Executable identity / updater / dispatch drift | **FAIL** | P1 | 10–16 | static |
| C4 | Effective Claude/Codex host inventory binding | **FAIL** (recert gap) | P0 | 12–20 | static |
| C5 | Child-env model id + Claude/Codex/GitHub auth | **FAIL** | P1 | 10–16 | static |
| C6 | `--permission-prompt-tool stdio` real behavior | **BLOCKED** (unverified vs live CLI) | P1 | 8–12 | static + owner canary |
| C7 | Controller total turn budget vs `--max-turns` | **FAIL** | P1 | 10–16 | static |
| C8 | Claude checkpoint schema + correlation | **FAIL** | P0 | 6–10 | reproduced+static |
| C9 | Codex `COMPLETE` schema + git/evidence binding | **FAIL** | P0 | 6–8 | reproduced+static |
| C10 | Queue/packet/worktree/branch/HEAD/status binding | **FAIL** (partial) | P1 | 10–14 | static |
| C11 | Fresh remote observation vs stale tracking refs | **FAIL** | P1 | 5–8 | static |
| C12 | Raw gate-result integrity (unpiped exit) | **FAIL** | P0 | 6–10 | reproduced+static |
| C13 | Process-tree / timeout / EOF / recovery | **FAIL** timeout · **PASS** containment+recovery | P1 | 14–20 | static |
| C14 | Real GitHub lifecycle topology | **BLOCKED** (shadow-only; no target branch) | P0 | 12–20 | static + reproduced |

**Totals:** launch-critical repair **117–183 h ≈ 15–23 working days**. P0: C1, C4, C8, C9, C12, C14. P1: C2, C3, C5, C6, C7, C10, C11, C13(timeout).

## Per-contract detail
Each row: **observed → expected → evidence (file:line / probe) → defect → files/functions → positive test / mutant test → estimate.** Full field set (raw exit, evidence digest, proof type, dependency) is in `LAUNCH_CONTRACT_RESULTS.json`.

### C1 — Controller source / stale-main (FAIL, P0, 3–5 h; depends C14)
- **Observed:** `docs/CONTROLLER_UPDATE_RUNBOOK.md:69-72` resolves the install source as `git -C <other-clone> rev-parse origin/main` and worktree-adds from it; retired ids hardcoded (`wt-m0t063` :22/33/44/133/146/160-162/211-214, `M0-T063` :227, `M0-T127` :242).
- **Evidence:** `git rev-list --left-right --count origin/main...HEAD` → `0  567`; `git ls-tree -r origin/main tools/agent_supervisor/` = **63 files vs 169** on control (missing `github_flow.py`/`launch_seam.py`/`command_docs.py`). `evidence/F01_source.txt` (`0cda078d…`).
- **Defect:** following the approved-looking runbook installs a controller 567 commits behind live; every flag is legal so syntax checks pass.
- **Fix:** rewrite runbook §1/§4/§11 to a canonical branch+SHA that contains the shipping code. **Positive:** doc-lint asserts the install ref contains `github_flow.py`. **Mutant:** ref=`origin/main` → lint fails.

### C2 — PowerShell command semantics / `$LASTEXITCODE` (FAIL syntactic-only, P1, 5–8 h)
- **Observed:** `supervisor_command_doc_check.py:69` calls only `command_docs.validate_document`; `validate_command` (`command_docs.py:313-315`) checks flag-**token** presence via argparse; `check_worktree_binding` exists (`:337-361`) but the CI entry never calls it. PowerShell only `shlex.split(posix=False)` (`:222`), never parsed/executed. CI `supervisor-bridge` (`.github/workflows/ci.yml:528-550`) is `windows-latest` but every step is `shell: bash` (`:537,546,549`); `$LASTEXITCODE` never captured.
- **Defect:** operator packages can be semantically wrong (wrong worktree, retired paths, stale source) and still report `12/0`.
- **Fix:** doc-check resolves `--task-packet`, calls `check_worktree_binding`, binds values; add a Windows PowerShell parse/dry-run job. **Mutant:** `--worktree`=primary checkout → must FAIL (today passes).

### C3 — Executable identity / updater / drift (FAIL, P1, 10–16 h; depends C4)
- **Observed:** `process.py:125-126` `FULL_HASH_MAX_BYTES=64 MiB`, `HEAD_DIGEST_BYTES=1 MiB`; `:275-284` files >64 MiB hashed as `sha256_head+size` (first 1 MiB + size). The ~265 MB Claude CLI always takes the partial path. Admission digest not in the manifest (`cli.py:2819`); dispatch (`claude_runner.py:1300-1337`) never re-hashes.
- **Defect:** a binary changed after the first 1 MiB (same size) evades the digest; no dispatch-time drift check.
- **Fix:** stream full sha256 (cache by size+mtime); re-verify before `Popen`. **Mutant:** two 100 MiB files identical first-1 MiB + equal size, differing at 2 MiB → digests must differ (collide today).

### C4 — Effective host inventory binding / recert gap (FAIL, P0, 12–20 h)
- **Observed:** `manifest.py:50-59 COVERED_PATTERNS` binds only the package tree + `config.toml`. **Unbound:** `.claude/settings.json` (`model=fable-5`, `fallbackModel=[opus-4-8]`, `effortLevel=xhigh`, hooks, `permissions.deny=[mcp__*]` — `:3-79`), `.claude/hooks/*`, `CLAUDE.md`, `.claude/rules/*`, skills/subagents/plugins/MCP, claude executable digest. `build_argv` (`:372-377`) pins no `--settings`/`--strict-mcp-config`, so the child reads model/effort/hooks/MCP/CLAUDE.md from ambient state.
- **Defect:** host-local state can change worker behavior AFTER recertification without invalidating the admitted identity — the exact class journey-4 hit with the model default.
- **Fix:** bind a captured host inventory into the manifest; pin `--settings`/`--strict-mcp-config`. **Mutant:** flip `effortLevel` or add an MCP server → verification halts (green today).

### C5 — Child-env model id + auth (FAIL, P1, 10–16 h)
- **Observed:** `process.py:104-108` allowlist preserves HOME/USERPROFILE, **drops** APPDATA/LOCALAPPDATA/GH_TOKEN/GITHUB_TOKEN/SSH_AUTH_SOCK/ANTHROPIC_API_KEY/OPENAI_API_KEY. Codex auth proof: **none** (`capability_probe.py:53-55` runs `--version/--help` under ambient env). GitHub: only anonymous `ls-remote` in the **supervisor** env (`start_gate.py:112-127`). Exact provider-reported model verified only for the orchestrator role (`cli.py:2795`), not worker/reviewer pre-dispatch.
- **Defect:** Claude/Codex/GitHub may fail only after dispatch (existence ≠ auth); dropping APPDATA/LOCALAPPDATA may itself break Windows keychain auth.
- **Fix:** preflight codex + github auth round-trips under the **exact** child env; revisit the env allowlist. **Mutant:** remove the codex credential source → probe FAILS (nothing fails today).

### C6 — `--permission-prompt-tool stdio` (BLOCKED, P1, 8–12 h + owner live session)
- **Observed:** runner passes literal `"stdio"` (`claude_runner.py:87`) and implements the protocol privately (control_request off stdout `:1427-1432` → `build_control_response` to stdin `:1717-1718`). `:98 CONTROL_RESPONSE_WRAPPER_VERIFIED=False` — self-declared **unverified** vs the live CLI; official docs define the flag as an MCP tool name, not `stdio`. **No per-permission-response deadline** (only the 900 s wall).
- **Defect:** the permission bridge rests on measured-private, doc-contradicted behavior the code itself marks unverified; a hung broker rides 900 s.
- **Fix:** add a response deadline + a live round-trip preflight probe. **BLOCKED_OWNER_GATE:** the live-CLI verification is owner-gated (capped model). **Mutant:** fake CLI never emits the request → unit must fail closed within the deadline (survives today).

### C7 — Total turn budget vs `--max-turns` (FAIL, P1, 10–16 h)
- **Observed:** `--max-turns = total_turns` (`cli.py:2677-2678`) enforced **per stream-json message**; `run_unit` has no cumulative turn/call counter; the reserved starvation message (`claude_runner.py:1435-1443`) gets a fresh full allowance; stdin closes on per-message completion (`:1444/:1453-1454`).
- **Defect:** a unit can consume ~2× `total_turns`; the "no new tool use" text is untrusted prompt guidance.
- **Fix:** controller-side cumulative counter; close stdin at `total_turns`. **Mutant:** worker ignores the reserved-turn instruction → stdin closes at the global budget (survives today).

### C8 — Checkpoint schema + correlation (FAIL, P0, 6–10 h)
- **Observed / reproduced:** `validate_checkpoint({summary:7, claims:'not-a-list', empty ids, usage:[]})` → **ACCEPTED** (`evidence/F02_checkpoint.txt`, `6bb63288…`). `from_dict` presence-only (`models.py:110-128`); `validate()` checks only status + usage (`:175-182`); weaker than `schemas/claude_checkpoint.schema.json` (`minLength:1`, per-field types). No run/task/session/checkpoint correlation to controller values. M0-T133's envelope fixes only the 4 git-state fields.
- **Defect:** a model-invented/corrupt checkpoint enters as valid controller state.
- **Fix:** enforce types + nonempty ids + schema_version + identity correlation. **Mutant:** `summary=int` / empty `run_id` / mismatched session / bad schema_version each raises.

### C9 — Codex `COMPLETE` binding (FAIL, P0, 6–8 h)
- **Observed / reproduced:** `validate_decision(COMPLETE, verified_repo_head='definitely-not-a-sha', origin='', facts=[{}])` → **ACCEPTED** (`evidence/F03_decision.txt`, `8019986e…`). `codex_reviewer.py`: `_reject_wrong_types` shape-only; `REQUIRED_BY_DECISION['COMPLETE']` requires only `evidence_refs` nonempty (`:141`); no SHA check, no controller-git parameter; SHAs never reach advancement (`next_task.py:702-725`). Equality lives only as model-facing prompt text (`:710`).
- **Defect:** a reviewer can COMPLETE the wrong/unverified state.
- **Fix:** COMPLETE-branch checks (40-hex head, nonempty origin/facts, reject `{}` evidence) + `expected_repo_head`/`expected_origin_main` bound to the frozen packet, wired at `loop.py:2041-2043`. **Mutant:** bad SHA / empty origin / head≠packet / `[{}]` evidence each raises.

### C10 — Queue/worktree/HEAD binding (FAIL partial, P1, 10–14 h)
- **Observed:** `TaskQueueEntry` (`next_task.py:424-446`) has no head, no status digest; eligibility (`:551-651`) + `launch_seam` (`192-284`) are path checks with **no `rev-parse HEAD`, no `status --porcelain`, no clean check**; branch re-bound onto args (`:859-864`) but never verified vs live git. Eligibility IS re-run pre-dispatch (`:829-868`) — but the HEAD/clean checks don't exist to run. Owner-typed first task not status-gated.
- **Defect:** a stale/dirty/wrong-HEAD successor worktree can enter under a valid task id.
- **Fix:** add `expected_starting_head` + status digest; measure live HEAD + porcelain; require clean+exact-HEAD for a fresh successor. **Mutant:** dirty tree / moved HEAD / wrong branch each skipped.

### C11 — Remote freshness (FAIL, P1, 5–8 h; depends C9)
- **Observed:** `EvidenceCollector` (`evidence.py:170`) defaults `allow_remote_reads=False` and reads LOCAL `origin/main` (`:116-124`) with no fetch-age proof; no `ls-remote` head+timestamp binding; `refresh_remote` (`:237-250`) is `not_configured` unless enabled.
- **Defect:** `git.origin_main`/`ahead_behind` in the frozen packet can be silently stale, feeding a COMPLETE decision.
- **Fix:** add a read-only `ls-remote` observation (head + `observed_at_utc`); mark stale absent a fresh observation. **Mutant:** local behind ls-remote head → flags stale (passes silently today).

### C12 — Raw gate-result integrity (FAIL, P0, 6–10 h)
- **Observed / reproduced:** unpiped `python tools/modularity_check.py --check` at audited `6f5d12a6` → **exit 1** (1432/1410); `M0-T133-G2-self-check.md:20-24` recorded exit 0 — caught by G3 (`:29-38`) + G4 (`:26-32`). Same class as the M0-T130 `modularity_check | tail` false green. `evidence/F04_audited_delta.txt` (`ddde77dc…`). No central runner records raw exit + digests. **Note:** the local unpushed renewal makes it exit 0 at 1435, but the owner directed **split, not renew** (R474/R475) — the launch fix is the split + a real gate-runner.
- **Fix:** `tools/gate_runner.py` records `{argv, returncode, stdout_sha256, stderr_sha256}`; gates consume the JSON. **Mutant:** wrap in `| tail`/`Tee-Object` → recorded returncode stays the tool's.

### C13 — Process tree / timeout / recovery (FAIL timeout · PASS containment+recovery, P1, 14–20 h; depends C6)
- **Observed:** ONE fixed 900 s wall watchdog (`claude_runner.py:1356-1365`), no phase deadlines. **PASS** containment: Windows Job Object kill-on-close, no breakaway, `IsProcessInJob`-verified (`process.py:363-395/481-549`), honest `taskkill /T /F` fallback (grandchild can escape on the fallback, acknowledged, not proven-zero). **PASS** recovery: `PAUSED_RECOVERY` reachable + exitable via `owner_cleared_pause→PREFLIGHT` (`state_machine.py:283`, `cli.py:1855-1880/3471`).
- **Defect:** one number can't distinguish healthy-draining / waiting-for-MCP / retry / never-arriving.
- **Fix:** phased deadlines (first-event, per-turn idle, permission-response, stream-drain, total) + a post-kill descendant-zero proof on the taskkill path. **Mutant:** worker spawns a detached grandchild then exits → assert zero descendants remain.

### C14 — GitHub lifecycle topology (BLOCKED, P0, 12–20 h — architecture)
- **Observed:** whole flow SHADOW-ONLY (`github_flow.py:3/21`; effects cross an injected `GitHubRunner` Protocol `:709-724`; `github_pr_merge` excluded from `MODELED_EFFECTS` `:56-64`); `push_policy.py:51 NO_PUSH_EXECUTION_IN_THIS_PHASE=True`; acceptance manual; R595 activation never lifted. **Topology:** `ls-remote` shows only `control/*`, task branches, and `main`; **no integration/develop/staging branch exists.** Control is 0/567 ahead of main (~1151 files); a task branch off control shares that 567-commit lineage → a `base:main` PR enumerates all 567.
- **Defect:** the owner-required end-to-end lifecycle (R472) is impossible today — the execution doesn't exist AND no sane PR target branch exists. Reconciling control↔main is an undefined large merge and a prerequisite architecture decision.
- **Fix:** establish a canonical integration branch; real `GitHubRunner` impl targeting it; reconcile the divergence. **Mutant:** `base=main` → PR commit-count assertion fails.
