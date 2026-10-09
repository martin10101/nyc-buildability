# G3 Code Review — M0-T096 (D-024 unit I)

> Verbatim reviewer return (code-reviewer agent, read-only, dispatched at frozen HEAD
> `1a935fb`; transport entity-decoding only — `&gt;`/`&lt;` from the return channel rendered
> as `>`/`<`). Recorded by the orchestrator.

## Identity verified

- Repository: `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24`, branch `control/D-024-fable-codex-loop`.
- `git rev-parse HEAD` = **`1a935fb2f6f5859da6418fd6750733be3e7589c7`** — matches the assigned frozen HEAD.
- Deliverable code commit **`5ff7f08`** is an ancestor of HEAD (`git merge-base --is-ancestor 5ff7f08 HEAD` = true). The four commits between `5ff7f08` and HEAD are control-plane only (G2 report, submit, progress, Amendment-8 capture); `git diff --stat 5ff7f08..HEAD -- tools/agent_supervisor tools/test_agent_supervisor_golden_run.py` is **empty**, so the reviewed code is byte-identical at HEAD to the frozen deliverable identity.
- Working tree is clean except one untracked file `project-control/reports/M0-T096.json` (outside the reviewed diff; see INFO-6).
- Reviewed delta: `git diff 2ae057b..5ff7f08` — `cli.py (+46/−8)`, new `golden_run.py (407)`, new `live_observation.py (451)`, new `test_agent_supervisor_golden_run.py (1017)`.

## What I executed

- `python -m pytest tools/test_agent_supervisor_golden_run.py -q` → **40 passed in 15.89s** (Python 3.11.9; this file has no PEP 695 generics, so it collects on 3.11).
- `python tools/modularity_check.py --check` → **selected 323 files; failures 0; warnings 8** (cli.py appears as a `symbol_ceiling` *warning*, not a failure; no new failure introduced).
- `python -c "from tools.agent_supervisor import cli, golden_run, live_observation"` → imports cleanly (confirms the pruned cli.py imports caused no breakage).
- Read the full diff plus the collaborating production modules `loop.py` (guardrail seam at 1580–1626), `refusal_bridge.py`, `guardrail_refusal.py`, and traced the epilogue placement in `cmd_start`.

## Verified correctness properties (independently re-derived)

- **Fail-closed for packets without authorization fields.** cli.py:2771–2787 builds `AuthorizedTaskRecord` from `packet.get("authorization")/("acceptance_criteria" or "stop_conditions")`. `AuthorizedTaskRecord.proven` (guardrail_refusal.py:129–133) requires task_id **and** authorization **and** non-empty acceptance_criteria; an empty packet yields `proven=False` → `classify_guardrail_refusal` returns `AMBIGUOUS_FAIL_CLOSED / CONDITION_AUTHORIZATION_UNPROVEN` (guardrail_refusal.py:400–408) → `GuardrailBridgeIntegration.evaluate` returns `triggered=False` with **no journal write** (refusal_bridge.py:926–929). The cli.py comment is accurate.
- **Existing behavior preserved.** The loop only diverges when `refusal_decision.triggered` (loop.py:1607); otherwise it falls through to the identical `no_valid_checkpoint` → PAUSED_RECOVERY stop. `evaluate` has no side effect on the non-recognized path, so wiring the bridge does not change the outcome for unauthorized/ordinary failures. The recognized-refusal case (record-intent + reason_code) is the intended, previously-inert Phase-E behavior now activated; still SHADOW-ONLY with no actuation channel.
- **No harness leak into production.** `golden_run` is imported **only** by the test pack (grep confirms zero production importers); its docstring's "production code never imports it" holds. `live_observation` is imported by cli.py — correct, it is the production watcher.
- **Safety of the watcher.** `verified_live` is a hardcoded constant `False` on every row (live_observation.py:289) and no code path sets it True (test + mutation confirm). Actuation is independently double-gated (`assert_actuation_permitted` requires a measured-live corpus shape AND R595; refusal_bridge.py:226–245); `REFUSAL_SHAPE_VERIFIED` is False on this build. So even a mislabeled `live_candidate` row unlocks nothing.
- **No shell=True; argv arrays only.** golden_run `_git` (40–42), the fake providers' inline `git`, and the wrapper launchers all use argv; `live_observation.py` uses no subprocess at all (structurally asserted by a test).
- **Redaction before persistence.** `build_observation_record` runs `sanitize_structure` over classification/response/outcome before storing (live_observation.py:268–284); `test_register_rows_are_sanitized_at_the_boundary` proves secrets never reach the register and `redaction_count>=1`.
- **CAS idempotency / no race.** `record_observations` writes each row via `compare_and_swap_state(key, None, record)` (live_observation.py:336); re-scans are counted no-ops. The epilogue runs while the SingleInstanceLock is still held (cli.py finally: epilogue → `lock.release()` → `journal.close()`), so no concurrent writer on the same journal.
- **Epilogue safety.** `journal`, `audit`, and `lock` are bound at cli.py:2860–2861 before the `try:` at 2863, so the finally-block epilogue introduces no new UnboundLocalError risk; the broad `except` is bounded and never breaks `start`.
- **Marker depth bound.** `_payload_carries_marker` caps recursion at depth 4 (live_observation.py:234–244); the injected refusal record carries `INJECTED-GOLDEN-RUN` in flat fields (authorization/evidence_excerpt at depth 1), well within the bound. Payloads are JSON-derived (no cycles).
- **Pruned cli.py imports genuinely unused.** The three remaining `"UNVERIFIED"` hits in cli.py are string literals, not the removed `preflight.UNVERIFIED` symbol; the other removed symbols have zero references; cli imports cleanly.
- **Modularity fit.** New logic went into two focused new modules (407 / 451 lines, both under the 600 warn line); only the essential bridge construction + epilogue (which can only live in `_run_loop` / `cmd_start`) was added to cli.py. `modularity_check --check` = 0 failures.
- **Evidence report honesty.** `project-control/reports/M0-T096-golden-run-evidence.md` documents the reuse boundary, the discovered integration defect, honest owner-gated boundaries, and a 12/12 mutation matrix that specifically kills the fail-open mutants I was probing (evidence-class default flip, marker-scan removal, verified_live flip, CAS→overwrite, provenance-check removal, bridge wiring nulled, epilogue scan dropped).

## Findings by severity

### BLOCKING
None.

### MAJOR
None.

### MINOR
- **MINOR-1 — Fake providers' inline git does not isolate from host global/system git config.** `tools/agent_supervisor/golden_run.py:167–175` (the `git()` helper inside `FAKE_CLAUDE_GOLDEN`) sets only author/committer identity, whereas the harness's own `_git` (lines 29–43) additionally sets `GIT_CONFIG_GLOBAL`/`GIT_CONFIG_SYSTEM=os.devnull`. Failure scenario: on a host whose *global* git config sets `commit.gpgsign=true` (with no signing key) or `core.hooksPath`, the fake producer's `git commit` (`check=True`) can fail/hang, crashing the fake worker and producing a golden-run failure unrelated to the code under test — while the harness's own base commit (which bypasses global config) succeeds, an inconsistency. Empirically the pack is 40/40 on this Windows host, so this is latent, not active. Recommend the inline `git` mirror `_GIT_ENV`.

### INFO
- **INFO-1 — Epilogue hardcodes `session_provenance="live"`.** cli.py (~3060) always scans as a live session; because the golden-run harness drives the real `cli.main`, harness rows depend entirely on the `INJECTED-GOLDEN-RUN` text marker to be reclassified injected. The failure direction is safe (verified_live constant False; actuation/graduation independently gated) and the marker discipline is enforced by mutation tests. Documented design; no action needed.
- **INFO-2 — Broad `except` records only the exception type name.** cli.py (~3062) audits `type(watch_error).__name__` with no message/traceback. Deliberate (bounded watcher + avoid leaking payload text), but a real watcher bug surfaces only as a bare type. Acceptable.
- **INFO-3 — No per-source isolation in `record_observations`.** live_observation.py:316–342: one malformed source that makes `build_observation_record`/`sanitize_structure`/`digest_of` raise aborts the whole session's scan (caught/audited by the epilogue). Self-heals via CAS re-scan each session; low impact.
- **INFO-4 — Test harness lives in the production package.** `golden_run.py` (materializes fake executables, shells out to git) sits under `tools/agent_supervisor/`. It is imported only by tests and documents that production never imports it; mild placement smell, not a policy violation.
- **INFO-5 — Prove-first registers check test *existence*, not *pass status*.** test file 831–1013 verifies each cited cross-file test name exists (source regex); it does not run them. Inherent to a traceability register; the producer's full-suite run (2,584 passed) is the pass evidence, and the three register meta-tests are green.
- **INFO-6 — Untracked report artifact.** `project-control/reports/M0-T096.json` is present in the working tree but outside the reviewed diff/allowed_paths for code; flagging so the orchestrator confirms it is not silently swept into the deliverable.

## Conclusion

The two new modules are cohesive, well-documented, and safe-by-construction; the cli.py wiring is a minimal, correctly-placed fix for a genuine discovered integration defect (the H1 refusal seam was never constructed in `start`), preserves prior behavior for unauthorized/ordinary packets (fail-closed AUTHORIZATION_UNPROVEN), and the passive-watcher epilogue is bounded, idempotent, redacted-before-persist, and cannot unlock any capability. Tests genuinely exercise the real `cli.main` surface with real git effects, and the 12/12 mutation matrix kills the fail-open shapes. All findings are MINOR/INFO; none require correction before acceptance.

VERDICT: PASS
