# M0-T145 G4 reports (verbatim reviewer returns, both rounds)

Saved VERBATIM by the orchestrator from the qa-engineer agent-return channel (2026-09-06;
transport entity-decoding only: `&gt;` → `>`, `&amp;` → `&`). Reviewer: independent
qa-engineer (read-only). ROUND 1 reviewed SHA 0671edd5 → PASS, later WITHDRAWN by the
reviewer itself after the G3 regression finding; ROUND 2 (delta re-attestation, appended at
the end of this file) reviewed SHA bac01a56 → **PASS** (authoritative).

---

# Gate Report

- Gate ID: M0-T145-G4
- Task ID: M0-T145 (readonly-guard residual: braced-variable assignment-fronted nested shell)
- Reviewer: qa-engineer (independent G4; read-only for the product tree)
- Producer: supervised-loop-fable-worker (run lineage `persistent-local-01`); guard/test apply mechanically performed by the orchestrator per report §6
- Result: **PASS**
- Clean environment/worktree used: yes — reviewed the frozen worktree `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m0t145`, branch `task/M0-T145-brace-guard`. Branch tip resolves to `0671edd5a0be16848eaa2b7e7c80e7c50511b998` (read directly from `.git/packed-refs`), matching the reviewed SHA (parent `29f9ee7b`). Python 3.11.9. Did not run `project_control.py`, `git`, or `gh`.

## Acceptance criteria reviewed

The packet has empty `acceptance_scenarios` (path-free governance backlog task). The acceptance surface is the objective's five obligations plus the documented test command:
1. Braced-variable assignment-fronted nested shell now DENIED for a governed read-only role.
2. RED-on-mutant + no-FP rows added for the braced form.
3. Guard docstring no longer implies the brace form is uncovered (now honestly states it is closed, with the remaining unsafe-charset-name residual named).
4. Bash pack kept behaviorally unchanged.
5. All pre-existing denials preserved (no regression).
6. Documented command `python -m pytest tools/test_readonly_agent_guard_powershell.py -q` exits 0.

## Directive/requirement verification

The task is in-regime (`directive_refs: [{D-001: ALL}]`). D-001 is the owner-directive-compliance-system directive: **136 requirements, every one scoped in `applicability.task_ids` to `M0-T023`** (the directive-system build — CLAUDE.md section, skills, registry, validator, verifier agent). Its authoritative per-requirement re-derivation at the frozen SHA is recorded by the separate **directive-compliance-verifier** gate (producer ≠ verifier), which the run-quality-gate skill explicitly delegates. That verdict is not this QA gate's to record.

| Requirement ID | Reviewed SHA / content identity | Verdict | Reproduced evidence |
|---|---|---|---|
| D-001 (ALL, 136 reqs — all `task_ids: [M0-T023]`) | `0671edd5` / guard+test working-tree | DELEGATED to directive-compliance-verifier gate | Out of QA-gate scope to adjudicate; recorded in `project-control/directives/D-001-.../verification.json`. |
| D-001-R041 (QA-observable substance: verifier stays read-only in the guard) | `0671edd5` | PASS (QA observation, not the recorded directive verdict) | `directive-compliance-verifier` remains in `READ_ONLY_AGENTS` (guard line 125); suite rows "named spawn (unknown identity) + PS write -> deny" and every governed-role deny row confirm the read-only enforcement mechanism is intact and unbroken by this change. |

QA-surface observation on D-001 consistency: the change is deterministic guard code plus provenance-bearing, executable tests delivered with the implementation; no legal interpretation, no producer self-approval, no published-rule surface. Nothing in the diff conflicts with the directive system. This is an observation supporting — not substituting for — the directive-compliance-verifier's gate.

## Steps independently executed

1. Documented command (in worktree): `python -m pytest tools/test_readonly_agent_guard_powershell.py -q` → `1 passed in 17.12s`, **exit 0**.
2. Direct-run full-row form: `python tools/test_readonly_agent_guard_powershell.py` → **`ALL CHECKS PASSED`, exit 0**. Includes the 10 M0-T145 braced-assign DENY rows, 6 braced no-FP ALLOW rows, and both M0-T145 RED-on-mutant rows, plus the entire prior suite (write cmdlets/aliases, .NET/COM/CIM, git/gh via PS, redirects, backtick normalization, scripting-write, identity pass-through, settings matcher, and 17 earlier RED-on-mutant teeth).
3. **Independent probe set** (my own payloads, not from the test file), piping PreToolUse JSON with `agent_type: "code-reviewer"` directly to `.claude/hooks/readonly_agent_guard.py`. 27 probes: 12 DENY braced/mixed-chain/whitespace/encoded variants (D1–D12), 7 benign braced read/pipe/discard ALLOW (A1–A7), 2 documented-residual ALLOW (R1–R2), 2 bare-vs-braced parity (P1–P2), 4 Bash-tool checks (B1–B4). Result: **`ALL PROBES MATCHED EXPECTATION`, exit 0**.
4. **Independent mutant reconstruction**: re-derived the two committed teeth from the REAL source (confirming each `old` substring is present in the live guard and the replacement actually changes the source), plus a third mutant of my own (removing the leading-char `_`-prefix line in `_debrace_var`, targeting `${2} = powershell -enc …`). Result: **`ALL MUTANT TEETH LOAD-BEARING`, exit 0** — each mutant ALLOWs while the real guard DENYs.
5. `python tools/modularity_check.py --check` → **`failures 0`**, 12 pre-existing warnings, none on either changed file.
6. `python -m ruff check <guard> <test>` → **`All checks passed!`, exit 0**.
7. Read `project-control/reports/M0-T145-guard-brace-residual.md` — present, honest, matches the landed code.

## Expected versus actual

| Probe (independent) | Expected | Actual |
|---|---|---|
| D1 `${MyVar} = powershell -EncodedCommand …` | DENY | DENY |
| D2 `${a.b.c}=cmd /c whoami` | DENY | DENY |
| D3 `${x}    =    powershell    -enc    AAAA` (heavy whitespace) | DENY | DENY |
| D4 `${_priv} = pwsh -NoProfile -Command Set-Content x 1` | DENY | DENY |
| D5 `${a}=${b}=${c}=cmd /c whoami` (triple braced chain) | DENY | DENY |
| D6 `${env:FOO} = start powershell -enc AAAA` (spawn alias) | DENY | DENY |
| D7 `${a} = $b = powershell -enc AAAA` (braced→bare chain) | DENY | DENY |
| D8 `$a = ${b} = powershell -enc AAAA` (bare→braced chain) | DENY | DENY |
| D9 `${x}=\tpwsh -e AAAA` (tab) | DENY | DENY |
| D10 `${x123} = powershell.exe -enc AAAA` (.exe) | DENY | DENY |
| D11 `Select-String -Pattern '${x}' notes.md; powershell -enc AAAA` | DENY | DENY |
| D12 `${A_B} =  pwsh  -EncodedCommand  QQBBAA==` | DENY | DENY |
| A1 `${result} = Get-Content README.md` | ALLOW | ALLOW |
| A2 `${data} = Get-ChildItem -Recurse \| Select-String -Pattern powershell` | ALLOW | ALLOW |
| A3 `Get-Content notes.md > ${null}` | ALLOW | ALLOW |
| A4 `${a-b-c} = git log --oneline -5` | ALLOW | ALLOW |
| A5 `${env:PATH} -split ';' \| Select-String powershell` | ALLOW | ALLOW |
| A6 `${x} = $y = Get-Content README.md` | ALLOW | ALLOW |
| A7 `gci *> ${null}` | ALLOW | ALLOW |
| R1 `${a b} = powershell -enc AAAA` (space in name — documented residual) | ALLOW | ALLOW |
| R2 `${a$b} = powershell -enc AAAA` (`$` in name — documented residual) | ALLOW | ALLOW |
| P1 `$cmd = 'powershell'` (pre-existing bare-form deny) | DENY | DENY |
| P2 `${cmd} = 'powershell'` (parity with P1) | DENY | DENY |
| B1 Bash `powershell -Command Set-Content x 1` | DENY | DENY |
| B2 Bash `${x} = powershell -enc AAAA` (PS-only fix; Bash unchanged) | ALLOW | ALLOW |
| B3 Bash `grep -n pwsh tools/x.py` | ALLOW | ALLOW |
| B4 Bash `echo hi > f.txt` | DENY | DENY |
| Mutant T1 drop debrace wiring | mutant ALLOW / real DENY | mutant ALLOW / real DENY |
| Mutant T2 narrow braced charset (drop `.`/`-`) | mutant ALLOW / real DENY | mutant ALLOW / real DENY |
| Mutant T3 (mine) drop `_`-prefix line | mutant ALLOW / real DENY | mutant ALLOW / real DENY |

## Evidence paths

- Guard: `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m0t145\.claude\hooks\readonly_agent_guard.py` (`_PS_BRACED_VAR` line 523, `_debrace_var` lines 526–531, wiring line 574 in `_ps_normalize`; honest docstring lines 68–79).
- Test: `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m0t145\tools\test_readonly_agent_guard_powershell.py` (M0-T145 section lines 499–547).
- Report: `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m0t145\project-control\reports\M0-T145-guard-brace-residual.md`.
- Frozen SHA proof: `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\.git\packed-refs` → `0671edd5a0be16848eaa2b7e7c80e7c50511b998 refs/heads/task/M0-T145-brace-guard`.
- My independent probe scripts (temp, tool-input only): `…\scratchpad\probe_m0t145.py`, `…\scratchpad\mutants_m0t145.py`.

## Human-style walkthrough findings

Not a UI task; no walkthrough applicable. The guard's behavior was exercised end-to-end by feeding real PreToolUse payloads to the actual hook subprocess (not a mocked call), which is the true runtime path.

## Regression/security/provenance findings

- **No regression**: the full prior suite (write cmdlets/aliases, .NET/COM/CIM, git/gh through PS, redirects, backtick normalization, scripting-write, identity pass-through, settings matcher, 17 earlier RED-on-mutant teeth) is green on the real guard. My B1–B4 probes plus every Bash-form suite row confirm the Bash pack is behaviorally unchanged, consistent with source inspection: `_ps_normalize` (hence `_PS_BRACED_VAR.sub`) is invoked only under `if powershell:` in `_shell_command_mutates`, so the Bash path is byte-identical.
- **Security substance verified**: the fix genuinely closes the M0-T109 G5 MEDIUM — the braced assignment-fronted encoded/nested shell (`${x} = powershell -enc …`) now reaches command position and DENYs, and the closure holds across whitespace, glued `=`, `.exe`, env-scoped names, dotted/hyphenated names, `${2}`, and chained/mixed braced+bare assignment forms I constructed independently. The bounded no-new-FP posture holds: benign braced reads/pipes/discards ALLOW, and `${null}` still normalizes to `$null` so `> ${null}` discards ALLOW.
- **Mutation proof is sound**: both committed M0-T145 teeth are genuinely derived from the live source (each replaced substring is present in the real guard and the replacement changes it), and each independently flips a real DENY to ALLOW when removed — not vacuously green. My additional T3 mutant shows the `${2}`-normalization prefix line is also load-bearing.
- **Provenance**: guard docstring (lines 68–79) and the report attribute the fix to M0-T145/the M0-T109 G5 finding, name the mechanism (`_ps_normalize`/`_PS_BRACED_VAR`), and honestly retain the unsafe-charset-name residual (my R1/R2 probes confirm that documented boundary behaves exactly as stated). Report §6 discloses that `.claude/hooks/*` is a broker security-file-class the worker could not edit and that the orchestrator applied the change — an authority/integration note, not a QA defect.
- **Observation (not a defect)**: `${cmd} = 'powershell'` (assigning the quoted string `'powershell'` to a variable) DENYs. This is pre-existing conservative behavior of `_effective_command_token` (shlex strips quotes, so `$cmd = 'powershell'` bare form already DENYs); the braced form now matches the bare form (parity, verified by P1/P2). Not introduced by M0-T145 and not a regression.
- **Modularity**: 0 failures; the two changed files are not among the 12 pre-existing warnings. The change is a bounded, cohesive addition (one named regex + one small named helper + one wiring line, same style as the surrounding module) — no responsibility mixing, no giant function, no new oversized file. **Ruff clean.**

## Defects

None.

## Required rework

None.

## Reviewer conclusion

**PASS.** The braced-variable assignment-fronted nested-shell residual is genuinely closed against the real guard at frozen SHA `0671edd5`: the documented pytest command exits 0; my 27 independent probes and 3 independently reconstructed mutant teeth all match expectation; the Bash pack is behaviorally unchanged (source-gated and probe-confirmed); no pre-existing denial is lost; the guard docstring is honest about both the closure and the remaining unsafe-charset-name residual; modularity and ruff are clean. The authoritative per-requirement D-001 verdict is delegated to the separate directive-compliance-verifier gate. The orchestrator should record this G4 result; no rework required from this gate.

---

## ROUND 2 (delta re-attestation after G3 rework, reviewed bac01a56) — PASS

# Gate Report (Delta Re-Attestation)

- Gate ID: M0-T145-G4 (delta re-attestation)
- Task ID: M0-T145
- Reviewer: qa-engineer (independent G4; read-only)
- Producer: supervised-loop-fable-worker; G3-rework apply by the orchestrator
- Result: **PASS** (at the new identity `bac01a56`)
- Prior reviewed identity `0671edd5`: **superseded** — my earlier PASS there is **withdrawn** (it carried a real regression I did not probe for; see below)
- Clean environment/worktree used: yes — worktree `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m0t145`, branch `task/M0-T145-brace-guard`. Loose ref `.git/refs/heads/task/M0-T145-brace-guard` = `bac01a561e20398d3606bd770703f8311a89e029`; reflog confirms `29f9ee7b → 0671edd5 → bac01a56 (G3 rework: assignment-scoped debrace)`. Python 3.11.9. No `project_control.py`/`git`/`gh` invoked.

## What changed and why my prior PASS was wrong

The G3 finding is correct and reproduces. At `0671edd5`, `_ps_normalize` debraced `${x}` → `$x` **globally**, before `_split_command_segments`. Because `{`/`}` are in `_SEGMENT_CHARS` (they double as segment separators), the global debrace deleted the braces and **glued** the following command token: `${x}powershell -enc …` → `$xpowershell -enc …` (a single non-shell token), which the guard then ALLOWED — whereas the PARENT guard split at the braces and DENIED it. Six brace-glued forms regressed. My earlier 27-probe set covered assignment forms, reads, residuals, and parity, but did **not** include the brace-glued-no-assignment vector, so I missed it. Recorded the review-method lesson to my agent memory.

The rework (`bac01a56`) scopes the debrace to assignment position: `_PS_BRACED_VAR = re.compile(r"\$\{([A-Za-z0-9_:.\-]+)\}(?=\s*=(?!=))")`. The lookahead rewrites a braced name only when immediately followed by `=` (optionally spaced; not `==`), so every non-assignment `${...}` keeps its braces and its separator role — restoring the parent's denials for glued commands while retaining the assignment-fronted closure.

## Steps independently executed (at `bac01a56`)

1. Documented command: `python -m pytest tools/test_readonly_agent_guard_powershell.py -q` → **`1 passed in 18.26s`, exit 0**.
2. Direct-run form → **`ALL CHECKS PASSED`, exit 0**, including the 10 braced-assign DENY rows, 6 no-FP ALLOW rows, the **6 new brace-glued DENY rows**, and all three M0-T145 mutant teeth.
3. **Independent probe set, 35 probes** (my 27 unchanged + 8 new glued/edge), piped as PreToolUse JSON with `agent_type: "code-reviewer"` to the reworked guard → **`ALL PROBES MATCHED EXPECTATION`, exit 0**.
4. **Independent mutant reconstruction, 4 teeth** (T2 literal updated to the lookahead form; new T4 = lookahead removal) → **`ALL MUTANT TEETH LOAD-BEARING`, exit 0**.
5. `python tools/modularity_check.py --check` → **`failures 0`** (neither changed file among the 12 pre-existing warnings).
6. `python -m ruff check <guard> <test>` → **`All checks passed!`, exit 0**.

## Expected versus actual (delta-relevant probes)

| Probe (my own) | Expected | Actual | Note |
|---|---|---|---|
| GD1 `${MyVar}powershell -enc QQBBAA==` (glued, no `=`) | DENY | DENY | Regression fixed; matches parent |
| GD2 `${a.b}cmd /c whoami` (glued cmd) | DENY | DENY | |
| GD3 `${x}${y}pwsh -e AAAA` (double-braced glued) | DENY | DENY | |
| GD4 `${z}git push origin main` (glued git) | DENY | DENY | git-argv pass on braced segment |
| GD5 `${q}start powershell -enc AAAA` (glued spawn alias) | DENY | DENY | |
| GD6 `${x} =powershell -enc AAAA` (asymmetric-space assignment) | DENY | DENY | lookahead `\s*=` still fires |
| GD7 `${x}=powershell -enc AAAA` (glued assignment) | DENY | DENY | |
| GE1 `${x}==powershell -enc AAAA` (`==` not assignment) | ALLOW | ALLOW | boundary: `(?!=)` correctly declines; parity with parent |
| A3 `Get-Content notes.md > ${null}` | ALLOW | ALLOW | now via `_PS_REDIRECT_TARGET_OK` brace form (not debrace); matches parent |
| A5 `${env:PATH} -split ';' \| Select-String powershell` | ALLOW | ALLOW | braces intact, matches parent |
| B2 Bash `${x} = powershell -enc AAAA` | ALLOW | ALLOW | Bash byte-identical (unchanged) |
| R1/R2 unsafe-charset braced names | ALLOW | ALLOW | documented residual (unchanged) |
| P2 `${cmd} = 'powershell'` | DENY | DENY | parity with bare form (unchanged) |
| Mutant T4 (drop assignment lookahead) | mutant ALLOW / real DENY | mutant ALLOW / real DENY | **independently reproduces the G3 regression** |
| Mutant T1/T2/T3 | mutant ALLOW / real DENY | mutant ALLOW / real DENY | all still load-bearing |

All 35 probes and 4 mutants matched expectation.

## Regression/security/provenance findings

- **G3 regression is closed and stays closed under stress**: my six independent glued-form probes (distinct from the test's six) all DENY, matching the parent guard. The assignment-fronted closure is retained (D1–D12, braced-assign rows), and the lookahead's boundary is correct (`${x} =powershell` DENYs via `\s*=`; `${x}==powershell` ALLOWs via `(?!=)`, matching parent).
- **The lookahead is load-bearing and the regression is real**: mutant T4 removes the lookahead (reverting to the global debrace of `0671edd5`) and `${x}powershell -enc` slips to ALLOW while the real guard DENYs — an independent, executable reproduction of the exact defect G3 found.
- **No new false positives; parent-parity restored for non-assignment braces**: `> ${null}`, `${env:PATH} -split`, braced reads, and pipes now behave as the PARENT guard (braces preserved) rather than the debraced form. All A-series reads still ALLOW.
- **Bash pack byte-unchanged** (`if powershell:` gating; B1–B4 confirm), **all prior denials preserved** (full suite green), **provenance honest** (guard docstring lines 520–526 document the G3 round-6 correction and the deleted-separator root cause; residual for unsafe-charset names retained).
- **Modularity 0 failures; ruff clean.** The fix is a one-token regex change plus retained helper — no boundary/growth concerns.

## Directive/requirement verification

Unchanged from the base gate: D-001 (`ALL`, 136 reqs, every one scoped `task_ids: [M0-T023]`) — authoritative per-requirement verdict is delegated to the separate directive-compliance-verifier gate at the new frozen identity `bac01a56`. QA-observable substance R041 (directive-compliance-verifier stays in `READ_ONLY_AGENTS`, mutations denied) remains PASS — the change did not touch the roster or the read-only enforcement path.

## Defects

None at `bac01a56`. (The regression at the superseded `0671edd5` is resolved by this rework.)

## Required rework

None.

## Reviewer conclusion

**PASS at content identity `bac01a561e20398d3606bd770703f8311a89e029`.** My prior PASS at `0671edd5` is withdrawn — that commit carried the real, G3-found brace-glued regression. The rework's assignment-scoped lookahead closes it: verified by the documented command (exit 0), 35 independent probes including 8 glued/edge forms of my own (all matched), and 4 load-bearing mutant teeth (one of which independently reproduces the regression). Non-assignment brace behavior now matches the parent guard, the assignment-fronted closure and all prior denials are retained, Bash is byte-unchanged, and modularity/ruff are clean. The orchestrator should record this G4 result against `bac01a56`; no rework required.
