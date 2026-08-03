# M0-T035 — G5 report (VERBATIM reviewer return)

**Orchestrator header (NOT part of the reviewer's return).** Independent `security-reviewer`
(spawn name `m0t035-g5`), dispatched read-only at frozen identity `d5a548e3…` / branch
`task/M0-T035-d006-edits` HEAD `f3635da`, spawned **pinned Fable 5** (restored regime; the
reviewer's honest disclosure below matches). Delivery provenance: the reviewer's role is denied
all shell file-writes by `readonly_agent_guard.py` (the guard fired exactly as designed — a live
positive control of the B-015 hardening), so the report arrived through the agent-return channel
and is preserved here verbatim, unaltered. R024 scan before commit: clean (the reviewer wrote
with repository-relative paths only).

**VERDICT: PASS** — zero blocking defects; observations O1–O4 non-blocking.

---

# G5 Security / Control-Integrity Gate Report — M0-T035

**Task:** M0-T035 — D-006 Section 3/5.2 edits: ORCHESTRATION_POLICY model-tiering amendment + code-graph awareness lines in eight agent definitions
**Gate:** G5 (security / control integrity), independent review
**Reviewer:** security-reviewer (spawned identity `m0t035-g5`), read-only
**Runtime model disclosure (honest):** Claude Fable 5 (`claude-fable-5`), spawned pinned. This is my actual runtime model.
**Review date:** 2026-08-02 (session clock; ledger timestamps for this task carry 2026-08-03 UTC)
**Verdict: PASS** — zero blocking defects; four non-blocking observations (O1–O4) below.

## 0. Frozen-identity verification (performed first, myself)

- `git rev-parse HEAD` on branch `task/M0-T035-d006-edits` returned `f3635dad60710046c212299e67b0682400df8079` at review start — **MATCH** with the frozen identity in my dispatch.
- Content identity **re-derived independently**: I imported the repository's own `tools/directive_registry.py` and computed `frozen_git_identity` over the task packet's `allowed_paths` at commit f3635da with `exclude_prefixes=("project-control/",)` and `control_plane_prefixes=("project-control/",)` (the exact parameterization of `_task_git_identity` in `tools/project_control.py`). Result: `d5a548e3264702e894a8179275b669eba761f661ddf12c1c3f92045092437092` — **MATCH** with the stamped identity (full value; the dispatch prefix `d5a548e3264702e8` matches).
- Cross-check: the G2 gate record and submit record stamp this same identity at reviewed_sha `6674f77` (the pre-lifecycle commit); my re-derivation at f3635da (which adds only lifecycle records) yields the identical value — confirming the control-plane material-identity design works as intended: lifecycle bookkeeping does not move the identity.
- **Environmental note (O4, non-blocking):** between my first verification command and later commands, the primary checkout was moved by the orchestrator to `control/D-007-supervisor-capture` at `62a247e`. I verified HEAD on the task branch **before** the move and completed the entire review against the immutable commit object `f3635da` via git plumbing (`git show`, `git diff 62a247e..f3635da`, `git ls-tree`), touching no checkout state. All findings bind to f3635da regardless of checkout position. The orchestrator should be aware that the checkout moved mid-review wave.

## 1. Authority containment — PASS

`git diff --name-status 62a247e..f3635da` touches exactly 17 files: `.claude/ORCHESTRATION_POLICY.md` (+13 lines, one new section), the eight named agent definitions (each exactly one line modified: `.claude/agents/backend-engineer.md`, `frontend-engineer.md`, `code-reviewer.md`, `security-reviewer.md`, `qa-engineer.md`, `rules-engineer.md`, `geospatial-engineer.md`, `data-contract-verifier.md`), and eight control-plane files under `project-control/` (two gate records, four reports, `state.json`, the task packet). **No** hooks, settings, rules, skills, or any other `.claude/` path; **no new file** under `.claude/agents/`; no frontmatter hunk in any agent definition (every hunk is in the body prose line). The `state.json` delta is lifecycle-only (adds `M0-T035` to the active list, updates timestamp). This is exactly the D-006-R027 envelope ("only the Section 5.2 one-line additions, the Section 3 policy amendment text…"). The Section 7 fallback (one new sweep-identity definition) was **not** engaged, consistent with the packet.

## 2. Effort-key hold (D-004-R159 permanent) — PASS

I grepped the entire delta (`git diff 62a247e..f3635da | grep -i effort`). The word appears on 4 added lines, **all** of them prose *about* the prohibition (the packet's AS-1 text, the producer report's SC-2 self-check documenting a zero-match grep, and a progress-log message). **No effort key, knob, field, or setting is introduced anywhere.** The new policy section and the eight sentences contain no effort language at all.

## 3. Read-only reviewer discipline — PASS

- `--no-regen` is real: `tools/code_graph/query.py` at f3635da defines `parser.add_argument("--no-regen", action="store_true", ...)` (line 407) and threads it through `load_graph` (lines 103–112, 445).
- The three read-only reviewer definitions (`code-reviewer`, `security-reviewer`, `data-contract-verifier`) received the variant sentence with `--no-regen` and the clause "if the cache is stale or missing, report that fact instead of regenerating (reviewers never run write-producing commands)". The sentence is permissive-read-only ("you may consult"); it cannot be read as authorizing writes — it explicitly restates the no-write rule.
- The five producer-variant sentences grant no new authority: "you may consult" a read-oriented query CLI is within existing producer tool access; no sentence touches ledger, git, gh, or acceptance authority. The layered read-only enforcement described in ORCHESTRATION_POLICY §2 (disallowedTools, PreToolUse guard `.claude/hooks/readonly_agent_guard.py`) is untouched by this diff.
- **Observation O3 (LOW, non-blocking, directive design not implementation defect):** `qa-engineer` received the producer variant (no `--no-regen`) yet sometimes acts as a G4 reviewer. This exactly matches D-006 Section 5.2, which confines the variant to the three named read-only roles; qa-engineer is not one of the six read-only-enforced roles, and deviating from the authorized text would itself have violated R027. Recording for the owner's awareness only.

## 4. Injection / supply-chain surface — PASS

- `git ls-tree f3635da tools/code_graph/` shows the tool is repository-tracked (`README.md`, `generate.py`, `query.py`); nothing is fetched.
- I scanned both files at f3635da for `urllib|requests|socket|http|subprocess|os.system|eval(|exec(`: **zero matches** in either file. The tool is a deterministic local parser with no network, no shell-out, no dynamic code execution. No untrusted-text execution path is created; the wired sentence marks output "advisory only — verify every material conclusion in actual source", which also defuses graph-content-as-authority injection.
- No dependency added, no lockfile or package-manifest file in the diff (confirmed by name-status).

## 5. Model-tiering policy text — PASS

The new ORCHESTRATION_POLICY section preserves every load-bearing constraint of D-006 Section 3: spawn-level only; one model per spawn; gate-class reviewer spawns "always carry their explicitly pinned model (D-004 R226/R161/R275)"; sweep identity is auditor-class (`progress-auditor` default), non-gate, non-producer, mechanical-read-only work only; "**Data, never judgment**" with the full enumeration (ruling, verdict, severity, interpretation, acceptance-grade conclusion, security/contract/geospatial/control-plane judgment) staying on the pinned or session model; dispatch must name each sweep spawn, model, exact scope, and the report records the split; "**Gate-class floor.** Gate-class reviewer identities are never spawned on a lower model for any phase"; and the closing "never downgrade judgment to save tokens." It declares itself an extension of the §2 Model policy ("it replaces nothing"), and §2's own faster-model carve-out (bounded read-only sweeps by the repository auditor) is consistent with the new section. **The text cannot reasonably be read as weakening gate-reviewer pinning or authorizing judgment on lower models.** Observation O2 (INFO): the implemented section omits the directive's Section 7 fallback clause authorizing one new sweep-identity definition — a strictly more restrictive rendering, matching the packet's "Section 7 fallback is NOT engaged"; textual-fidelity nuances are G3's ruling, but from the security side the omission removes an authorization rather than adding one.

## 6. Evidence hygiene (R024, public repo) — PASS with one precedented pattern

I scanned **every added line** of the delta with pattern classes (describing, never quoting): OS usernames; absolute drive-letter paths in both slash forms; POSIX-mapped user paths; hostname patterns; tmux/pane/session-id patterns; email addresses; secret/token signatures (cloud key prefixes, PAT prefixes, JWT header, PEM header, bearer tokens). Results: **zero** usernames, absolute user paths, hostnames, session ids, pane ids, emails, or secret-shaped strings. The only identifier-class matches are two adjacent lines in the producer report recording the producer's repository-relative worktree path and branch name, each containing a runtime agent-spawn id (**Observation O1**, non-blocking): the same pattern appears in ten-plus previously committed and accepted reports (M0-T030, M0-T033, M0-T034 among them), is repository-relative, and carries no user or host information.

## 7. Control-plane records — PASS

At f3635da: `project-control/gates/M0-T035-G0.json` (reviewer `orchestrator`, role `administrative`, PASS, stamped at the pre-work identity `6a3345c4660bd09b2a411ba16ce30f35df63f10091e0038ea5354f1ebfbe7785` / reviewed_sha `62a247e` — I independently re-derived that pre-work identity too and it matches) and `project-control/gates/M0-T035-G2.json` (reviewer `orchestrator`, role `self_check`, PASS, stamped at the in-regime identity `d5a548e3…` / reviewed_sha `6674f77`). Both are the two gate classes the reserved-identity rule permits the orchestrator to author (M0-T014 G5 defect-D1 regime); both judgment gates (G3, G5) went to independent reviewers. The submit record `project-control/reports/M0-T035.json` is stamped with the same in-regime identity and sha, requests `awaiting_gate`, names producer `backend-engineer`, references the evidence map, and lists the nine applicable D-006 requirement rows (R017/R018/R019/R020/R023/R026/R027/R028/R030) matching the packet. Task packet at f3635da is `awaiting_gate`. Lawful shape throughout.

## Defect summary

No CRITICAL, HIGH, or MEDIUM defects. Non-blocking observations: **O1** (LOW/INFO) worktree agent-id lines in the producer report, precedented and repository-relative; **O2** (INFO) Section 7 fallback clause omitted from the policy section — strictly more restrictive, matches packet intent; **O3** (LOW) qa-engineer's wired sentence lacks `--no-regen` by directive design despite its occasional reviewer role — owner-awareness only, implementation exactly matches the authorization; **O4** (process note) the primary checkout moved off the frozen branch mid-review — review completed against the immutable commit object, no impact on findings.

## Reproduction commands (run from repository root; frozen commit `f3635da`)

1. `git diff --name-status 62a247e..f3635da` — 17-file containment (dimension 1).
2. `git diff 62a247e..f3635da -- .claude/` — full authorized-edit inspection (dimensions 1, 3, 5).
3. `git diff 62a247e..f3635da | grep -in effort` — effort-key sweep (dimension 2).
4. `git show f3635da:tools/code_graph/query.py | grep -n "no.regen"` and `git ls-tree f3635da tools/code_graph/` — flag reality and tool provenance (dimensions 3, 4).
5. Identity re-derivation: python one-off importing `tools/directive_registry.frozen_git_identity` over the packet's `allowed_paths` at `f3635da` with `exclude_prefixes=("project-control/",)`, `control_plane_prefixes=("project-control/",)`, `require_clean=False` (clean-stamp precondition unavailable off-HEAD; identity is git-blob-canonical so the value is unaffected).
6. `git show f3635da:project-control/gates/M0-T035-G0.json`, `…G2.json`, `git show f3635da:project-control/reports/M0-T035.json` — record shapes (dimension 7).

**VERDICT: PASS.** The M0-T035 delta is exactly within the D-006-R027 authorization, introduces no effort key, no write authority, no injection or supply-chain surface, no hygiene leak beyond a precedented repository-relative worktree id, and its control-plane records are lawfully shaped at a verified frozen identity. Reviewed read-only on Claude Fable 5 (spawned pinned); no repository files written, no checkout state touched.
