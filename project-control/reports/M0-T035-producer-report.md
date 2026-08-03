# M0-T035 — Producer report

**Task:** D-006 Section 3/5.2 edits — ORCHESTRATION_POLICY model-tiering amendment + code-graph awareness lines in eight agent definitions
**Producer identity:** `backend-engineer` (isolated worktree)
**Worktree:** `.claude/worktrees/agent-aa345382c345e1875`
**Branch:** `worktree-agent-aa345382c345e1875`
**Base HEAD at claim (frozen head for this report):** `62a247e8e28d5630f5c052cd475102059614acfd`
**Directive refs:** D-006 (source-001.md Sections 3, 5.2, 7); applicable rows R017/R018/R019/R020/R023/R026/R027/R028/R030
**Requested status:** `awaiting_gate`

Authority note (ADR-005): this producer did NOT run `tools/project_control.py`, `git commit`, `git push`, or `gh`. All git commands run were read-only (`status`, `diff`, `hash-object`, `rev-parse`, `config`). The orchestrator integrates.

---

## 1. Files changed

`git diff --stat` (working tree vs. `62a247e`):

```
 .claude/ORCHESTRATION_POLICY.md          | 13 +++++++++++++
 .claude/agents/backend-engineer.md       |  2 +-
 .claude/agents/code-reviewer.md          |  2 +-
 .claude/agents/data-contract-verifier.md |  2 +-
 .claude/agents/frontend-engineer.md      |  2 +-
 .claude/agents/geospatial-engineer.md    |  2 +-
 .claude/agents/qa-engineer.md            |  2 +-
 .claude/agents/rules-engineer.md         |  2 +-
 .claude/agents/security-reviewer.md      |  2 +-
 9 files changed, 21 insertions(+), 8 deletions(-)
```

Plus this report (`project-control/reports/M0-T035-producer-report.md`, new file — untracked at the time the diff above was taken, therefore not in `git diff --stat`).

No other path was created, modified, or deleted. No new agent definition. No frontmatter line in any agent file was touched (every agent-file hunk is a single body-prose line: lines 12–15, all below the closing `---` of the frontmatter).

---

## 2. Per-file change detail (exact added text)

### 2.1 `.claude/ORCHESTRATION_POLICY.md` — new section (13 inserted lines)

Placement: immediately after the end of §2 (the section that carries the existing **Model policy** and **Producer confinement** paragraphs), before the `---` rule that precedes `## A. Lead-only authority`. This puts the tiering rule directly after the existing model/spawn rules it extends, and leaves the A–H lettered subsections and §3 untouched.

Exact inserted text:

```markdown
## Model tiering for mechanical work (D-006 Section 3)

**Source:** owner directive D-006 Section 3 — `project-control/directives/D-006-dispatch-efficiency-and-graph-wiring/source-001.md` (a spawn-level amendment to this policy). This section extends the §2 **Model policy** rule above; it replaces nothing.

Tiering is **spawn-level only**. D-004's live spawn rules bind **one model per spawn**, and gate-class reviewer spawns always carry their explicitly pinned model (D-004 R226/R161/R275); no per-phase model mechanism exists inside a spawn.

- **Mechanical-sweep identity.** A non-gate, non-producer, **auditor-class** identity — the existing `progress-auditor` definition by default — may be spawned on a faster model, selected at dispatch, for bounded, read-only, **mechanical** work only: pattern scans, digest computation and comparison, occurrence counting, file inventory, diff reconstruction, and grep sweeps.
- **Data, never judgment.** A sweep's output is data (counts, paths, hashes, matches), never judgment. Every ruling, verdict, severity, interpretation, acceptance-grade conclusion, and every security, contract, geospatial, or control-plane judgment remains on the pinned or session model. Producer model rules are unchanged (the D-004-R298 producer ceiling governs producers).
- **Dispatch and reporting.** A dispatch that uses mechanical-sweep spawns names each spawn, its model, and its exact scope; the consuming reviewer cites the sweep's data as input evidence and remains solely responsible for the ruling; the report records the split.
- **Gate-class floor.** Gate-class reviewer identities are never spawned on a lower model for any phase. If D-004's spawn rules would be violated by this mechanism as specified, stop and propose a D-004 amendment rather than proceeding.

The existing prohibition stands: **never downgrade judgment to save tokens.**
```

(The 13th inserted line is the trailing blank line before the existing `---`.)

Constraint-by-constraint trace to D-006 source-001.md §3 (AS-3):

| D-006 §3 constraint | Where carried |
|---|---|
| spawn-level only; one model per spawn; gate-class spawns carry pinned model (R226/R161/R275) | paragraph 2 |
| sweep identity is non-gate, non-producer, auditor-class; `progress-auditor` by default; faster model selected at dispatch; bounded read-only mechanical work only, with the six named work kinds | bullet 1 |
| output is data (counts, paths, hashes, matches), never judgment; every ruling/verdict/severity/interpretation/acceptance-grade conclusion and security/contract/geospatial/control-plane judgment stays on the pinned or session model; producer model rules unchanged (R298 ceiling) | bullet 2 |
| dispatch names each spawn + model + exact scope; consuming reviewer cites sweep data as input evidence and remains solely responsible for the ruling; report records the split | bullet 3 |
| gate-class reviewer identities never on a lower model for any phase; if D-004 spawn rules would be violated, stop and propose a D-004 amendment | bullet 4 |
| never downgrade judgment to save tokens | closing line |

Section 7 fallback NOT engaged: `progress-auditor` is compatible, so no new agent definition was created.

### 2.2 Five producer/QA definitions — one sentence appended to the final body paragraph

Files: `.claude/agents/backend-engineer.md`, `.claude/agents/frontend-engineer.md`, `.claude/agents/qa-engineer.md`, `.claude/agents/rules-engineer.md`, `.claude/agents/geospatial-engineer.md`.

Exact sentence added (identical in all five, appended after the last existing sentence of the role-guidance paragraph that already covers navigation/evidence practice, before the `## Ledger and integration protocol` heading):

```
For dependency/impact/who-consumes questions not answered by the packet's navigation block, you may consult `python tools/code_graph/query.py` (advisory only — verify every material conclusion in actual source; see tools/code_graph/README.md) before broad Grep/Glob/Read sweeps.
```

Anchor sentence each was appended to:

- `backend-engineer.md` (line 13): "…External sources use connector abstractions and fixtures."
- `frontend-engineer.md` (line 15): "…Create Playwright human-journey scenarios."
- `qa-engineer.md` (line 13): "…never edit implementation while acting as reviewer."
- `rules-engineer.md` (line 13): "…G6 and human approval are mandatory."
- `geospatial-engineer.md` (line 13): "…Distinguish boundary touches from material overlap."

### 2.3 Three read-only reviewer definitions — one `--no-regen` variant sentence

Files: `.claude/agents/code-reviewer.md`, `.claude/agents/security-reviewer.md`, `.claude/agents/data-contract-verifier.md`.

Exact sentence added (identical in all three):

```
For dependency/impact/who-consumes questions not answered by the packet's navigation block, you may consult `python tools/code_graph/query.py --no-regen` (advisory only — verify every material conclusion in actual source; see tools/code_graph/README.md) before broad Grep/Glob/Read sweeps; if the cache is stale or missing, report that fact instead of regenerating (reviewers never run write-producing commands).
```

Anchor sentence each was appended to:

- `code-reviewer.md` (line 12): "…Save a gate report with reproducible findings."
- `security-reviewer.md` (line 12): "…Record a G5 report."
- `data-contract-verifier.md` (line 13): "…Record a G1 PASS/FAIL/BLOCKED report."

Flag existence verified read-only (no write to `tools/**`): `--no-regen` is a real CLI flag — `tools/code_graph/query.py:407` (`parser.add_argument("--no-regen", action="store_true", …)`), documented at `tools/code_graph/README.md:146` and `:154` (under `--no-regen` it prints a one-line `STALE (...)` error and refuses to regenerate).

---

## 3. Self-check results

### SC-1 — Scope containment (AS-1)

`git status --porcelain` (before this report file was written):

```
 M .claude/ORCHESTRATION_POLICY.md
 M .claude/agents/backend-engineer.md
 M .claude/agents/code-reviewer.md
 M .claude/agents/data-contract-verifier.md
 M .claude/agents/frontend-engineer.md
 M .claude/agents/geospatial-engineer.md
 M .claude/agents/qa-engineer.md
 M .claude/agents/rules-engineer.md
 M .claude/agents/security-reviewer.md
```

Exactly the 9 authorized edit paths; 0 additions, 0 deletions, 0 renames. Nothing under `.claude/hooks/`, `.claude/rules/`, `.claude/skills/`, `.claude/settings*.json`, `tools/`, `.github/`, `services/`, `apps/`, `packages/`, or `CLAUDE.md`. No new file under `.claude/agents/`. `tools/code_graph/**` unmodified (read only).

### SC-2 — No `effort` key (D-004 standing hold)

```
$ git diff -U0 | grep -c -i "effort"
0
(grep exit 1)
```

Zero matches of any case of "effort" anywhere in the diff — therefore no new `effort` key.

### SC-3 — Exactly one added sentence per agent file, no frontmatter change

`git diff -U0 -- .claude/agents/` shows exactly one hunk per file, each `@@ -N +N @@` (1 line replaced by 1 line): backend-engineer @13, code-reviewer @12, data-contract-verifier @13, frontend-engineer @15, geospatial-engineer @13, qa-engineer @13, rules-engineer @13, security-reviewer @12. Every one of those line numbers is in body prose below the frontmatter terminator; no `name:`, `description:`, `tools:`, `disallowedTools:`, `model:`, `permissionMode:`, `isolation:`, `memory:`, or `skills:` line appears in the diff.

### SC-4 — Reviewer variants carry `--no-regen` (AS-2)

```
$ grep -c -- "--no-regen" .claude/agents/*.md
.claude/agents/code-reviewer.md:1
.claude/agents/data-contract-verifier.md:1
.claude/agents/security-reviewer.md:1
… all 22 other agent definitions: 0
```

All 8 wired files contain exactly one occurrence of the literal `advisory only` (verified by byte count = 1 each), and each cites `tools/code_graph/README.md`.

### SC-5 — Advisory-only phrasing preserved (D-006-R019 / D-005 amendment 2)

```
$ git diff -U0 | grep -n -i -E "must (use|consult|run) .*(graph|query\.py)|required to (use|consult)|always (use|consult) .*graph"
(no output; exit 1)
```

No mandatory-use phrasing was introduced. Every wired sentence is permissive ("you may consult"), explicitly labelled "advisory only", and instructs verification in actual source.

### SC-6 — Directive-compliance validator (AS-4)

```
$ python tools/validate_directive_compliance.py --check
validator exit: 0
```

Exit 0 with no findings printed. Expected: no registry file was changed by this task.

### SC-7 — Environment probe

`python --version` → `Python 3.11.9`. Full command execution and repo read access were available in this session; no permission denial occurred at any point.

---

## 4. SHA-256 of the 9 edited files (final bytes)

Working-tree files are **CRLF** on disk (repo has a root `.gitattributes`; local `core.autocrlf=true`, so committed blobs are LF). Both identities are given so the orchestrator can verify a byte-for-byte port either way.

### 4.1 SHA-256 of working-tree bytes (CRLF, as they exist in the worktree)

| SHA-256 | bytes | path |
|---|---|---|
| `59a4169718f33242fccbb25f2689bdc66304c4a96a7c65a80f20e396bbb51b3f` | 13562 | `.claude/ORCHESTRATION_POLICY.md` |
| `78d04b5c6eab78d1b5aab0688184e255fa119b0e4a8f04e6d34ed101df5c6707` | 1971 | `.claude/agents/backend-engineer.md` |
| `7b892a32aa18a9512750ca778769a93fe758ada00c1133b58542e8adcfd757cb` | 1988 | `.claude/agents/frontend-engineer.md` |
| `136d78dcfc81ba3d26fe877f4a4c08cb042463ce76c9993076914f481b25aae6` | 1764 | `.claude/agents/qa-engineer.md` |
| `25d76f7fdafc41bd02a1bae7bb2a5efc6e5a4ee7b9a955d7dea1fead71db84a9` | 2006 | `.claude/agents/rules-engineer.md` |
| `0d058c0aa67979c4d0e9d78d9dcf0d2a6314ea1622694b7d3f90388c272a9d90` | 1940 | `.claude/agents/geospatial-engineer.md` |
| `c92a7d0cf94dcc93377736dd15baede452eb6c607b64adb4d43273323da9117d` | 1554 | `.claude/agents/code-reviewer.md` |
| `ddc44813490029d915cc83e6a9495e035b4220a1d449a6181dd4525f3a95e1f0` | 1678 | `.claude/agents/security-reviewer.md` |
| `361f1cf2ac01c0611975d181b0138e7af58d92dae86028c11bbc7f11d84d6f6f` | 1662 | `.claude/agents/data-contract-verifier.md` |

### 4.2 SHA-256 of LF-normalized bytes (what git stores / what a LF checkout yields)

| SHA-256 (LF) | bytes | path |
|---|---|---|
| `8236b9c46ef1dbf3015b5954592a5d462dbd7bc582b79cb8ce0eccd5950e419b` | 13443 | `.claude/ORCHESTRATION_POLICY.md` |
| `74ac099231ff29bc9082af0cacb7b42d27a977473aea3e832cda535367927c09` | 1954 | `.claude/agents/backend-engineer.md` |
| `d3951c03577cd68d44a9889259c3fffd4491e6e9080b51d5dce7720049667540` | 1969 | `.claude/agents/frontend-engineer.md` |
| `ffce360c427a3bba80c8faaf07a3b7d935c00e45ede57899501a588fb3d1eef0` | 1747 | `.claude/agents/qa-engineer.md` |
| `f3775ff5d8f275be9871f308480c7feeb91df9349e9e9cc604e5738979177b0b` | 1989 | `.claude/agents/rules-engineer.md` |
| `0990f900528d1f5282542d88cf5bcce0c7d060e440932a5e6308ae0116b69c78` | 1923 | `.claude/agents/geospatial-engineer.md` |
| `3e06636279500ee3182fa8ba9b7b18e544fe30cf9c62b1fccf90fa4bc5f92ee2` | 1538 | `.claude/agents/code-reviewer.md` |
| `41994fc4f31456b7945770c62b5a967799a851771b1afe80fbd210d614843cfc` | 1662 | `.claude/agents/security-reviewer.md` |
| `37ed7fd7e44a14208a5bfc396d388507e4c9e27c4a8bf8a08274fa2fdd6888a6` | 1645 | `.claude/agents/data-contract-verifier.md` |

### 4.3 Git blob identity (`git hash-object`, post-normalization)

```
10120decb0090ab443a5c60fc99f61b04e52035f  .claude/ORCHESTRATION_POLICY.md
4fd1abc2a192dbdc9605c7675410c1f635a45645  .claude/agents/backend-engineer.md
0106b81735dd5c34c0a4c0899eb125e5cafc73f1  .claude/agents/frontend-engineer.md
d852cdef87fc0c3426b1f29472c515125eea4646  .claude/agents/qa-engineer.md
802d45370a20c1e28203691b9ea0b890b1ce75f2  .claude/agents/rules-engineer.md
d4e5ced307d3696348d1fd1213c335fc3bc0a457  .claude/agents/geospatial-engineer.md
ed681de3e35c316e8183cd492c1fa7e30311cc5e  .claude/agents/code-reviewer.md
e8c3d0221aabc35085b859d9715d8ce54a0f8508  .claude/agents/security-reviewer.md
bf94f74d9895fee0050e0f7569c37ce84e19ef29  .claude/agents/data-contract-verifier.md
```

---

## 5. Model disclosure (honest)

This producer spawn was dispatched with an explicit Opus 5 model value under the D-004-R298 producer ceiling. The runtime model reported to this agent by its own environment is **Opus 5 (1M context), model id `claude-opus-5[1m]`**. That is the model that performed every edit and self-check in this report. This is a self-report of the runtime environment string, not an independently attested measurement; the orchestrator holds the authoritative dispatch record.

---

## 6. N=6 adoption measurement note (D-006 §6 / D-006-R024) — dispatch 1 of 6 (producer)

**Dispatch class:** producer (writing, worktree-isolated). **Model:** Opus 5 (`claude-opus-5[1m]`), single model for the whole spawn — no model tiering, no mechanical-sweep spawn was used or needed for this dispatch (the packet named every file).

**Scope statement (as dispatched, D-006 §1 delta scope + §5 exact-file packet):** exactly 10 paths — `.claude/ORCHESTRATION_POLICY.md`, the 8 named `.claude/agents/*.md` definitions, and `project-control/reports/M0-T035-producer-report.md`. Reads outside the write scope were bounded and enumerable: `project-control/directives/D-006-dispatch-efficiency-and-graph-wiring/source-001.md` (the authorizing text), `project-control/tasks/M0-T035.json` (the packet), and a targeted read-only grep of `tools/code_graph/` to confirm the `--no-regen` flag exists. **No whole-tree scan was performed** and none was needed: total files opened = 12; total content greps = 3, all path-bounded.

**Settled findings cited, not re-derived (D-006 §2):** that D-006 was captured and issued on the M0-T027 acceptance condition; that `progress-auditor` is a compatible sweep identity (settled in the packet, so the §7 fallback is not engaged); and the R307 disposition recorded at capture. None were re-verified by this producer, and none needed to be for these edits.

**Graph-usage visibility (D-006 §5.4):** this dispatch involved **no** dependency/impact/who-consumes question — the packet named every target file explicitly — so `tools/code_graph/query.py` was **not** run. Stated reason direct navigation was chosen: the exact-file packet supplied the complete file set; a graph query would have added cost with zero navigational value.

**`/usage` figures — honest limitation:** the D-006 §6 instrument asks for `/usage` Session figures at dispatch start and end. **These are not observable from inside a spawn.** A subagent cannot invoke the `/usage` slash command (slash commands are an interactive client surface, not an agent tool), and no per-spawn token accounting is exposed to the agent's own context. I therefore report **no** start/end `/usage` numbers rather than estimating them, per the standing rule against unmeasured savings claims (D-005-R039). If per-dispatch figures are required for the N=6 series, they must be captured by the orchestrator/session side at dispatch start and end, or from the platform's usage surface — the producer side of the split can supply only the scope statement, model, and qualitative navigation record above, all of which are given.

**No saving is claimed** by this report for any D-006 lever.

---

## 7. Assumptions, limitations, and uncertainty disclosed

1. **Section placement judgment.** The packet left the ORCHESTRATION_POLICY insertion point to producer judgment ("choose the location that reads naturally"). I placed the new section at the end of §2, directly after the existing **Model policy** / **Producer confinement** paragraphs and before the `---` preceding `## A. Lead-only authority`, and I gave it a plain title (no `2a.`/letter prefix) so the title matches the packet string exactly. A reviewer preferring a lettered or numbered placement should treat this as a style finding, not a content one; the constraint set is unaffected.
2. **Sentence attachment style.** Each agent-file sentence was appended to the end of an existing paragraph rather than added as a standalone paragraph, so the diff is exactly one changed line per file. This satisfies "exactly one added sentence" and makes scope containment trivially auditable.
3. **`D-004-R298` label.** D-006 §3 says "R298's ceiling governs producers" without the `D-004-` prefix; I wrote `D-004-R298` in the policy text because ORCHESTRATION_POLICY.md is read outside the D-004 context and bare `R298` would be ambiguous there. The other D-004 rule ids appear as `D-004 R226/R161/R275`, matching the source's own form.
4. **Not verified by me (out of scope):** the D-006 requirements.json row texts (I worked from `source-001.md` Sections 3/5.2/7 and the packet), and whether any other document cross-references ORCHESTRATION_POLICY §2 by ordinal in a way the new untitled-number section could disturb (I added no number, which minimizes that risk, but I did not sweep for cross-references — that would have required a whole-tree scan the delta scope excludes).
5. **CRLF/LF.** Working-tree bytes are CRLF; committed blobs will be LF under `core.autocrlf=true`. Any per-file hash verification during the port must state which identity it is comparing (§4.1 vs §4.2).

---

## 8. Requested status

`awaiting_gate` — G0/G2/G3/G5 as contracted. Producer did not and cannot record any ledger transition (ADR-005); the orchestrator records claim/progress/submit and integrates the branch.
