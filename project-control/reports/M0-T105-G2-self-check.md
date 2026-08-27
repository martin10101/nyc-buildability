# M0-T105 G2 self-check (producer = fable-orchestrator-session)

Recorded 2026-08-27 UTC at the deliverable identity (the commit citing D-024-R155/R173 this
report lands beside). Machine: installed claude 2.1.247 (measured at use), local Python 3.11.9
(repo CI runs 3.12 — M2-T015 lesson; nothing here uses 3.12-only syntax; no PEP 695 generics).

## 1. Test evidence at the frozen identity

| Pack | Result |
|---|---|
| Event-bus pack `tools/test_agent_supervisor_event_bus.py` | **32 passed** (S1–S11 all mapped; the one live row — the S8 version drift tooth — PASSES against installed 2.1.247 and skips when claude absent) |
| ALL `tools/` test files except `test_directive_compliance.py` (single background run) | **2,680 passed, 3 skipped, 0 failed** in 598.8s — supervisor-freeze suite baseline (≥ 1,165 / 0 failures) re-established at the frozen identity |
| `python tools/validate_directive_compliance.py --check` standalone (the excluded file's subject) | **EXIT=0** (control-plane CI runs the pack itself on every push — M0-T104 precedent) |
| Readonly-guard self-runner packs (M0-T108 regression) | **ALL CHECKS PASSED** ×2; `.claude/hooks/readonly_agent_guard.py` + `agent_dispatch_guard.py` byte-untouched (`git diff` empty) |
| Mutation self-check (9 hand-applied mutants across all three new modules + the recorder) | **9/9 killed** (dedup-check-removed, uuid-mask-identity, remember-before-append, sequence-rollback-removed, step-label-swap, text-stored-verbatim, drift-sets-swapped, recorder-prints-to-stdout, replay-seen-ignored); pack GREEN after restoration (a stale byte-length-identical `.pyc` from the M7 mutant was detected and cleared — caches purged before the definitive runs) |

## 2. Static checks

- `ruff check` (0.13.0 — now the CI version locally) on all five changed Python files: **clean**.
  Whole-tree `ruff check .` reports only pre-existing findings in files this task does not touch
  (`project-control/reports/M0-T054-protected-config/doctor_proof.py`, `tools/agent_supervisor/cli.py`
  — present at baseline bc77972).
- `python tools/modularity_check.py --check`: no new warnings (largest new file 284 lines).
- No-leak needle scan over every new path (username, drive-rooted user paths, POSIX home paths,
  key/token shapes, bearer, email, full session UUIDs): **CLEAN** except the M0-T104-precedented
  benign class — the two `MLFLL` hits ARE the leak-needle assertion strings inside the test pack
  itself, and the single full UUID is the deliberately synthetic `SESSION_UUID` test constant
  (marked `# synthetic`), which the S4 test proves is MASKED in every durable record.

## 3. Packet-obligation walk (self-audit)

Durable hook records via the REUSED journal (sanitize-first/atomic/bounded/rotated) ✓ (S1/S5/S10);
dedup idempotency key stored on the record, publish-time + replay-time dedup ✓ (S2/S6); ordering
via `bus_sequence`, monotonic across restart ✓ (S1/S6); restart-safe replay = pure read, no effect
re-emission, registry state reconstructed ✓ (S6); stream-JSON subagent ingestion outside Fable
context, `parent_tool_use_id` attribution, typed `StreamEventError` on malformed lines, statusLine
sidecar stays primary (no sidecar surface in the module — asserted) ✓ (S3/R154); R042 labels on
every usage number, absent → unknown never zero ✓ (S3); R043 final-request caveat on result-event
usage (`final_request_*`, never whole-run) ✓ (S3); redaction: paths `[HOME]`-masked, prompts
withheld, secrets redacted, raw session/task UUIDs digest-masked by the bus ✓ (S4); unknown event
names recorded honestly `known: false` ✓ (S7); unknown stream types `known_type: false` ✓ (S3);
2.1.247 catalog fixture at official-docs confidence (same method as the 2.1.220 capture), recorded
drift = NONE, deterministic fixture↔code reconciliation + live version tooth ✓ (S8); recorder =
thin fail-closed stdout-silent bounded command hook, stdin payload, no HTTP, no tokens, no
settings.json registration (separate reviewed change), never blocks/injects/messages ✓ (S9/S11);
`readonly_agent_guard.py` untouched (M0-T108/T109 scope) ✓ (S11 tooth); no transcript polling
added anywhere ✓ (module has no transcript reader); hooks-stay-fast: recorder skips replay-warm
(`warm_rotated=False`) and fsync (statusline-precedent), bounded stdin ✓.

## 4. Known limitations (disclosed for review)

1. `test_directive_compliance.py` not run locally (cannot complete in a local window at the
   28-directive registry size — M0-T104 precedent); its subject ran standalone (validator EXIT=0)
   and control-plane CI runs the pack on every push.
2. Per-event payload fixtures are documentation-confidence except UserPromptSubmit
   (measured-live, masked copy of the R162 capture); each payload carries its own honest
   confidence label. The C1 owner-gated canary (R192/R197) upgrades them to measured-live.
3. The stream fixture is session-evidence confidence (shapes mirror `claude_runner` measured
   handling); a `--forward-subagent-text`-specific event type, if distinct on 2.1.247, would
   ingest honestly as `known_type: false` until C1 captures it live.
4. The recorder store default (`.claude/telemetry/hook_events.jsonl`) follows the accepted
   M0-T099/M0-T100 statusline runtime-state precedent (gitignored). `NYCB_EVENT_STORE_PATH` is a
   test-only override, exercised by the S9 subprocess tests.
5. Hook REGISTRATION is deliberately absent: `.claude/settings.json` is forbidden_paths for this
   task; wiring is a separate reviewed change (packet text; recorder docstring).
