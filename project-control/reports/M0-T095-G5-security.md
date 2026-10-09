# M0-T095 — G5 independent security review (verbatim reviewer return)

Saved VERBATIM by the orchestrator from the read-only `security-reviewer` agent's return
channel (transport entity-decoding only; the harness's instruction-shaped-pattern
neutralization note is transport framing and is excluded). Review conducted at frozen
identity `5974f42b468f4565460914ce3c9413834cc42000`; delta attestation at corrected
identity `a3030ba6c907475436cebcf16936375d4e004fb4` appended below.

---VERBATIM-RETURN-BEGIN---
I have completed the full independent review. All 78 tests pass, the shadow-only posture is verified, the redaction backstop is proven, and no guard/forbidden path was touched. One factual discrepancy in the producer report (modularity warning status) is a G3 concern, not security. Here is my G5 security report.

---

VERDICT: PASS

# G5 Security Review — M0-T095 "D-024 G: root-cause repair gate + GitHub effect integration"

- Reviewer: security-reviewer (read-only, independent; producer = fable-orchestrator-session)
- Reviewed identity: HEAD `5974f42b468f4565460914ce3c9413834cc42000` (confirmed live == frozen)
- Deliverable `1e86670`, report `cef5ded`, evidence map `068bdbd`, base `11ad5c5`
- Files in scope: `tools/agent_supervisor/repair_gate.py` (NEW, +826), `tools/test_agent_supervisor_repair_gate.py` (NEW, +878), `project-control/reports/M0-T095-repair-gate.md`
- Reproduction: `python -m pytest tools/test_agent_supervisor_repair_gate.py -q` → **78 passed in 0.27s** (Python 3.11.9)

## Summary

The unit adds one pure-policy module of deterministic records and predicates plus its executable proof pack. It performs no I/O, spawns no process, opens no socket, reads no clock, and touches no live-effect registry. Every security boundary named in the packet holds. No critical, high, or medium security findings. Two INFO notes (defense-in-depth observation + one out-of-security-scope factual discrepancy in the producer report for the G3 reviewer's attention). Security verdict: PASS.

## Findings

None at CRITICAL / HIGH / MEDIUM / LOW severity.

### INFO-1 — checkpoint_section self-redacts free-prose only; identity/key fields rely on build_packet backstop (defense-in-depth, not a leak)
`tools/agent_supervisor/repair_gate.py:797-826`. `checkpoint_section` routes the two producer-controlled free-prose surfaces through `redaction.redact_text` — finding `detail` (line 818) and each answer value (line 824). It does **not** itself redact `task_id` (811), `defect_id` (812), or `unknown_questions` (822). I verified empirically that a synthetic `ghp_`+36 token placed in `defect_id` survives the *raw* `checkpoint_section` output but is caught by `evidence.build_packet`'s whole-packet `redact_structure` pass (`evidence.py:435`) and does **not** reach the built packet. Because `build_packet(extra_sections=...)` is the sole documented and only wired transmission path (the module has no live consumer — see shadow confirmation below), no secret reaches a review packet in the clear. Recommendation (non-blocking): should a future caller ever serialize `checkpoint_section` output directly to any sink without `redact_structure`, those three fields would be unredacted; a one-line docstring caveat would harden the contract. The scoped test `test_answers_are_routed_through_redaction` (test line 725) correctly proves the free-prose case; the identity/key fields are covered by the build_packet layer.

### INFO-2 — report modularity claim is inaccurate (out of G5 security scope; for G3/code-reviewer)
Report §4.3 states "no warning on either new file." Running `python tools/modularity_check.py --check` at HEAD emits `warn review_signal: tools/agent_supervisor/repair_gate.py - above the warning threshold` (module SLOC ≈ 625, over the 600 warn threshold, under the 750 justify / 1000 hard thresholds — a warn, not a fail; CI is not blocked). This is a cohesion/modularity matter for the G3 gate, not a security issue, and does not affect the security posture or this verdict. Flagged only because it is a factual discrepancy the orchestrator should note; the producer did separately record a cohesion judgment (§4.3), which the file supports (one responsibility: acceptance/review-time record protocols; no I/O/persistence/effects).

## Boundary confirmations (each item from the review scope)

**SHADOW-ONLY posture**
- No subprocess/network/file side-effects in `repair_gate.py`: CONFIRMED. Imports are `dataclasses`, `re`, `typing`, and internal `redaction`/`models.digest_of`/`policy` only (lines 47-55). A grep for `os|subprocess|socket|requests|urllib|open(|Popen|datetime.|.now(` returned only the docstring negative "never `datetime.now`" (line 8). No file/network/process primitive is present.
- E6 exercises `GitHubFlow` only through an injected fake runner + temporary journal: CONFIRMED. `E6DuplicatePrCreateTests` (test lines 468-486) drives the real `gf.GitHubFlow` with `_PrRunner` (recording fake, lines 455-465) and a `DurableJournal` in a `tempfile.TemporaryDirectory`; it asserts the second create returns `performed=False`/`already_created` and never reaches the runner (`len(flow.runner.prs) == 1`). The idempotency it relies on is the real `_guard`→CONFIRMED path in `github_flow.py:843-846`.
- Nothing lifts/weakens the R595 activation gate: CONFIRMED. No reference to R595, activation, or MODELED_EFFECTS anywhere in the new files; the module is pure records/predicates and changes no activation state.
- MODELED_EFFECTS / live-path registries untouched: CONFIRMED. `git diff --name-only 11ad5c5..5974f42 -- tools/agent_supervisor` lists **only** `repair_gate.py`. `external_effects.py`, `push_policy.py`, `github_flow.py`, `policy.py` are unmodified.

**Authority boundaries**
- No new Codex/reviewer write capability (R021/R022): CONFIRMED. The module exposes only record constructors and evaluators; no reviewer invocation, no git/gh/write surface. E9's read-only-reviewer contract is cited to the unchanged `test_agent_supervisor_reviewer.py` proof, not re-implemented.
- Classification never authorizes a merge (E10/E11): CONFIRMED. `PRClassification.allowed_actions` is `()` for `pre_existing`, `expected_open_held`, and `stale_candidate` (`repair_gate.py:711-733`); only the current task's *own* PR receives the single routing token `evaluate_via_github_flow` (720), which is not an effect — the actual merge still passes `github_flow.evaluate_merge` S5.5 + owner authority. Cross-proof `test_the_existing_flow_refuses_an_unauthorized_merge` (test 535-543) shows the S5.5 gate independently refuses an unauthorized pre-existing PR.
- Owner holds win precedence: CONFIRMED. `classify_pr` checks `owner_hold` FIRST (line 711), returning `expected_open_held` with `()` even when the PR was opened by the current task (`test_an_owner_hold_wins_over_task_ownership`, test 557-561). PR #241 fixture is classified deliberately-unmerged (test 528-533).
- `repair_gate_disposition` never auto-accepts (R078): CONFIRMED (`repair_gate.py:404-432`). Incomplete answers → `rejected`; complete answers with no verdict → `review_required` ("completeness is never acceptance"); only an explicit `PASS` → `accepted_by_review`; `FAIL`/`BLOCKED` → `rejected`; any unrecognized verdict fails closed to `review_required`. Proven by `test_complete_answers_never_auto_accept` and `test_an_unrecognized_verdict_fails_closed_to_review_required`.

**Redaction / leak surfaces**
- Producer answers + finding details routed through `redaction.redact_text` before riding the packet: CONFIRMED (`repair_gate.py:818,824`). `test_answers_are_routed_through_redaction` proves a `ghp_`+36 secret in an answer is absent from `canonical_json(section)` and replaced by `[REDACTED...]`. `redact_text` matches that token via the `github_pat` pattern (`redaction.py:44`). A secret-bearing answer cannot reach the packet in the clear (and build_packet re-redacts — INFO-1).
- `REPAIR_GATE_SECTION_KEY` collides with no `PROHIBITED_MARKER_KEYS` entry: CONFIRMED. `"repair_gate_checkpoint"` (`repair_gate.py:794`) is absent from every category set in `review_packet.PROHIBITED_MARKER_KEYS` (`review_packet.py:280-296`); the dynamic test `test_the_section_key_collides_with_no_prohibited_marker` and `test_the_content_guard_admits_a_packet_carrying_the_section` (via `guard_packet`) both pass.
- No credentials/secrets/user paths embedded in the new files (repo is PUBLIC): CONFIRMED. The only secret-shaped literal is the synthetic redaction test fixture `secret = "ghp_" + "E" * 36` (test line 726) — a fake used to exercise redaction, not a live credential. No `sk-ant-`, real `ghp_`, `AKIA`, `C:\Users\...`, or `/home/...` strings present.

**Fail-closed checks**
- Unknown vocab raises typed `RepairGateError`: CONFIRMED — unknown repair mode (line 170), layer kind (103), evidence tool (121), plus `missing_identity`/`missing_exception_id`/`bad_pr_number`. Proven by `RecordShapeTests`.
- Undecidable compatibility expiry BLOCKS acceptance: CONFIRMED. `compatibility_expired` RAISES on a missing expiry fact (`repair_gate.py:510-516`); `evaluate_acceptance` catches `RepairGateError` and adds the id to `expired`, blocking acceptance (539-551). Proven by `test_an_undecidable_expiry_blocks_fail_closed`.
- Blank identities never validate reviews: CONFIRMED (`review_still_valid` lines 577-579; `test_a_blank_identity_fails_closed`). An identity change invalidates the prior review (585-588).
- Unknown review verdicts stay `review_required`: CONFIRMED (line 430-432).
- Freeze-citation validator (R017/E13) rejects uncited supervisor change records: CONFIRMED. `validate_freeze_citation` (760-785) requires `D-024-R###` in BOTH packet and commit message when `touches_supervisor` (via the reused `policy.CONTROLLER_PATHS`) is true; proven by the E13 suite (uncited → two refusals; packet-only → commit refusal; fully cited → pass; non-supervisor → exempt).

**Guards untouched**
- `.claude/hooks`, `.claude/settings.json`, `.claude/ORCHESTRATION_POLICY.md`, and every packet forbidden path unmodified: CONFIRMED. `git diff --name-only 11ad5c5..068bdbd` = exactly the 4 producer files (`repair_gate.py`, test, `M0-T095-repair-gate.md`, `M0-T095-evidence-map.json`); none is a forbidden path. A targeted diff over `.claude/hooks .claude/settings.json .claude/ORCHESTRATION_POLICY.md tools/project_control.py external_effects.py push_policy.py` across the *entire* range `11ad5c5..5974f42` returned empty. (The `project-control/tasks/M0-T095.json` and `state.json` edits appear only in the orchestrator control commit `5974f42`, outside the producer deliverable range — expected control-plane writes, not producer scope violations.)
- Supervisor-freeze citation D-024-R105 present in packet + commit messages: CONFIRMED. Cited in the task packet (report §0/§4.4) and in all four commit subjects/bodies (`1e86670`, `cef5ded`, `068bdbd`, `5974f42`), satisfying `.claude/rules/supervisor-freeze.md` §3 (cite in BOTH packet and commit).

**Dependency security**
- No new dependency added: CONFIRMED. Both new files import only the Python standard library and existing in-package modules; no manifest/lockfile touched. G5 provenance review of a new package is not triggered.

**Platform controls not applicable to this unit (justification)**
- Cross-tenant isolation, service-role secrecy, private storage, SSRF, upload controls: N/A. `repair_gate.py` is a deterministic in-memory policy module — no Supabase/RLS surface, no service role, no storage, no HTTP client, no upload path. There is no tenant, network, or storage boundary within scope for this unit; the GitHub-effect *verification* is done against the pre-existing, unmodified `github_flow`/`external_effects`/`push_policy` proofs (cited, not re-implemented).
- Prompt-injection defenses: PRESERVED. All producer/record content is treated as data — the R078 question set is a CLOSED tuple (`repair_gate.py:358-365`) and unknown answer keys are refused (`evaluate_checkpoint_answers` lines 391-396), so a producer cannot substitute its own questions or move any decision to a looser lane; no producer string is interpreted as control flow, executed, or fed to `eval`/subprocess. This inherits the unchanged `policy.py` posture (stated reasons never read by classification).
- Least privilege / log redaction: PRESERVED. The module confers no privilege (only refusal/acceptance records that still require independent review + owner authority); its two `re` patterns are simple anchored/bounded expressions with no ReDoS exposure; it emits no logs itself, and all outbound transmission is redacted twice (checkpoint_section free-prose + build_packet whole-packet).

## Shadow-only / live-wiring confirmation
`repair_gate` is imported only by its own test file (`grep` across `tools/**.py`), and `checkpoint_section` is referenced only in the module and the test. There is no production/activated consumer — the review-packet wiring is present as a record-only helper, consistent with the SHADOW-ONLY freeze posture. No live path is altered.

## Verdict
All security boundaries in the packet are independently verified at the frozen identity; 78/78 tests reproduced green; no CRITICAL/HIGH/MEDIUM/LOW security defect. INFO-2 (modularity warning vs. report claim) is referred to the G3 code-reviewer and does not affect security.

VERDICT: PASS
---VERBATIM-RETURN-END---

## Delta attestation (corrected identity `a3030ba`) — VERBATIM

---VERBATIM-DELTA-BEGIN---
DELTA-VERDICT: PASS

Delta attestation (G5, M0-T095) — reviewed `git diff 7c3af52..a3030ba` at HEAD `a3030ba`, read-only.

The correction round is behavior-neutral and my prior G5 PASS carries to identity `a3030ba`. Three files changed, none altering any executable path:

1. `tools/agent_supervisor/repair_gate.py` — the ONLY code-file change is a 6-line docstring addition inside `checkpoint_section` (after "independent review.", before `return`). It documents the redaction contract exactly as INFO-1 recommended (free-prose redacted here; `task_id`/`defect_id`/question keys rely on `build_packet`'s `redact_structure` backstop; never serialize directly to an external sink). No statement, branch, constant, or signature changed. My INFO-1 note is now closed.

2. `project-control/reports/M0-T095-repair-gate.md` — report wording (§4.2/§4.3 modularity correction addressing my INFO-2, now referred/resolved for G3; plus a Bootstrap Gate-0/MCP attestation section). Documentation only.

3. `project-control/reports/M0-T095-G2-self-check.md` — producer self-check report; not a deliverable code/guard file.

Verified: no change to `tools/test_agent_supervisor_repair_gate.py`, `.claude/hooks`, `.claude/settings.json`, `external_effects.py`, `push_policy.py`, or any forbidden path in this delta; the intervening commits `068bdbd..7c3af52` (Amendment-7 registry capture + LF normalization/G2 record) touched no M0-T095 deliverable code. Tests reproduced: `78 passed` at `a3030ba`. SHADOW-ONLY posture, authority boundaries, closed-vocabulary fail-closed behavior, redaction surfaces, and R595/live-registry non-involvement are all unchanged. Both INFO items from the original report are now resolved.

G5 security PASS holds at identity a3030ba.
---VERBATIM-DELTA-END---
