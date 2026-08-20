<!-- Orchestrator preservation note (report-preservation rule, 2026-07-16): the review
below was returned through the agent-return channel by the independent read-only
G5 security reviewer (fresh replacement agent after the first G5 agent went
unresponsive without delivering a report) and is saved VERBATIM (transport
entity-decoding only). Received 2026-08-19. Verdict: PASS with one required
correction - recorded as gate G5 PASS per the gate-verdict semantics rule; the
section-4 F-1 documentation correction is BLOCKING for acceptance. Everything
below this line is the reviewer's text. -->

# G5 Independent Security Review — M0-T077 (D-020 program-wide MCP default-deny)

**Reviewer:** security-reviewer (fresh, independent replacement; no prior agent's conclusions reused)
**Anchor reviewed:** `a861c4d86289df9b331acba6b3a53243bdb96a8a` (branch `task/M0-T077-mcp-default-deny`, PR #240)
**Base:** `31c50a09bd1671d111f21923c6a2d739f51187dd`
**Worktree (read-only):** `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m0t077`
**Proof worktree used:** `C:\Users\MLFLL\Downloads\nyc-zoning\wt-t077-proof` (detached at `eb742f2`)

## VERDICT: **PASS with one required correction**

Per `.claude/rules/project-control.md` gate-verdict semantics this is recorded as **PASS**; the §4 correction is **BLOCKING for acceptance**.

No secret, token, credential, connection string, database key, or private account content is exposed by any committed artifact or by the PR body. The enforcement artifact is correct, minimal, and empirically effective at repository roots; the validator is stdlib-only, read-only, and cannot pass vacuously; no protected surface was touched; the owner's global configuration is byte-identical and unrelated projects retain every connector. The one MAJOR finding is a **disclosure defect, not an implementation defect**: the reports characterize the residual exposure too narrowly, and the narrowing is wrong in a way that is live in this very session.

I modified nothing in any repository worktree. All scratch fixtures were created under my OS temp directory and deleted at the end of the review. I did not invoke Airtable, Microsoft 365, Pencil, or Supabase tools at any point (D-020 §3).

---

## 1. Probes executed

### Charter item 1 — secret / private-data exposure

| # | Command | Result |
|---|---|---|
| 1 | `python .github/scripts/secret_scan.py` (from worktree) | **PASS — no findings.** 2950 files in 13.66 s; 3 pre-existing exact-path allowlist entries, 8 pre-existing inline pragmas, 7 binaries skipped — none of them a M0-T077 artifact; exit 0 |
| 2 | `git diff 31c50a09..a861c4d \| grep '^+' \| grep -v '^+++'` | 4086 added lines extracted to temp for scanning |
| 3 | 21 secret-pattern counts over those 4086 lines (JWT `eyJ…`, `sbp_`, `sb_secret`, `sb_publishable`, `service_role`, `sk-ant-`, `ghp_`, `github_pat_`, `gho_`, `AKIA`, `postgres(ql)://`, `mysql://`, `mongodb(+srv)://`, `SUPABASE_*KEY`, `ANTHROPIC_API_KEY=`, `Bearer <token>`, PEM private key, `xox[baprs]-`, `AIza…`) | **0 matches on every pattern.** Counts only — no matched content was printed |
| 4 | Supabase project-ref truncation: `grep -o 'dyiv'` vs `grep -o 'dyiv[[:alnum:]]'` | `dyiv` occurs **5 times**; occurrences followed by an alphanumeric character: **0**. Every committed occurrence is exactly the 4-character truncation `dyiv…`. No artifact exposes a longer prefix |
| 5 | `grep -oE '[a-z0-9]{20,}'` minus pure-hex (a Supabase ref is 20 lowercase alnum) | **0 candidates** — the full ref appears nowhere in the diff |
| 6 | `grep -oE '[A-Za-z0-9+/_-]{24,}'` with mixed case + digit, minus pure hex → 53 distinct candidates; classified by benign-shape regex | 48 match artifact/identifier shapes (`M0-T077-*`, `D-020-*`, `disabledMcpjsonServers`, doc URLs). The 5 remainders resolve to a worktree path fragment (`…Users/MLFLL/Downloads/nyc-zoning/wt-m0t077`, len 43) and four report identifiers, all in `M0-T077-review-G3.md` / `tasks/M0-T077.json`. **No high-entropy secret** |
| 7 | Read `project-control/reports/M0-T077-review-G3.md` (460 lines, the committed reviewer preservation file) in full | **Clean.** It states explicitly at line 189: *"I deliberately keep the full project ref out of this report though my probe output displayed it."* It cites only `dyiv…`, no tokens, no account contents |
| 8 | Read `M0-T077-mcp-audit.md` in full | Clean. Names the env **key** `SUPABASE_ACCESS_TOKEN` and states the value "was never displayed, logged, or committed" — a key name is not a secret. Digests truncated to 12 hex chars |
| 9 | `gh pr view 240 --json body` + scan | **Clean.** No token, key, ref, or account content. Head OID `a861c4d…` matches the anchor; base `main`; state OPEN |
| 10 | Private-path exposure count in added lines | `MLFLL` appears in **5** added lines across 3 files: the verbatim owner directive `source-001.md`, the `worktree` field of `tasks/M0-T077.json`, and the G3 review header. Repo-wide precedent on `31c50a09`: **39 of 120** task packets and **192** report files already contain it |

### Charter item 3 — authority / protected surface

| # | Command | Result |
|---|---|---|
| 11 | `git diff --name-status 31c50a09..a861c4d` | 22 files. **Zero** under `tools/agent_supervisor/`, `tools/model_routing.py`, `apps/`, `services/`, `packages/`, `supabase/`. The only workflow touched is `.github/workflows/ci.yml`. Every `project-control/{tasks,gates,reports}` file carries the `M0-T077` id; the only directive directory is D-020's new one |
| 12 | Programmatic semantic diff of `project-control/directives/index.json` (JSON-parsed both revisions) | **Pure append confirmed:** 19 → 20 entries, `ADDED: ['D-020']`, `REMOVED: []`, order of all 19 pre-existing entries preserved, **`MODIFIED pre-existing entries: []`**. Only other change is the top-level `updated_at`. Note the *textual* diff is 317+/303− because the file was re-serialized (10559 → 10409 bytes, 303 → 318 lines) — a reader relying on `git diff` alone cannot see that it is an append; the parse proves it is |
| 13 | `git diff … -- project-control/state.json` | `+"M0-T077"` into `active_tasks` and an `updated_at` bump. Nothing else |
| 14 | `git diff … -- .claude/settings.json` | Purely additive: 19 inserted lines, 0 deleted. `$schema`, `model`, `fallbackModel`, `effortLevel`, `env`, `hooks` untouched |
| 15 | `git rev-parse eb742f2:.claude/settings.json b0200803:… a861c4d:…` | `dd11cd79e01f309c524f00906ff1266de439a287` — **identical across all three**, confirming the enforcement artifact is unchanged since `eb742f2` as stated in the charter |
| 16 | `git status --porcelain` for the five enforcement artifacts | Clean. The only dirty file in the worktree is `project-control/state.json`, an `updated_at` timestamp bump (`22:34:48` → `22:42:35`) — orchestrator bookkeeping, no content impact |

### Charter item 4 — global preservation

| # | Command | Result |
|---|---|---|
| 17 | `hashlib.sha256` of `C:\Users\MLFLL\.mcp.json` | `1fc898cc6935…` — **matches** the proof's before-value; 280 B |
| 18 | `hashlib.sha256` of `C:\Users\MLFLL\.claude\settings.json` | `a738fcfa9573…` — **matches** the proof's before-value; 5759 B |
| 19 | `claude mcp list` from `C:\Users\MLFLL\Downloads` (non-repository, confirmed not a git tree) | **All connectors available to unrelated projects:** Airtable ✔ Connected, Microsoft 365 ! Needs authentication, pencil ✔ Connected, supabase ✔ Connected. Nothing was disconnected or removed account-wide |
| 20 | `claude mcp list` in `wt-t077-proof` (clean detached worktree @ `eb742f2`) | `No MCP servers configured.` |
| 21 | `claude mcp list` in `wt-m0t077` root (@ `a861c4d`) | `No MCP servers configured.` |

### Charter item 5 — validator execution safety

| # | Command | Result |
|---|---|---|
| 22 | `grep -nE '^\s*(import\|from)' tools/validate_mcp_policy.py` | `__future__`, `argparse`, `json`, `sys`, `pathlib` — **stdlib only**, no third-party import |
| 23 | `grep -nE 'open\(\|write_text\|write_bytes\|mkdir\|unlink\|rmtree\|shutil\|os\.remove\|subprocess\|os\.system\|requests\|urllib\|socket'` | **No matches.** The only I/O is `Path.read_text` — read-only, no network, no subprocess |
| 24 | Vacuous-pass probes on the p1 paths (temp fixtures, `--settings` override): missing file, unparseable JSON, root=array, root=null, empty object `{}`, path-is-a-directory, zero-byte file | **exit=1 on all seven.** No exception path yields silent success. I also traced every shape predicate: none can raise (each guards with `isinstance` before subscripting, and the `defaultMode` check is a tuple membership test), and an unexpected raise would surface as a traceback with a nonzero exit — still fail-closed |
| 25 | `python tools/validate_mcp_policy.py --check` on the real committed settings | exit **0** |
| 26 | `python tools/test_mcp_policy.py` | **Ran 35 tests — OK**, exit 0 |
| 27 | `yaml.safe_load(.github/workflows/ci.yml)` + job/step enumeration | Both steps are steps **7 and 8 of 9** in the **existing `control-plane` job** — no new job, no `if:` guard, no `needs:` gating. Workflow triggers are `push` and `pull_request`, so the validator runs on every push and PR |

---

## 2. Findings

### F-1 — MAJOR (required correction): the residual exposure is characterized too narrowly; in-session subagents inherit the parent process's connector set regardless of their own working directory

Claude Code resolves MCP configuration **once per `claude` process, at session start**. Agent/Task-tool subagents dispatched inside that session are not new `claude` processes — they inherit the parent's resolved server set no matter which directory they are assigned to work in.

Direct evidence, from this review session itself:

- My own working directory is `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m0t077`.
- A fresh `claude mcp list` in **that exact directory** returns `No MCP servers configured.` (probe 21).
- Yet my own tool roster carries `mcp__supabase__execute_sql`, `mcp__supabase__apply_migration`, `mcp__pencil__*`, and `mcp__claude_ai_Airtable__*`, and my system prompt carries the Supabase, Pencil, and Airtable MCP server instructions.

The parent orchestrator session reports its primary working directory as `C:\Users\MLFLL` — the user-profile root, which is where the `.mcp.json` carrying the Supabase server lives (audit §5). So the entire agent tree performing this repository's work, including the producer and every reviewer, is running with live production-database tools attached, while `claude mcp list` inside the same worktree correctly reports none.

Why this is a finding and not merely the already-disclosed boundary: the committed artifacts *do* disclose that sessions launched outside the repository are ungoverned, and that is the underlying mechanism. But both artifacts then narrow the residual to a single case that is not the operative one:

- `docs/MCP_DEFAULT_DENY_POLICY.md:122-124` — *"supervised workers always launch with `cwd` set to the worktree ROOT … so agent sessions are covered; **the residual is a HUMAN starting a session one level down**."*
- `M0-T077-fresh-session-proof.md:136` — *"Supervised workers always launch at the worktree root and are therefore covered."*

"Agent sessions are covered" is true for **supervisor-launched** workers (`tools/agent_supervisor/claude_runner.py`, verified read-only and correctly evidenced in the supervisor report). It is false for **Agent-tool subagents of an interactive orchestrator session**, which are not supervisor-launched and which constitute this program's dominant operating pattern today. The stated residual — a human starting a session one directory down — is the *narrower* case; the broader and currently active one is unstated.

A disclosure sweep confirms the gap is real rather than a wording quibble: across `MCP_DEFAULT_DENY_POLICY.md`, the fresh-session proof, the supervisor report, and the audit, the terms `subagent`, `sub-agent`, `per-process`, and `parent session` return **zero** hits.

This matters under the program's own threat model. The audit names ambient Supabase exposure as *"the highest-risk item in this audit"* (mcp-audit §5) because it reaches the production datastore named in Permanent Principle 5. D-020's objective is that *"every ordinary Claude Code session working in NYC Buildability"* defaults to no unrelated connector; as operated today, the sessions doing the work do not.

This is a **documentation/disclosure** correction, not a code or configuration one. The settings artifact is already as strong as a project-scope mechanism permits, and D-020 §6 explicitly forbids modifying global settings as a workaround — which is precisely why §6 requires instead that the exact limitation and the smallest owner-gated next step be reported. That was done thoroughly for the supervisor gap and for the subdirectory gap (G3 F-1), and it is incomplete here.

**Required correction (documentation only):** in `docs/MCP_DEFAULT_DENY_POLICY.md` "Honest enforcement boundary" and `M0-T077-fresh-session-proof.md` §5, state that (a) MCP resolution happens per-process at session start, so subagents dispatched by a session inherit that session's connector set regardless of the directory they work in; (b) consequently a session started outside a repository worktree root — including an orchestrator session started at the user-profile directory, the current pattern — leaves its whole agent tree with the ambient connectors; and (c) correct the two sentences that reduce the residual to "a HUMAN starting a session one level down." The smallest operational next step is a practice rule (start orchestrator and interactive sessions from a repository worktree root), alongside the already-recorded owner-gated managed-settings option. No settings, validator, or CI change is needed, and the enforcement blob should not move.

### F-2 — MINOR: committed artifacts and the PR body carry pre-correction counts

`M0-T077-submission.md:41-42` describes the validator as *"~210 lines"* with *"28 tests"*, and line 53 records *"28/28 OK"*. The shipped validator is 310 lines and the suite is **35 tests** (probe 26) after the `b0200803` whole-file-shape correction. The PR #240 body likewise says *"18 removal/weakening regressions"* and enumerates *"five officially supported keys"*, omitting the sixth addition `permissions.deny: ["mcp__*"]`. No security impact — the artifacts understate rather than overstate coverage — but a later reader reconciling evidence to code will hit a mismatch. Refresh the counts, or note that the submission report is frozen at the pre-correction identity.

### F-3 — INFO: `.claude/settings.local.json` is gitignored and outranks project settings, so CI cannot see a local weakening

`.gitignore:64` ignores `.claude/settings.local.json`, and local scope has higher precedence than project scope. `tools/validate_mcp_policy.py` validates only `.claude/settings.json`, so a local override is structurally invisible to the CI gate. No such file exists in this worktree (checked). Residual risk is bounded and I am not asking for a change: the G3 reviewer's probes 3–5 empirically showed an aggressive `settings.local.json` (connectors re-enabled, allowlist populated, denylists emptied, auto-approval on) still yields `No MCP servers configured`, because `deniedMcpServers` merges with deny-precedence and `permissions.deny: ["mcp__*"]` cannot be re-allowed by another level. The unreachable-by-CI property is worth knowing; the exposure it creates is not material.

### F-4 — INFO: `index.json` reads as a rewrite in `git diff` but is semantically an append

Recorded so the next reviewer does not have to re-derive it (probe 12). Any future review of this file should parse rather than eyeball the diff.

### F-5 — INFO: private absolute paths are present but are established repository convention

`C:\Users\MLFLL\...` appears in 5 added lines (probe 10) — in the verbatim owner directive (immutable by directive rule 2), the task packet's standard `worktree` field, and the G3 reviewer's header. 39 of 120 task packets and 192 report files already on `main` carry the same string. This is not a D-020 §5 category (secret, token, credential, connection string, database key, account content, or private *external* data), and AS-7's redaction clause is satisfied for the categories that matter. Flagging only for completeness.

### F-6 — INFO: what I verified as genuinely sound

- The default-deny policy works: `No MCP servers configured` from two independent worktree roots (probes 20, 21) against a live control showing all four connectors from a non-repo directory (probe 19).
- Global preservation is exact: both non-volatile owner files hash-match their pre-implementation digests (probes 17, 18), and every connector remains fully usable outside the repository.
- The validator is a clean security artifact: stdlib-only, read-only, no network, no subprocess, fail-closed on all seven degenerate-input paths, 35 passing regressions, wired unconditionally into an existing job that runs on push and PR.
- Containment is clean: nothing under any forbidden path, no other task's evidence, no other directive, no other workflow.
- The task does not overclaim merge-blocking anywhere — the `ci.yml` comment, the policy doc, and the submission report all now state that failing checks gate merges only to the extent branch protection requires, which matches `main` being unprotected.

---

## 3. Not testable, and why

1. **Whether a user-scope `allowedMcpServers` entry can broaden the empty project allowlist.** Requires writing the owner's `~/.claude/settings.json`, prohibited by D-020 §6.5-6.6. The caveat is documented in the policy doc; its premise rests on official documentation, not measurement. Unchanged from G3.
2. **Managed-settings precedence** (`managed-settings.json`). None exists on this machine; installing one is an owner-machine action. The proposed owner-gated next step therefore cannot be validated here, only judged mechanically correct.
3. **`claude --mcp-config` / `--strict-mcp-config` injection.** G3 probe 10 found the variadic flag consumed the subcommand and reported no working invocation. I did not re-attempt it (charter: do not duplicate G3). Relevance is bounded: it is explicit user action at CLI scope, the supervisor provably never passes it (G3 probe 47), and project-scope `permissions.deny: ["mcp__*"]` cannot be overridden by a higher level.
4. **Behavioral verification that `permissions.deny: ["mcp__*"]` strips MCP tools.** Owned by G3 and verified there behaviorally (probes 37–39: tools present without the rule, absent with it, still absent under `defaultMode: "bypassPermissions"`). Not re-run per charter. I did not exercise it myself because doing so would require invoking a connector, which D-020 §3 forbids during this task.
5. **A live supervised worker launch.** Owner-present only under D-018/D-019; correctly declared as an owner-gated residual by the producer.
6. **CI executing the new steps on GitHub.** I parsed the workflow and ran both commands locally; I did not trigger or observe a remote run.
7. **Exhaustiveness of the consumer-discard shape space.** G3 fuzzed 18 shapes against the whole-file assertion with zero bypasses. I did not re-fuzz. The structural design (closed key set, element types, fail-closed on unknown) is what supports the claim, not the sample size.

---

## 4. Required correction before acceptance

**F-1 (major, documentation only):** disclose per-process MCP resolution and subagent inheritance in `docs/MCP_DEFAULT_DENY_POLICY.md` and `M0-T077-fresh-session-proof.md` §5, and correct the two sentences that narrow the residual to "a HUMAN starting a session one level down." Record the operational next step (start orchestrator and interactive sessions at a repository worktree root) alongside the existing owner-gated managed-settings option. `.claude/settings.json` must not change — blob `dd11cd79…` should remain the artifact every probe in G3 and G5 was run against.

**F-2 (minor, at the orchestrator's discretion):** refresh the validator line-count and test-count figures in `M0-T077-submission.md`, or annotate that section as frozen at the pre-correction identity.

---

## 5. Confirmations required by the charter

- **Secret/private-data exposure:** none. Repository scanner PASS; 21 secret patterns at zero across all 4086 added lines; the Supabase project ref never appears beyond its 4-character truncation in any committed artifact; the committed G3 reviewer report leaks nothing and says so explicitly; the PR #240 body is clean.
- **Undisclosed weakening vector:** one found — F-1. The subdirectory case, user-scope allowlist broadening, and interactive user action are all disclosed and are not findings.
- **Authority/protected surface:** intact. No supervisor, routing, application, service, package, supabase, other-workflow, or other-task file modified; `index.json` is a verified pure append.
- **Global preservation:** confirmed. Both digests match (`1fc898cc…`, `a738fcfa…`); a fresh non-repository `claude mcp list` shows all four connectors still available to unrelated projects.
- **Validator execution safety:** confirmed. Stdlib-only, read-only, no vacuous-pass path, correctly wired into the existing `control-plane` job on push and pull_request.


---
---

<!-- Orchestrator preservation note: CORRECTION CONFIRMATION below, returned through
the agent-return channel by the same independent read-only G5 reviewer after the
blocking F-1 disclosure correction was committed at f254698, saved VERBATIM
(transport entity-decoding only). Received 2026-08-19. Verdict: CORRECTION
CLOSED — the G5 PASS gate's blocking correction is resolved and independently
verified. Everything below is the reviewer's text. -->

# G5 Correction Confirmation — M0-T077 at `f254698bb70b86abd1e1741acbb7b884debe358e`

**Reviewer:** security-reviewer (same independent read-only agent that returned the G5 verdict)

## VERDICT: **CORRECTION CLOSED**

Both the blocking F-1 disclosure correction and the minor F-2 count refresh are verified closed. No new findings. I modified nothing; all checks were read-only.

---

## Item 2 first — the enforcement artifact did not move ✓

```
git rev-parse eb742f2:.claude/settings.json a861c4d:.claude/settings.json f254698:.claude/settings.json
dd11cd79e01f309c524f00906ff1266de439a287   (identical across all three)
```

`git diff --name-status a861c4d..f254698 -- .claude/settings.json tools/validate_mcp_policy.py tools/test_mcp_policy.py .github/workflows/ci.yml` returns **empty** — all four enforcement artifacts are byte-unchanged. Every enforcement probe from G3 and from my G5 review therefore carries over untouched, which is exactly what a documentation-only correction should look like.

The correction commit touches 7 files (`docs/MCP_DEFAULT_DENY_POLICY.md`, `M0-T077-fresh-session-proof.md`, `M0-T077-submission.md`, `tasks/M0-T077.json`, `state.json`, plus the new `gates/M0-T077-G5.json` and `reports/M0-T077-review-G5.md`). Full base-to-head containment at `31c50a09..f254698`: **24 files, all inside the frozen contract, none in `forbidden_paths`**.

## Item 1 — F-1 disclosure CLOSED, and accurate against my own measurements ✓

I re-read both sections rather than accepting the diff on trust.

**`docs/MCP_DEFAULT_DENY_POLICY.md`** — a new "Per-process resolution and subagent inheritance (G5 F-1)" bullet in the Honest enforcement boundary states all four elements I asked for, correctly:

- **Per-process resolution:** *"Claude Code resolves MCP configuration ONCE per `claude` process, at session start."* ✓
- **Subagent inheritance:** *"Agent-tool subagents dispatched inside a session are not new processes — they INHERIT the parent session's connector set regardless of the directory they are assigned to work in."* ✓
- **The operative consequence, stated concretely:** a session started outside a worktree root — *"including an interactive orchestrator session started at the user-profile directory, the operating pattern at the time this policy landed"* — carries ambient connectors *"including live Supabase tools"* through its entire agent tree, *"even while its agents work inside this repository and a fresh `claude mcp list` in the same worktree correctly reports none."* That is precisely the asymmetry I demonstrated from inside my own session. ✓
- **The narrowing is gone.** *"the residual is a HUMAN starting a session one level down"* is deleted and replaced with: *"The residuals are therefore: any interactive session (and its whole subagent tree) started anywhere other than a repository worktree root, including one level down inside the repository."* The adjacent overclaim *"so agent sessions are covered"* is likewise corrected to *"SUPERVISOR-launched workers always start with `cwd` set to the worktree ROOT … so supervised sessions are covered"* — accurate, and it preserves the true supervisor mitigation without letting it read as blanket agent coverage. ✓
- **Operational rule + owner-gated close-out both recorded:** *"**Operational rule (smallest next step):** start orchestrator and interactive sessions FROM a repository worktree root. **Smallest owner-gated close-out:** an owner-installed managed settings file (an owner-machine action outside repository scope, deliberately not performed by this task)."* ✓

**`M0-T077-fresh-session-proof.md` §5** — carries the parallel disclosure, corrects *"Supervised workers always launch at the worktree root and are therefore covered"* to *"SUPERVISOR-launched workers…"*, and adds one sentence that is stronger than what I requested and is the right thing to say: *"The fresh-process runs in this report measure what a NEW session gets; they do not retrofit protection onto an already-running session."* That names the exact reason the evidence set and the lived exposure diverged. ✓

**Residual-overclaim sweep at `f254698`.** `grep -ril` for `"agent sessions are covered"`, `"one level down"`, `"residual is a HUMAN"`, and `"HUMAN starting"` across `docs/MCP_DEFAULT_DENY_POLICY.md` and every `M0-T077-*.md`:

- The policy doc and the fresh-session proof — **the two normative documents** — return **no match** for any of the four. ✓
- Remaining hits are only in `M0-T077-review-G3.md` and `M0-T077-review-G5.md` (verbatim preserved reviewer text, correctly immutable historical record) and in `M0-T077-submission.md`, where the phrase appears **inside quotation marks describing what was corrected** (*"the two sentences that narrowed the residual to \"a HUMAN starting a session one level down\" are corrected"*). Correct usage, not a live claim.

Positive-coverage check: `subagent`, `per-process`/`once per`, `inherit`/`INHERIT`, and `worktree root` now each appear in **both** normative documents — up from zero hits for the first three when I ran the same sweep during the review.

## Item 3 — counts refreshed correctly ✓

**Submission report**, verified against ground truth rather than the diff alone:

| Claim | Was | Now | Ground truth |
|---|---|---|---|
| validator size | "~210 lines" | "~310 lines" | `wc -l tools/validate_mcp_policy.py` = **310** ✓ |
| test count (table) | "28 tests" | "35 tests" | `python tools/test_mcp_policy.py` → **Ran 35 tests … OK** ✓ |
| test count (self-check) | "28/28 OK" | "35/35 OK" | same ✓ |
| validator description | "every policy invariant … consumer-discard shape guards" | "exact policy-key values, merge preservation, and a whole-file shape assertion" | matches the shipped p1–p9 design ✓ |

`python tools/validate_mcp_policy.py --check` → exit **0** at `f254698`. A new "G5 correction" section records both F-1 and F-2 honestly, including the line *"The enforcement blob `dd11cd79…` did not change."*

**PR #240 body** (head now `f254698…`) refreshed correctly on all three points I raised:

- "five officially supported keys" → *"six officially supported policy entries"*, now explicitly listing *"the un-overridable deny-first tool rule `permissions.deny: [\"mcp__*\"]`"*. ✓
- "18 removal/weakening regressions" → *"35 removal/weakening regressions"*, with the validator described as a whole-file shape assertion *"because one mistyped key makes Claude Code silently discard the entire settings file."* ✓
- Beyond the refresh, the body's Proof section now surfaces both disclosed limitations to any PR reader: *"sessions started in a repository SUBDIRECTORY load no project settings, and subagents INHERIT the connector set of a parent session started outside a worktree root — operational rule: start sessions from a repository worktree root; owner-gated close-out: managed settings."* ✓

## Incidental checks

- **Gate record** `project-control/gates/M0-T077-G5.json`: `result: PASS`, `reviewer: security-reviewer`, `role: independent_review`, `report_file` pointing at the preservation file, `reviewed_sha: 6666dc7e…`, manifest `dce3b584…`. Correct.
- **Preservation file** `project-control/reports/M0-T077-review-G5.md` (160 lines): header truthfully labels the text VERBATIM, names the fresh-replacement circumstance, records the verdict as "PASS with one required correction — recorded as gate G5 PASS per the gate-verdict semantics rule; the section-4 F-1 documentation correction is BLOCKING for acceptance." Body matches what I sent.
- **Secret re-scan of the 234 newly added lines** (`a861c4d..f254698`): `dyiv` followed by an alphanumeric = **0**; JWT, `postgres://`, and `Bearer <token>` patterns = **0**. Six patterns (`sbp_`, `sb_secret`, `service_role`, `sk-ant-`, `ghp_`, `github_pat_`) each show one hit — all on **line 36 of my own preserved G5 report**, which is the probe-3 row *listing the pattern names I scanned for*. Confirmed to be bare prefixes: every one of them followed by a 6+ character value-like token returns **0**. `python .github/scripts/secret_scan.py` at `f254698` → **PASS, no findings**, exit 0, with no new allowlist or pragma entries required.

## One note for the acceptance record (not a finding)

The G5 gate is recorded at `reviewed_sha: 6666dc7e…`, and the blocking correction landed afterwards at `f254698`. That ordering is correct and mirrors the G3 precedent, but it means the gate record alone does not evidence the closure. Acceptance should therefore be recorded at an identity **at or after `f254698`**, with this confirmation as the evidence that the pre-acceptance blocking item is closed.

---

**Bottom line:** G5 F-1 and F-2 are both closed. The disclosure is accurate, complete, and free of the narrowing that produced the finding; the enforcement blob `dd11cd79…` is untouched, so no prior probe result is invalidated; the counts and PR body match shipped reality. I have no remaining findings against this task. My unchanged not-testable items stand as listed in §3 of the original report — chiefly user-scope allowlist broadening, managed-settings precedence, and a live supervised worker launch, all three blocked by D-020's own prohibitions rather than by anything this task did.
