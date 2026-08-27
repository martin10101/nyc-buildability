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

print("== Correction round (G3 D1/D2/D3, G5 C1/C2/C3, G4 A1/A2/A3, D4) ==")
# D1/C1/A2 — write-cmdlet aliases now denied
for cmd in ["ac x.txt hi", "clc x.txt", "mi a.txt b.txt", "epcsv -Path r.csv -InputObject foo",
            "sp -Path HKCU:Soft -Name v -Value 1", "rp -Path x -Name y", "mkdir newdir"]:
    check(f"C1 alias deny: {cmd[:30]}", "DENY", ps(ROLE, cmd))
# D2 — .NET ::new() writer constructors
check("D2 StreamWriter::new deny", "DENY", ps(ROLE, '[System.IO.StreamWriter]::new("C:/x.txt")'))
check("D2 FileStream::new deny", "DENY", ps(ROLE, '[IO.FileStream]::new("x",2)'))
check("D2 BinaryWriter::new deny", "DENY", ps(ROLE, '[IO.BinaryWriter]::new($s)'))
# C2 — COM + CIM/WMI
check("C2 COM FileSystemObject deny", "DENY",
      ps(ROLE, "$f=New-Object -ComObject Scripting.FileSystemObject; $f.CreateTextFile('x')"))
check("C2 COM Shell.Application deny", "DENY",
      ps(ROLE, "$s=New-Object -ComObject Shell.Application; $s.ShellExecute('cmd')"))
check("C2 CIM Win32_Process Create deny", "DENY",
      ps(ROLE, "Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{CommandLine='calc'}"))
check("C2 WMI Win32_Process Create deny", "DENY",
      ps(ROLE, "Invoke-WmiMethod -Class Win32_Process -Name Create -ArgumentList 'calc'"))
# D3 — nested-shell laundering via the BASH tool (symmetric)
check("D3 bash>powershell -Command deny", "DENY", bash(ROLE, "powershell -Command Set-Content x 1"))
check("D3 bash>pwsh -c deny", "DENY", bash(ROLE, "pwsh -c Set-Content"))
check("D3 bash>cmd /c deny", "DENY", bash(ROLE, "cmd /c echo hi"))
check("D3 ps>powershell -enc deny", "DENY", ps(ROLE, "powershell -enc SQBFAFgA"))
# A1 — call-operator / dot-source quoted literal
check("A1 & 'Set-Content' deny", "DENY", ps(ROLE, "& 'Set-Content' x.txt 1"))
check("A1 &'Remove-Item' deny", "DENY", ps(ROLE, "&'Remove-Item' x.txt"))
check('A1 & "Out-File" deny', "DENY", ps(ROLE, '& "Out-File" -FilePath x'))
check("A1 . 'Set-Content' deny", "DENY", ps(ROLE, ". 'Set-Content' x 1"))
check("A1 & 'gh' pr create deny", "DENY", ps(ROLE, "& 'gh' pr create --title x"))
check("A1 & 'git' push deny", "DENY", ps(ROLE, "& 'git' push origin main"))
# C3 — the -Encoding read false-positive is fixed (was denied by former _PS_ENCODED)
check("C3 Get-Content -Encoding allow", "ALLOW", ps(ROLE, "Get-Content -Encoding UTF8 README.md"))
check("C3 Import-Csv -Encoding allow", "ALLOW", ps(ROLE, "Import-Csv -Encoding UTF8 rows.csv"))
check("C3 Select-String -Encoding allow", "ALLOW",
      ps(ROLE, "Select-String -Encoding utf8 -Path x.py -Pattern TODO"))
# A3 — ${null} redirect discard
check("A3 > ${null} allow", "ALLOW", ps(ROLE, "gci > ${null}"))
# nested-shell precision: the word mentioned in a read is not a nested shell
check("nested precision: echo cmd allow", "ALLOW", bash(ROLE, "echo cmd foo"))
check("nested precision: grep pwsh allow", "ALLOW", bash(ROLE, "grep pwsh tools/x.py"))
check("nested precision: & 'git' log read allow", "ALLOW", ps(ROLE, "& 'git' log --oneline -5"))
check("nested precision: & 'Get-Content' read allow", "ALLOW", ps(ROLE, "& 'Get-Content' README.md"))
# D4 — write hidden in a non-'command' tool_input field still caught (defensive extraction);
# malformed tool_input still fails closed.
check("D4 write in 'script' field deny", "DENY",
      {"hook_event_name": "PreToolUse", "tool_name": "PowerShell", "agent_type": ROLE,
       "tool_input": {"script": "Set-Content x.txt hi"}})
check("D4 pure read in 'script' field allow", "ALLOW",
      {"hook_event_name": "PreToolUse", "tool_name": "PowerShell", "agent_type": ROLE,
       "tool_input": {"script": "Get-Content README.md"}})
check("D4 malformed tool_input (string) fails closed", "DENY",
      {"hook_event_name": "PreToolUse", "tool_name": "PowerShell", "agent_type": ROLE,
       "tool_input": "Set-Content x 1"})
check("D4 command as int fails closed", "DENY",
      {"hook_event_name": "PreToolUse", "tool_name": "PowerShell", "agent_type": ROLE,
       "tool_input": {"command": 123}})

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
    "mutant drops nested-shell pass -> bash>powershell would slip": (
        SRC.replace("or _launches_nested_shell(cmd)", ""),
        bash(ROLE, "powershell -Command Set-Content x 1"),
    ),
    "mutant drops call-operator unwrap -> & 'gh' pr create would slip": (
        # gh lives in the shared _MUTATING core whose leading class excludes
        # quotes, so ONLY the call-operator unwrap makes `& 'gh'` reachable.
        SRC.replace(
            'return _PS_CALL_QUOTED.sub(lambda m: " " + m.group(2), normalized)',
            "return normalized"),
        ps(ROLE, "& 'gh' pr create --title x"),
    ),
    "mutant drops ::new() constructor tooth -> StreamWriter::new would slip": (
        SRC.replace(
            r"| \[(?:System\.)?IO\.(?:StreamWriter|FileStream|BinaryWriter)\]::new\b",
            ""),
        ps(ROLE, '[IO.StreamWriter]::new("x.txt")'),
    ),
    "mutant drops ComObject tooth -> New-Object -ComObject would slip": (
        SRC.replace(r"| New-Object\s+-ComObject\b", ""),
        ps(ROLE, "New-Object -ComObject Scripting.FileSystemObject"),
    ),
    "mutant drops CIM/WMI tooth -> Win32_Process Create would slip": (
        SRC.replace(
            r"| Invoke-(?:Cim|Wmi)Method\b[^;|]*?(?:Win32_Process\b|-MethodName\s+Create\b|-Name\s+Create\b|Create\b)",
            ""),
        ps(ROLE, "Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{CommandLine='c'}"),
    ),
    "mutant drops alias 'ac' -> Add-Content alias would slip": (
        SRC.replace(
            "ac|clc|mi|epcsv|sp|rp|spps|rbp|swmi|icm", "spps|rbp|swmi|icm"),
        ps(ROLE, "ac x.txt hi"),
    ),
    "mutant drops defensive field extraction -> write in 'script' field would slip": (
        SRC.replace(
            "    for key, value in tool_input.items():\n"
            "        if key == \"command\":\n"
            "            continue\n"
            "        if isinstance(value, str):\n"
            "            parts.append(value)\n",
            ""),
        {"hook_event_name": "PreToolUse", "tool_name": "PowerShell", "agent_type": ROLE,
         "tool_input": {"script": "Set-Content x.txt hi"}},
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
