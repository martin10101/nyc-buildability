# M0-T048 gate evidence — the two skipped supervisor-suite tests (D-010 R155/R156)

Orchestrator-captured evidence per owner instruction 2026-08-08 (D-010 source-016). Command run at
the frozen review identity (control branch `control/M0-T048-c2-close`, review identity
`fee612ae724085576aad23c0fd1d387fa89e800d`, capture commit `9119934` tree; code paths identical to
`fee612a`), on the owner's Windows 11 PC, non-elevated session:

```
python -m pytest tools/test_agent_supervisor_*.py -q -rs
...
SKIPPED [1] tools\test_agent_supervisor_policy.py:449: cannot create a symlink here:
  [WinError 1314] A required privilege is not held by the client:
  'C:\Users\MLFLL\AppData\Local\Temp\tmpnoog6yge' ->
  'C:\Users\MLFLL\AppData\Local\Temp\tmphp1yj0tk\tools\agent_supervisor\escape'
SKIPPED [1] tools\test_agent_supervisor_process.py:448: POSIX-only guard
1380 passed, 2 skipped in 127.45s (0:02:07)
```

## R155 — the two skipped tests, named, with pytest-reported reasons

1. **`PolicyEscapeTests::test_symlink_escape_is_denied`** (`tools/test_agent_supervisor_policy.py:451`)
   — reason: `cannot create a symlink here: [WinError 1314] A required privilege is not held by the
   client`. The test first ATTEMPTS `os.symlink(...)` and self-skips only when the OS refuses.
   Creating a true NTFS symlink requires `SeCreateSymbolicLinkPrivilege` (elevation or Windows
   Developer Mode); this non-elevated session on the owner's PC does not hold it.

2. **`test_job_objects_report_unavailable_off_windows`** (`tools/test_agent_supervisor_process.py:449`)
   — reason: `POSIX-only guard` (`@unittest.skipIf(os.name == "nt", ...)`). The test asserts the
   POSIX-side fallback: `job_objects_available()` is `False` and `WindowsJobObject()` raises
   `ProcessError` on non-Windows platforms. By definition it can never run on Windows.

## R156 — adjudication: stale-by-accident vs legitimately environment-conditional

**Both skips are legitimately environment-conditional. Neither is stale or accidental. No
follow-up unskip task is contracted** (the owner's criterion — "a test that could run here but is
being skipped by accident" — is met by neither: (1) genuinely cannot create a symlink in this
non-elevated session; (2) genuinely cannot run on Windows at all).

Per-test reasoning and compensating coverage:

1. `test_symlink_escape_is_denied` — the skip is a live runtime-capability check (it fires only
   after an actual failed `os.symlink` attempt), not a stale marker. **Compensating automated
   coverage exists and runs here:** `PolicyEscapeTests::test_junction_escape_is_denied`
   (`test_agent_supervisor_policy.py:468`) exercises the SAME escape-denial verdict — tier
   `HARD_DENY`, reason code `symlink_or_junction_escape` — via a directory **junction**, which
   needs no special privilege on Windows, and it is among the 1380 passing tests at this identity
   (as are the junction/hardlink escape probes in `test_agent_supervisor_adversarial.py`).

2. `test_job_objects_report_unavailable_off_windows` — platform guard by design; its Windows
   counterparts (`test_job_object_kills_assigned_process`, skipUnless-nt) run and pass here.
   Leaving it skipped on Windows is the intended behavior.

## Advisory notes (transparency, no action required)

- The `supervisor-bridge` CI job (windows-latest, deliberate per its in-file rationale of
  2026-08-03) also reports **2 skipped** (latest main run 31239200235, job 93057151495:
  `1363 passed, 2 skipped`), but the CI invocation runs plain `pytest` without `-rs`, so the CI log
  does not name them. The POSIX-only guard necessarily skips there too (Windows runner); if the
  symlink variant also lacks the privilege there, the symlink-specific variant currently executes
  in no automated environment — the junction variant remains the automated coverage of the same
  denial path in every environment. Optional owner choices, neither contracted here: add `-rs` to
  the CI pytest invocation for skip transparency, and/or enable Developer Mode on a runner/PC to
  execute the symlink variant.
- Full skip-capable enumeration of the suite (grep `skipIf|skipTest|skipUnless`): all remaining
  conditionals are Windows-affirmative (`skipUnless nt`) or runtime-capability probes
  (`mklink /J`, `mklink /H`, parent-pid) that pass/run in this environment — consistent with
  exactly the two skips above.
