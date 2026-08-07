@echo off
rem M0-T045 R595 supervised rehearsal - Phase R1 (cycle-1 live run).
rem Runs the code under test (task/M0-T045-r595-rehearsal @ 492a0f4) against the
rem owner's immutable controller config. Supervised mode with NO pre-approved
rem prompt digest: the continuation prompt is HELD at WAIT_FOR_OWNER by design.
rem Threshold 1 arms the rotation seam on the first real usage reading.
cd /d C:\Users\MLFLL\Downloads\nyc-zoning\orch
echo R595 Phase R1 starting (this window shows the live supervised run)...
python -m tools.agent_supervisor start --mode supervised --checkout "C:/Users/MLFLL/AppData/Local/Temp/r595/synthrepo" --runtime-base "C:/Users/MLFLL/AppData/Local/Temp/r595/runtime-r595" --claude-executable "C:/Users/MLFLL/.local/bin/claude.exe" --codex-executable "C:/Users/MLFLL/AppData/Roaming/npm/codex.cmd" --task-packet "C:/Users/MLFLL/AppData/Local/Temp/r595/packet.json" --config "C:/SupervisorController/config.toml" --model-selection "C:/SupervisorController/model_selection.toml" --repo "C:/Users/MLFLL/AppData/Local/Temp/r595/synthrepo" --worktree "C:/Users/MLFLL/AppData/Local/Temp/r595/wt-probe" --branch synthetic/probe-r595 --stage docs-continuity --run-id run_r595_rehearsal --prompt "Append one short dated line to docs/continuity-log.md summarizing the README's current state, then report a structured checkpoint for the current authorized stage." --max-cycles 2 --max-turns 12 --unit-timeout 900 --context-rotation-threshold 1 --json > "C:\Users\MLFLL\AppData\Local\Temp\r595\r1-start-output.json" 2> "C:\Users\MLFLL\AppData\Local\Temp\r595\r1-start-stderr.txt"
echo exit %ERRORLEVEL% > "C:\Users\MLFLL\AppData\Local\Temp\r595\r1-exit.txt"
echo.
echo R1 finished - exit code recorded to r1-exit.txt. You may close this window.
pause
