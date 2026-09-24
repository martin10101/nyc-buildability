# M0-T159 — G4 identity-carry check (qa-engineer "qa-m0b", read-only)

> Transmission history: pinned at fa7e5fae, delivered as one SendMessage ending with END-OF-REPORT; no
> truncation. Saved verbatim by the orchestrator (transport wrapper tags removed only). The check confirms
> the original G4 (M0-T159-G4.md, PASS at a57bb8de) carries to the re-frozen identity: tools/ unchanged since
> the G4 material, the four re-pointed packs re-run at HEAD (150 passed, 0 skipped), and the correction's
> test claims accurate. This record re-stamps G4 at the re-frozen content identity.

---

M0-T159 G4 identity-carry check (qa-engineer, read-only). HEAD PINNED at start: fa7e5fae8c9d (matches expected). Tested tree byte-stable throughout; I ran no write/git-write/supervisor/project_control verb.

CHECK 1 — tools/ unchanged since the G4 material: PASS.
`git diff --stat cfc3d22c HEAD -- tools` is EMPTY: no test, fixture, or controller file changed. `git show cdd62c5c --stat` = exactly 2 files, both reports-only (M0-T159-producer-report.md, M0-T159-recertification.md); cherry-pick of 651271b6, parent ab2a6730, as stated. Full-repo diff cfc3d22c→HEAD touches only unrelated M5 tasks (apps/web, services/api) + ledger files — nothing under tools/. So the tested surface is byte-identical to what G4 PASSed at a3f24ff3/cfc3d22c; the verdict's material basis is unchanged.

CHECK 2 — four re-pointed packs at HEAD: PASS.
`python -m pytest tools/test_agent_supervisor_{capability_probe,event_bus,native_adapter,routing_probe}.py` → 150 passed, 0 skipped in 43.4s. Matches the reviewer's recorded C0 (150 passed, 0 skipped); the claude-gated live teeth ran here (no CI skip-masking).

CHECK 3 — correction's new test claims vs advisories A1–A7: accurate, no overstatement.
- F7 (recert §1/§2): rewords "fixtures OUTSIDE the manifest root" → "INSIDE tools/agent_supervisor/fixtures/ but matched by NONE of COVERED_PATTERNS." Independently verified against manifest.py:50-59 — the 8 patterns the report lists are exact and fixtures/*.json is genuinely uncovered. Matches A7 precisely; more precise than the original wording, not an overstatement.
- F5/F6 (both reports): newly discloses probe_meta.claude_binaries 3→1 and routing assistant_events 2→1 / 3→2 as PATH-shim / stream-granularity only. This ADDS the exact disclosure A6 flagged as missing; accurate.
- Condition-6 canary (recert §5.12): states plainly that --restricted / dontAsk / --json-schema were NOT exercised live at 2.1.281, that a --help probe cannot see a flag removal (only a live run can), and mounts a supervised one-cycle canary as mitigation. Consistent with A1/A3/A5 — it understates, not overstates.
- "Discovery-backlog candidates" list records the version-hardcoded routing tooth + fixtures-not-manifest-covered + start-gate-trusts-fixtures gaps as OPEN, consistent with A1/A2/A7. Nothing claims the teeth prove more than G4 found.

FINDINGS. BLOCKING: none. ADVISORY: A1–A7 stand unchanged (all pre-existing; the correction discloses but does not close them — A5's "name the three teeth as PASSED" nicety is still not added, but the 0-skip pack run above independently covers its risk at this head).

The G4 test-adequacy verdict carries to the new content identity.

M0-T159 G4 VERDICT (identity carry): PASS

END-OF-REPORT
