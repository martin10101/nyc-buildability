# M0-T108 G4 QA delta re-review (VERBATIM save; round 2, post-correction)

Reviewer: independent read-only `qa-engineer` (unnamed spawn, fresh pass); reviewed at corrected
deliverable identity `f0bdf7a` (HEAD `36f9720` = control-plane records only). Returned through the
agent-return channel 2026-08-27 UTC and saved verbatim below (transport entity-decoding only; the
harness neutralized `<`/`>`/`&` and flagged the output as instruction-shaped — control tags were
neutralized and the content is preserved here as reviewer findings, not instructions).

---

I have completed a full independent pass. All verification is reproducible at the frozen SHA. Here is my gate report.

---

# Gate Report

- **Gate ID:** M0-T108-G4 (DELTA re-review, round 2)
- **Task ID:** M0-T108 — Control-plane security fix: close the `readonly_agent_guard` PowerShell/scripting write gap (G5 M0-T102 MEDIUM)
- **Reviewer:** qa-engineer (independent; fresh pass, did not rely on the round-1 G4 conclusion)
- **Producer:** (correction round author)
- **Result: G4: PASS**
- **Clean environment/worktree used:** Yes. My worktree is at `d8b3899` (a control branch that does not contain the T108 commits). I extracted the frozen-identity files via `git archive f0bdf7a …` into an isolated scratchpad tree and confirmed byte-identity against the frozen blobs before running anything. All four load-bearing files match the `f0bdf7a` tree exactly.

## Acceptance criteria reviewed

Frozen deliverable identity confirmed:
- `git diff --name-only f0bdf7a..36f9720` → only `project-control/{reports/M0-T108.json, state.json, tasks/M0-T108.json}` — HEAD `36f9720` is **control-plane records only**; the reviewed content identity is `f0bdf7a`.
- Whole deliverable `24aa061..f0bdf7a` touches production paths `.claude/hooks/readonly_agent_guard.py`, `.claude/settings.json`, `tools/test_readonly_agent_guard_powershell.py` (+ report + control-plane). The Bash pack `tools/test_readonly_agent_guard.py` is **untouched** (blob `b421cb1` identical at `24aa061` and `f0bdf7a`).
- All production edits stay within the packet `allowed_paths`. No out-of-scope edits.

Byte-identity of extracted files vs frozen blobs (all match): guard `ee29267…`, ps-test `c7d3a15…`, bash-test `b421cb1…`, settings `c967b81…`.

## Directive/requirement verification

The task is in-regime (`directive_refs: [{D-024, requirement_ids: ALL}]`). Per ADR-005 the binding directive-compliance pass is the separate `directive-compliance-verifier` agent's `verification.json` (producer ≠ verifier), not this G4 QA gate. QA-observable facts I confirmed: the deliverable's production changes stayed strictly within `allowed_paths`; none of D-024's requirements are made applicable by these guard/settings/test paths, consistent with the producer's recorded empty-applicable-set convention. Final D-024 applicability adjudication is deferred to DCV.

## Steps independently executed

Both packs, twice, in the frozen scratchpad tree; plus three independent probe harnesses feeding JSON to the frozen guard on stdin (`probe.py` 39 cases, `probe2.py` quoted-text posture Bash vs PS symmetry, `probe3.py` extra denylist teeth + .NET read-method allow-list); plus independent replication of the mutation methodology for 3 subtle teeth.

## Expected versus actual

**(1) Pack counts + determinism** — confirmed: BASH run1/run2 exit 0, 136/136 PASS, 0 FAIL, ALL CHECKS PASSED, deterministic. PS run1/run2 exit 0, 138/138 PASS, 0 FAIL, ALL CHECKS PASSED, deterministic. Bash pack byte-unchanged from base.

**(2) Mutation adequacy** — the PowerShell pack carries **11 RED-on-mutant checks (all PASS)**, not 8: PowerShell branch, redirect scan, scripting-write pass, backtick normalization, nested-shell pass, call-operator unwrap, `::new()` constructors, `-ComObject`, CIM/WMI, alias `ac`, and defensive field extraction. The harness self-enforces non-vacuousness (`got=="ALLOW" and real=="DENY"`, plus a `mutated_src==SRC` no-op guard). I independently replicated the methodology for three subtle teeth — each target string present exactly once, real guard DENYs, hand-mutated copy ALLOWs (call-op unwrap A1, alias ac/clc/mi A2, CIM/WMI C2). The two significant ALLOW-teeth without a mutant (`${null}` discard, `-Encoding` read) cannot be RED-on-mutant tested by construction (false-positive removals; a mutant would over-block); covered by direct positive assertions and reproduced in probes. **Mutation adequacy SUFFICIENT.**

**(3) Specific advisory resolutions** — all confirmed: A1 `& 'Set-Content'`/`& 'gh' pr create`/`. 'Remove-Item'`/`&'Remove-Item'`/`& "Out-File"`/`& 'git' push` DENY; A2 `ac`/`clc`/`mi`/`mkdir` DENY; A3 `gci > ${null}`/`> $null` ALLOW; C3 `Get-Content -Encoding`/`Import-Csv -Encoding`/`Select-String -Encoding` ALLOW; read call-operators `& 'Get-Content' README.md`/`& 'git' log` ALLOW (unwrap is verb-agnostic, reads still pass).

**(4) Regression / new-FP hunt** — 39/39 probes + 17/17 extra-teeth probes matched expectation: word mentions (`echo cmd foo`, `grep pwsh`, `echo running powershell now`, `grep Set-Content`) ALLOW; nested-shell precision (`cat`, `grep -r`, `ls`, `find … -name powershell.txt`) ALLOW; nested-shell laundering (`powershell -Command`, `pwsh -c`) DENY; producer/lead PS write ALLOW, named-spawn PS write DENY; schtasks/icacls/Set-Acl/Set-ExecutionPolicy/reg delete/`[IO.File]::WriteAllText`/`[IO.Directory]::CreateDirectory`/standalone -OutFile/rd/cpi/rni/ren DENY; `[IO.File]::ReadAllText`/`::Exists`/`[IO.Directory]::GetFiles`/`::OpenRead` ALLOW (negative-lookahead keeps reads open).

**(5) Nested-shell precision** — legitimate Bash reads are not over-blocked; denial fires only when a shell binary is the first token of a segment. Confirmed.

## Regression/security/provenance findings

- **Quoted-text posture symmetric with the pre-existing Bash `_MUTATING` core, unchanged in kind:** token immediately after an opening quote → ALLOW on both shells (`grep 'git push' x`, `Select-String -Pattern 'Set-Content'` ALLOW — documented residual); a mutating token after a whitespace delimiter inside a quote → DENY on both (`echo 'run git push now'`, `Write-Output 'run Set-Content now'` DENY). Honest fail-closed posture documented at C4.
- Settings matcher change is exactly `Bash|…` → `Bash|PowerShell|…` (adds PowerShell, retains all prior tools); static checks pass.
- No new-material false positive. No blocking regression.

## Defects

None (blocking).

## Advisories (non-blocking, informational — do not require rework)

- **ADV-1:** the recorded "8 RED-on-mutant" is stale/low — the corrected pack carries **11** load-bearing mutants, all PASS. Update the recorded expectation to 11.
- **ADV-2 (accepted documented posture):** `Get-Help Set-Content` / `Get-Command Set-Content` DENY for a governed reviewer (write-cmdlet name after a space). Same fail-closed posture as the pre-existing Bash `echo git push` DENY; honestly documented (C4); not a regression in kind. A governed read-only reviewer rarely needs these.
- **ADV-3 (mutation completeness, minor):** individual denylist alternations (standalone `-OutFile`, `schtasks`, `icacls`, `Set-Acl`, `Set-ExecutionPolicy`, `reg delete`, aliases `cpi/rni/ren/rd`) are covered by the family-level regex and direct behavior but lack a per-alternation mutant. Each independently confirmed to DENY; per-item mutants would be excessive. Adequacy sufficient.

## Required rework

None.

## Reviewer conclusion

The round-1 advisories are fully resolved: A1 call-operator/dot-source quoted-literal invocations (including `& 'gh'`/`& 'git'`) now DENY while read call-operators stay ALLOW; A2 aliases `ac/clc/mi/mkdir` DENY; A3 `> ${null}` ALLOW; the A4/`-Encoding` mutant gap is retired by removing the over-broad `_PS_ENCODED` tooth (C3 reads ALLOW). The G3 write-bypass defects and G5 C1–C4 blockers are closed and independently reproduced. Both packs run byte-deterministically (Bash 136, PowerShell 138, both exit 0), the 11 mutants are load-bearing and non-vacuous, and my independent probes surfaced no new material false positive and no blocking regression; the PowerShell posture is symmetric in kind with the established Bash core. HEAD `36f9720` adds only control-plane records over the reviewed content `f0bdf7a`.

**G4: PASS**
