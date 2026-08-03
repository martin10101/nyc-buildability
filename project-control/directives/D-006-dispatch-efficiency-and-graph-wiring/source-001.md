# D-006 — source-001 (verbatim owner directive) — Dispatch Efficiency and Code-Graph Wiring (v1.2)

Captured verbatim per `.claude/skills/directive-compliance` §1. Channel: owner_draft_issued_on_condition —
the owner authored this draft (v1.0→v1.1→v1.2, all 2026-07-31), registered it pending-capture behind
M0-T027 acceptance (`project-control/directives/PENDING-CAPTURE-dispatch-efficiency-and-graph-wiring.md`),
and pre-issued it through D-004 amendment 17 (D-004-R679: "on acceptance, the pending draft v1.2 is
ISSUED"), confirmed by the amendment-18 resume authorization (D-004-R714). M0-T027 was accepted
2026-08-03 (54th accepted task, PR #144, checkpoint CP-0036), so the issuance condition is satisfied
and this capture executes D-004-R679 exactly as captured.

Head at capture time: `control/D-006-efficiency-capture` branched from
`origin/main` = `aa257b88d6a0fb13b9d6bfc5372b352f05c6d234` (the merge commit of PR #144).

Source bytes re-verified immediately before capture (D-004-R679): the untracked repo-root draft
`OWNER_DIRECTIVE_DRAFT_dispatch-efficiency-and-graph-wiring.md` hashes to
`bd6c4ec2151202bb5209ee62f4cc2a3f94538cd40b695604ceff0e32d1c22b6b` — MATCHES the v1.2 digest in
the tracked pending-capture record and in D-004-R679. Superseded digests retained there for
provenance (v1.1 `357eb381…`, v1.0 `733bc12d…`).

§5.4's orientation claim re-verified at capture-time head as its own text requires:
`git merge-base --is-ancestor 11f3540c aa257b8` succeeds — `11f3540c` IS an ancestor of the
capture head.

R307 disposition recorded at capture (required by §8; governed by the D-004-R680 mechanical rule
and the owner's amendment-18 resume instruction "R307: DEFERRED arm"): the amendment-17 closeout
round's gate-class spawns (round-3 G3/G5, the M0-T027 final-verification and re-ruling passes)
ran under the temporary explicit-Opus-5 regime, so the disposition is **DEFERRED** with that
evidence, carrying a re-check at the next gate dispatch. THE RE-CHECK HAS SINCE BEEN PERFORMED
AND SUCCEEDED: the next gate-class dispatch after the owner's resume — the M0-T027 first
post-accept deferral verification (spawn `m0t027-poav`, 2026-08-03) — was spawned with an
explicit pinned Fable 5 value and honestly disclosed runtime model id `claude-fable-5`
(`project-control/reports/M0-T027-post-accept-deferral-verification.md`, Part 1 §A.4). Fable 5
pinning is therefore restored for gate-class spawns from that dispatch onward; the formal
DISCHARGE determination of the temporary-Opus-5 exception remains the owner's, surfaced in the
Step 7 consolidated report. §3's "pinned or session model" baseline reads accordingly.

R024 scan before commit: the text below contains no session identifier, machine username,
absolute user path, or hostname. No redaction required.

---

## THE OWNER DIRECTIVE (verbatim, complete — v1.2 bytes)

# Owner Directive (DRAFT) — Dispatch Efficiency and Code-Graph Wiring

**Status:** Draft for owner review. Not yet issued, not yet captured.
**Revision note (v1.1, 2026-07-31):** Sections 3, 5.2, 5.3, 5.4, and 8 reconciled to the pre-flight conflict findings (D-004 one-model-per-spawn rules, reviewer read-only discipline vs. query.py cache regeneration, source-003 citation and amendment-2-item-8 relationship, stale orientation SHA, R307 disposition). This revision changes the file's SHA-256; the pending-capture record must be re-hashed.
**Revision note (v1.2):** Section 3 names the sweep identity — an existing auditor-class definition, default `progress-auditor` — and Section 7 authorizes creating one new definition only as a fallback if none is compatible, closing the pre-flight's post-update finding. Re-hash the pending-capture record again.
**Queue position:** After M0-T027 closes. Do not capture, claim, or act on this while M0-T027 is open.
**Capture:** When issued, capture verbatim through the directive-compliance process (the orchestrator decomposes into rows per the intake standard; do not weaken, combine, or omit obligations).
**Motivation:** Verifier and producer dispatches routinely cost 150–250k tokens per spawn on the session model. Post-hoc review of the M0-T027 verification passes shows the cost concentrates in (a) whole-tree re-scans, (b) re-derivation of already-ruled findings, (c) mechanical scanning on the most expensive model, and (d) model-driven file discovery that a deterministic tool could pre-compute. Agent-teams guidance from the platform vendor confirms each teammate is a separate instance with its own context (≈7x a single session), so per-dispatch scope is the dominant cost lever.

---

## 1. Delta-scoped verification (dispatch standard)

Verification and review dispatches must state an explicit evidence scope, defaulting to:

- the files changed since the last independently verified HEAD (named by SHA in the dispatch), plus
- any registry rows whose source or subject those files touch.

Whole-tree or whole-registry re-scans require a stated trigger in the dispatch (e.g., first pass on a branch, integrity alarm, registry migration, or a finding that impeaches earlier scope). "Scan everything again" is no longer a permissible default.

This changes dispatch practice only. It does not weaken any gate: a verifier that finds cause may always widen its own scope, and must say it did.

## 2. Settled-findings rule (dispatch standard)

A dispatch must enumerate the prior passes' rulings that are **settled** (verdicts, counts, digests, boundaries already independently verified at a named HEAD). Settled findings are not re-derived; they are cited. A verifier may reopen a settled finding only with new evidence that contradicts it, and must flag the reopening explicitly.

## 3. Model tiering for mechanical work (ORCHESTRATION_POLICY amendment, spawn-level)

D-004's live spawn rules bind **one model per spawn**, and gate-class reviewer spawns must carry their explicitly pinned model (R226/R161/R275); no per-phase model mechanism exists inside a spawn. Tiering is therefore implemented at the **spawn level**, extending the existing repository-auditor pattern:

- A dedicated **mechanical-sweep identity** — non-gate, non-producer, auditor-class — may be spawned on a faster model, selected at dispatch, for bounded, read-only, mechanical work only: pattern scans, digest computation and comparison, occurrence counting, file inventory, diff reconstruction, and grep sweeps. The sweep identity is an existing auditor-class definition (default: `progress-auditor`) where compatible; only if no existing definition is compatible does Section 7 authorize creating exactly one new sweep-identity definition.
- Its output is data (counts, paths, hashes, matches), never judgment. Gate-class reviewer spawns and producer spawns keep their existing model rules unchanged (R298's ceiling governs producers); every ruling, verdict, severity, interpretation, acceptance-grade conclusion, and security/contract/geospatial/control-plane judgment remains on the pinned or session model.
- A dispatch using mechanical-sweep spawns names each spawn, its model, and its exact scope; the consuming reviewer cites the sweep's data as input evidence and remains solely responsible for the ruling; the report records the split.
- Gate-class reviewer identities are never spawned on a lower model for any phase. If D-004's spawn rules would still be violated by this mechanism as specified, stop and propose a D-004 amendment rather than proceeding.

The existing prohibition stands: never downgrade judgment to save tokens.

## 4. Small, self-contained teammate tasks (dispatch standard)

One focused question or bounded deliverable per teammate spawn. Omnibus dispatches that ask a single teammate to re-derive broad state are split. Where several small questions exist, prefer sequential focused spawns or a single spawn with an explicit enumerated scope over one open-ended mandate.

## 5. Exact-file packets and graph warm-start (packet standard + agent-definition wiring)

### 5.1 Packet navigation block

Task packets and dispatch prompts should name the exact files (and where useful, line ranges) the work concerns. When the task involves relationship or dependency questions and the file set is not already known, the orchestrator runs one bounded query:

    python tools/code_graph/query.py <bounded neighborhood / who-consumes / impact query>

and pastes the resulting file list into the packet as a **navigation block**, marked advisory. The subagent starts with the map instead of re-deriving it. `query.py` is deterministic and costs no model tokens; only its pasted output does.

### 5.2 Subagent awareness (one-line definition edit)

Add one sentence to the producer and reviewer agent definitions that perform code navigation (at minimum: backend-engineer, frontend-engineer, code-reviewer, security-reviewer, qa-engineer, rules-engineer, geospatial-engineer, data-contract-verifier):

> For dependency/impact/who-consumes questions not answered by the packet's navigation block, you may consult `python tools/code_graph/query.py` (advisory only — verify every material conclusion in actual source; see tools/code_graph/README.md) before broad Grep/Glob/Read sweeps.

**Read-only reviewer variant.** For the read-only reviewer roles among the eight (code-reviewer, security-reviewer, data-contract-verifier), the wired sentence additionally requires `--no-regen`: if the cache is stale or missing, the reviewer reports that fact instead of regenerating — reviewers never run write-producing commands (ADR-005), and default cache regeneration writes `graph.json`/`graph.meta.json` outside the repository, past the B-015-hardened guard's scope. The orchestrator's packet-time query (Section 5.1) doubles as the cache warm, so a reviewer's `--no-regen` normally finds a fresh cache.

### 5.3 Selectivity preserved

D-005 amendment 2 stands unchanged: graph use remains **selective and advisory, never required on every task**, and graph output is never authoritative evidence. Nothing in this directive makes graph use mandatory; it makes the tool *known* and its use *visible*.

Citation for capture: "amendment 2" is the M0-T030 GO-WITH-CONDITIONS owner decision recorded in `project-control/directives/D-005-codebase-knowledge-graph-pilot/source-003-amendment.md` (amendment numbers are offset by one from file names; cite the file path). Amendment 2 item 8 reserved graph injection into Agent Teams workflows beyond the pilot as a **separate owner decision**: this directive **is** that decision, exercised exactly to the extent of Sections 5.1–5.2 — packet navigation blocks and advisory awareness lines — and no further. Capture must state that relationship explicitly so the resulting rows read as exercising the reservation, not conflicting with it.

### 5.4 Usage visibility

When a dispatch or packet involves a graph-eligible question (dependency/impact/who-consumes/blast-radius), the report records either the graph query used (command + one-line result summary) or the stated reason direct navigation was chosen. This creates the audit trail that currently does not exist (as of origin/main 11f3540c — an ancestor of current main; re-verify this claim at capture-time head).

## 6. Measurement discipline (binding)

Consistent with D-005-R039 and the standing rule against unmeasured savings claims:

- No token, time, or cost saving may be claimed from any change in this directive without measurement.
- For the first N=6 dispatches after adoption (mix of verifier and producer), record the `/usage` Session figures at dispatch start and end, alongside the dispatch's scope statement and model tiering, in the task's report or a single adoption note.
- After N=6, the orchestrator summarizes observed deltas versus comparable pre-adoption dispatches (the M0-T027 verification passes may serve as the pre-adoption baseline) and reports to the owner. Claims follow the data; if a lever shows no benefit, say so.

## 7. Containment and non-goals

- No file accepted on origin/main is modified by this directive.
- No gate, verdict standard, adversarial-framing practice, or acceptance requirement is weakened. These changes narrow *scope defaults* and *model assignment for mechanical work*, not rigor.
- The only `.claude/` edits authorized are the Section 5.2 one-line additions, the Section 3 policy amendment text if required, and — only if no existing auditor-class definition is compatible — one new mechanical-sweep agent definition under `.claude/agents/` (Section 3).
- Nothing here amends D-005's trust model, R024/PII handling, or the M0-T027 closeout.
- This directive does not authorize the Codex↔Claude supervisor work (separate directive, separate task).

## 8. Owner decision requested

Issue as-is, issue with edits, or decline. If issued: capture verbatim, create one controlled task for the policy/definition edits (Sections 3 and 5.2) with exact allowed paths, and adopt the dispatch/packet standards (Sections 1, 2, 4, 5.1, 5.4, 6) as orchestrator practice from the next dispatch onward.

Capture must also record the owner's explicit **R307 disposition** — whether Fable 5 restoration discharges the temporary explicit-Opus-5 pinning for gate reviewers — since Section 3's baseline ("pinned or session model") depends on it, and the registry currently holds no restoration record.
