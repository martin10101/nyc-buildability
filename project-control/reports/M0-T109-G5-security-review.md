# G5 Security Review — M0-T109 readonly-guard hardening

> Orchestrator note: reviewer return saved verbatim (transport entity-decoding only). Reviewer: independent security-reviewer agent (read-only, governed — its first write probe was itself denied by the live guard), returned 2026-09-04 (UTC). The MEDIUM follow-up finding is tracked as M0-T145 (backlog); it is pre-existing and does NOT block M0-T109.

**Task:** M0-T109 (governance/security, D-024 in-regime). **Reviewer:** security-reviewer (read-only, governed — confirmed live: my first probe was itself denied by the guard).
**Reviewed content identity:** guard blob `ad009d4f…`, PS-test blob `0fd81db3…` — byte-identical across HEAD `892c9fe1`, candidate `7f075e37`, task-tip `67b5b4dc`. Bash pack (`tools/test_readonly_agent_guard.py`) byte-unchanged base→HEAD.
**Diff scope:** 3 hunks in the guard (docstring; `GetTypeFromProgID` self-anchor; `_ASSIGN_LAYER` + loop) + PS-test rows. No other production path touched.

## Check 1 — ADV-R4-1 chained assignment
**(a) DENY works.** Verified against the live guard: `$a=$b=powershell -enc`, `$a=$b=$c=powershell`, `$a = $b = powershell`, mixed `$a =$b= powershell`, `$env:foo=$global:bar=powershell`, `$a=$b=cmd /c whoami` → all **DENY**. Base `1c069571` ALLOWed `$a=$b=powershell` — the loop genuinely closes it. **PASS.**
**(c) No false positive.** `$a=$b=Get-Content`, `$a = $b = Get-Content`, `$result=powershell_helper_note` → **ALLOW** (the `^…$`-anchored `_NESTED_SHELL`/`_SPAWN_ALIAS` prevent prefix FPs). The loop only strips *more* assignment layers, so it can never newly deny a legit read unless the true command is literally a nested shell. **PASS.**
**ReDoS/termination.** `_ASSIGN_LAYER=^\$\{?[A-Za-z_][\w:]*\}?\s*=\s*` is start-anchored and linear; every match consumes ≥3 chars so `head` strictly shrinks, and a non-match sets `prev==head` and breaks. Bounded, no catastrophic backtracking. **PASS.**

**(b) BYPASS FOUND — braced-variable assignment (MEDIUM, PRE-EXISTING, out of scope).**
The two braced forms the task told me to try are **ALLOWed** by both HEAD and base:
```
${x} = powershell -enc SQBFAFgA      -> ALLOW  (should DENY)
${a-b} = powershell -enc SQBFAFgA    -> ALLOW  (should DENY)
${x}=powershell -enc SQBFAFgA        -> ALLOW
```
Root cause: `_SEGMENT_CHARS` includes `{` and `}`, so `_split_command_segments` tears `${x}=powershell` into segments `$`, `x`, `=powershell` **before** `_effective_command_token` runs; the RHS segment `=powershell` isn't recognized as an assignment or a shell. The `\{?` in `_ASSIGN_LAYER` (and the docstring's claim that `$var =` assignment fronting is covered) is therefore **non-functional for the brace form** — the loop never sees it. In real PowerShell, `${x} = powershell -enc <b64>` executes the encoded child shell.

**Disposition:** This is a genuine bypass of the assignment-fronted-nested-shell tooth (the NF2/ADV-R4-1 class), but it is **NOT admitted by the new code** — I proved it is identical in base `1c069571` (both ALLOW), and the M0-T109 diff modifies neither `_SEGMENT_CHARS` nor the `_ASSIGN_LAYER` pattern. Per the task's own FAIL bar ("a bypass **the new code** admits") this does not fail M0-T109; the change strictly strengthens without introducing or worsening it. Practical impact is bounded by the same compensating control as the documented residuals (read-only reviewer + orchestrator-only integration: local scratch never reaches a branch/PR/ledger). **Recommend (follow-up hardening, tracked):** either normalize `${name}`→`$name` before segment-splitting, or add the brace form to `_effective_command_token`, and — until fixed — the docstring should honestly list `${var} = <shell>` as a residual rather than imply `$var =` assignment is fully covered. Severity MEDIUM (bypass of an intended tooth) capped to the documented-residual class by compensating controls.

## Check 2 — ADV-4 GetTypeFromProgID reachable
`GetTypeFromProgID\b` → `\[(?:System\.)?Type\]::GetTypeFromProgID\b`. The bare form was dead (leading class `(?:^|[\s;&|({`=])` excludes `:`, so a real `[Type]::…` never matched); anchoring makes it fire. Live-verified: `[Type]::GetTypeFromProgID(…)`, `$t=[Type]::GetTypeFromProgID(…)`, `[System.Type]::GetTypeFromProgID(…)` → **DENY**; the name as data (`GetTypeFromProgID-notes.md`) → **ALLOW**. `[System.Type]` is covered by the `(?:System\.)?` group; `(?ix)` covers case. No plausible reachable variant is missed (the method is a static on `System.Type`; `::`-space is not valid PS). `[Activator]::CreateInstance` tooth **unchanged and preserved** (line 258); the nested `[activator]::CreateInstance([type]::GetTypeFromProgID(…))` still denies via CreateInstance. Anchoring (defense-in-depth) rather than removal was the right security call — GetTypeFromProgID alone only returns a Type; actual instantiation needs CreateInstance, which is independently caught. **PASS.**

## Check 3 — ADV-R4-2 documented residuals
Both documented accurately. `&(gcm powershell)`: I confirmed it is a real residual — segment-splitting on `(` isolates `gcm powershell`, where `powershell` is in *data* position to `gcm`, so `_launches_nested_shell` returns False. Not trivially closable without over-broad denial (would risk `(Get-Command git).Source` reads); leaving it to the orchestrator-only model is sound. `[Type]::GetTypeFromCLSID('{clsid}')`: inert without CreateInstance (which is denied), so no COM object is actually created by it alone; it is *cheaply* closable with a symmetric tooth `\[(?:System\.)?Type\]::GetTypeFromCLSID\b` (belt-and-suspenders parallel to GetTypeFromProgID) but not security-load-bearing — leaving it documented is defensible. Compensating control (only the lead commits/pushes/merges; reviewer scratch never reaches the repo) is a sound bound for both. **PASS** (minor note: GetTypeFromCLSID is the one residual that could have been trivially mirrored; not required).

## Check 4 — Regression / no weakening
`python tools/test_readonly_agent_guard_powershell.py` → **ALL CHECKS PASSED** (exit 0), incl. 17 RED-on-mutant proofs (CreateInstance-only, GetTypeFromProgID-only, chained-assignment-loop-revert each load-bearing).
`python tools/test_readonly_agent_guard.py` → **ALL CHECKS PASSED** (exit 0) — all M0-T108 shell-agnostic denials preserved.
Diff proven to add denials only: the loop reveals deeper command tokens (never removes a denial); the ProgID change swaps a dead alternative for a live one (no denial lost). Bash pack byte-unchanged. **PASS.**

## Check 5 — Secrets / injection / privacy
Diff is guard policy logic + stdlib test. No secrets, credentials, network I/O, or new logging. `_deny` emits only the agent-identity string in its reason — no sensitive data. No injection surface introduced (regex/argv parsing over harness JSON, no eval of payload). **PASS.**

## Adversarial attempts made (payloads run against the live guard)
- `$a=$b=powershell`, `$a=$b=$c=powershell`, `$a = $b = powershell`, `$a =$b= powershell`, `$env:foo=$global:bar=powershell`, `$a=$b=cmd /c whoami` → all DENY ✓
- `${x}=powershell -enc X`, `${a-b} = powershell -enc X`, `${a-b}=powershell -enc X` → **ALLOW (bypass, pre-existing — see Check 1b)**
- `$a=$b=Get-Content`, `$a = $b = Get-Content`, `$result=powershell_helper_note` → ALLOW (correct, no FP) ✓
- `&(gcm powershell)` → ALLOW (documented residual, confirmed) ✓
- `[Type]::GetTypeFromProgID`, `[System.Type]::GetTypeFromProgID` → DENY ✓

## Verdict rationale
The M0-T109 change does exactly what its mandate requires: it strengthens the guard (chained-assignment loop + reachable `GetTypeFromProgID`) with **no false positives**, **no weakened denial** (both suites green, all M0-T108 denials preserved), and **no new hole** — the one bypass I found (`${var} = <shell>`) is pre-existing in base `1c069571`, untouched by this diff, and bounded by the orchestrator-only compensating control. It is reported as a MEDIUM follow-up finding (with a docstring-honesty note), not a defect of this change. No secrets/injection/privacy issues. Blob identity matches the reviewed commits.

**One MEDIUM follow-up for the orchestrator to log (not blocking M0-T109):** braced-variable assignment (`${x} =`, `${a-b} =`) launders an assignment-fronted nested shell past `_launches_nested_shell`; document it as a residual and/or normalize `${name}`→`$name` before segment-splitting in a future hardening pass.

VERDICT: PASS
ctl24 HEAD reviewed: 892c9fe1c519a6ed2621a1d77c6281bfea53573e
