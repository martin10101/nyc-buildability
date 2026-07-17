# Secret-scan + contracts-validator exit-code evidence (owner correction 5, 2026-07-17)

Owner finding: `python ... | tail; echo $?` captures tail's exit code, not Python's, and is
not valid evidence. Method used here instead (PowerShell 5.1): each scanner invoked via
`cmd /c "python <script> > <outfile> 2>&1"` — `cmd /c` propagates the child Python process
exit code — with `$LASTEXITCODE` captured on the immediately following line before any other
command, then the redirected output displayed. Recorded by the orchestrator.

Command template per tree:

```powershell
Set-Location <tree>
cmd /c "python .github\scripts\secret_scan.py > $env:TEMP\scan_<tree>.txt 2>&1"
$sc = $LASTEXITCODE   # captured immediately
cmd /c "python .github\scripts\validate_contracts.py > $env:TEMP\val_<tree>.txt 2>&1"
$vc = $LASTEXITCODE   # captured immediately
```

## Results (all runs 2026-07-17, post C1v2-corrections + bf97-mjsy fixtures)

| Tree | Commit state | secret_scan.py exit | secret_scan last line | validate_contracts.py exit | validator last line |
| --- | --- | --- | --- | --- | --- |
| main | `9f25ebb`+ledger edits | **0** | `secret-scan: PASS -- no findings` | **0** | `Checked 6 schema file(s); 0 failure(s).` |
| .claude/worktrees/M0-T010 (task/M0-T010-expansion-integration @ c0769ae) | clean | **0** | `secret-scan: PASS -- no findings` | **0** | `Checked 6 schema file(s); 0 failure(s).` |
| .claude/worktrees/M1-T007 (task/M1-T007-dob-now-research, C1v2 corrections + 4 new bf97-mjsy fixtures staged-uncommitted at run time) | dirty (pre-commit) | **0** | `secret-scan: PASS -- no findings` | **0** | `Checked 6 schema file(s); 0 failure(s).` |

PASS is recorded here only because the underlying Python processes returned zero, per the
owner's evidence standard. Full redirected outputs were inspected at `%TEMP%\scan_*.txt` /
`%TEMP%\val_*.txt` (transient; last lines quoted above are from those files).
