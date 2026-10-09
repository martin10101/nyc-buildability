# fixtures.ps1 - shared fixture builders for the controller-update source-binding
# tests (M0-T138; D-024-R613). Dot-sourced by test_*.ps1; not a test itself.
#
# Builds a deterministic throwaway git repository with three commits:
#   shaA - tools/agent_supervisor WITHOUT mrl_launch_draft.py (missing-module case)
#   shaB - adds mrl_launch_draft.py: the fixture's "accepted" candidate
#   shaC - changes only a root-level file: internally self-consistent wrong
#          commit whose tools/agent_supervisor subtree EQUALS shaB's
# plus an 'origin' remote URL, so the script's identity checks are exercised
# against real git plumbing, never mocks.

function Invoke-FixtureGit {
    param([string]$Repo, [string[]]$GitArgs)
    $global:LASTEXITCODE = $null
    $out = & git -C $Repo -c user.name=fixture -c user.email=fixture@example.invalid @GitArgs 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw ("fixture git failed (" + ($GitArgs -join ' ') + "): " + ($out -join ' '))
    }
    return ($out | Out-String).Trim()
}

function New-FixtureWork {
    $work = Join-Path $env:TEMP ('ctl24-srcbind-' + [guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory -Force -Path $work | Out-Null
    return $work
}

function New-FixtureRepo {
    param([string]$Root)
    $repo = Join-Path $Root 'repo'
    New-Item -ItemType Directory -Force -Path $repo | Out-Null
    $global:LASTEXITCODE = $null
    & git init -q $repo 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) { throw 'fixture git init failed' }
    Invoke-FixtureGit -Repo $repo -GitArgs @('config', 'core.autocrlf', 'false') | Out-Null
    Invoke-FixtureGit -Repo $repo -GitArgs @('remote', 'add', 'origin', 'https://example.invalid/fixture-pack.git') | Out-Null

    $pkg = Join-Path $repo 'tools\agent_supervisor'
    New-Item -ItemType Directory -Force -Path (Join-Path $pkg 'schemas') | Out-Null
    New-Item -ItemType Directory -Force -Path (Join-Path $pkg 'ps_tests') | Out-Null
    New-Item -ItemType Directory -Force -Path (Join-Path $pkg 'launchers') | Out-Null
    Set-Content -LiteralPath (Join-Path $pkg 'cli.py') -Value 'print("fixture cli")' -Encoding ascii
    Set-Content -LiteralPath (Join-Path $pkg 'manifest.py') -Value 'print("fixture manifest")' -Encoding ascii
    Set-Content -LiteralPath (Join-Path $pkg 'mrl_launch_manifest.py') -Value 'print("fixture launch manifest")' -Encoding ascii
    Set-Content -LiteralPath (Join-Path $pkg 'command_docs.py') -Value 'print("fixture command docs")' -Encoding ascii
    Set-Content -LiteralPath (Join-Path $pkg 'schemas\example.schema.json') -Value '{"fixture": true}' -Encoding ascii
    Set-Content -LiteralPath (Join-Path $pkg 'README.md') -Value '# fixture package' -Encoding ascii
    Set-Content -LiteralPath (Join-Path $pkg 'ps_tests\run_ps_tests.ps1') -Value 'exit 0' -Encoding ascii
    Set-Content -LiteralPath (Join-Path $pkg 'launchers\run.cmd') -Value '@echo fixture' -Encoding ascii
    Invoke-FixtureGit -Repo $repo -GitArgs @('add', '-A') | Out-Null
    Invoke-FixtureGit -Repo $repo -GitArgs @('commit', '-q', '-m', 'A: package without mrl_launch_draft') | Out-Null
    $shaA = Invoke-FixtureGit -Repo $repo -GitArgs @('rev-parse', 'HEAD')
    $treeA = Invoke-FixtureGit -Repo $repo -GitArgs @('rev-parse', ($shaA + '^{tree}'))
    $subtreeA = Invoke-FixtureGit -Repo $repo -GitArgs @('rev-parse', ($shaA + ':tools/agent_supervisor'))

    Set-Content -LiteralPath (Join-Path $pkg 'mrl_launch_draft.py') -Value 'print("fixture launch draft")' -Encoding ascii
    Invoke-FixtureGit -Repo $repo -GitArgs @('add', '-A') | Out-Null
    Invoke-FixtureGit -Repo $repo -GitArgs @('commit', '-q', '-m', 'B: accepted candidate with mrl_launch_draft') | Out-Null
    $shaB = Invoke-FixtureGit -Repo $repo -GitArgs @('rev-parse', 'HEAD')
    $treeB = Invoke-FixtureGit -Repo $repo -GitArgs @('rev-parse', ($shaB + '^{tree}'))
    $subtreeB = Invoke-FixtureGit -Repo $repo -GitArgs @('rev-parse', ($shaB + ':tools/agent_supervisor'))

    Set-Content -LiteralPath (Join-Path $repo 'notes.txt') -Value 'root-level change only' -Encoding ascii
    Invoke-FixtureGit -Repo $repo -GitArgs @('add', '-A') | Out-Null
    Invoke-FixtureGit -Repo $repo -GitArgs @('commit', '-q', '-m', 'C: self-consistent wrong commit (same subtree)') | Out-Null
    $shaC = Invoke-FixtureGit -Repo $repo -GitArgs @('rev-parse', 'HEAD')
    $treeC = Invoke-FixtureGit -Repo $repo -GitArgs @('rev-parse', ($shaC + '^{tree}'))
    $subtreeC = Invoke-FixtureGit -Repo $repo -GitArgs @('rev-parse', ($shaC + ':tools/agent_supervisor'))

    return @{
        repo = $repo
        shaA = $shaA; treeA = $treeA; subtreeA = $subtreeA
        shaB = $shaB; treeB = $treeB; subtreeB = $subtreeB
        shaC = $shaC; treeC = $treeC; subtreeC = $subtreeC
    }
}

function New-BindingFile {
    # Schema v2 (M0-T139; D-024 Amendment 42): transaction keys are derived from
    # the destination when a test does not override them, so every case gets a
    # self-consistent isolated binding.
    param([string]$Path, [hashtable]$Values)
    $destParent = Split-Path -Parent $Values.destination
    $controllerRoot = $Values.controller_root
    if (-not $controllerRoot) { $controllerRoot = $destParent }
    $backupRoot = $Values.backup_root
    if (-not $backupRoot) { $backupRoot = ($Values.destination + '-backups') }
    $runtimeDir = $Values.a1_runtime_dir
    if (-not $runtimeDir) {
        $runtimeDir = Join-Path $destParent ('NYCBuildabilitySupervisor\' + ('a' * 64))
    }
    $backupEvidence = $Values.backup_evidence
    if (-not $backupEvidence) { $backupEvidence = ($Values.destination + '-backup-evidence.json') }
    $rollbackEvidence = $Values.rollback_evidence
    if (-not $rollbackEvidence) { $rollbackEvidence = ($Values.destination + '-rollback-evidence.json') }
    $binding = [ordered]@{
        schema = 'controller_update_source_binding/v2'
        authority = 'fixture'
        source_repo = $Values.repo
        expected_origin_url = 'https://example.invalid/fixture-pack.git'
        commit_sha = $Values.commit_sha
        commit_tree_sha = $Values.commit_tree_sha
        subtree_path = 'tools/agent_supervisor'
        subtree_tree_sha = $Values.subtree_tree_sha
        required_modules = @(
            'tools/agent_supervisor/mrl_launch_draft.py',
            'tools/agent_supervisor/cli.py',
            'tools/agent_supervisor/manifest.py')
        source_worktree = $Values.source_worktree
        destination = $Values.destination
        controller_root = $controllerRoot
        backup_root = $backupRoot
        a1_runtime_dir = $runtimeDir
        backup_evidence = $backupEvidence
        rollback_evidence = $rollbackEvidence
        controller_manifest = $Values.controller_manifest
        evidence_out = $Values.evidence_out
    }
    $binding | ConvertTo-Json -Depth 5 | Out-File -FilePath $Path -Encoding utf8
    return $Path
}

function Initialize-TxSources {
    # Creates what -Phase backup needs to exist: an OLD controller tree at the
    # destination (distinct content from every fixture candidate, plus a stale
    # cache dir that must never be copied) and the shared A1 runtime fixture.
    param([string]$BindingPath)
    $binding = Get-Content -LiteralPath $BindingPath -Raw | ConvertFrom-Json
    $dest = [string]$binding.destination
    New-Item -ItemType Directory -Force -Path (Join-Path $dest 'launchers') | Out-Null
    New-Item -ItemType Directory -Force -Path (Join-Path $dest '__pycache__') | Out-Null
    Set-Content -LiteralPath (Join-Path $dest 'cli.py') -Value 'print("OLD controller cli")' -Encoding ascii
    Set-Content -LiteralPath (Join-Path $dest 'legacy_module.py') -Value 'print("legacy only in old tree")' -Encoding ascii
    Set-Content -LiteralPath (Join-Path $dest 'launchers\run.cmd') -Value '@echo old' -Encoding ascii
    Set-Content -LiteralPath (Join-Path $dest '__pycache__\stale.pyc') -Value 'stale' -Encoding ascii
    $runtime = [string]$binding.a1_runtime_dir
    if (-not (Test-Path -LiteralPath $runtime)) {
        New-Item -ItemType Directory -Force -Path (Join-Path $runtime 'sub') | Out-Null
        Set-Content -LiteralPath (Join-Path $runtime 'journal.db') -Value 'fixture journal bytes' -Encoding ascii
        Set-Content -LiteralPath (Join-Path $runtime 'sub\state.json') -Value '{"fixture": true}' -Encoding ascii
    }
    return $binding
}

function Invoke-BackupPhase {
    # Runs -Phase backup for a case and asserts nothing: callers judge the
    # result. Convenience only.
    param([string]$ScriptPath, [string]$BindingFile)
    return Invoke-UpdateScript -ScriptPath $ScriptPath -Phase backup -BindingFile $BindingFile
}

function Invoke-UpdateScript {
    # Runs the real operator script exactly the way the owner runs it: a fresh
    # powershell.exe -File process, raw $LASTEXITCODE, no piping.
    param([string]$ScriptPath, [string]$Phase, [string]$BindingFile)
    $so = [System.IO.Path]::GetTempFileName()
    $se = [System.IO.Path]::GetTempFileName()
    $global:LASTEXITCODE = $null
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $ScriptPath -Phase $Phase -BindingFile $BindingFile 1>$so 2>$se
    $code = $global:LASTEXITCODE
    $stdout = ''
    if (Test-Path -LiteralPath $so) { $stdout = [System.IO.File]::ReadAllText($so) }
    $stderr = ''
    if (Test-Path -LiteralPath $se) { $stderr = [System.IO.File]::ReadAllText($se) }
    Remove-Item -LiteralPath $so, $se -Force -ErrorAction SilentlyContinue
    return @{ exit_code = $code; stdout = $stdout; stderr = $stderr }
}

function Write-CraftManifestScript {
    # Independent implementation on purpose: python hashlib + fnmatch mirror the
    # production manifest generator, so the PS script's projection is
    # cross-checked against a second implementation, not against itself.
    param([string]$Path)
    $lines = @(
        'import fnmatch, hashlib, json, os, sys',
        'root, out = sys.argv[1], sys.argv[2]',
        'PATTERNS = ["*.py", "schemas/*.json", "prompts/*.md", "config.toml",',
        '            "config.example.toml", "launchers/*.cmd", "launchers/*.ps1", "README.md"]',
        'EXCLUDED = {"model_selection.toml", "controller_manifest.json"}',
        'EXCLUDED_DIRS = {"__pycache__", ".pytest_cache", ".git"}',
        'files = {}',
        'for dirpath, dirnames, filenames in os.walk(root):',
        '    dirnames[:] = [d for d in dirnames if d not in EXCLUDED_DIRS]',
        '    for name in filenames:',
        '        rel = os.path.relpath(os.path.join(dirpath, name), root).replace("\\", "/")',
        '        if name in EXCLUDED:',
        '            continue',
        '        if any(fnmatch.fnmatch(rel, pat) for pat in PATTERNS):',
        '            with open(os.path.join(dirpath, name), "rb") as handle:',
        '                data = handle.read().replace(b"\r\n", b"\n")',
        '            files[rel] = hashlib.sha256(data).hexdigest()',
        'with open(out, "w", encoding="utf-8") as handle:',
        '    json.dump({"manifest_version": 1, "files": files,',
        '               "manifest_digest": "fixture-digest"}, handle, indent=1)',
        'print(len(files))'
    )
    Set-Content -LiteralPath $Path -Value $lines -Encoding ascii
    return $Path
}
