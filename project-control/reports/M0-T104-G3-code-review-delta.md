# M0-T104 G3 code review (round 2 — delta re-review) — VERBATIM reviewer return

Orchestrator note: saved verbatim from the resumed code-reviewer agent-return channel (transport
entity-decoding only). Delta re-review at re-frozen deliverable identity `f610aab` (HEAD `94d7bd9`,
control records only). Verdict recorded by the orchestrator: PASS.

---

Full supervisor suite green: **2209 passed, 2 skipped, 0 failed** (the +5 delta over round 1's 2204 is exactly the five new adapter tests). Freeze baseline re-established. Here is my delta re-review report.

---

# G3 Delta Re-Review Report — M0-T104 (D-024 Amendment 3 unit C: native runtime adapter)

**Reviewer:** code-reviewer (independent, read-only)
**Task:** M0-T104 · **Gate:** G3 (round 2, delta) · **Re-frozen deliverable identity:** `f610aab` (HEAD `94d7bd9` adds only gate records)
**Round-1 verdict:** PASS with finding #1 (MEDIUM) as blocking correction + ADV #2–#5.
**Verdict: PASS** — finding #1 genuinely closed; no correctness regression; all advisories addressed or standing-minor.

## Reproduction (commands run at `f610aab`, read-only)
| Command | Result |
|---|---|
| `python -m pytest tools/test_agent_supervisor_native_adapter.py tools/test_agent_supervisor_capability_probe.py -q` | **77 passed in 18.79s** (72→77: five new correction-pinning tests; live rows executed against installed claude 2.1.247) |
| `python tools/modularity_check.py --check` | **failures 0; warnings 5** — the 5 are pre-existing; neither new module flagged (native_runtime.py 661 pl, runtime_backend.py 321 pl) |
| `python -m pytest tools/ -k agent_supervisor -q` | **2209 passed, 2 skipped, 560 deselected in 611s** — supervisor-freeze baseline (≥1165 / 0 failures) re-established; +5 over round-1's 2204 = exactly the new adapter tests |

## Verification of the requested items

**(1) Finding #1 (MEDIUM child-env fail-open) — genuinely CLOSED.**
- `NativeBackgroundBackend.__init__` (`runtime_backend.py:147-148`): `self._base_env = os.environ if base_env is None else base_env` — the field is now always a `Mapping`, never `None`.
- `dispatch` (`runtime_backend.py:158-159`): `env = child_environment(self._base_env)` unconditionally — the old `if self._base_env is not None else None` fail-open branch is **gone**. There is no code path that passes `env=None` (raw inherit) into a `--bg` producer spawn.
- I confirmed no *other* dispatch path reintroduces fail-open: `ControllerBackend.dispatch` delegates to the injected existing controller (out of scope, R180); the `env=None` default in `run_command` is used only by read-only probe/observe/verb calls, which do not spawn a transcript-bearing producer, so marker-stripping is correctly scoped to `dispatch` alone.
- New test `test_dispatch_default_backend_still_strips_child_env` (`:204-220`) pins it by mutation: a **default-constructed** `NativeBackgroundBackend(run)` with `CLAUDECODE`/`CLAUDE_CODE_*` set in `os.environ` (via monkeypatch) must produce `env` with no `CLAUDECODE`, no `CLAUDE_CODE_*` prefix, PATH preserved, and `env is not None`. Reverting to `env=None` reddens the `assert env is not None` and the marker assertions. The module docstring claim ("always explicit, never inherited as-is", `native_runtime.py:26-29`) is now true.

**(2) No correctness regression introduced by the corrections.**
- **Determinism:** `BackendSelection`, `build_detection_fixture`, `build_agents_fixture` still timestamp-free; masking is idempotent (verified: both committed agents-listing fixtures are content-identical to round 1 because their rows carry no full UUID/home path and their sessionIds already contain `-[MASKED]`).
- **Fail-closed selection:** `select_runtime_backend`/`background_gaps` unchanged — still degrades to controller on any non-`supported` capability incl. `unknown`/absent.
- **Fail-closed parse:** `parse_agents_json` unchanged.
- **No-duplicate reconcile core:** `needs_controller_review` returns only `unexpected_exit`; `safe_to_dispatch = needs_controller_review` is a class-level alias to the *same* property descriptor (both resolve to `unexpected_exit`), verified by `test_restart_no_duplicate_and_unexpected_exit` asserting both names equal `(gone_id,)` and `running_id not in needs_controller_review`. The new `feed_available=False` guard (`:282-287`) is a pure *fail-closed addition* (raises `reconcile_feed_unavailable`), pinned by `test_reconcile_refuses_unavailable_feed`.
- **Synonyms/rename:** `_classify_row` code branches are byte-for-byte the round-1 logic — only the docstring (`:516-527`) was rewritten to document the measured set vs the defensive synonyms (my round-1 ADV-4). No behavior change; `test_completed_classification`, `test_canary_measured_idle_and_stopped_literals`, `test_unknown_status_stays_unknown_never_guessed` all still green.
- **G5 F1 charset validation** (`DispatchSpec.__post_init__`, `:411-418`): flag-shaped `agent`/`tools` values now rejected at construction (`invalid_agent`/`invalid_tools`) as primary defense; the post-build `forbidden_flag` denylist (`:454-457`) remains as belt-and-suspenders. Verified the two layers don't conflict and legitimate values (`agent="backend-engineer"`, `tools="Bash,Edit,Read"`, `tools=""` disable-all) still construct. Pinned by `test_agent_tools_value_charsets` + updated `test_forbidden_flags_cannot_be_smuggled_via_values`.
- **G5 F3 recursive mask** (`_mask_value`/`mask_session_row`, `:617-644`): now a comprehensive pass over every string value (home-redaction + UUID truncation) rather than a 3-field allowlist; the sessionId/id 8-char collapse is guarded by `"-[MASKED]" not in value` so it's idempotent. Pinned by `test_mask_session_row_comprehensive_all_fields` (asserts no full UUID survives anywhere).
- **G4 ADV-2 verb `check=`** (`_run_verb`, `:181-211`): `check=True` surfaces a daemon rejection as typed `{verb}_failed`; `check=False` (default) preserves the raw result — so `test_stop_logs_respawn_attach_argv` (default path, ok results) is unaffected. Pinned by `test_verb_check_surfaces_daemon_failure`.

**(3) Modularity still clean after growth.** native_runtime.py 661 pl (~490 SLOC) and runtime_backend.py 321 pl are both under the 600-SLOC warn threshold; checker reports 0 failures and neither module is flagged. Both remain single-responsibility (native CLI-surface primitives; backend selection + wrappers + reconciliation). My round-1 ADV-2 (the fixture/masking serialization group inside native_runtime.py is a natural extraction candidate) still stands and grew slightly with the recursive masker — non-blocking; the file is cohesive and under threshold.

**(4)** `python -m pytest tools/test_agent_supervisor_native_adapter.py tools/test_agent_supervisor_capability_probe.py -q` → **77 passed** (matches the expected count).

## Residuals (all non-blocking)
- **ADV-2 (standing):** native_runtime.py mixes external I/O + domain logic + serialization/masking in one 661-pl module; extract the `build_*_fixture`/`mask_session_row`/`_mask_value` serialization group if it grows further. Under threshold, checker-clean.
- **ADV (minor):** the post-build `forbidden_flag` denylist (`build_background_argv:454-457`) is now effectively unreachable via normal construction (no validated field can be flag-shaped) and no test hits that specific branch directly; it is intentional defense-in-depth and harmless — keep, but it is a safety net, not a covered path.
- Round-1 ADV-3 (`--session-id` required-but-never-emitted) and ADV-4 (classifier inventory vs report §3.5) are both resolved via the added inline comment (`:129-133`) and the rewritten `_classify_row` docstring.

## Conclusion
The one blocking correction from round 1 (child-env fail-open dispatch default) is genuinely and testably closed: the strip is now unavoidable on every `--bg` dispatch, including the default construction. The additional G4/G5 hardenings (agent/tools charset validation, comprehensive recursive masking, reconcile feed-down fail-closed guard + honest rename, verb error-surface) are correct, fail-closed, and each independently pinned, with zero regression to determinism, fail-closed selection/parse, or the no-duplicate reconcile core. All 77 in-scope tests pass, the full 2209-test supervisor freeze suite passes with zero failures, and modularity is clean.

**VERDICT: PASS** — no blocking or MEDIUM residuals; two minor standing advisories (ADV-2 extraction candidate; defense-in-depth denylist now a safety net).
