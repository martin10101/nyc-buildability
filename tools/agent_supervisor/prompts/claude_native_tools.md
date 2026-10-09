# Native-tool preference (D-024 Amendment 14, R294)

Supervisor-owned fixed text appended to every dispatched worker unit. It is
worker-facing guidance ONLY: it carries no token quota, percentage, countdown, or
conserve-tokens pressure (D-024-R045), and it changes NOTHING about the command
broker, the classifier, or the owner gates. The empirical basis is the measured
routing fixture `fixtures/shell_routing_2026-08-29_m0t120_2_1_251.json` and the
first live run's shell-first ASK stops (`M0-T113-activation-evidence.md` item 4).

---

--- NATIVE-TOOL PREFERENCE (D-024-R294) ---
Use the native repository tools for all repository discovery and editing:

- To FIND code, files, or text: use Grep, Glob, and Read. Do not shell out to
  `powershell`, `pwsh`, `cmd`, `bash`, `sh`, `Get-ChildItem`, `dir`, `ls`,
  `findstr`, `grep`, `cat`, `type`, `Select-String`, `Get-Content`, or any
  ad-hoc script to list directories, search text, or read files.
- To CHANGE a file: use Edit and Write. Do not use `sed`, `echo >`, redirection,
  here-strings, `Set-Content`, `Add-Content`, or any shell command to write or
  patch files.
- The ONLY commands you run through the approval broker are the validation
  commands your task packet documents (its `documented_test_commands`). Run those
  exactly as documented; propose no other shell command for discovery or editing.
- A shell command for routine discovery or editing will be held for a human and
  will stall this run. Native tools are in scope and do not stall it. When a task
  genuinely needs a command that is not documented, stop and report why in your
  checkpoint rather than improvising a shell command.
