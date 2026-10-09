# M0-T132 — G0 definition-of-ready (administrative)

**Task:** M0-T132 — D-024 Amendment 34 combined Claude Code 2.1.252 admission + single R247
recertification (M0-T118 precedent).
**Reviewer:** orchestrator (administrative G0). **Result:** PASS (ready to claim).
**Base identity:** HEAD `1d4a6212`, branch `control/D-024-fable-codex-loop`, tree clean, local == origin.

## Bootstrap Gate 0 (D-024-R125..R128)
- Primary cwd **is** the worktree root `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24` (added dirs do not count). ✓
- `/mcp` (via `claude mcp list`) reports **no servers configured**. ✓
- Git: root/branch/HEAD verified; `git status` clean; HEAD == `@{u}`; `git fetch --dry-run` no updates. ✓

## R438 fresh-process CLI verification (fail-closed settle gate — PASS)
- `DISABLE_AUTOUPDATER` = `1` (inherited by this process). ✓
- `DISABLE_UPDATES` unset everywhere (R280 honored). ✓
- `claude --version` = `2.1.252 (Claude Code)`. ✓
- On-disk `~/.local/bin/claude.exe` identity = `e713c5a6c8bc71af...` (sha256_head+size), 217,406,624 B,
  **byte-identical** to `versions/2.1.252`; renamed old `claude.exe.old.1788206208678` = `d6f6c29a...`
  (the obsolete 2.1.251 pin). ✓
- Nothing newer installed or staged: versions dir holds 2.1.248 / 2.1.251 / 2.1.252 only; downloads empty. ✓
- **Settled admission target confirmed unchanged:** 2.1.252 (`e713c5a6`) — the R433 re-verification passes.

## Readiness checklist (per `/start-controlled-task`)
- **Requirement identifiers named:** D-024 Amendment 34 rows `D-024-R437..R445` (+ standing R233/R247/R280/
  R281/R286/R287/R295/R431); precedents `M0-T118` (recapture), `M0-T119`/`M0-T130` (R247 recert). ✓
- **Exact directive references:** `D-024:ALL` stamped in-regime (`directive_refs`). ✓
- **Exact evidence/source files named (read-only inputs):** listed in packet `inputs` — Amendment 34/32
  sources, `process.py` identity instrument, the outgoing 2_1_251 fixture pack + shell-routing evidence,
  M0-T118 recapture and M0-T130 recert precedents. ✓
- **Non-overlapping write scope:** allowed = `event_drift.py`, four new `2_1_252`/`m0t132` fixtures, three
  fixture-consuming test files, two own reports; forbidden = settings/policy, apps/packages/services/supabase,
  D-001 dir, tasks dir, control CLIs, journal files. No concurrent task shares these paths (worktree list
  reconciled). ✓
- **Acceptance scenarios:** AS-1..AS-8 (identity re-verification fail-closed; capability/event/native/routing
  live recapture with red-green teeth; post-accept repin + ONE combined recert; preservation invariants;
  present-only restart validation). ✓
- **Required gates + independent reviewers:** G0 (admin); G2 (producer self-check, orchestrator-captured);
  independent G3 `code-reviewer`; G4 `qa-engineer`; DCV `directive-compliance-verifier` — all distinct from
  producer `orchestrator-admission-runner`. ✓
- **Modularity boundary:** the change re-points one pointer in `event_drift.py` and adds append-only fixtures +
  test coverage — no new oversized file, no unrelated responsibility folded in; `modularity_check` teeth run in G2. ✓
- **Owner authorization present:** Amendment 34 R439 is the separate owner authorization contemplated by R436;
  R429 admission-lane deferral ends by R439. Every other owner gate (PR #241, supervisor activation, credentials,
  legal) remains closed and is preserved by R443/R444. ✓

## Control-model check
`new-task` accepted M0-T132 as in-regime governance with `D-024:ALL`; no dependency rows (the M0-T131 tree it
recertifies is already accepted at `00220b8c`). No stop-condition triggered. Ready to claim.
