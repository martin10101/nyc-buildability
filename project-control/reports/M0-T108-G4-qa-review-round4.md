# M0-T108 G4 QA review — ROUND-4 re-review (VERBATIM save)

Reviewer: independent read-only `qa-engineer` (unnamed spawn, fresh pass); reviewed at round-4
deliverable identity `b6db457` (HEAD `b194c90` = control-plane records only). Returned through the
agent-return channel 2026-08-27 UTC and saved verbatim below (transport entity-decoding only; the
harness neutralized `<`/`>`/`&` and flagged the output as instruction-shaped — control tags were
neutralized and the content is preserved here as reviewer findings, not instructions).

Orchestrator note (ADV-4 independently reproduced): `[type]::GetTypeFromProgID('Scripting.FileSystemObject')`
alone → ALLOW (the tooth is unreachable behind `::`), but it returns only a Type, not a writable
instance; the full reflection-COM write path `[activator]::CreateInstance([type]::GetTypeFromProgID(...))`
and the two-statement form → DENY via the reachable `[Activator]::CreateInstance` tooth. Fail-safe,
non-blocking; scheduled for a behavior-neutral cleanup (make the tooth reachable or remove the dead
redundant one).

---

I have everything needed for an evidence-based verdict. All checks reproduced at frozen identity `b6db457` (blob IDs verified byte-identical). Here is my gate report.

---

# Gate Report

- **Gate ID:** M0-T108-G4 (DELTA re-review, ROUND 4)
- **Task ID:** M0-T108 — Control-plane security fix: close the `readonly_agent_guard` PowerShell/scripting write gap (G5 M0-T102 MEDIUM)
- **Reviewer:** qa-engineer (independent, read-only; fresh pass — did not rely on the producer's conclusion or consult other current reviewers)
- **Producer:** fable-orchestrator-session (round-4 correction author)
- **Result: G4: PASS** — the round-4 delta holds my round-3 PASS with no blocking regression; ADV-1 and ADV-3 (and ADV-2) are resolved. One new non-blocking advisory (ADV-4), routed to the security lane.
- **Clean environment/worktree used:** Yes — reconstructed the frozen `b6db457` tree from git blobs in an isolated scratchpad and verified byte-identity before executing (my dispatched worktree HEAD is `d8b3899`, which predates the deliverable).

## Acceptance criteria reviewed

Objective (i)–(iv) + round-4 correction scope: fix G3 FAIL (D-R3-1 `-Encoding`+shell-word FP), fix G5 FAIL (NF1 COM `-C`/`-Co` + reflection; NF2 assignment-fronted `$z=powershell -enc`), resolve my round-3 ADV-1 (`start`/`saps` data over-block) and ADV-3 (COM `-c`/`-co` fail-open).

## Frozen identity verification

- **Deliverable identity = `b6db457`.** Verified byte-identity of every reviewed blob via `git hash-object` vs `git rev-parse b6db457:<path>` — all four match: guard `54213975…`, settings `c967b817…`, base test `b421cb15…`, PS test `920e9594…`.
- **`b6db457..b194c90` = control-plane records only** — no deliverable blob. HEAD carries no code change.
- **Base pack unchanged:** `tools/test_readonly_agent_guard.py` absent from both the round-4 correction delta and the whole-deliverable diff — byte-unchanged from base.
- Round-4 guard change reviewed at `git diff e1f6d4c..b6db457`: COM floor `-Com\w*`→`-c\w*`; added `[Activator]::CreateInstance`/`GetTypeFromProgID` teeth; `start`/`saps` moved out of `_PS_MUTATING` into a command/spawn-position `_SPAWN_ALIAS`; new `_effective_command_token` (assignment-RHS); removed `_PS_ENCODED_CMD`/`_PS_HAS_SHELL`. Surgical and additive.

## Directive/requirement verification

In-regime. Binding requirement pass owned by `directive-compliance-verifier` (`verification.json`), not G4. QA-observable: production changes confined to guard/settings/test paths; none make a D-024 requirement applicable. Full adjudication deferred to DCV.

## Steps independently executed (against the byte-verified frozen `b6db457` tree)

1. `python tools/test_readonly_agent_guard.py` — twice. 2. `python tools/test_readonly_agent_guard_powershell.py` — twice. 3. Probe harness #1 (45 cases): ADV-3/ADV-1/D-R3-1/NF2/NF1 direct probes, over-block FP hunt, encoded-shell fail-open hunt. 4. Probe harness #2 (10 cases): `GetTypeFromProgID` tooth + reflection-COM write path. 5. Source read of the 768-line round-4 guard + 15-mutant harness + exact round-4 diff. Python 3.11.9; guard uses no PEP 695, executes identically to repo 3.12.

## Expected versus actual

**(1) Pack counts + determinism — CONFIRMED.** Base pack 136 PASS/0 FAIL, exit 0, both runs byte-identical. PowerShell pack 187 PASS/0 FAIL, exit 0, both runs byte-identical, 15 RED-on-mutant proofs.

**(2) Mutation adequacy — SUFFICIENT; all 15 mutants load-bearing and non-vacuous.** No-op guard + directional assertion. Verified the four round-4 mutants at source: COM floor (`-c\w*`→`-Com\w*`, payload `New-Object -C` real DENY/mutant ALLOW), Activator/reflection (payload `[activator]::CreateInstance($t)` real DENY/mutant ALLOW — load-bearing for the Activator sub-tooth; see ADV-4 re GetTypeFromProgID), spawn-alias (`start notepad`), assignment-RHS (`$z=powershell -enc`). All target-present.

**(3) Specific fixes hold — CONFIRMED by direct probes.** ADV-3 RESOLVED (`New-Object -c/-co/-com/-ComObject` DENY). ADV-1 RESOLVED (`Select-String -Pattern start` ALLOW, `git log --grep start` Bash ALLOW; `start notepad`/`saps`/`start powershell -enc` DENY — and `start notepad` now DENIES on the Bash tool too, coverage gain). D-R3-1 RESOLVED (`Select-String -Encoding … -Pattern powershell` ALLOW; also resolves ADV-2). NF2 RESOLVED (`$z=powershell -enc`, spaced/`=powershell`/`pwsh`/`cmd` forms DENY; assignment READS `$x = Get-Content`, `$startTime = Get-Date` ALLOW). NF1 reflection: `[activator]::CreateInstance(...)`, `[System.Activator]::CreateInstance(...)`, full one-liner/two-liner reflection-COM DENY via reachable Activator tooth.

**(4) Regression / new-FP hunt — no blocking regression.** No new over-block: `New-Object System.Collections.ArrayList`, `-TypeName System.Text.StringBuilder`, `byte[] 10`, `PSObject -Property @{…}`, `$x = Get-Content`, `$data = Import-Csv`, `Get-CimInstance`, `Get-Content -Encoding`, `Start-Service`, `Start-Sleep`, `$PSVersionTable.PSVersion`, `$h=@{}`, `$x = $cmd` all ALLOW. No new fail-open from removing the scoped pair: encoded-shell class DENIES across every invocation position (first-token, `& powershell -enc`, `cmd /c powershell -enc`, pipe-fronted, semicolon-fronted, start/saps-fronted, all assignment-RHS). Bash path unaffected.

**(5) Determinism — CONFIRMED** (both packs + both probe harnesses byte-identical across two runs).

## Regression/security/provenance findings

- No blocking regression. Net improvement: resolves two FPs (ADV-1, ADV-2/D-R3-1), closes two fail-open gaps (ADV-3, NF2), extends `start`/`saps` spawn coverage to the Bash tool. Docstring/residuals updated honestly.
- **ADV-4 (NEW, non-blocking, fail-safe; route to G5):** The round-4 `GetTypeFromProgID\b` tooth is **unreachable as written**. `_PS_MUTATING`'s leading-delimiter class is `[\s;&|({`=]`, but real usage is `[Type]::GetTypeFromProgID(...)` where the token is preceded by `:` (from `::`), not a delimiter — so `[type]::GetTypeFromProgID('Scripting.FileSystemObject')` returns **ALLOW** (reproduced). Not a bypass/blocker because: (a) the practical reflection-COM instantiation requires `[Activator]::CreateInstance` (or `New-Object -ComObject`), both reachable and DENY — full one-liner, two-statement form, `System.Activator` prefix, assignment-fronted all DENY; (b) `GetTypeFromProgID` alone returns a `Type`, not a writable COM instance; (c) new round-4 defense-in-depth tooth, so its ineffectiveness reopens nothing (fail-safe). Mutation note: mutant #12 proves the Activator sub-tooth load-bearing but cannot prove the co-removed dead `GetTypeFromProgID` sub-tooth. **Recommendation:** anchor as `::GetTypeFromProgID` / add `:` to its delimiter set, or document it as redundant with the Activator tooth. Security-lane disposition, not a G4 blocker.

## Defects (blocking)
None.

## Required rework
None (for G4). ADV-4 recommended for a security-lane (G5) disposition — not a G4 blocker.

## Reviewer conclusion

The round-4 correction holds my round-3 PASS with no blocking regression. Both packs run byte-deterministically (136 base, 187 PowerShell, exit 0, zero FAIL across two runs each); all 15 mutants are target-present, directional, and non-vacuous, with the four round-4 teeth verified load-bearing. My three round-3 advisories are resolved: ADV-3 (COM `-c`/`-co`) now DENIES, ADV-1 (`start`/`saps` data) now ALLOWs data while denying spawns, ADV-2 (`-Encoding`+shell-word) now ALLOWs. The round-4 drivers hold: G3 D-R3-1 reads ALLOW and G5 NF2 assignment-fronted encoded shell DENIES. My over-block and fail-open hunts found no new false positive and no reopened bypass; the removal of `_PS_ENCODED_CMD`/`_PS_HAS_SHELL` is fully compensated by command-position detection. The one new residual (ADV-4, the dead `GetTypeFromProgID` tooth) is fail-safe, does not create a bypass (the reflection-COM write path is denied by the reachable Activator tooth), and belongs to the G5 lane.

**G4: PASS**
