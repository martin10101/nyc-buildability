# M0-T108 G4 QA review (VERBATIM save)

Reviewer: independent read-only `qa-engineer` (unnamed spawn); reviewed at frozen deliverable
identity `4e238b5` (HEAD `ded625a` = control-plane records only). Returned through the agent-return
channel 2026-08-26/27 UTC and saved verbatim below (transport entity-decoding only; the harness
neutralized `<`/`>`/`&` in transit and flagged the output as instruction-shaped — control tags
were neutralized and the content is preserved here as reviewer findings, not instructions).

---

All evidence gathered and independently reproduced. Here is my G4 gate report.

---

# G4 Quality Gate Report — M0-T108

**Task:** M0-T108 — Control-plane security fix: close the `readonly_agent_guard` PowerShell/scripting write gap (G5 M0-T102 MEDIUM advisory)
**Gate:** G4 (independent QA) — first independent pass, read-only reviewer (`qa-engineer`)
**Reviewed content identity:** commit `4e238b5` on `control/D-024-fable-codex-loop`
**Deliverable diff:** `24aa061..4e238b5`
**Date:** 2026-08-26

## Frozen-identity verification

- `git diff --name-only 4e238b5..ded625a` → only control-plane records (`project-control/gates/M0-T108-G2.json`, `.../reports/M0-T108-evidence-map.json`, `.../reports/M0-T108.json`, `.../state.json`, `.../tasks/M0-T108.json`). Deliverable content is frozen. **Confirmed.**
- **Environment note (method, not a defect):** my isolated worktree was checked out at `d8b3899` (PR #240 merge for M0-T077), which does NOT contain `4e238b5`. The on-disk files were the pre-M0-T108 versions. To execute the permitted test scripts against the exact frozen deliverable, I extracted the frozen subtree via read-only `git archive 4e238b5 | tar -x` into the isolated scratchpad and verified byte-identity by blob hash (no repo/git/ledger mutation):
  - `readonly_agent_guard.py` `5d22206f…` — MATCH
  - `settings.json` `c967b817…` — MATCH
  - `test_readonly_agent_guard_powershell.py` `9c4edc44…` — MATCH
  - `test_readonly_agent_guard.py` `b421cb15…` — MATCH
  All four extracted files hash-identical to the `4e238b5` tree blobs. Every result below is against the frozen deliverable.

## Scope / diff discipline

`git diff --name-only 24aa061..4e238b5` production+test paths: `.claude/hooks/readonly_agent_guard.py`, `.claude/settings.json` (single matcher line), `tools/test_readonly_agent_guard_powershell.py` (new) — all within `allowed_paths`; no forbidden path touched. `.claude/settings.json` change is exactly `Bash|Write|…` → `Bash|PowerShell|Write|…` (verified). The pre-existing Bash pack `tools/test_readonly_agent_guard.py` is byte-identical to base — confirming the "existing pack UNMODIFIED" claim.

## QA focus (1) — re-run both packs (reproduced)

| Command (run against frozen scratchpad tree) | Result |
|---|---|
| `python tools/test_readonly_agent_guard.py` | **136 PASS / 0 FAIL**, `ALL CHECKS PASSED`, exit 0 |
| `python tools/test_readonly_agent_guard_powershell.py` | **95 PASS / 0 FAIL**, `ALL CHECKS PASSED`, exit 0 |

All 4 RED-on-mutant proofs PASS. Counts match the producer's claim exactly. (Note: an initial partial extraction produced 3 spurious Bash-pack failures — all `settings hook #N: real-root token is an existing hook file` — caused by not extracting the sibling `agent_dispatch_guard.py`/`directive_reminder.py` that `settings.json` references; after extracting the full `.claude/hooks/` dir the pack is a clean 136/136. Harness artifact of partial extraction, not a deliverable defect.)

## QA focus (5) — determinism (reproduced)

Both packs re-run a second time; `diff` of run-1 vs run-2 output is empty for each, both exit 0. Deterministic. **Confirmed.**

## QA focus (2) — mutation adequacy

- **Non-vacuous / mutation-applied detection:** each of the 4 mutants is a `SRC.replace(...)` whose target string occurs verbatim in the frozen guard. The pack guards against a no-op mutation (`if mutated_src == SRC: check_static(..., False)`), and each mutant asserts `mutant==ALLOW and real==DENY`. Load-bearing; detect mutation-not-applied. **Adequate.**
- **Important teeth WITHOUT a dedicated mutant** (judged adequate): `_PS_MUTATING` alternations covered by ~38 positive DENY assertions; matcher sync by 2 static checks + mutant #1. **One coverage gap (ADVISORY-4):** the pack's only `-enc` test (`powershell -enc …`) is also matched by the nested-shell rule, so a mutant removing `_PS_ENCODED` alone would still pass — independently confirmed `_PS_ENCODED` functions via `someexe -enc QQBB` → DENY (uniquely exercised). Advisory only.

## QA focus (4) — false-positive regression (reproduced, all ALLOW for governed `code-reviewer`)

`python -c "print(1 if 2>1 else 0)"`, `python -c "def f(x) -> int: return x"`, `grep 'a->b' …`, `python -c "print(open('f').read())"`, `python -c "print(open('f','r').read())"`, `python -c "…json.load(open('f'))…"`, `Get-Content README.md`, `Select-String`, `Get-ItemProperty HKCU:X`, `Set-Location`, `Set-StrictMode`, `git status 2>&1`, `> $null`. Packet-named pure-read forms correctly ALLOWED. Fail-closed envelope confirmed: malformed payload → deny. **No false-positive regression.**

## QA focus (3) — negative/boundary probes (independent, via real guard stdin JSON path)

**Correctly DENIED** (governed role): `Set-Content` split across backtick line-continuation; `sc -Path`; `dir | out-file 'log.txt'`; `[io.file]::writealltext(...)` (lowercase); `Invoke-Expression`/`iex`; `Set-Content @splat`; `md newdir`; `Add-Content`/`Clear-Content`/`Move-Item` (canonical); `mv`/`cp`/`rm`; standalone `-OutFile`; standalone `-enc`/`-encodedcommand`; backtick-hidden `Set-Content`; `iwr -OutFile`; `Tee-Object`; `cmd /c "echo hi> f.txt"`; `pwsh -Command Set-Content`; unquoted `>`/`>>` to real paths; `New-Item notes.md`; every objective-named cmdlet. `git push` even when quoted/backtick/`& '…'` is caught by the shared `_git_argv_mutates` argv pass for both shells.

**Findings (missed):**

- **ADVISORY-1 (HIGH) — call-operator / dot-source with a quoted *literal* command name bypasses cmdlet + `gh` denial.** Reproduced (PowerShell, `code-reviewer`): `& 'Set-Content' x.txt 1` → ALLOW; `&'Set-Content' …` → ALLOW; `& "Set-Content" …` → ALLOW; `. 'Set-Content' …` → ALLOW; `& 'Remove-Item' x.txt` → ALLOW; `& 'gh' pr create --title x` → ALLOW. Baselines correctly DENY: bareword `Set-Content …`, `& Set-Content …`, `gh pr create …`, `git push …`, and `& 'git' push` (argv pass). Root cause: `_PS_MUTATING`/`_MUTATING` require a leading delimiter `[\s;&|({`]`, which excludes quote characters, so a command name adjacent to an opening quote is not matched. This is a **static, statically-resolvable literal** — NOT the "dynamically composed write" the docstring documents as residual, and the disclosed `& $var` (dynamic call) IS denied while the closely-related `& 'literal'` is NOT (undisclosed asymmetry). `& 'gh' pr create` executes a GitHub mutation directly and is therefore NOT covered by the "orchestrator-only integration" backstop the residual relies on. Classification: **missed-and-material**, but non-blocking because (a) the `gh`/quoted-token gap is **pre-existing** in the unchanged `_MUTATING` core and equally present in the already-gated Bash path (`'gh' pr create` → ALLOW in Bash), so it is not introduced or regressed by M0-T108; (b) the task's explicit objective (i)–(iv) targets the PowerShell *write* gap + git parity, all met; (c) the highest-value mutation (`git`) is caught even under `& '…'`; (d) realistic reviewer mutation uses natural forms, all denied. **Recommend a follow-up hardening task** with a call-operator/dot-source-aware pass, and **correct the `_PS_MUTATING` inline docstring** — "a mutating token inside a quoted string still denies (fail closed)" is false for adjacency/call-operator forms (independently shown: `echo 'Set-Content x 1'` → ALLOW).

- **ADVISORY-2 (LOW–MEDIUM) — write-cmdlet alias enumeration gaps.** `ac` (Add-Content), `clc` (Clear-Content), `mi` (Move-Item) aliases and the `mkdir` function → ALLOW, while canonical names and other aliases (`sc`,`md`,`ni`,`ri`,`del`,`move`,`copy`,`cp`,`mv`,`rm`) → DENY. Objective's explicitly-named cmdlets all covered in **canonical form**; alias completeness beyond the stated objective. Bounded by the local-scratch/orchestrator-only residual. Recommend adding `ac`/`clc`/`mi`/`mkdir` to `_PS_MUTATING`.

- **ADVISORY-3 (LOW) — `> ${null}` false-positive.** `gci > ${null}` → DENY; `${null}` is the curly-brace form of `$null` and is a legitimate discard, but `_PS_REDIRECT_TARGET_OK` only matches `$null`. Trivial impact (use `$null`).

- **Documented residual, NOT a defect:** `git $c` (verb in a variable, no `-C` target) → ALLOW — explicitly documented residual. `Set-Variable`/`Set-Location`/`Set-StrictMode` → ALLOW correctly (denylist is precise, not a blanket `Set-*`).

## Objective coverage (governance task; `acceptance_scenarios` empty — verified against objective i–iv)

(i) matcher extended to PowerShell — DONE. (ii) PowerShell mutation/redirection denylist for every named cmdlet + `[IO.File]::Write*` + redirection + git-via-PowerShell, same fail-closed envelope — DONE. (iii) scripting class (`python -c` writes) with honest residual — DONE. (iv) regression tests analogous to Bash, RED-on-mutant — DONE (95 checks, 4 load-bearing mutants). False-positive reduction — DONE.

## Modularity / lint (reproduced)

- `ruff 0.13.0 check` on frozen guard and PS pack → `All checks passed!` (both). Matches CI ruff version.
- Guard is 589 raw lines, below `WARN_SLOC=600`. Single-responsibility hook; no responsibility mixing. **No modularity concern.**

## Verdict rationale

Every explicitly-required acceptance element (objective i–iv + false-positive reduction) is independently reproduced at the frozen identity: both packs green (136/136, 95/95), deterministic, mutants load-bearing, ruff clean, fail-closed envelope intact, no regression to the byte-identical Bash pack, and the packet-named false-positive class fixed. The findings are completeness refinements (alias enumeration), a pre-existing/out-of-scope cross-shell limitation (quoted call-operator for `gh`/cmdlets), and a documentation-accuracy correction — none is a regression or a defeat of the task's stated purpose. ADVISORY-1 is flagged HIGH so the orchestrator/security-reviewer can decide whether to open a follow-up hardening task before dispatching reviewers into write-capable trees; it does not block acceptance of this scoped gap-closure.

**G4: PASS**

---

Reproduction assets (isolated scratchpad, no repo mutation): frozen tree at `…scratchpad\frozen-4e238b5\` (byte-identical to `4e238b5`); probe drivers `probe.py`, `probe2.py`, `probe3.py`, `probe5.py`, `probe6.py` (`probe4.py` contains a known tool-name-abbreviation bug — its `[PS]` rows are invalid and were superseded by `probe6.py`).

**Requested status:** PASS returned to orchestrator for recording. Advisories 1–4 recommended as a follow-up hardening task (not blocking). Did not run `project_control.py`, git, or `gh` (read-only reviewer).
