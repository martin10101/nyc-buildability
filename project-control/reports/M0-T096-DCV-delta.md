# DCV DELTA Re-Attestation — M0-T096 (D-024 unit I)

> Verbatim reviewer return (directive-compliance-verifier agent, SendMessage delta
> re-attestation over `git diff 1a935fb..635fac5`). Recorded by the orchestrator.

## Identity

- New frozen HEAD: **`6dede159785764ad149ec33dcf1cef76a18bd062`** (control tip); corrections commit **`635fac5a867cb28b3ef6cd79109e371e59921ae2`** is its ancestor and the resubmit `--sha`; origin matches; deliverable code is byte-frozen from 635fac5 to HEAD (`git diff 635fac5 HEAD -- tools/…` empty).
- Delta over my verified `1a935fb`: `git diff 1a935fb 635fac5` = 4 code/test files (+50/−15) inside `allowed_paths` + 5 control-plane reports; **no forbidden path touched**.

## What I reproduced at the delta

- Applicable set re-resolved: **ok=True, 83 ids, max R230** — unchanged; evidence-map key set still set-equal (no new gap). (b) confirmed.
- `python -m pytest tools/test_agent_supervisor_golden_run.py -q` → **40 passed** (18.07s) at the new identity.
- Targeted: expanded `test_capture_is_idempotent_and_carries_the_five_fields`, `test_no_code_path_writes_verified_live_true`, `test_register_rows_are_sanitized_at_the_boundary`, `test_the_harness_marker_wins_over_a_live_session_scan`, `test_the_start_epilogue_scans…` → **5 passed**.
- `grep verified_live` in live_observation.py: still **constant `False`** (line 295); the only "true" token is the docstring at line 440; no `verified_live=True` write path.
- `tools/modularity_check.py --check` → **failures 0** (same 8 pre-existing warnings).

## Delta impact on the flagged rows (all four changes are hardening, none regressive)

| Change (source) | Rows touched | Effect |
|---|---|---|
| golden_run.py: fake-provider git env adds `GIT_CONFIG_GLOBAL/SYSTEM=os.devnull` (G3 MINOR-1) | **R182** | STRENGTHENED — fake providers now fully isolated from user git config; disposable/deterministic property hardened. Not weakened. |
| live_observation.py: 3 scalar fields (`installed_version_shape`, `applicable_shape`, `source_record_key`) now pass `sanitize_structure` (G5 INFO-2) | **R226, R223, R224** | STRENGTHENED — the five R226 capture fields remain present and now more are sanitized at the boundary; `verified_live` unchanged (False); closed vocabulary unchanged. |
| test pack: capture test seeds all 6 discovery branches, asserts rows_written==6 and full `set(EVENT_TYPES)` coverage (G4 MINOR-1) | **R226, R223** | STRENGTHENED — every discovery branch / closed-vocab event type behaviorally covered; a renamed source key can no longer silently un-capture an event kind. |
| cli.py: watcher scan in nested try; `lock.release()`+`journal.close()` moved into `finally` (G5 INFO-1) | **R226, R030** | STRENGTHENED — lock/journal cleanup now unconditional even under BaseException; "bounded watcher never breaks start" property reinforced. |
| R045 (no worker-facing text) | — | UNCHANGED — watcher still emits no worker message; structural passivity test green. |
| R091 (one consolidated round) | — | REAFFIRMED — exactly ONE correction commit `635fac5` applying all four sibling findings (G3/G4/G5), one new frozen identity, single resubmit; this is precisely the R091 consolidate→freeze→re-review shape. |

(a) No requirement in my 83-row SATISFIED matrix is invalidated or weakened; the watcher-touching rows R223/R224/R226 are strengthened. (b) No new applicable-requirement gap (set still 83, no forbidden path, scope clean). (c) All 83 rows re-affirm SATISFIED at 635fac5.

Citation updates (non-substantive): R226/R223 now additionally cite the expanded `test_capture_is_idempotent_and_carries_the_five_fields` (6 sources / full closed vocabulary); R226/R030 additionally cite the cli.py nested-`finally` cleanup. No state change on any row.

DELTA VERDICT: PASS
