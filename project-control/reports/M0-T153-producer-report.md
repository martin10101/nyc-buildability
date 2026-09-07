# M0-T153 Producer Report - D-033 T-B (rev 3, verifier-boundary rework 2026-09-07)

Under the 16,384-byte untracked-content bound (evidence.py:71) the supervisor
packet carries this file IN FULL (size proven by a passing probe, section 5).
Rev 3 delivers the three rework items: (1) the verifier-boundary regression -
a COMPLETE decision the REAL `codex_reviewer.validate_decision` admits, with
an allowed enum value, proven to drive its rows through the supported seam to
a recorded accept(); (2) the corrected module-boundary account (section 4);
(3) checkpoint discipline - the checkpoint now IDENTIFIES the collector-omitted
implementation and test ranges for SUPERVISOR-collected, digest-bound excerpts
instead of carrying worker-quoted slices, which cannot authenticate source.

## 0. Identity (current snapshot, measured by this rework unit)

- Task M0-T153 (governance, M0), stage claimed. Producer:
  supervised-loop-fable-worker (not a reviewer/gate recorder; ADR-005).
- Identity NOW: branch `task/M0-T153-accept-engine`, HEAD
  `3ff47c7aef22e26227d9bab2532fc51d75bde3fa` (git rev-parse, full 40-hex);
  `git status --porcelain` names exactly: modified `cli.py`, `gate_wave.py`,
  `test_agent_supervisor_gate_wave.py`; untracked `accept_engine.py`,
  `test_agent_supervisor_accept_engine.py`, this report.
- STATE DISCLOSURE: at this unit's start the accept-engine test file ALREADY
  held `RealDecisionBoundaryTests` (a prior interrupted pass of this same
  rework instruction wrote it; the rev-2 report predates it, hence rev 2's
  1,296-line/76-test claims). THIS unit verified that regression green through
  the documented commands, re-measured every digest (section 3), and stamped
  all claims to the current tree - nothing below relies on rev-2 counts.
- Qualifying evidence (supervisor-freeze rule s3): **D-033-R002, D-033-R006**,
  cited in the packet objective; commit-message citation = orchestrator duty.
- Holds ALL preserved; nothing activates (D-033-R005): both D-033 stage
  switches DEFAULT OFF (`accept_engine.py:183` choices-bound `default=""`;
  `:204-205` the enable check - packet-visible region), supervisor SHADOW-ONLY,
  R595 path, Tier D / Section 20, every hold.

## 1. Producer work content

1. `tools/test_agent_supervisor_accept_engine.py` - **79 tests** (was 76),
   **8 MUTATION partners** (switch, verifier separation, rank-blind merge,
   self-check/wave precondition, recorder allow-set, recorder queue-bound,
   identity freshness, seam re-assert). All fakes in-process.
2. REWORK ITEM 1 - the verifier-boundary regression
   (`RealDecisionBoundaryTests` :788-837 + helpers :749-785): a COMPLETE raw
   decision carrying every schema-required field, the ALLOWED enum value
   `COMPLETE` (asserted against the real schema's enum), and the correlation
   ids is admitted by the REAL `codex_reviewer.validate_decision` - and its
   sentinel rows reach the acceptance stage through the SUPPORTED seam
   (`run_acceptance_stage` -> `dispatch_verification`, the reviewer validating
   at exactly the `conduct_ephemeral_review` call shape with the passed
   `expected_task_id`/`expected_checkpoint_id`, -> `extract_rows` -> worst-of
   merge -> registry transcription -> ONE recorded accept()). Negative half:
   the legacy `'APPROVE'` fake value and incomplete decisions (missing
   `model_used`; COMPLETE without evidence_refs) are refused AT that boundary
   - the row path is proven live-compatible, not fake-only.
3. **4 tests** in `tools/test_agent_supervisor_gate_wave.py` closing both T-A
   advisories (regression + mutation pairs): G5 L1 `G2ReportRedactionTests`
   :998-1038; G3 D-2 `LiveVerdictTamperTests` :1046-1094. Suite 63 -> 67.
4. `accept_engine.py`/`gate_wave.py`/`cli.py` T-B code: in the tree at this
   unit's start, modified by NO rework pass (probe-verified byte-identical to
   the rev-2 digests, section 3).

## 2. Packet-item mapping (named tests in the accept-engine suite)

| Packet item | Evidence (class :lines) |
|---|---|
| Schema-valid sentinel rows | `RowExtractionTests` :642-741 (drift guard :653-664; empty-set attestation :676-680) |
| Malformed + oversized refusal | same :682-722; 64k exactness :724-741 |
| Live decision boundary (rework 1) | `RealDecisionBoundaryTests` :788-837 (real-validator admission :795-804; legacy/incomplete refusals :806-822; seam-to-accept regression :824-837) |
| Worst-of dedup | `WorstOfMergeTests` :844-901; MUTATION :872-879 |
| Producer != verifier | `VerifierDispatchTests` :542-634; MUTATION :573-579 |
| Self-check rejection | `WavePreconditionTests` :1028-1083; MUTATION :1068-1083 |
| Transcription atomicity | `TranscriptionTests` :909-1020; failed-replace :1009-1020 |
| Precondition preservation | `AcceptRecorderTests` :1091-1144 (real `project_control.py` argv, `--agent orchestrator`); parks-no-retry :1214-1227 |
| HEAD drift (I3) | `AcceptanceStageTests` :1152-1261; drift regression :1242-1253 (stamp never forged forward, no accept()); MUTATION :1255-1261 |
| Recorder restrictions | allow-set/queue/argument refusals :1101-1129; MUTATIONs :1131-1144 |
| Enabled/disabled CLI seams | `CliSeamTests` :1269-1395 (flags-off `assertIs` :1302-1311; unhosted refusal :1313-1329; re-assert MUTATION :1331-1344; full-ON `gate,gate,gate,accept` + audit chain :1362-1384; non-COMPLETE parks :1386-1395); `StageSwitchTests` :399-534 (OFF MUTATION :429-436; real `cli.build_parser()` :520-534) |
| Module measurement | `ModuleSizeTests` :374-391 (repo counter, every run) |

Gate-wave additions (TRACKED - reviewable in the packet diff): :998-1038,
:1046-1094 as above. D-033 rows (transcription aid; verification is the
independent verifier's alone): R001 wave preconditions + advisories locked;
R002 stage end-to-end behind the switch; R003 switch DEFAULT
OFF/refused-by-name/sealed; R005 OFF==today tripwires, holds untouched; R006
separation + self-check + recorder bounds, mutation-locked; R007 packet
citation present (commit half = orchestrator).

## 3. Digest reconciliation (dual convention) + code map

**Convention** (why a raw sha256 never equals the collector digest): raw =
sha256 over file bytes; collector (evidence.py:404 -> :410 -> models.py:33-66)
= `digest_of(text)` - sha256 over `canonical_json` of the file decoded
`utf-8-sig, errors="replace"` (BOM stripped, CRLF->LF) wrapped as a JSON
string literal. Cross-convention inequality is expected, NOT drift. For LF
BOM-free files both conventions bind the same byte sequence.

All values below were re-measured by THIS unit's probe run (section 5):

| File | bytes | eol | lines | sha256 raw / collector digest |
|---|---|---|---|---|
| accept_engine.py | 58,601 | LF | 1,189 | `7e5a9e0b5ee484ffa3d093d4ea3d9380f9a9736b0d541236c70ce42de02e19a9` / `17dfe90f0ac967d9cb37da3b779435f473f3bca7a17a1ada92ad28b16eabef06` |
| gate_wave.py | 55,471 | CRLF | 1,118 | `313177a9e2d43ec52cedd3702d95e27994c15ccf520657856094844d52ec1425` / `eb5fbbf314e4f3c5a4c1472f48e617e51111f8782bfc874eb1082711ae6795b8` |
| cli.py | 191,261 | CRLF | 3,602 | `148a4641dff34ab4a6e8678b6feb0b634749783bb20e6ea361c90b13eb6894b1` / `64a40b58690405abdb9e485097911a0acecd8ed7e9319bef9a960402f797a494` |
| test_.._accept_engine.py | 68,945 | LF | 1,399 | `1e250b2ae1acd4e55ca308d60c58edef16253f1985c6a9c1d8623f29671dd476` / `3fd1eb66cb6e0528328300b829d443b168b4757a73b89f28642f558bbad2d53f` |
| test_.._gate_wave.py | 55,576 | CRLF | 1,098 | `3cdd2ee608eb9cff449a00db5dbde456cb21138060c8ad97dad15eacc99b56b1` / `07ca768d14ca2a43b1606196092b6fc30e32d5c5176559c123e81e8773e68336` |

(Lines = `splitlines()`. The three source files and the gate-wave test file
are byte-identical to rev 2; only the accept-engine test file changed. The
gate-wave test row is the rev-2 value: the probe rode in that file and cannot
bind its own restored state - the supervisor's collection re-binds it.)

**Collector truncation** (16,384 B/file, evidence.py:71): the packet's
untracked view cuts `accept_engine.py` inside **line 321** and the
accept-engine test file inside **line 389**; the digests above bind the FULL
files. Per the rework instruction, the checkpoint's `reports[]` entries
IDENTIFY the omitted implementation spans and their test ranges so the
SUPERVISOR collects digest-bound excerpts itself; worker-quoted slices alone
cannot authenticate missing source and none are carried.

Code map, `accept_engine.py`:

| Span | Lines | Content |
|---|---|---|
| AE-01 | 1-173 | constants: `ROWS_CEILING_BYTES=64_000` :76, `ROW_STATE_RANK` :83-87, `ACCEPT_ALLOW_SET` :91, `ROW_SENTINEL` :116, immunized `VERIFIER_CONTRACT` :121-143 |
| AE-02 | 176-313 | switch: `assert_acceptance_enabled` :197-205; `managed_acceptance_start_gate` :208-253; `register_stage_switches` :272-282; `stage_start_gate` :285-297; `record_enable` :300-313 |
| AE-03 | 321-467 | `_assert_verifier_separated` :347-381; `plan_verifier_dispatch` :390-413; `dispatch_verification` :416-447; `_assert_record_bound` :450-467 |
| AE-04 | 475-659 | `_parse_sentinel_row` :479-509; `extract_rows` :512-594 (ceiling :542-552); `worst_of_merge` :597-628; `assert_rows_clean` :631-659 |
| AE-05 | 667-794 | `verification_path_for` :667; `build_task_verification` :680-730; `transcribe_task_verification` :733-794 (atomic :777-792) |
| AE-06 | 802-825 | `assert_identity_fresh`; `_submission_identity` :994-1018; `_live_head` :1021-1026 |
| AE-07 | 833-905 | `AcceptRecorder`: allow-set :859-867; queue pin :869-876; `build_argv` :878-898; `record_accept` :900-905 |
| AE-08 | 913-1189 | `_assert_wave_satisfies` :951-991; `run_acceptance_stage` :1029-1135; `run_with_post_complete_stage` :1143-1189 |

`gate_wave.py` (tracked; delta in packet diff): L1 redact-before-persist in
`write_g2_report` (:762; `redact_structure(body)` :785-787, count+labels
stored); D-2 live read-back in `run_gate_wave` (:882; `verify_verdict_report`
call :1003, def :549). `cli.py` touch points: :227 import; :2939-2943 the ONE
seam call; :2964-2966 `stage_start_gate` at `cmd_start`; :3376
`register_stage_switches(start)`.

## 4. Module boundary (rev-3 CORRECTION; accept_engine.py unchanged)

**Measurement** (`tools/modularity_check.py source_lines`, policy s10): 996
SLOC, scan certain; hard 1,000. `--check` selects tracked files only, so the
untracked module enters the census when the orchestrator commits;
`ModuleSizeTests` runs the SAME counter every suite run and fails above
HARD_SLOC. This section is the recorded justify-band justification, not a
waiver.

**CORRECTION (rework item 2)**: rev 2 claimed "no
storage/serialization/presentation/CLI parsing here". As written that was
wrong. The module contains five distinguishable concerns:

1. **Parsing** - `_parse_sentinel_row`/`extract_rows` (:479-594) decode
   sentinel row payloads out of validated decision facts;
   `_submission_identity` (:994-1018) and `transcribe_task_verification`
   (:744) parse registry/submission JSON.
2. **Serialization** - `build_task_verification` (:680-730) shapes the
   `task_verifications[]` container row; `transcribe_task_verification`
   serializes the merged v2 document (:777); result dataclasses via `to_dict`.
3. **Persistence** - `transcribe_task_verification` writes the registry file
   atomically (tempfile + `os.replace`, :777-792); `record_enable` (:300-313)
   writes the durable journal; refusals/stage results append to the audit log.
4. **Process invocation** - `AcceptRecorder.record_accept` (:900-905) invokes
   the REAL `project_control.py accept` via `process.run`/`minimal_env`;
   `_live_head` (:1021-1026) reads git HEAD through the collector's runner.
5. **Orchestration** - `run_acceptance_stage` (:1029-1135) sequences the
   chain; `run_with_post_complete_stage` (:1143-1189) is the CLI seam.

**Coupling rationale** (why ONE module): the five are thin faces of one
responsibility - one green independently-reviewed wave -> one recorded
acceptance, NO new authority - and none exists independently of it. Each is
acceptance-specific glue over shared machinery owned elsewhere: parsing
consumes the validated decision boundary (`codex_reviewer.validate_decision`
+ the provider schema own the decision shape; only the sentinel row encoding
is local); serialization/persistence touch exactly ONE registry document
shape the engine never creates or upgrades, and `accept()` re-checks every
row on the authoritative side; process invocation reuses `process.run` and
the evidence collector; orchestration composes only this module's steps.
Splitting a face out would export half of a fail-closed trust chain: switch
-> separation -> extraction -> merge -> clean gate -> transcription ->
freshness -> bounded recorder are mutation-tested as ONE chain, and a
detached importable "transcription writer" or "accept runner" reachable
without the switch and separation checks would be a new unguarded authority
surface (exactly what D-033-R006 forbids).

**Separation rationale** (how they stay separable inside): the AE-01..AE-08
sections layer one-way (constants -> switch -> dispatch -> rows ->
transcription -> freshness -> recorder -> stage); each concern sits in its
own section with its own test class and no section reaches back up.
`AcceptRecorder` is deliberately separate from
`gate_wave.ControlPlaneRecorder` (different authority surfaces, fixed
allow-sets, neither reaches the other's subcommands); imports are one-way, no
cycle; there is no presentation, and no CLI parsing beyond the one
`add_argument` registration cli.py must not duplicate. **Headroom duty**: 4
SLOC under hard - nontrivial growth MUST split; first candidates along the
concern lines above: `AcceptRecorder` (~73 SLOC, process invocation) and the
transcription persistence block (:733-794), each behind facade imports.

## 5. Verification (current snapshots, this unit, 2026-09-07)

**CURRENT SNAPSHOT** - the four documented commands re-run by THIS unit at
the section-3 digests (final tree), actual outputs:

1. accept-engine pytest -> **`79 passed`**
2. gate-wave pytest -> **`67 passed`**
3. ruff (five files, exactly as documented) -> **`All checks passed!`**
4. `modularity_check.py --check` -> **`selected 358 files; failures 0;
   warnings 14`** (all pre-existing; none names accept_engine.py;
   gate_wave.py's justify-band signal carries the M0-T152 justification).

**Probe disclosure (measurement only; no real test failed in any run)**:
command 2 ONCE with a deliberately-failing harvest probe appended to the
gate-wave suite (`1 failed, 67 passed`; the designed failure carried the
section-3 measurements - the accept-engine test file cannot hash itself, so
the probe rides the sibling suite); probe deleted, file restored. Then
command 2 ONCE with a PASSING probe asserting this report's final size fits
the 16,384-byte bound and the accept-engine test file still matches its
section-3 raw digest (`68 passed`); probe removed; command 2 re-proven
`67 passed`. The supervisor's `command_transcripts` and `untracked_content`
sections re-prove the green state and digests independently at each
collection.

## 6. NOT done / outstanding

No commit (orchestrator duty; message must cite D-033-R002 + D-033-R006). No
gate record, submit, accept, registry write, queue advance, push, or PR. No
change to `accept_engine.py`/`gate_wave.py`/`cli.py`; no collector/evidence
infrastructure touched (out of scope). No switch enabled: both D-033 stages
DEFAULT OFF; every owner hold stands (D-033-R005). The rework directive's
capture/binding is the orchestrator's (producers cannot write under
`project-control/directives/**`). OUTSTANDING: (1) orchestrator commit of the
two test files + this report with the R002/R006 citations; (2) independent
gates G0/G2/G3/G5 (producer != reviewer); (3) DCV rows at the reviewed
identity (this report is a CLAIM, never proof); (4) frozen-candidate
supervisor-suite re-baseline (>= 1165, 0 failures) - orchestrator duty.
