"""Stdlib regression test for the M0-T108 readonly-guard PowerShell/scripting
write-gap fix (.claude/hooks/readonly_agent_guard.py; G5 M0-T102 MEDIUM).

Proves, for a governed read-only role using the PowerShell tool:
- write cmdlets, their aliases, .NET IO writers, -OutFile, encoded/nested
  shells, Add-Type, Invoke-Expression, Start-Process, and the dynamic call
  operator are DENIED;
- git/gh/control-plane mutations issued through PowerShell are DENIED,
  including a git verb hidden behind PowerShell backtick escapes;
- unquoted redirects to real paths are DENIED while `$null` targets and
  stream merges are ALLOWED;
- genuine read-only PowerShell inspection is ALLOWED.

Proves the M0-T108 false-positive fix on BOTH shells: a literal `>` inside a
quoted string (python -c comparisons, arrow annotations, grep patterns) no
longer denies, while every unquoted redirect denial is retained.

Proves the best-effort scripting-write pass: inline `open(...,'w')`-class
idioms are DENIED for governed roles while mode-less/`'r'` opens (pure reads,
the observed M0-T102 reviewer false-positive class) stay ALLOWED.

Proves pass-through is unchanged: the lead (no identity keys) and a roster
producer keep full access; a named spawn fails closed; the settings matcher
lists the PowerShell tool.

RED-on-mutant: byte-mutated copies of the guard (PowerShell branch removed;
redirect scan removed; scripting pass removed) are executed from a temp tree
and shown to ALLOW what the real guard DENIES — proving each new tooth is
load-bearing, not vacuously green.

Run: python tools/test_readonly_agent_guard_powershell.py
"""
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
GUARD = REPO / ".claude" / "hooks" / "readonly_agent_guard.py"

ROLE = "code-reviewer"          # governed read-only roster role
PRODUCER = "backend-engineer"   # write-authorized roster role

FAILURES = []


def run_guard(payload_obj, guard_path=None):
    text = payload_obj if isinstance(payload_obj, str) else json.dumps(payload_obj)
    return subprocess.run(
        [sys.executable, str(guard_path or GUARD)],
        input=text, capture_output=True, text=True, timeout=30,
    )


def decision(payload_obj, guard_path=None):
    r = run_guard(payload_obj, guard_path)
    return ("DENY" if '"permissionDecision": "deny"' in r.stdout else "ALLOW"), r


def shell_payload(agent, tool, command):
    p = {"hook_event_name": "PreToolUse", "tool_name": tool,
         "tool_input": {"command": command}}
    if agent is not None:
        p["agent_type"] = agent
    return p


def check(name, expect, payload_obj, guard_path=None):
    got, r = decision(payload_obj, guard_path)
    ok = got == expect
    print(f"{'PASS' if ok else 'FAIL'}  {name}"
          + ("" if ok else f"  [expect={expect} got={got} rc={r.returncode}]"))
    if not ok:
        FAILURES.append(name)


def check_static(name, ok):
    print(f"{'PASS' if ok else 'FAIL'}  {name}")
    if not ok:
        FAILURES.append(name)


def ps(agent, command):
    return shell_payload(agent, "PowerShell", command)


def bash(agent, command):
    return shell_payload(agent, "Bash", command)


BACKTICK = chr(96)

print("== PowerShell write cmdlets / aliases (governed role) ==")
for cmd in [
    "Set-Content -Path x.txt -Value hi",
    "Add-Content x.txt more",
    "Clear-Content x.txt",
    "Out-File -FilePath out.log -InputObject $x",
    "Get-Process | Out-File p.txt",
    "New-Item -ItemType File notes.md",
    "Remove-Item -Recurse -Force build",
    "Move-Item a.txt b.txt",
    "Copy-Item src.py dst.py",
    "Rename-Item old.txt new.txt",
    "Set-ItemProperty -Path HKCU:\\X -Name v -Value 1",
    "Tee-Object -FilePath t.log",
    "Export-Csv -Path rows.csv",
    "Compress-Archive -Path src -DestinationPath out.zip",
    "sc x.txt hi",
    "ni newfile.txt",
    "ri oldfile.txt",
    "del stale.txt",
    "md newdir",
    "move a b",
    "copy a b",
]:
    check(f"PS cmdlet deny: {cmd[:44]}", "DENY", ps(ROLE, cmd))

print("== PowerShell .NET / dynamic / nested-shell vectors (governed role) ==")
for cmd in [
    "[IO.File]::WriteAllText('x.txt','hi')",
    "[System.IO.File]::AppendAllText('x.txt','hi')",
    "[IO.File]::Delete('x.txt')",
    "[IO.Directory]::CreateDirectory('d')",
    "[IO.Path]::GetTempFileName()",
    "New-Object System.IO.StreamWriter('x.txt')",
    "Invoke-WebRequest https://example.com -OutFile a.bin",
    "Invoke-RestMethod -Uri u -Method POST -Body $b",
    "Invoke-Expression $cmd",
    "iex (Get-Content payload.ps1 -Raw)",
    "Start-Process notepad",
    "Add-Type -TypeDefinition $src",
    "powershell -enc SQBFAFgA",
    "powershell.exe -NoProfile -Command Set-Content x 1",
    "cmd /c echo hi",
    "& $tool --do-things",
    "reg add HKCU\\Software\\X /v k /d v",
]:
    check(f"PS vector deny: {cmd[:44]}", "DENY", ps(ROLE, cmd))

print("== git/gh/control-plane through PowerShell (governed role) ==")
for cmd in [
    "git push origin main",
    "git commit -m fix",
    '& git -C "C:/some repo" push',
    "git.exe add -A",
    f"git pu{BACKTICK}sh",                      # backtick-hidden verb
    f"git -C 'a b' {BACKTICK}\ncommit -m x",    # backtick line continuation
    "gh pr create --title x",
    "python tools/project_control.py accept --task-id M0-T001",
    "npm install leftpad",
]:
    check(f"PS git/gh deny: {cmd[:40]}", "DENY", ps(ROLE, cmd))

print("== PowerShell redirects (governed role) ==")
check("PS redirect deny: Get-Content x > out.txt", "DENY",
      ps(ROLE, "Get-Content x > out.txt"))
check("PS redirect deny: git status >> log.txt", "DENY",
      ps(ROLE, "git status >> log.txt"))
check("PS redirect deny: 1>C:\\out.txt", "DENY",
      ps(ROLE, "Get-ChildItem 1>C:\\out.txt"))
check("PS redirect allow: > $null", "ALLOW", ps(ROLE, "Get-ChildItem > $null"))
check("PS redirect allow: 2>$null", "ALLOW", ps(ROLE, "git status 2>$null"))
check("PS redirect allow: 2>&1", "ALLOW",
      ps(ROLE, "python -m pytest tools 2>&1"))

print("== PowerShell read-only surface stays ALLOWED (governed role) ==")
for cmd in [
    "Get-Content README.md",
    "Get-ChildItem -Recurse tools",
    "Select-String -Path tools/*.py -Pattern TODO",
    "git status",
    "git log --oneline -5",
    "git diff HEAD~1",
    "gh pr view 241",
    "python -m pytest tools/test_readonly_agent_guard.py",
    "(Get-Command git).Source",
    "Get-CimInstance Win32_Process",
    "Get-Item x.txt",
    "Get-ItemProperty HKCU:\\X",
    "Measure-Object -Line",
    "Get-Content x.md | Select-Object -First 5",
]:
    check(f"PS read allow: {cmd[:44]}", "ALLOW", ps(ROLE, cmd))

print("== False-positive fix: quoted '>' is literal on BOTH shells ==")
for tool_fn, label in ((bash, "bash"), (ps, "ps")):
    check(f"{label} quoted-> allow: python -c comparison", "ALLOW",
          tool_fn(ROLE, 'python -c "print(1 if 2>1 else 0)"'))
    check(f"{label} quoted-> allow: arrow annotation", "ALLOW",
          tool_fn(ROLE, 'python -c "def f(x) -> int: return x"'))
check("bash quoted-> allow: grep pattern", "ALLOW",
      bash(ROLE, "grep 'a->b' tools/x.py"))
check("bash unquoted redirect still denied", "DENY",
      bash(ROLE, "echo hi > f.txt"))
check("bash append still denied", "DENY", bash(ROLE, "cat a >> b"))
check("bash fd-dup still allowed", "ALLOW",
      bash(ROLE, "python -m pytest 2>&1"))
check("bash /dev/null still allowed", "ALLOW",
      bash(ROLE, "git log 2>/dev/null"))

print("== Best-effort scripting-write pass (both shells) ==")
check("bash python -c open-w denied", "DENY",
      bash(ROLE, "python -c \"open('f','w').write('x')\""))
check("ps python -c open-a denied", "DENY",
      ps(ROLE, "python -c \"open('f','a').write('x')\""))
check("bash write_text denied", "DENY",
      bash(ROLE, "python -c \"import pathlib; pathlib.Path('f').write_text('x')\""))
check("bash os.remove denied", "DENY",
      bash(ROLE, "python -c \"import os; os.remove('f')\""))
check("bash shutil.rmtree denied", "DENY",
      bash(ROLE, "python -c \"import shutil; shutil.rmtree('d')\""))
check("bash pure read open(f) ALLOWED (observed FP class)", "ALLOW",
      bash(ROLE, "python -c \"print(open('f').read())\""))
check("bash pure read open(f,'r') ALLOWED", "ALLOW",
      bash(ROLE, "python -c \"print(open('f','r').read())\""))
check("bash read json.load ALLOWED", "ALLOW",
      bash(ROLE, "python -c \"import json; print(json.load(open('f'))['k'])\""))

print("== Identity pass-through unchanged ==")
check("lead (no identity) + PS Set-Content -> allow", "ALLOW",
      ps(None, "Set-Content x.txt hi"))
check("producer roster + PS Set-Content -> allow", "ALLOW",
      ps(PRODUCER, "Set-Content x.txt hi"))
check("named spawn (unknown identity) + PS write -> deny", "DENY",
      ps("my-reviewer-name", "Set-Content x.txt hi"))
check("governed + PS Write tool deny unchanged", "DENY",
      {"hook_event_name": "PreToolUse", "tool_name": "Write",
       "agent_type": ROLE, "tool_input": {"file_path": "x", "content": "y"}})
check("malformed payload fails closed", "DENY", "not-json{{{")

print("== Settings matcher lists the PowerShell tool ==")
settings = json.loads((REPO / ".claude" / "settings.json").read_text(encoding="utf-8"))
matchers = [e.get("matcher", "") for e in settings["hooks"]["PreToolUse"]]
guard_matcher = next(m for m in matchers if "readonly" in json.dumps(
    [h for e in settings["hooks"]["PreToolUse"] if e.get("matcher") == m
     for h in e["hooks"]]))
check_static("matcher covers PowerShell",
             re.search(r"\bPowerShell\b", guard_matcher) is not None)
check_static("matcher still covers Bash and write tools",
             all(re.search(rf"\b{t}\b", guard_matcher)
                 for t in ("Bash", "Write", "Edit", "MultiEdit", "NotebookEdit")))

print("== RED-on-mutant: each new tooth is load-bearing ==")
SRC = GUARD.read_text(encoding="utf-8")
MUTANTS = {
    "mutant drops PowerShell branch -> Set-Content would slip through": (
        SRC.replace('SHELL_TOOLS = frozenset({"Bash", "PowerShell"})',
                    'SHELL_TOOLS = frozenset({"Bash"})'),
        ps(ROLE, "Set-Content x.txt hi"),
    ),
    "mutant drops redirect scan -> unquoted redirect would slip through": (
        SRC.replace("or _unquoted_redirect(cmd, powershell=powershell)", ""),
        ps(ROLE, "Get-Content x > out.txt"),
    ),
    "mutant drops scripting pass -> open-for-write would slip through": (
        SRC.replace("or _SCRIPT_WRITE.search(cmd)", ""),
        bash(ROLE, "python -c \"open('f','w').write('x')\""),
    ),
    "mutant drops backtick normalization -> hidden git verb would slip": (
        SRC.replace("cmd = _ps_normalize(cmd)", "pass"),
        ps(ROLE, f"git pu{BACKTICK}sh"),
    ),
}
with tempfile.TemporaryDirectory() as td:
    for name, (mutated_src, payload) in MUTANTS.items():
        if mutated_src == SRC:
            check_static(f"{name} [mutation applied]", False)
            continue
        mpath = Path(td) / "mutated_guard.py"
        mpath.write_text(mutated_src, encoding="utf-8")
        got, _ = decision(payload, guard_path=mpath)
        # The mutant must ALLOW (i.e. the real guard's DENY is due to the
        # mutated tooth); the real guard must DENY the same payload.
        real, _ = decision(payload)
        check_static(name, got == "ALLOW" and real == "DENY")

print()
if FAILURES:
    print(f"{len(FAILURES)} FAILURE(S):")
    for f in FAILURES:
        print(f"  - {f}")
    sys.exit(1)
print("ALL CHECKS PASSED")
