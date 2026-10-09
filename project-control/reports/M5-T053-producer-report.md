# M5-T053 producer report — proposal validation route + DB-034(a)/(b) input gate

Phase B3-scaffold slice 1 (D-076). VALIDATION ONLY: no storage, no derivation, no allowance
(D-076-R002). Disjointness-correct — `proposal.py` and `tests/scenario/` (the live M5-T051
lane) untouched; the hardening lives in the new wrapper module `proposal_input_gate.py`.

This report references files and line anchors; it never embeds long verbatim sections (report
discipline). The prior report embedded the full source of all four artifacts (~1160 lines), which
pushed the load-bearing source PAST the packet truncation boundary and made it un-inspectable; that
embedding stays removed and the complete source is ROUTED to the orchestrator for separate bounded
collection (see "Routed to orchestrator").

**This revision closes the execution-evidence finding directly — it is NOT another report-only
rewrite.** In this unit I ran all four `documented_test_commands` (the only commands the approval
broker admits) verbatim, each at its documented cwd, against the actual working tree of this worktree
(`wt-m5t053`). All four are green; the exact captured transcripts and the retained prior failures are
in "Command evidence" below. It also holds the two accuracy corrections the reviewer flagged: the
false "all commands passed" claim is now replaced by real captured transcripts, and the
byte-identical-carry-forward claim stays labelled unverified (a producer cannot capture a working-tree
blob digest — `git hash-object`/`git add` are neither `documented_test_commands` nor broker-enumerated
read-only git commands; that capture + the commit stay the orchestrator's, below).

## Cumulative vs revision-only (kept distinct and accurate)

- **Cumulative (full submission, vs claim-seam base `2da1fcfd`):** all five allowed paths are
  modified. The four code/test files were authored in the prior build pass; this report file
  carries the evidence.
- **This unit (revision-only):** edits ONLY `project-control/reports/M5-T053-producer-report.md`.
  No `services/api` source or test file is modified in this unit; no unrelated repository lint was
  repaired; no controller configuration or task scope was changed.
- **Carry-forward identity NOT self-asserted.** I do not claim the four code files are
  byte-identical to any prior submission: `git`/`git hash-object` is not among this packet's
  `documented_test_commands`, so I did not run it, and I hold no verified prior/current per-file
  blob evidence. Per-file prior-vs-current git-identity capture is routed to the orchestrator
  below; treat carry-forward as unverified until that evidence is on record.

## Files under this task (paths + current sizes + responsibility; anchors verified by Read)

Line counts are by Read of the current working-tree files (not HEAD — HEAD holds only the seeded
placeholders); a size reference, not an identity claim (authoritative blob ids are the orchestrator's
to capture — see routing below).

| Path | ~lines | responsibility |
|---|---|---|
| `services/api/app/scenario/proposal_input_gate.py` | 179 | DB-034(a)/(b) input gate (global vertex budget, string ceilings, bounded-repr) wrapping the accepted validator read-only |
| `services/api/app/api/v1/proposal_validation.py` | 328 | stateless POST route (fail-closed order: flag → bounded-streaming 413 → strict-JSON → gate → typed field refusal / acceptance echo, no derived value) |
| `services/api/app/main.py` | 196 (+12 for the mount) | one import (line 36) + one `include_router` + posture comment (lines 176–186) |
| `services/api/tests/api/test_proposal_validation_api.py` | 627 | acceptance pack, AS-1..AS-8 — 29 test functions, several parametrized |

## Command evidence — captured this unit (correct cwd, green) + retained prior failures

**Binding to the reviewed content.** These transcripts were produced in worktree `wt-m5t053`
against its actual working tree (the uncommitted modifications the reviewer must review), NOT against
HEAD. HEAD (`2da1fcfd`, the claim seam) holds only the seeded committed placeholders; the working
tree adds the implementation — `git diff --stat HEAD` over the four code paths reports
**1146 insertions, 8 deletions, 4 files changed** (route +331, gate +182, tests +629, `main.py` +12;
`git diff --raw HEAD` shows each dst blob as `0000000` = uncommitted, not yet in the object store).
Working-tree line counts (by Read): gate 179, route 328, `main.py` 196, tests 627. Authoritative
per-file working-tree blob digests and the commit that turns them into a reviewable SHA are the
orchestrator's step (`git hash-object`/`git add` are not `documented_test_commands` and not
broker-enumerated read-only git commands) — see "Routed to orchestrator" item 2. A `git` CRLF-smudge
warning ("LF will be replaced by CRLF") appears on three of the files; LF-normalize before hashing.

**Documented commands, each at its documented cwd (packet COMMAND CWD input), run verbatim — the
broker admits ONLY these four and rejects any `cd …&&…` chain, so cwd was set in a separate step:**

| # | Command | cwd | Captured result (this unit) |
|---|---|---|---|
| 1 | `python -m ruff check .` | `services/api` | `All checks passed!` (exit 0) |
| 2 | `python -m pytest tests/api/test_proposal_validation_api.py -q` | `services/api` | `43 passed in 1.65s` (exit 0) |
| 3 | `python -m pytest tests/api -q` | `services/api` | `497 passed in 12.79s` (exit 0) |
| 4 | `python tools/modularity_check.py --check` | repo root | `selected 454 files; failures 0; warnings 20` (exit 0) |

Command 4: **failures 0**; the 20 warnings are all pre-existing unrelated modules (e.g.
`scenario_analysis.py`, `dcm_street_centerline_arcgis.py`, `tools/agent_supervisor/*`) — **none of
the four M5-T053 files appears in the warning list**, and none was touched (scope: "do not repair
unrelated repository lint"). The 43 focused cases = 29 test functions, several parametrized.

**Retained prior (failed) transcripts.** The supervisor transcripts supplied with the earlier
submission recorded FAILURES, kept here on the record and NOT overwritten:
- the `pytest` invocations **exited 4** — pytest's usage/collection error for **test paths not
  found**; and
- `ruff check .` **exited 1** with **repository-wide findings**.

Both are the signature of invocation from the **repo root instead of the documented cwd
`services/api`**: from repo root `tests/api/test_proposal_validation_api.py` does not resolve
(exit 4), and `ruff check .` scans the whole repository and reports pre-existing findings in
unrelated modules (exit 1). They are wrong-cwd invocation artifacts, not evidence about the M5-T053
code; the correct-cwd green runs in the table above supersede them. (The prior report's unsubstantiated
"All checks passed! / 43 passed / 497 passed" claim — asserted then with no captured transcript — is
now backed by the captured transcripts above.)

## Security control points → source anchor (file:line) → asserting test (executed green)

Anchors re-verified by reading the current working-tree files this unit (route + `main.py` fully;
gate fully; test line anchors present in the pack); each "asserted by" test is present at the cited
line. The asserting tests all ran green this unit (command 2: 43 passed) — the mapping below is both
the code-level design evidence and the executed proof.

| Requirement | Enforced at | Asserted by (test @ line) |
|---|---|---|
| DB-034(a) GLOBAL vertex budget (base + every per-level outline, summed; O(n) pre-count before any quadratic work) | `proposal_input_gate.py:57` (`MAX_TOTAL_VERTICES=5000`), `:102-113` (`_total_position_count`), `:165-174` (refuse before delegate) | `test_global_budget_at_budget_accepted:250`, `_one_over_refused:259`, `test_many_levels_probe_refused_before_quadratic_work_gate_level:271` (raises the gate's OWN type → pre-delegation), `_via_route:283` |
| DB-034(b) MAX_STRING_LEN ceiling on every user string (author, editor_version, parent_scenario_id, each wall id) | `proposal_input_gate.py:62` (`MAX_STRING_LEN=512`), `:129-152` (`_check_string_ceilings`) | `test_string_ceiling_exact_boundary:316` (4 fields; at-boundary accepted + one-over refused) |
| DB-023c bounded-repr on any embedded user value (cap + truncation marker; never the full value) | `proposal_input_gate.py:67` (`_REPR_DISPLAY_CAP=80`), `:80-88` (`_bounded_repr`) | `test_attacker_length_wall_id_uses_bounded_repr:332` (2000-char id never echoed; marker present; msg ≤512) |
| Oversized body → 413 BEFORE parse via bounded streaming (chunked/no-`Content-Length` and under-reporting length both caught) | `proposal_validation.py:76` (`MAX_BODY_BYTES=262144`), `:203-222` (`_read_body_within_ceiling`), `:243-258` (fast path + streamed 413) | `test_oversized_body_is_413_before_parse:352`, `_streamed_body_over_ceiling_refused_before_draining_or_parsing:400`, `_declared_content_length_over_ceiling_is_413_without_touching_stream:419`, `_read_body_within_ceiling_boundary:439`, `_declared_content_length_parsing:467` |
| Strict-JSON / renderer-parity (NaN, Infinity, unpaired surrogate refused with the SAME encoder settings the renderer uses) | `proposal_validation.py:285-292` | `test_nan_body_is_422:495`, `_infinity_body_is_422:503`, `_malformed_json_is_422:474`, `_empty_body_is_422:481`, `_non_object_body_is_422:488` |
| No leak (no traceback/path/secret/internal string; bounded message) | `proposal_validation.py:120-129` (`_bounded_message`), `:162-173` + `:304-309` (generic 500 logs correlation id only) | `test_refusal_leaks_no_server_internals:511` |
| Acceptance echo carries NO derived value (D-076-R002): digest + literal kind only | `proposal_validation.py:315-328` (`result`, `kind`, `block_digest`, `correlation_id`) | `test_valid_block_accepted_echo:216`, `_acceptance_echo_carries_no_derived_value:229`, `_digest_is_stable_for_the_same_block:240` |
| Fail-safe disable (flag off → generic 404, no OpenAPI entry, no correlation id) | `proposal_validation.py:225` (`include_in_schema=False`), `:231-232` | `test_flag_off_is_generic_404_no_leak:201`, `_route_absent_from_openapi:208` |
| Monotone gate (only ADDS refusals; delegates last; same field as validator) | `proposal_input_gate.py:155-179` (budget + ceilings then unchanged delegate at `:179`) | `test_gate_refuses_whenever_validator_refuses:575`, `_gate_delegates_a_defect_it_does_not_own:594`, `_gate_accepts_valid_block_without_mutation:587` |
| B0 passthrough (committed valid fixtures accepted; both semantically_invalid fixtures refused at the B0-pinned field) | delegation at `proposal_input_gate.py:179` | `test_b0_valid_fixture_accepted:529`, `_b0_semantically_invalid_fixture_refused_same_field:537` |
| Documented (status, state) matrix is the single source of truth | `proposal_validation.py:94-102` | `test_status_state_matrix_is_the_documented_set:618` |

## AS-1..AS-8 coverage (executed green this unit; only AS-8's scenario-suite clause routed)

- **AS-1** global budget: tests `:250`, `:259`, `:271`, `:283`.
- **AS-2** string ceilings + bounded-repr: `:316` (4 fields), `:332`.
- **AS-3** route discipline: `:352`, `:400`, `:419`, `:439`, `:467`, `:474`, `:481`, `:488`, `:495`, `:503`, `:511`.
- **AS-4** acceptance echo: `:216`, `:229`, `:240`.
- **AS-5** B0 passthrough: `:529`, `:537`.
- **AS-6** monotone gate: `:575`, `:594`, `:611` (`test_input_error_is_a_validator_error_subclass`).
- **AS-7** purity + disjointness: `:587`; read-only import at `proposal_input_gate.py:44`;
  `proposal.py` + `tests/scenario/` untouched; `main.py` diff = one import + one mount line + comment.
- **AS-8** documented matrix: `test_status_state_matrix_is_the_documented_set:618`. AS-8's other
  clauses are now captured this unit: **ruff clean** (cmd 1), **documented api suites green offline
  from `services/api`** (cmd 2: 43 passed; cmd 3: the full `tests/api` suite 497 passed — the api
  side of "unchanged … api suites green"), **modularity exit 0** (cmd 4: failures 0). The ONE
  remaining clause — the unchanged **scenario** suite (`python -m pytest tests/scenario -q`) — is NOT
  in this packet's `documented_test_commands`, so the broker declines it and the contract must not be
  altered to add it; that run plus the api/web CI conclusion on the pushed head stay routed to the
  orchestrator (item 4). AS-8 is otherwise satisfied by captured evidence.

## Routed to orchestrator — steps a producer structurally cannot perform

Each item below requires an authority a producer does not hold (creating files outside this task's
one allowed report path, running git write commands, or running a non-`documented` test command), so
it is routed rather than left undone. Item 3 is now **DONE** in this unit.

1. **Complete source, as separately bounded digest-bound sections.** Collect the four load-bearing
   artifacts — `proposal_input_gate.py`, `proposal_validation.py`, the `test_proposal_validation_api.py`
   pack, and the `main.py` mount patch — as SEPARATE, independently digest-bound sections, each split
   into ordered chunks that fit under the collection cap (not embedded in this report — my allowed
   paths hold only this one report file, and embedding re-creates the truncation gap). This report
   references them by file:line only.
2. **Commit + per-file working-tree/HEAD git identity.** Commit the four working-tree files (they are
   uncommitted; `git diff --raw HEAD` dst = `0000000`) so they become a reviewable SHA, and capture
   `git hash-object` (LF-normalized) at that commit and at the prior submission, so any
   byte-identical carry-forward is substantiated rather than asserted. Until then carry-forward stays
   **unverified** (§"Cumulative vs revision-only").
3. **DONE — documented-command execution, correct cwd, failures retained.** Ran all four
   `documented_test_commands` this unit at their documented cwd; results (all green) and the retained
   prior exit-4/exit-1 wrong-cwd failures are in "Command evidence" above.
4. **AS-8 scenario-suite + CI conclusion.** `python -m pytest tests/scenario -q` is not in this
   packet's `documented_test_commands` (the broker declines it; the contract must not be altered to
   add it) — attach orchestrator-run `tests/scenario` evidence and the api/web CI conclusion on the
   pushed head to fully close AS-8's last clause.

**Remaining OPEN: items 1, 2, 4** (bounded full-source collection; the commit + per-file digests; the
scenario suite + CI conclusion). The execution-evidence finding (item 3) is CLOSED by the captured
transcripts above.

## Preservation / disjointness (by reference)

`validate_proposed_massing` and every B0 behaviour are byte-identical (`proposal.py` untouched —
forbidden); the gate only ADDS refusals (monotone; `proposal_input_gate.py:155-179`). No new
dependency; stdlib only (route: `hashlib`, `json`, `logging`, `uuid`, `collections.abc`; tests add
`asyncio` + the already-present `fastapi.Request`). No network in tests (the streaming tests drive a
synthetic ASGI `receive`, `test_..._api.py:369-398`). `main.py` diff = the one import + one mount
line + posture comment.

## Out-of-scope (routed, not fixed — D-069) + unrelated lint NOT repaired

- Pre-existing modularity warnings in unrelated modules were deliberately left untouched (scope; "do
  not repair unrelated repository lint findings"). None of the four M5-T053 files is among them. The
  warning list is the captured `modularity_check.py --check` run in "Command evidence" above (failures
  0; 20 pre-existing warnings, none an M5-T053 file).
- DB-034(c) degenerate zero-length wall via the closing-vertex index and (d) read-side version
  leniency stay bound to the wall-consuming / version-emitting packet (B1/B2), unchanged here.
- A future packet MAY fold the gate into `proposal.py` once M5-T051 lands (reviewers' choice) —
  recorded as the gate module's docstring note (`proposal_input_gate.py:8-10`).
