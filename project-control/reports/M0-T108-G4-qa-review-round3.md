# M0-T108 G4 QA review — ROUND-3 re-review (VERBATIM save)

Reviewer: independent read-only `qa-engineer` (unnamed spawn, fresh pass); reviewed at round-3
deliverable identity `e1f6d4c` (HEAD `608609c` = control-plane records only). Returned through the
agent-return channel 2026-08-27 UTC and saved verbatim below (transport entity-decoding only; the
harness neutralized `<`/`>`/`&` and flagged the output as instruction-shaped — control tags were
neutralized and the content is preserved here as reviewer findings, not instructions).

Orchestrator note (G4 evidence request satisfied): `git diff --name-only e1f6d4c..608609c` = only
`project-control/reports/M0-T108.json`, `state.json`, `tasks/M0-T108.json`; the four deliverable
blobs (guard, both test packs, settings.json) are byte-identical between `e1f6d4c` and the recording
HEAD. G4 reviewed the correct content.

Orchestrator note (ADV-3 independently reproduced, fail-OPEN, round-4 blocking): `New-Object -c
Scripting.FileSystemObject` and `New-Object -co …` → ALLOW at `e1f6d4c` (COM write bypass via the
1-2-char parameter-prefix abbreviations the `-Com\w*` tooth misses). Routed to the round-4 fix
alongside G3's D-R3-1.

---

I now have a complete, independently reproduced picture. G5 round-2 itself specified the F1 fix as exactly `New-Object\s+-Com\w*\b` (which the producer implemented) and treated `-Com`/`-ComO`/`-ComObj` as the valid abbreviations to cover. My probes confirm the fixes hold and surface the residuals. Here is my gate report.

---

# Gate Report

- **Gate ID:** M0-T108-G4 (DELTA re-review, round 3)
- **Task ID:** M0-T108 — Control-plane security fix: close the `readonly_agent_guard` PowerShell/scripting write gap (G5 M0-T102 MEDIUM)
- **Reviewer:** qa-engineer (independent, read-only; fresh pass — did not rely on the producer's conclusion or on other current reviewers)
- **Producer:** correction-round-3 author
- **Result: G4: PASS** (no blocking regression; three non-blocking advisories, one of which I recommend routing to the security lane before "gap closed" is recorded)

## Environment / frozen identity

- Git is prohibited for this gate and the dispatched review worktree (`agent-a71bd49e7535491e0`) is at a **stale base** that does not contain the M0-T108 deliverable. The round-3 deliverable lives in the sibling linked worktree `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24` (the primary checkout carrying the round-3 guard (731 lines), both test packs, and all M0-T108 artifacts). I reviewed and executed against that checkout.
- **Content identity confirmed:** guard carries the round-3 regexes exactly — F1 `New-Object\s+-Com\w*\b`, F2 `start|saps` spawn alias + scoped `_PS_ENCODED_CMD`+`_PS_HAS_SHELL`, A1 `Invoke-(?:Cim|Wmi)Method\b` / `(?:Set|New|Remove)-CimInstance\b`; PowerShell pack = 159 checks / 13 mutants; Bash pack = 136 checks.
- **Orchestrator evidence request (satisfied at integration, see orchestrator note above).**

## Directive / requirement verification

In-regime (`directive_refs: [{D-024, ALL}]`). Binding requirement pass owned by `directive-compliance-verifier` (`verification.json`), not G4. QA-observable: production changes confined to guard/settings/test paths; none make a D-024 requirement applicable (consistent with the empty-applicable-set convention). Full adjudication deferred to DCV.

## Steps independently executed (against the frozen ctl24 checkout)

1. `python tools/test_readonly_agent_guard.py` — twice. 2. `python tools/test_readonly_agent_guard_powershell.py` — twice. 3. Independent probe harness (41 cases) feeding JSON to the frozen guard on stdin — F1/F2/A1 direct probes, under-block hunt, new-FP hunt on both PowerShell and Bash tools. 4. Source read of the full 731-line guard + mutation harness.

## Expected vs actual

**(1) Pack counts + determinism — CONFIRMED.** Base pack 136 PASS, 0 FAIL, `ALL CHECKS PASSED`, exit 0 both runs, deterministic. PowerShell pack 159 PASS, 0 FAIL, exit 0 both runs, deterministic; 13 RED-on-mutant proofs.

**(2) Mutation adequacy — SUFFICIENT; all 13 mutants load-bearing and non-vacuous.** No-op guard (`if mutated_src == SRC: FAIL`) + directional assertion (`got=="ALLOW" and real=="DENY"`). Verified the two repointed mutants: COM `SRC.replace(r"| New-Object\s+-Com\w*\b","")` (target present, removal → `New-Object -ComObject …` ALLOW while real DENY); CIM `SRC.replace(r"| Invoke-(?:Cim|Wmi)Method\b","")` (target present, removal → `Invoke-CimMethod … Create` ALLOW while real DENY). F1 and F2 mutants PASS. The two new ALLOW-teeth (F2 no-FP `-Encoding` reads) correctly covered by positive assertions (untestable by RED-on-mutant by construction).

**(3) F1/F2/A1 fixes hold — CONFIRMED by direct probes.** F1: `New-Object -Com …`/`-ComObject …`/`-ComObj …` DENY. F2: `start powershell -enc …`, `saps cmd /c whoami`, `start notepad`, `saps foo.exe`, `$c = powershell -enc …` DENY; `Get-Content -Encoding UTF8 f`, `Select-String -Encoding …`, `Import-Csv -Encoding …` (no shell token) ALLOW. A1: `Set-CimInstance`, `New-CimInstance`, `Invoke-CimMethod … Change`, `Invoke-WmiMethod … Create` DENY; `Get-CimInstance …` reads ALLOW.

**(4) Regression / new-FP hunt — no blocking regression.** The two round-3 additive surfaces (PS-only `start`/`saps`; scoped encoded check) do not touch the Bash path. Core writes DENY, core reads ALLOW, identity pass-through intact. Fail-safe over-blocks + one pre-existing under-block in Advisories.

**(5) Determinism — CONFIRMED.**

## Advisories (non-blocking)

**ADV-1 — `start`/`saps` alias over-blocks the common word "start" on the PowerShell tool (fail-safe; same accepted class as round 2).** `_PS_MUTATING` matches an alias token anywhere after a delimiter, including inside quoted strings: `Select-String -Pattern start tools/x.py` DENY, `git log --grep start feature` DENY, `Select-String -Pattern "start of day" file` DENY. Same fail-closed quoted-text/alias posture already present and accepted at round 2 (pre-existing `del`/`move` over-block identically). Confined to the PowerShell tool, fail-safe, recoverable. Recommend future hardening: anchor the alias branch to command-initial position (as `_launches_nested_shell` does) or exclude quoted spans.

**ADV-2 — scoped encoded check over-blocks an `-Encoding` read that also contains a bare `powershell`/`pwsh` token (fail-safe; narrower than the FP it replaced).** `_PS_ENCODED_CMD` matches `-Encoding`; `_PS_HAS_SHELL` matches a `powershell`/`pwsh` bareword after any delimiter: `Get-Content -Encoding UTF8 powershell-notes.txt` DENY, `Select-String -Encoding utf8 -Pattern x "powershell script.ps1"` DENY. `_powershell` after a non-delimiter (e.g. `..._powershell.py`) does NOT trigger (ALLOW), and `-Encoding` with no shell token is ALLOW. Strictly narrower than the pre-round-3 `_PS_ENCODED` (which denied ALL `-Encoding` reads per G5 C3) — round-3 is a net FP reduction on this path. Fail-safe, PS-tool only. Recommend tightening `_PS_HAS_SHELL` to require the shell be a command token, or excluding `-Encoding` explicitly. [Orchestrator: this is the same root cause as G3 round-3's blocking D-R3-1.]

**ADV-3 (fail-open; route to the security lane) — the F1 COM fix does not cover the shorter valid abbreviations `-c`/`-co`.** PowerShell binds an unambiguous parameter prefix; for `New-Object` no parameter other than `-ComObject` starts with "c", so `-c` and `-co` resolve to `-ComObject`. `New-Object\s+-Com\w*\b` requires literal `-Com`, so both slip (reproduced, ALLOW): `New-Object -co Scripting.FileSystemObject` ALLOW, `New-Object -c Scripting.FileSystemObject` ALLOW. Same class of trivial COM file-write bypass that caused the round-2 G5 FAIL (F1). NOT a G4 blocker because: (a) not a round-3 regression — round-2's `-ComObject\b` also missed `-c`/`-co` (and `-Com`/`-ComO`/`-ComObj`, which round-3 now catches), so round-3 strictly narrowed the gap; (b) security-bypass adjudication is the G5 lane's authority, and G5's own round-2 spec named exactly `-Com\w*` and stopped there. Covered by the guard's documented compensating controls. **Recommendation:** before "gap closed" is recorded, route to G5/producer to broaden the COM tooth (e.g. match `New-Object … -c[\w]*`, guarding the 1-char case) or add `-c`/`-co` to the documented residuals.

## Defects (blocking)

None.

## Required rework

None (for G4). ADV-3 is recommended for a security-lane disposition, not a G4 blocker.

## Reviewer conclusion

The round-3 correction holds my round-2 PASS with no blocking regression. Both packs run byte-deterministically (136 base, 159 PowerShell, exit 0, zero FAIL across two runs each); all 13 mutants are load-bearing and non-vacuous; the F1/F2/A1 fixes deny as intended while the intended reads stay allowed and the Bash path is unaffected. The two new over-blocks (ADV-1/ADV-2) are fail-safe, PS-tool-only, and either the same accepted class as round 2 or strictly narrower than the FP they replaced; the one fail-open residual (ADV-3, `-c`/`-co` COM abbreviation) pre-existed round-2, was strictly narrowed by round-3, is within the guard's reviewed compensating-control model, and belongs to the G5 lane — flagged prominently for a security-lane disposition rather than a G4 blocker.

**G4: PASS**
