---
name: powershell-parse-testing
description: To test a PowerShell script for parse validity, use the WinPS 5.1 Parser API (not exit codes); $var: interpolation hazard vs legitimate $env: namespace
metadata:
  type: feedback
---

To regression-test a PowerShell script for PARSE validity, assert on the Windows
PowerShell 5.1 language parser's error list, NOT on the process exit code.

**Why:** A parse failure ALSO exits non-zero, so an exit-code check masquerades as an
intended runtime refusal (e.g. M0-T049: a broken `harden_controller_config.ps1` never
parsed, yet the existing "refuses unelevated" test stayed GREEN because a parse error also
exits non-zero and printed unrelated text). Only the parser's own error count catches
"never parsed". A fully-parsed script reaches its runtime guards (e.g. the elevation
`Write-Error`) at a real line number; a parse-failed one dies at the offending token.

**How to apply:** From `powershell.exe` (WinPS 5.1, NOT `pwsh`, so 5.1 tokenizer semantics):
`[System.Management.Automation.Language.Parser]::ParseFile(path,[ref]$t,[ref]$e)|Out-Null; $e.Count` — assert 0, print `$e.Message` on failure. Guard with skipUnless(IS_WINDOWS and
shutil.which("powershell")). Also prove RED by parsing a reverted-defect copy OUTSIDE the repo.

The defect class: `"$SomeVar:(text)"` in a double-quoted string — PS parses the `:` after an
interpolated variable as a scope/drive qualifier, so the whole file is a parse error. Fix
with the brace form `"${SomeVar}:(text)"`. NOTE `"$env:USERNAME"` etc. is NOT this bug —
`env:`/`global:`/`script:` are legitimate namespace qualifiers. Audit only for a plain
variable followed by `:` and a non-name char.
