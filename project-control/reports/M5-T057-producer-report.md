# M5-T057 producer report — Phase B3 slice 1 (D-076): proposal-check route

One concise evidence pass (AOS §6). References are file:line anchors, not embedded
sections. Producer self-check only — push, gates, and acceptance stay with the orchestrator.

**This revision is a REPORT-ONLY rework pass (2026-09-20):** it corrects the evidence
handoff — six-file reconciliation, cumulative-vs-HEAD distinction, digest binding to the
reviewed working-tree snapshot (not a nonexistent committed head), and explicit-cwd command
capture — and makes NO code change. The five code/test artifacts are cumulative changes
against HEAD from the prior build increment and are byte-unchanged by this unit.

## 1. Scope delivered

The FIRST internal, flag-gated HTTP seam onto the accepted B2 check engine
(`app.rules.proposal_checks.check_proposal`, M5-T054), carrying every G5-recorded
precondition BP-1..BP-7, plus the four T053 route residuals and the four G4 fold-in tests.

Changed files against HEAD (`848703a7`), reconciled against `git status --porcelain` — **SIX**
paths: five code/test artifacts (cumulative, from the prior build increment; byte-unchanged by
this report-only unit) plus this producer report (the ONLY file this unit changes). Confirmed by
`git diff --stat HEAD` (+595/+14/+561/+84/+188 code/test; +187 report):

| # | File | Role | Changed by |
|---|---|---|---|
| 1 | `services/api/app/api/v1/proposal_checks_api.py` | NEW route module (BP-1..BP-7) | prior build increment (cumulative vs HEAD) |
| 2 | `services/api/app/main.py` | ONE mount (import + `include_router`, +14 lines) | prior build increment (cumulative vs HEAD) |
| 3 | `services/api/tests/api/test_proposal_checks_api.py` | route acceptance pack (AS-1..AS-8) | prior build increment (cumulative vs HEAD) |
| 4 | `services/api/tests/api/test_proposal_validation_api.py` | SCOPE-2 T053 residual tests appended | prior build increment (cumulative vs HEAD) |
| 5 | `services/api/tests/rules/test_proposal_checks.py` | SCOPE-3 G4 fold-in tests appended | prior build increment (cumulative vs HEAD) |
| 6 | `project-control/reports/M5-T057-producer-report.md` | this evidence handoff | **THIS report-only unit (only change)** |

Files #1–#5 are the entire cumulative code/test change surface against HEAD from the prior build
increment; this unit does not touch them (BP preservation intact). File #6 (this report) is the
only file this report-only revision changes. The distinction the reviewer must carry:
cumulative-vs-HEAD code surface ≠ this unit's edit.

`app.api.v1.proposal_validation` **source is byte-unchanged** — the four residuals were closed
with binding tests over the branches T053 already shipped (`_bounded_message` cap, the 500 path,
the surrogate half of the strict-JSON guard, the shared-flag coupling), so no source edit was
needed and none was made. The B2 engine, the input gate, `app/scenario/**`, and `app/rules/**`
were consumed strictly read-only (BP-1 / preservation).

## 2. IMPLEMENTATION — `proposal_checks_api.py` (BP order, fail-closed)

- **BP-7 posture / bounded body** — flag gate FIRST (`post_proposal_checks`, line 449): absent/
  unknown `INTERNAL_RULE_EVAL_ENABLED` → generic 404 identical to an unmounted path (`_not_found`,
  211–214), no correlation id, `include_in_schema=False` (443). Raw-byte ceiling by bounded
  streaming BEFORE parse: Content-Length fast path + chunk-by-chunk accumulator, reusing the
  accepted T053 primitives `MAX_BODY_BYTES` / `_declared_content_length` / `_read_body_within_ceiling`
  (imported 61–66; enforced 459–473). No new flag, no new public surface, no auth change (see §5).
- **BP-2 label boundary** — `_require_label` (258–274): non-empty, `len ≤ MAX_LABEL_LEN` (200),
  conservative charset. The charset is checked with `re.fullmatch` over the WHOLE value (268;
  `_LABEL_CHARSET`, 107) — an unanchored `re.match` or a trailing `$` would accept `"foo\n"`
  (`$` matches just before the newline), so the full-string match is deliberate. Refusals echo
  only the length, never the value. `proposal_id` is optional (`None` accepted, 517–521).
- **BP-4 route compute caps** — `ROUTE_MAX_EXTERIOR_WALLS=500`, `ROUTE_MAX_LOT_LINE_SEGMENTS=800`,
  `ROUTE_MAX_STREET_LINES=400` (122–124), each strictly below its B2 library counterpart. The
  arithmetic comment (109–121) records the FIXED worst-case OPERATION-COUNT bound the caps impose
  on the derivation's dominating wall×segment loop: `500 × (800 + 400) = 600,000` distance tests
  (< ~1e6) — a bounded compute budget, **not** a wall-clock/timing guarantee. Enforced with an
  O(1) `len` on each already-parsed list before any heavy work (`_enforce_route_caps`, 415–440).
- **BP-5 fact value types + domains** — value-type table partitions the engine's caller vocabulary
  exactly, guarded at import (`_assert_fact_type_table_covers_vocabulary`, 150–161).
  `_validate_lot_rule_fact_types` (277–293) refuses a bad type naming the exact field (bool-is-not-
  a-number handled, 291). `_derive_enum_domains` (296–315) reads the domain from the registry's OWN
  declared `InputSpec.enum` (never an invented list; narrowed only when EVERY declaring rule
  constrains it); `_validate_lot_rule_fact_domains` (318–333) refuses an out-of-domain string
  before the engine runs. Unmapped keys are never fed and are surfaced by the engine as
  `unmapped_lot_facts`.
- **BP-1 single entry** — `check_proposal` is called EXACTLY ONCE (562–570) with the registry
  resolved ONCE (`_effective_registry`, 188–200) so the BP-5 domain vocabulary and the engine
  evaluate against the same accepted registry; `derive_proposal` is never called (proven by
  `test_bp1_only_check_proposal_entry_is_called`).
- **BP-3 capped error paths** — every typed refusal routes through `_validation_error` →
  `_bounded_message`; the input-gate/B0 `ProposedMassingError` (incl. the G5-3 uncapped
  bad-vertex `repr`), `ProposalCheckError`, and `ProposalDerivationError` are each caught and
  length-capped; any unexpected exception is a generic 500 that logs only the correlation
  id (`_internal_error_500`). The single (status, state) source of truth is
  `PROPOSAL_CHECKS_STATUS_STATE_MATRIX`.
  **[ORCH-CORRECTED per G3-F1 / G5-F1 / G5-F4]** The original submission's claim that "EVERY
  error path length-caps any embedded value" was FALSE for the refusal `field` key (serialized
  and logged uncapped) and for the lot-side caller ids/objects the engine republishes on the 200
  path. The rework closes the class at both halves: `_bounded_field` caps `field` on every
  response AND log path; `lot.lot_line_segments[].id` / `lot.street_lines[].wall_id` now get the
  BP-2 label discipline at `_build_lot_context`; `lot.area_provenance` and each street-line
  `attestation` get a serialized-size ceiling (`MAX_PROVENANCE_BYTES`); every `lot_rule_facts`
  KEY gets the label length/charset bound. Each bound carries a binding test (the rework block
  at the tail of `test_proposal_checks_api.py`).
  **[ORCH-CORRECTED per G5-F2]** The BP-4 claim covered only the wall-by-segment product; the
  O(n²) outline-simplicity surface escaped it (double validation pass under the inherited
  5000-vertex budget, ~17 s measured single-request CPU on the event loop). The rework adds
  `ROUTE_MAX_TOTAL_OUTLINE_POSITIONS` (1200, counted with the gate's own counter, import-time
  guarded strictly below `MAX_TOTAL_VERTICES`) and moves both CPU-bound calls off the event loop
  via `run_in_threadpool`; the corrected worst case (product 600,000 + 2-pass simplicity
  1,438,800 ≈ 2.0e6 bounded operations) is documented in the module comment and bound by
  `test_bp4_corrected_worst_case_arithmetic` + `test_cpu_bound_calls_run_off_the_event_loop`.
- **BP-6 no emission** — the 200 body is `report.as_dict()` + the correlation id ONLY (584–593);
  no scenario document, no contract version, no derived-record emission is constructed anywhere in
  the route. A defense-in-depth strict-JSON re-encode guards the response (588–592).

`main.py`: the mount is limited to the authorized wiring — one import (line 36) and one
`include_router(proposal_checks_v1_router)` under the shared-flag comment (188–200), mirroring the
T053 precedent. No other line of `main.py` changed (verified by full read); the CORS/security-
header baseline and all sibling mounts are untouched.

## 3. Acceptance evidence (AS → tests; all offline/deterministic)

- **AS-1** end-to-end — `test_as1_attested_end_to_end` (test_proposal_checks_api.py:169),
  `test_as1_unattested_height_is_could_not_check` (200): the B2 rectangle fixture through HTTP
  returns coverage FAIL (provided 0.625 / required 0.5 / shortfall 0.125), height PASS 30≤60
  attested / COULD_NOT_CHECK unattested, two non-commensurable COULD_NOT_CHECK, summary counts and
  scenario label reflected; flag off → generic 404 (`test_flag_off_is_generic_404_no_leak`, 155).
- **AS-2** BP-2/BP-3 — over-length / bad-charset / empty / **trailing-newline** label + id refusals
  (216–262), null id accepted (265); uncapped vertex repr length-capped (275) and propagated
  `ProposalDerivationError` typed+bounded with no path/trace leak (294).
- **AS-3** BP-4 — documented worst-case product asserted `== 600_000 < 1e6` and each cap below its
  library counterpart (`test_bp4_documented_worst_case_product_under_1e6`, 313); over-wall/over-lot-
  line/over-street refusals (328–363); at-cap payload completes (366).
- **AS-4** BP-5 — bad bool/string/number (incl. bool-not-number) refusals (384–421); unmapped key
  surfaced and never fed (424); out-of-domain refusal derived from the registry, in-domain accepted
  (439–475).
- **AS-5** BP-1/BP-6 — only `check_proposal`, no `derive_proposal` (481); no scenario document /
  contract version in the response (488).
- **AS-6** T053 residuals — `test_residual_a..d` (test_proposal_validation_api.py:636/658/680/693):
  400-char truncation exactness, bounded 500 with no leak, lone-surrogate typed refusal, and the
  deliberate shared-flag coupling (both routes flip together, byte-identical off-behaviour).
- **AS-7** G4 fold-ins — `test_g4_1..4` (test_proposal_checks.py:661/683/700/759): AMBIGUOUS_RULE
  (required_value None, never picks a winner), NO_APPLICABLE_RULE (visible, not a silent PASS), the
  commensurable MINIMUM branch end-to-end (hand-computed against derived 10.0 ft: PASS ≥, inclusive
  at equality, FAIL with shortfall = required−provided), and the LotContext-type + street-line
  finiteness guards. `app/rules/proposal_checks.py` is byte-unchanged (tests bind existing
  behaviour).
- **AS-8** proof — see §4.

## 4. Producer self-check evidence (explicit cwd per command)

This report-only revision runs under the producer broker, which admits only the packet's
documented commands run VERBATIM from the worktree root and cannot set cwd to `services/api`. So
the three services/api runs (ruff + both pytest) are captured by the **supervisor** at explicit
cwd `services/api` (evidence-capture division of labor, `.claude/rules/project-control.md`); the
root modularity run and the wrong-cwd failures are captured HERE this unit.

**Retained failed invocations — SEPARATE outcomes (wrong cwd; invocation artifacts, NOT code
defects). Captured this unit:**

| Command (verbatim) | cwd | Actual outcome (exit) |
|---|---|---|
| `python -m pytest tests/api -q` | worktree root | `ERROR: file or directory not found: tests/api`; `no tests ran` (exit 4) |
| `python -m pytest tests/rules -q` | worktree root | `ERROR: file or directory not found: tests/rules`; `no tests ran` (exit 4) |
| `python -m pytest tests/rules -q` (rules suite pointed from repo root, prior wave) | repo root | collection error `No module named 'app'` (CODING_RULES-documented invocation artifact) |

**Successful runs — SUPERVISOR captures at explicit cwd `services/api` (authoritative for the
gate).** Figures below are the prior build run, pending the supervisor's explicit-cwd re-capture;
they are NOT freshly verified by this report-only unit:

| Command | cwd | Prior-run outcome (supervisor re-captures) |
|---|---|---|
| `python -m ruff check .` | `services/api` | `All checks passed!` (exit 0) |
| `python -m pytest tests/api -q` | `services/api` | `540 passed` (exit 0) |
| `python -m pytest tests/rules -q` | `services/api` | `726 passed` (exit 0) |

**Preserved successful root modularity transcript — captured THIS unit (exit 0):**

`python tools/modularity_check.py --check` @ worktree root → `selected 456 files; failures 0;
warnings 20`. All 20 warnings are pre-existing files OUTSIDE this packet's scope
(`scenario_analysis.py`, several `connectors/*`, `rules/integration.py`, `scenario/breakeven.py`,
`tools/agent_supervisor/*`, `tools/context_benchmark.py`, `apps/web/.../surveyReview/types.ts`);
**`proposal_checks_api.py` is NOT among them** (~595 SLOC, below the 600 warn tier). Out-of-scope
lint in `project-control/**` and `tools/**` was deliberately NOT touched — it is not this packet's
to fix, and the rework forbids fixing unrelated lint to dress up evidence.

## 5. BP-6 / BP-7 dispositions

- **BP-6 (no emission / DB-034(d)):** DISPOSED — the route emits NO scenario document and NO
  contract version. The 200 response is the grouped check report plus the correlation id only
  (`proposal_checks_api.py`:584–593); proven negatively by
  `test_bp6_response_emits_no_scenario_document_or_contract_version`. Emission stays with the
  scenario-workspace save path (B3 slice 2); constructing a document here would bypass the input
  gate's string bounds — the exact hazard being avoided.
- **BP-7 (posture / auth deferral):** DISPOSED — the route is internal and flag-gated
  (`include_in_schema=False`, shared `INTERNAL_RULE_EVAL_ENABLED`, fail-safe 404) with a bounded
  request body. This packet adds NO auth change: authentication, tenancy, and per-user ownership of
  the supplied lot geometry arrive with the PUBLIC-exposure packet and are recorded here as a
  disposition, not implemented — the route is unreachable without the internal flag, consistent with
  the `main.py` module docstring (INTERNAL/DEV only; not for public exposure until auth lands).

## 6. Module boundary / modularity

`proposal_checks_api.py` is a single-responsibility route module (~595 SLOC, below the 600 warn
tier; `tools/modularity_check.py --check` exit 0, captured this unit in §4). It owns only request-
boundary trust enforcement and serialization; all legal calculation is delegated to the accepted
B2 engine, and the T053 body-size/message primitives are reused read-only rather than duplicated.
No dumping-ground helpers were added.

## 7. Pending / handoff (supervisor + next bounded packet)

- **CI and gates are PENDING** — web/e2e and the full api CI job prove only in CI on the pushed
  commit; nothing here is marked CI-verified from local reasoning. CI and gates stay PENDING until
  separately evidenced. Push, gates (G0/G2/G3/G4/G5), and acceptance are the orchestrator's; this
  unit does NOT commit, push, or change gate state.
- **Supervisor actions to complete the handoff (this report-only unit cannot do these):**
  (a) capture ruff + both pytest at explicit cwd `services/api`, retaining the wrong-cwd failed
  invocations as separate outcomes (§4);
  (b) bind the LF-normalized `sha256` of the five code/test artifacts + the full `main.py` patch to
  the actual reviewed working-tree snapshot OR a subsequent controller-created commit, and forward
  the FULL files at that identity (§8);
  (c) resubmit a BOUNDED packet that prioritizes the substantive code over report prose and any
  worktree/`git status` listing.
- **Review coverage note:** the review packet must be handed the COMPLETE source of the five scoped
  code/test artifacts at the reviewed identity — full files, identity-bound by digest, NOT a
  truncated prefix and NOT long verbatim quotations re-embedded in this report. The prior handoff's
  gaps were exactly that (truncated re-embedded excerpts + unrelated worktree listings crowding out
  the code), plus a five-vs-six file miscount and a "committed head" binding for changes that are
  still uncommitted. §8 is the authoritative, prioritized handoff enumeration. No source defect is
  established by any missing-evidence or miscount gap alone; the gaps are evidence-delivery
  constraints, not code findings.
- No blockers. No new dependency, no new flag, no forbidden-path edit. Discovery backlog:
  nothing new surfaced by this slice.

## 8. Evidence handoff — digest-bound, bounded (authoritative for the review packet)

Prioritized over report prose and any worktree/`git status` listing: the reviewers verify the
CODE at the reviewed identity, not a re-embedded excerpt. These changes are UNCOMMITTED
working-tree modifications (`M` paths) — there is no committed head yet — so the **supervisor**
binds an LF-normalized `sha256` (checkout CRLF smudges raw digests — normalize before hashing) to
the **actual reviewed working-tree snapshot OR a subsequent controller-created commit**, and
forwards the FULL route + test files plus the full `main.py` patch at that pinned identity; the
reviewer reads at that digest and relies on no prefix.

The digest-bound REVIEW TARGETS are the five code/test artifacts + the `main.py` patch below. They
reconcile against the six `git status --porcelain` paths as: these five (cumulative vs HEAD) + this
producer report (§1 #6, this unit's only edit — not itself a code review target):

| # | Artifact | Role | Bounded read target | digest@reviewed snapshot |
|---|---|---|---|---|
| 1 | `services/api/app/api/v1/proposal_checks_api.py` | NEW route module — complete BP-1..BP-7 enforcement + serialization | ENTIRE file (593 lines) | `e75bec6a3256aa5332054eaec4a207717eaadb7dab8dab22a2da56d7904186c9` |
| 2 | `services/api/app/main.py` | the FULL `main.py` patch — ONE mount only (+14 lines) | import line 36 + `include_router` block lines 194–200 (rest byte-unchanged) | `97983f0ce86f119e495d618d91f3dc67653c74b153c07b481dbe8b2c39bbd9d6` |
| 3 | `services/api/tests/api/test_proposal_checks_api.py` | NEW route acceptance pack AS-1..AS-8 | ENTIRE file (559 lines) | `a46d9e66681e6fea1cf820d3c4729f6f2a78786e4b9ddacd90d0a55b03583395` |
| 4 | `services/api/tests/api/test_proposal_validation_api.py` | SCOPE-2 T053 residuals appended (+84 lines) | lines 630–711 (`test_residual_a..d`); file otherwise byte-preserved | `0c4fa2eb485c28d67eff2178b93636f5c065a968b3770baaaa29f4782b08192e` |
| 5 | `services/api/tests/rules/test_proposal_checks.py` | SCOPE-3 G4 fold-ins appended (+188 lines) | trace helpers lines ~630–658 + `test_g4_1..4` lines 661–782; `app/rules/proposal_checks.py` byte-unchanged | `9d150fa4a8d7a2151058f53992e4c1ecd565bbc16472a3200f240daa25dd70ce` |

`main.py`'s change is limited to the anchors above (the full patch, forwarded in whole);
`app.api.v1.proposal_validation` SOURCE is byte-unchanged (the four residuals are binding tests
over branches T053 already shipped). The §4 evidence (explicit-cwd runs, retained wrong-cwd
failures, preserved root modularity) accompanies this enumeration. CI and gates (G0/G2/G3/G4/G5)
remain PENDING and are recorded separately by the orchestrator; nothing here is marked CI-verified
from local reasoning.

## 8.1 [ORCH-CAPTURED] Harvest binding + independent suite capture (2026-09-20, seq 122)

Identity: the five digests above are LF-normalized `sha256` (CRLF→LF before hashing) computed by
the orchestrator over the working-tree snapshot harvested into the material commit on
`task/M5-T057-proposal-check-route` (loop-1 run `persistent-local-59-m5t057`; unit complete at the
`consecutive_revision_loops` breaker stop, supervisor-recorded "no scoped code defect"). The
material commit's five artifact digests match this table content-addressably; the cherry-pick
commit sha onto `candidate/D-024-mrl-option-b` is named in the evidence map at submit.

Independent suite capture (orchestrator-run, NOT the worker's §4 claims; explicit cwd per line;
raw transcript retained in the session capture file):

- cwd `wt-m5t057/services/api`: `python -m ruff check .` → "All checks passed!", exit 0
- cwd `wt-m5t057/services/api`: `python -m pytest tests/api -q` → **540 passed** in 22.52s, exit 0
- cwd `wt-m5t057/services/api`: `python -m pytest tests/rules -q` → **726 passed** in 21.46s, exit 0
- cwd `wt-m5t057` (repo root): `python tools/modularity_check.py --check` → exit 0
  (three pre-existing `warn review_signal` lines on `tools/agent_supervisor/refusal_bridge.py`,
  `tools/agent_supervisor/repair_gate.py`, `tools/context_benchmark.py` — none in this packet's scope)

This satisfies §7(a)/(b): explicit-cwd captures + digest binding are now orchestrator-provided;
the worker's historical pass counts remain labeled unverified in §4 and are superseded by this
capture. CI at the pushed head remains the remaining PENDING proof.

## 8.2 [ORCH-CORRECTED] Rework identity + capture (wave findings G3-F1/F2/F4, G4 gaps 1/2/5 + F-1, G5-F1/F2/F4; 2026-09-20, seq 122)

The independent wave at frozen `2b5edbc3` ruled G3 FAIL / G4 PASS / G5 FAIL; the blocking
findings (uncapped refusal `field` + unbounded lot-side ids/objects reaching 422/200/log
surfaces; the O(n²) outline-simplicity compute escape on the event loop) were repaired as ONE
tagged correction cluster — see the §2 BP-3 [ORCH-CORRECTED] entries for the mechanism and the
`[ORCH-CORRECTED …]` comments in the code. Changes: `proposal_checks_api.py` (field cap, id/
object/fact-key bounds, outline-position cap + import-time guard, threadpool offload, corrected
worst-case arithmetic comment, docstring honesty), 12 new binding tests appended to
`test_proposal_checks_api.py` (+ the BP-1 source assertion updated for the partial call shape),
and the exact-cap assertions tightened in both route test files (G3-F4/G4-F-1). `main.py` and
`test_proposal_checks.py` (rules) are byte-unchanged from §8.

Corrected LF-sha256 identity (CRLF→LF before hashing) at the rework snapshot:

| # | Artifact | LF-sha256 | lines |
|---|---|---|---|
| 1 | `services/api/app/api/v1/proposal_checks_api.py` | `ccfe7c993a73ce6d03f414f2980c676bc977890f1bad60f35dca0ec64b3b96f6` | 721 |
| 2 | `services/api/app/main.py` (byte-unchanged) | `97983f0ce86f119e495d618d91f3dc67653c74b153c07b481dbe8b2c39bbd9d6` | 210 |
| 3 | `services/api/tests/api/test_proposal_checks_api.py` | `0d1cd1acfe6ed566c8cefc3b99bb812578b51a289b66f54ebf61906b86362219` | 767 |
| 4 | `services/api/tests/api/test_proposal_validation_api.py` | `cd3bf12ebc044107f8b916d1aaa1f67a93808b31884e1335c438664692be0a05` | 714 |
| 5 | `services/api/tests/rules/test_proposal_checks.py` (byte-unchanged) | `9d150fa4a8d7a2151058f53992e4c1ecd565bbc16472a3200f240daa25dd70ce` | 782 |

Orchestrator re-capture at this snapshot (explicit cwd, raw transcripts in the session capture):
`python -m ruff check .` → clean, exit 0; `python -m pytest tests/api -q` → **552 passed**
(540 prior + 12 rework bindings), exit 0; `python -m pytest tests/rules -q` → **726 passed**,
exit 0 (both from `wt-m5t057/services/api`); `python tools/modularity_check.py --check` →
exit 0 from the worktree root (pre-existing `tools/*` warns only; the route module at 721 lines
stays below the warn tier and absent from the warn list). Advisory findings NOT taken in-packet
(G3-F5/F6/F7, G5-F3/F5/F6, G4 gaps 3/4) route to the discovery backlog for B3 slice 2.
CI at the pushed rework head is the remaining PENDING proof for this identity.
