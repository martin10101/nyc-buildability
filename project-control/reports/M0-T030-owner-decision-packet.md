# CODE GRAPH PILOT — OWNER DECISION PACKET (D-005, task M0-T030)

Author: orchestrator. Discharges D-005-R049/R055/R056/R060/R089 (Part 19 A–M structure).
Nothing proposed in sections H–K is implemented; every integration below awaits a separate owner GO
(D-005-R089; owner clarification 10). Sources: gate reports M0-T030-G3/G4/G5, delta review,
benchmark rev2, producer report, directive verification — all committed under project-control/reports/.

## A. Current repo/control state
- main at PR #113 merge `613c4b1` when the task branched; task branch `task/M0-T030-codegraph`
  final reviewed head `a51b710db08ad66eeeb14eb76a8e13ec32cf67d2`; CI 28/28 green including the new
  `code-graph` job.
- Active lanes untouched: no product tree, dependency manifest, hook, or config surface in the diff
  (verified independently by G5 and the directive verifier). B-015 (teammate readonly-guard gap)
  remains OPEN and unaffected. The 33 orphaned `.claude/worktrees` husks were excluded from
  indexing, never modified; any cleanup is a separate proposal.

## B. Tool due diligence (Graphify — decision already ratified)
`graphifyy` (PyPI): first release 2026-04-04; ~171 releases in ~116 days; single dominant author;
`graphify install` writes a PreToolUse hook + CLAUDE.md content; v0.9.25 (July) destroyed a user's
entire `~/.claude/settings.json` (issue #2167, fixed 0.9.27 only days ago); open issues #2202
(hook text behaves like prompt injection) and #2145 (hook misses subagents); no git-SHA provenance
in output; PyPI single-y `graphify` unregistered (typosquat slot). Under the 7-complete-day age
gate, every safe version was too young on 2026-07-29 and every old-enough version carried the
destructive bugs. **Owner ratified WAIT/REJECT (source-002); not reopened here.**

## C. Pilot setup (in-house replacement)
- Isolated worktree `.claude/worktrees/M0-T030-codegraph`, branch from frozen `613c4b1`; producer
  in a separate agent worktree; orchestrator transplanted and committed.
- Deliverables: `tools/code_graph/generate.py` (stdlib ast + syntactic TS import resolution),
  `tools/code_graph/query.py` (bounded CLI), `tools/code_graph/README.md` (trust model),
  `tools/test_code_graph.py` (29 fixture tests), one additive CI job, benchmark + reports.
- Artifacts are NEVER committed: generated into an out-of-repo cache keyed by a non-self-referential
  source fingerprint (source bytes + `apps/web/tsconfig.json`, CRLF-normalized). Real-repo scale:
  235 input files → 2,907 nodes / 1,491 edges in ~3–9 s; queries sub-second; CI job 8 s.

## D. Graph quality
- Maps well (confidence `exact`): Python imports incl. relative forms (983 exact), TS/TSX imports
  incl. `@/` alias resolution (237 exact), symbol definitions with line anchors.
- Honest degradation: `derived` contract-touchpoint edges (259) are filename-stem heuristics;
  `partial` (3) for dynamic imports; `unresolved` (9 — CSS/JSON targets) carry raw specifiers,
  never guesses. **No caller/callee edges exist in V1** (owner clarification 1).
- Known false-negative classes (found by the benchmark, documented in README): non-import
  relationships — byte-copied schema bundles, semantic "knows-about" couplings (benchmark Q4/Q7).

## E. Benchmark results (load-bearing; 18 questions, A baseline vs B graph-first, independent judges)
- Correctness: **B 18/18 vs A 15/18**. Completeness: **B 16/18 vs A 13/18**. Questions with false
  claims: **B 1 vs A 4**. Judge winners: B 5, A 2, ties 11.
- **Part-18 criterion 6 (materially reduces unnecessary exploration): NOT DEMONSTRATED.**
  B used MORE operations (291 vs 166) and opened ~2× the files; the mandated verify-in-source trust
  model converts cheap graph hits into extra reads. The honest claim is *higher answer quality on
  dependency/impact questions*, not lower cost, at this repo size (~220 source files).
- No token claims; per-agent elapsed time excluded as non-reproducible (interrupted+resumed run).
- The pilot may NOT be summarized as "fully successful" under Part 18: 11 of 12 criteria
  demonstrated; criterion 6 was not.

## F. Security/control findings
G5 PASS across all eight dimensions (supply chain, hook/config surface, network/execution,
filesystem safety, injection, secrets, CI, prompt-injection/exfiltration surface). Zero new
dependencies (test-enforced stdlib-only); zero hooks; artifacts structurally cannot carry file
contents. Non-blocking advisories on record: hash-bind graph.json in meta (LOW), cache key by
full repo path (INFO), OSError handling in cache read (INFO), symlinked-file note (INFO).

## G. Staleness/update strategy (implemented)
Fingerprint recomputed on every query (sub-second); mismatch → auto-regenerate with notice, or
`--no-regen` → exit 3 `STALE`. Stale data cannot be served silently; nothing is committed, so no
product PR can ever fail on a stale graph. G3's blocking correction (tsconfig missing from the
fingerprint) was found, fixed, re-tested (29/29), and delta-reviewed CLOSED. No git hooks; no
update automation beyond this (any future automation is a separate proposal).

## H. Proposed Claude context-routing integration (RECOMMENDATION ONLY)
Controlled task → read minimal packet capsule → `query.py find/impact/downstream` on the task's
named modules → read ONLY the authoritative source files the graph surfaces → implement → verify.
Concretely: add one paragraph to the task-packet template ("navigation: query the code graph first;
verify in source; graph is advisory") and mention `tools/code_graph/README.md` in CLAUDE.md's
routing table. No hooks, no automatic injection, no context dumping (hard cap stays).

## I. Proposed multi-agent use (RECOMMENDATION ONLY)
Proven in the benchmark itself: parallel read-only agents shared one pre-generated cache with a
stable fingerprint, zero contention, zero stale serves. Proposal: orchestrator pre-generates once
per session/worktree; producer/reviewer prompts may include 3–5 graph query results as the task's
"neighborhood capsule". No confinement change; the graph never justifies loosening any guard
(B-015 work proceeds independently).

## I2. Six-PRD expansion audit (RECOMMENDATION ONLY — clarification-10 target (e))
When you later lift the expansion-planning hold and the six design-platform PRDs are audited
against the existing codebase, graph-first navigation is proposed as the audit's working method:
(1) map each PRD capability onto existing modules with `find`/`impact`/`downstream` queries to
expose implemented-vs-missing surface deterministically instead of by repo-wide grepping;
(2) hand each audit reviewer a bounded neighborhood capsule (3–5 query results) per capability;
(3) require every audit claim to be verified in source per the trust model (advisory index only).
This proposes HOW the future audit would navigate — it does not start expansion planning, does not
touch the 19 proposed tasks/9 contracts/P1–P8, and leaves the §2 owner-review hold in
`.claude/rules/expansion-agent-dispatch-hold.md` fully in force; usage begins only on your GO.

## J. Mission-Control integration (RECOMMENDATION ONLY)
Later, an "Engineering Map" view could join product-map.json systems to graph neighborhoods
(system → key files → upstream/downstream). Reuses graph.json; requires a Mission-Control task and
a fresh owner GO (Part 20 boundary: not authorized by this pilot).

## K. Relationship to future graphs
- **Layer B (project/control graph) design note (Part 14, not implemented):** a read-only projection
  GENERATED from canonical sources — nodes: task, directive, requirement, blocker, milestone, gate,
  PR, product system, file, module, contract; edges: IMPLEMENTS/PART_OF/DEPENDS_ON/BLOCKED_BY/
  MODIFIES/DELIVERS/REVIEWS/CONSUMED_BY — emitted by a stdlib generator reading
  project-control/*.json + git, stamped with the same fingerprint discipline, never manually edited,
  never a competing source of truth (ledger/CLI remain authoritative). Natural join point: task
  packets name allowed_paths; the code graph names modules under them.
- **Layer C (NYC evidence knowledge graph): explicitly NOT this system.** Properties, BBL/BIN,
  districts, rules, filings, plan sets, benchmark cases, solver runs need their own data model,
  provenance and temporal semantics (D-005-R057/R080 recorded).

## L. Recommendation (exactly one)
**GO WITH CONDITIONS** — adopt the in-house code graph as advisory navigation infrastructure.
Conditions (all cheap, none blocking today's acceptance):
1. Advisory-only trust model stays mandatory (README categories verified in source, always).
2. No hooks, no auto-injection, no config changes — usage is explicit CLI invocation only.
3. Enumeration answers for contract/impact questions must state the derived-edge limitation
   (benchmark Q4/Q7 class) until a follow-up hardening task addresses non-import edges.
4. Follow-up hardening backlog item (not started without owner GO): hash-bind graph.json in meta
   (G5 LOW), accept `--limit` after subcommands, full-path cache key, OSError robustness.
5. Graphify remains WAIT; revisit only on explicit owner instruction.

## M. Exact next controlled task(s), if GO
1. **M0-T031 (proposal): code-graph hardening + usage wiring** — the four condition-4 fixes plus
   the CLAUDE.md routing-table mention and task-packet navigation paragraph (H/I above).
   Small, stdlib-only, same gate set.
2. **Later, separate owner decisions:** layer-B project-graph generator (K design note);
   Mission-Control Engineering Map (J); any Graphify re-evaluation (B).
None of these starts without your explicit GO (D-005-R089).
