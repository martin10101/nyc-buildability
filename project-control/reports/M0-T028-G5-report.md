# M0-T028 — G5 independent security review (verbatim reviewer return)

Preservation note (report-preservation rule, `.claude/rules/project-control.md`): the reviewer
returned this report through the agent-return channel; it is saved verbatim below with transport
entity-decoding only (`&lt;` -> `<`, `&amp;` -> `&`, `&gt;` -> `>`). Reviewer: security-reviewer
(read-only, explicit Fable 5 spawn). Frozen SHA reviewed: e8a7dbfa2145b76f91b8e5272769a1447a940525.

---

# Gate Report

- **Gate ID:** M0-T028-G5
- **Task ID:** M0-T028 (D-004 Step 3; blocker B-015 fix)
- **Reviewer:** security-reviewer (independent; read-only; not the producer)
- **Producer:** backend-engineer (diff ported by the orchestrator to `task/M0-T028-readonly-guard`)
- **Result: PASS** — with 4 required corrections that are BLOCKING for acceptance and for B-015 closure (recorded as PASS per `.claude/rules/project-control.md` gate-verdict semantics)
- **Clean environment/worktree used:** yes — `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\.claude\worktrees\M0-T028-readonly-guard`

**Frozen SHA pinned by me:**
```
git -C "<worktree>" rev-parse HEAD   -> e8a7dbfa2145b76f91b8e5272769a1447a940525   (matches the frozen SHA)
git -C "<worktree>" status --porcelain -> (empty)                                   (clean)
git -C "<worktree>" branch --show-current -> task/M0-T028-readonly-guard
git -C "<worktree>" merge-base 4a4bf2d5.. HEAD -> 4a4bf2d572edce963a355d9d997a2e05833c1dbf (base is ancestor)
git -C "<worktree>" log --oneline 4a4bf2d5..HEAD -> e8a7dbf  (single commit)
```

## Acceptance criteria reviewed

| AS | Verdict | Independently reproduced evidence |
|---|---|---|
| AS-1 (primary H1/H2 payload) | PASS (stored artifact verified + partially corroborated live) | `project-control/reports/M0-T028-TEAMMATE-PAYLOAD-EVIDENCE.md` present at the frozen SHA, internally consistent, sanitized. I independently corroborated **both halves I can reach**: the hook DOES fire for spawned agents (H1 refuted) and an **unnamed** spawn carries its roster role in `agent_type` — my own reviewer session was denied three times with `'security-reviewer' is operationally read-only: …`, a string that exists only in `readonly_agent_guard.py`. The named-spawn half is unreproducible for me (no Agent tool in my roster) and legitimately rests on orchestrator capture. |
| AS-2 (tool-unavailability reconciliation) | PASS | Evidence file §4. I verified the mechanism claim independently: all 7 governed roles carry `disallowedTools: Write, Edit, MultiEdit, NotebookEdit, Agent` + `permissionMode: plan` (`.claude/agents/*.md`), and my own live tool roster is Read/Grep/Glob/Bash/Skill with no write or MCP tools — the roster layer holds independently of payload identity, exactly as claimed. |
| AS-3 (sentinel denied by the guard itself) | PASS at unit level (live deferral recorded, verified as recorded) | Named-spawn sentinel payload denied by the guard, reason emitted by the guard and naming the spawn identity: `"permissionDecisionReason": "'m0t028-diag-probe' is operationally read-only: repository/GitHub/control-plane mutation and shell file-writes are blocked…"`. Live end-to-end deferral is recorded in the packet (risk 2, `owner_review_state`) and report §7.1 — a disclosed item, not a new finding. |
| AS-4 (no regression) | PASS | `python tools/test_readonly_agent_guard.py` → **131 checks, 131 PASS, 0 FAIL, exit 0** (my run). Plus my own two independent regression proofs below (base suite vs new guard: 89/89; 388-comparison decision differential: 0 weakenings). |
| AS-5 (R100 quoting) | PASS with LOW residual (L-3) | All four hook commands quoted (`.claude/settings.json:10,19,29,39`); key-delta vs base = only the three `args` arrays removed, **no keys added**; no machine paths. I additionally proved the new command string actually executes end-to-end under both shells with the real root (see "Steps independently executed" A/B). |
| AS-6 (R101 gitignore) | PASS | `git -C "<worktree>" check-ignore -v .claude/settings.local.json` → `.gitignore:64:.claude/settings.local.json` (repo file, not machine-global). Nested worktree copies were already covered by `.gitignore:57 .claude/worktrees/`. |
| AS-7 (R144 index.json) | PASS | Re-derived from source, not from the report: `project-control/directives/index.json` → `/directives[3]` `D-004` `affected_tasks = ["M0-T027","M0-T028"]` at the frozen SHA. Nothing left to correct; correctly not edited. |
| AS-8 (control plane + secret scan) | PASS (all reproduced by me) | `validate_directive_compliance.py` → `directive registry OK: 5 directive(s), 5 active…` exit 0; `test_project_control.py` → `OK: all 14 project-control test groups passed`; `test_directive_compliance.py` → `Ran 55 tests … OK`; `test_agent_dispatch_guard.py` → `ALL CHECKS PASSED`; gitleaks 8.30.1 on all 6 changed files → `no leaks found` (5 files scanned individually, all clean). |
| AS-9 (containment) | PASS | `git diff --name-status 4a4bf2d5..HEAD` = exactly 6 paths (4 code/config M + 2 reports A). Forbidden-path grep over the diff (M0-T025, pilot reports, `directives/`, master_plan/state/gates/checkpoints, `.claude/agents/`, `.claude/rules/`, CLAUDE.md, control CLI, services/apps/packages/render.yaml, settings.local.json) → **NONE**. No `effort` key: settings.json added-key set is empty; the only `effort` strings in the diff are prose in the two reports (see I-1). |
| AS-10 (B-015 closure) | Correctly NOT performed | `B-015` status at frozen SHA = `open`. Orchestrator-only, post-merge, post-live-sentinel. |

## Directive/requirement verification (security-relevant subset; full 286-row pass belongs to `directive-compliance-verifier`)

| Requirement ID | Reviewed SHA / content identity | Verdict | Reproduced evidence |
|---|---|---|---|
| D-004-R100 | e8a7dbf | PASS (LOW residual L-3) | All 4 hook commands single-string with double-quoted `${CLAUDE_PROJECT_DIR}` path; proven space-safe (shlex: 1 token; unquoted control: 2 tokens) and proven executable under `sh` and `cmd.exe` |
| D-004-R101 | e8a7dbf | PASS | `check-ignore -v` attributes the match to `.gitignore:64` |
| D-004-R132 | e8a7dbf | PASS | Neither pilot report appears in `diff --name-only`; no `project-control/directives/**` path touched |
| D-004-R134 / R135 | e8a7dbf | PASS (deferred-as-required, recorded) | Live re-run explicitly deferred in packet risk 2 / `owner_review_state` / report §7.1; not claimed as done |
| D-004-R139 / R140 | e8a7dbf | PASS | Task packet and both reports bind the work to B-015 under M0-T028 |
| D-004-R141 (scope a: evidence) | e8a7dbf | PASS | Primary payload artifact exists, weighs the tool-unavailability positive, names H2; corroborated live for the unnamed-spawn shape |
| D-004-R142 (scope b: reviewer-class teammates denied writes) | e8a7dbf | PASS for the B-015 failure mode; **partial-coverage residual flagged** (F-2) | Named/unknown identities: 63/63 mutating commands newly DENIED. Gap: `human-journey-reviewer` and `visual-quality-reviewer` — reviewer-class roster roles that ADR-005 line 20 classifies read-only — still pass through when spawned UNNAMED (pre-existing at base, now codified by the new docstring) |
| D-004-R143 (scope c: tests) | PASS | Sentinel case + R100 case + R101 verification all present and passing |
| D-004-R144 (scope d) | PASS | Already correct in `index.json`; explicitly stated with primary verification |
| D-004-R159 (no effort key ever written) | PASS (INFO I-1) | settings.json added-key set empty; no `effort`/`effortLevel` key in any changed file. The string `effort` appears only as documentation of an *observed harness payload field* in the two reports — not a written key |
| D-004-R022 / R053 (never touch M0-T025) | PASS | No `M0-T025` path in the diff |

## Steps independently executed

1. **Pin + cleanliness** — `rev-parse HEAD`, `status --porcelain`, `merge-base`, `log --oneline` (outputs above).
2. **Full diff review** — `git diff 4a4bf2d5..HEAD` (all 6 files, read in full), `diff --name-status`, forbidden-path grep.
3. **Producer's suite, my run** — `cd "<worktree>" && python tools/test_readonly_agent_guard.py` → 131/131 PASS, exit 0.
4. **No-weakening proof #1 (base expectations vs new guard)** — extracted the **pre-fix** suite (`git show 4a4bf2d5:tools/test_readonly_agent_guard.py`) and executed it unmodified against the **new** guard: `checks=89 PASS=89 FAIL=0 rc=0 / ALL CHECKS PASSED`.
5. **No-weakening proof #2 (decision differential)** — 63 mutating + 34 read-only commands × 4 identity classes = **388 base-vs-new comparisons**:
   - governed reviewer: 97/97 identical (all mutations denied both, all read-only allowed both) — **0 weakenings, 0 new over-denials**
   - roster producer / lead: 97/97 identical (pass-through preserved)
   - **NAMED spawn (B-015 shape): 63 mutations newly DENIED, 34 read-only still ALLOWED, 0 weakenings** — the fix, with no read-only collateral
6. **Byte-identity of the untouched security core** — at blob level, the region from `# Repository / GitHub / control-plane` to `def main():` (`_MUTATING`, `_REDIRECT`, `_GIT_*` tables, `_is_git`, `_git_sub_mutates`, `_split_command_segments`, `_git_argv_mutates`, `_deny`) is **byte-identical to base: 10,947 bytes**. `READ_ONLY_AGENTS` and `WRITE_TOOLS` identical. All 6 committed blobs are LF-only (no CRLF injected; the working-copy CRLF is an autocrlf artifact only).
7. **Adversarial identity fuzzing (44 payloads)** — `agent_type` as int/float/bool(True/False)/0/`[]`/`{}`/nested dict/list-containing-a-roster-name/null; whitespace-only; tab/newline; NUL-suffixed roster and governed names; wrong case; `.md` suffix; `../agents/…` traversal; Cyrillic homoglyph; 2 MB identity; `agent_id`-only; `agentType`-only; `agent_type`+`agentType` conflicts; empty payload; JSON string/number/null/non-JSON/empty stdin. **Every unknown/coerced identity failed CLOSED; every malformed payload denied; no bypass found.**
8. **Fail-open stress** — real backslash-newline continuations ×1/3/1 000/50 000 → all correctly DENIED; 20 k segments, 50 k unbalanced quotes, 200 k-char quoted `-C` path, 20 k nested `$(`, 60 k astral-unicode, 10 k NUL bytes → all DENIED, rc=0, ≤0.2 s. Regex worst case (3.4 s at 400 KB) occurs **only on inputs that classify as ALLOW**, so a hook timeout cannot convert a DENY into an ALLOW (2 MB input containing a real mutation classified in 0.09 s).
9. **R100 end-to-end shell proof** — the expanded command string executed through a POSIX shell and through `cmd.exe`, both emitting the guard's deny JSON; plus quoted-vs-unquoted argv grouping for a spaced root (1 token vs 2), and a demonstration that command substitution *is* evaluated inside the double quotes (L-3).
10. **Which config actually wires the hook** — primary checkout HEAD = `4a4bf2d5` with the **`args`** form; `.claude/settings.local.json` keys = `[$schema, env, permissions]` (**no hooks**); global `~/.claude/settings.json` (**no hooks**). Therefore the *base* `args` wiring is empirically functional (it denied my commands), which reframes R100 (see M-1).
11. **Roster-surface enumeration** — 25 `.md` stems, no stray non-agent `.md`; 7 governed vs **18 pass-through write-authorized** identities enumerated.
12. **Secret hygiene** — 12-pattern regex scan (usernames, Windows/Unix abs paths, UUID session/prompt IDs, long hex, `claude.ai/code/session`, key/token/bearer, `sk-`/`ghp_`/`xox`, supabase service-role/anon, env-var-with-value, transcript_path, pane IDs) over all 6 changed files → **clean** (only false positives: Python kwargs, the base git SHA); gitleaks 8.30.1 → `no leaks found` on every changed file.
13. **Guard I/O surface** — no `open()`, no logging, no `subprocess`, no `os.environ`; only `sys.stdin.read()` and one `sys.stdout.write` in `_deny`. No leftover diagnostic instrumentation from the evidence capture.
14. **Control-plane + companion suites** — validator, `test_project_control.py`, `test_directive_compliance.py`, `test_agent_dispatch_guard.py` (all green, outputs above).

## Expected versus actual

| Expectation | Actual |
|---|---|
| Named/unknown spawned identity cannot mutate | Confirmed: 63/63 mutating forms denied; write tools denied; `agent_id`-only denied |
| No previously-denied command becomes allowed | Confirmed twice (389 independent comparisons + 89-check base suite), and by 10,947-byte blob identity of the classification core |
| No read-only command newly denied | Confirmed: 34 read-only commands unchanged in all 4 identity classes |
| Malformed payload still fails closed | Confirmed: non-JSON, array, string, number, null, empty stdin → DENY |
| Empty/unreadable roster fails closed | Confirmed by code (`except OSError: return set()`, `.claude/hooks/readonly_agent_guard.py:77-78`) and by executing a byte-identical guard copy from a tree with no `../agents` (producer's §11, reproduced in my run) |
| Lead unaffected | Confirmed: no-identity payload passes through, including mutations |
| Hook cannot crash on adversarial input | **Partially false** — see L-1 (non-string `command` / non-dict `tool_input` → uncaught exception → fail OPEN) |

## Evidence paths

- `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\.claude\worktrees\M0-T028-readonly-guard\.claude\hooks\readonly_agent_guard.py`
- `…\.claude\worktrees\M0-T028-readonly-guard\.claude\settings.json`
- `…\.claude\worktrees\M0-T028-readonly-guard\.gitignore`
- `…\.claude\worktrees\M0-T028-readonly-guard\tools\test_readonly_agent_guard.py`
- `…\.claude\worktrees\M0-T028-readonly-guard\project-control\reports\M0-T028-TEAMMATE-PAYLOAD-EVIDENCE.md`
- `…\.claude\worktrees\M0-T028-readonly-guard\project-control\reports\M0-T028-producer-report.md`
- `…\.claude\worktrees\M0-T028-readonly-guard\project-control\tasks\M0-T028.json`
- `…\.claude\worktrees\M0-T028-readonly-guard\project-control\directives\D-004-agent-teams-runtime-adoption\requirements.json`
- `…\.claude\worktrees\M0-T028-readonly-guard\docs\adr\ADR-005-agent-permission-and-gate-workflow.md` (line 20 — reviewer classification)
- `…\.claude\worktrees\M0-T028-readonly-guard\.claude\hooks\agent_dispatch_guard.py` (lines 59-67 — name not inspected)

## Human-style walkthrough findings

Not applicable (no UI surface). The operator-facing surface is the denial message; it is precise, names the identity, states what is allowed, and directs the agent to `SendMessage` — verified verbatim in three live denials of my own session and in synthetic named-spawn payloads.

## Regression/security/provenance findings

**CRITICAL: none. HIGH: none.**

**M-1 (MEDIUM) — the enforcement layer's wiring form was changed to a form not proven live, and hook failure is fail-open.**
`.claude/settings.json:10,19,29,39` replaces `{"command":"python","args":["${CLAUDE_PROJECT_DIR}/…"]}` with `"command": "python \"${CLAUDE_PROJECT_DIR}/…\""` for **all four** hook entries. I established that the **old** form was empirically working at the base (primary checkout at `4a4bf2d5`, no `hooks` key in `.claude/settings.local.json`, no `hooks` in the global settings — yet the guard fired and denied my Bash calls). The new form is proven to execute under `sh` and `cmd.exe` with the real root, but **nothing in this task's evidence proves the harness's hook-config parser accepts it and still delivers the payload on stdin**. Because a failing hook is a non-blocking error, being wrong silently disables: the read-only guard (B-015 regression), the **B-007 dispatch guard** (kept as a mandated regression backstop by `.claude/rules/expansion-agent-dispatch-hold.md` §1), and `directive_reminder.py` on SessionStart + UserPromptSubmit. *Exploit/impact scenario:* no attacker needed — a silent config-form mismatch reverts every hook-based control while all tests still pass. *Remediation:* the already-mandatory fresh-session rerun must cover all four entries, not just the sentinel (see C1).

**M-2 (MEDIUM) — write authorization is defined negatively, so the roster directory is now a runtime privilege surface that grows by default.**
`readonly_agent_guard.py:354-358` grants pass-through to any identity that is a `.claude/agents/*.md` stem outside `READ_ONLY_AGENTS`. At this SHA that is **18 identities**, including `orchestrator`, `human-journey-reviewer`, and `visual-quality-reviewer` — and ADR-005 line 20 explicitly classifies `human-journey-reviewer` as a reviewer with a read-only toolset, while its definition at this SHA carries `tools: … Write` and `permissionMode: default`. Verified live: `agent_type` of `human-journey-reviewer`, `visual-quality-reviewer`, or `orchestrator` → mutating git, redirects, and `project_control.py accept` all ALLOWED. Two consequences: (a) an unnamed spawn of a reviewer-class role can mutate the repo and the ledger, weakening review independence (R142's spirit); (b) **adding any new `.md` to `.claude/agents/` silently mints a write-authorized identity**, with only PR review as a control (no test pins the set; CI would not fail). This is *pre-existing at base* (base allowed every non-listed identity), so it is **not a regression**, but the diff now codifies it as intentional ("A KNOWN roster definition outside READ_ONLY_AGENTS is a write-authorized producer/specialist", docstring lines 17-21), which makes the gap look deliberate. *Remediation:* replace the negative rule with a positive `PRODUCER_AGENTS` allowlist (unknown roster additions then default to governed), or add the two reviewer roles to `READ_ONLY_AGENTS`; add a test pinning the write-authorized set so a roster addition fails CI.

**L-1 (LOW) — no exception envelope: `main()` can crash, and a crashed hook fails OPEN.**
`readonly_agent_guard.py:369-370`. Reproduced (exit 1, no decision emitted, tool would proceed): `tool_input` as string → `AttributeError: 'str' object has no attribute 'get'`; `tool_input` as list → same; `command` as int → `TypeError: expected string or bytes-like object, got 'int'`; `command` as list → same. Not agent-reachable through the Bash tool schema (string `command` required), and for these shapes the base *allowed* them outright, so **no weakening** — but the fix expands the population reaching this line from 7 roles to every unknown identity. *Remediation:* wrap the `main()` body in `try/except Exception:` → `_deny("read-only guard: internal error (fail-closed)")`.

**L-2 (LOW) — the lead is identified by identity ABSENCE (negative evidence).**
`readonly_agent_guard.py:350-353`. Reproduced: `agent_type=""` **and** `agent_id=""` → ALLOW (mutation permitted); whitespace-only with no `agent_id` → ALLOW. Correct for every observed payload shape (spawns always carried `agent_id`), but if the harness ever emits an empty identity for a spawn, that spawn is ungoverned. *Remediation:* pin the observed lead shape in a test with an explicit comment, and re-check on any harness upgrade.

**L-3 (LOW) — R100's double-quoted form introduces shell metacharacter interpretation of the expanded project path.**
Reproduced: with a root containing `$(printf INJECTED)`, the substitution **is evaluated** inside the double quotes (`argv= ['…/srv/INJECTED/repo/x.py']`). A root containing `"`, `` ` ``, or `$(` would break quoting or inject; the retired `args` array form was shell-free and immune to both spaces and metacharacters. No live exposure (the real root is alphanumerics/hyphens/backslashes; a sibling checkout path has only a space). *Remediation:* extend `check_settings_commands()` to assert the expanded root contains no `"`, `` ` ``, `$`, `;`, `|`, `&`, or document the assumption alongside R100.

**L-4 (LOW) — evidence-count claim in the producer report is inaccurate.**
`project-control/reports/M0-T028-producer-report.md:102` claims "132 checks (90 pre-existing preserved verbatim + 42 new)". Actual: the suite emits **131** checks; the pre-fix suite emits **89**; the report's own pasted transcript contains **131** `PASS` lines. Gate evidence counts must be exact. *Remediation:* correct to 131 = 89 + 42 (or annotate).

**L-5 (LOW, informational) — identity string handling nuances (unchanged from base).** `"backend-engineer "` (trailing space) passes through via `.strip()`; comparison is case-sensitive, so `Backend-Engineer` / `CODE-REVIEWER` fail **closed** (safe direction). Neither is agent-controlled.

**Requested dimension coverage**
- **Bypass analysis (dim 1):** no bypass found across 44 adversarial identity payloads. `agent_type` precedes `agentType` (`:348`); `agent_id`-only is governed; non-string identities coerce via `str()` and fail closed; empty-string-with-`agent_id` is governed; NUL/homoglyph/case/`.md`/traversal variants all fail closed; **OSError semantics match the claim** (`:77-78` returns `set()`, and an empty roster governs every spawned identity — verified by executing the guard from a roster-less tree). The **roster-producer-name residual is properly recorded** (evidence file §5 lines 118-120; producer report §7 item 2) — I judge it **acceptable**, since naming is lead-controlled and the lead already holds full write authority, i.e. no privilege *escalation*; the realistic risk is prompt-injection-induced naming, mitigated by orchestrator-only integration and the containment diff, and mechanically closable in `agent_dispatch_guard.py` (which today inspects only `subagent_type` against 5 blocked names, lines 59-67 — it never looks at the spawn name). **Roster-directory manipulation** requires an identity that can already write, so it is a lateral, not an escalation — but see M-2 for the default-grows-open problem.
- **No weakening (dim 2):** proven three independent ways (blob identity of the 10,947-byte classification core; 89/89 pre-fix suite against the new guard; 388-comparison differential with 0 weakenings and 0 new read-only denials). Malformed-payload fail-closed deny intact.
- **Fail-open hazards (dim 3):** one real gap (L-1); no crash on huge strings (2 MB), nested objects, astral unicode, NUL bytes, 50 k line continuations, 20 k segments, or unbalanced quotes; timeout cannot flip DENY→ALLOW (slow paths are ALLOW-classified inputs).
- **R100 injection/quoting (dim 4):** quoting correct for spaces (proved in-shell); no new keys; no machine-specific values; **no effort key anywhere** (added-key set empty); residual L-3.
- **R101 + secret hygiene (dim 5):** `check-ignore` resolves to the repo `.gitignore:64`; nested worktree copies covered by `:57`; both reports and all code files clean under a 12-pattern scan and gitleaks.
- **Containment (dim 6):** exactly the 4 allowed code/config paths + the 2 M0-T028 reports; M0-T025, both pilot reports, the D-004 capture, agent definitions, rules, control CLI, and all product code untouched.
- **Residual-risk honesty (dim 7):** **honest.** The docstring discloses the scripting-language write residual and names detection/orchestrator-only integration as the backstop (lines 39-44); §7 discloses the naming residual, the classification residuals, and the unit-level-only AS-3. I verified the scripting residual is real (`python -c open(...,'w')`, `node -e writeFileSync`, `python -c subprocess git push`, `python - <<EOF` all classify as non-mutating), so "read-only" means *shell-level* mutation control plus tool-roster removal — stated, not oversold.
- **Not applicable to this diff (justified):** cross-tenant isolation, service-role secrecy, private storage, SSRF, upload controls — no product/runtime code, no network, no DB/storage, no user input path. **Log redaction:** the guard performs zero file I/O and no logging; the deny reason never echoes attacker-controlled command text (good prompt-injection hygiene — nothing from `tool_input` re-enters the model context).
- **Disclosed items verified as recorded (not findings):** producer's harness-auto-worktree deviation and orchestrator diff port (report §1, §7.4 — and I confirmed the ported result is a single commit on `task/M0-T028-readonly-guard`, base `4a4bf2d5` as ancestor, clean tree, exactly the 6 files); live sentinel deferral to the fresh-session rerun (packet risk 2, `owner_review_state`, report §7.1).

**INFO:** the evidence file (lines 47-53) records the session-global `effort = {"level":"xhigh"}` payload field in a document that states all machine-specific values are redacted — not a secret and not a written key, but it is session-configuration detail; the orchestrator may want it noted. Separately, the guard's conservative classification over-denies reviewer analysis one-liners containing `>=`, `->`, or a space-delimited `install` (it denied three of my own read-only commands); fail-safe direction, pre-existing, worth a note in reviewer guidance.

## Defects

None blocking correctness of the fix. Findings M-1, M-2, L-1, L-2, L-3, L-4 as above.

## Required rework (BLOCKING for acceptance and for B-015 closure; none require reopening the reviewed SHA)

- **C1 (from M-1):** the mandatory fresh-session rerun must prove **all four** hook entries fire under the new single-string form — (a) the live sentinel deny from `readonly_agent_guard.py` (AS-3), (b) the `agent_dispatch_guard.py` path on an `Agent|Task` dispatch, (c) `directive_reminder.py` on SessionStart and (d) on UserPromptSubmit. If any entry does not fire, revert that entry to the empirically-working `args` form and re-review.
- **C2 (from M-2):** open a follow-up task to convert write authorization to a positive `PRODUCER_AGENTS` allowlist (or add `human-journey-reviewer`/`visual-quality-reviewer` to `READ_ONLY_AGENTS`), reconcile those definitions with ADR-005 line 20, pin the write-authorized set in a test, and correct the docstring's "roster definition outside READ_ONLY_AGENTS = write-authorized producer/specialist" generalization. Also evaluate extending `agent_dispatch_guard.py` to refuse a spawn name colliding with a roster stem (closes the naming residual mechanically).
- **C3 (from L-1):** add the fail-closed exception envelope around `main()`.
- **C4 (from L-4):** correct the 132/90/42 check-count claim in the producer report to 131/89/42.

## Reviewer conclusion

**PASS** (with C1–C4 blocking acceptance and B-015 closure). At `e8a7dbfa2145b76f91b8e5272769a1447a940525` the B-015 root cause is correctly diagnosed on primary evidence, and the fix is a strict, minimal, fail-closed improvement: the security-critical command-classification core is byte-identical to base (10,947 bytes), every previously denied form is still denied (389 independent comparisons plus the unmodified 89-check pre-fix suite), no read-only command is newly denied, and the B-015 payload shape moves from fully permissive to 63/63 mutations denied while retaining all read-only inspection. Adversarial identity fuzzing found no bypass, and the OSError/empty-roster fail-closed claim matches the code and executes as documented. The residual risks are honestly disclosed; the two MEDIUM items are (M-1) an unproven-live wiring form under fail-open semantics, which the owner-mandated fresh-session rerun must be widened to cover, and (M-2) a pre-existing negative-allowlist design that the diff codifies and that should be inverted in a follow-up task rather than by amending accepted work.

---

Orchestrator addendum (recorded at gate time, not part of the reviewer return): C3 and C4 were
applied as the bounded delta d5eb642e (own G3/G5 delta reviews, both PASS). C1 is bound into the
Phase-8 fresh-session procedure (all four hook entries must be proven firing). C2 is presented to
the owner as a follow-up task proposal in the return packet; it is pre-existing at base, not a
regression of this fix.
