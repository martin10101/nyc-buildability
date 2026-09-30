# NYC BUILDABILITY — D-019 NEXT-SESSION HANDOFF (2026-08-19)

EXTERNAL FILE — lives OUTSIDE every Git checkout, on owner instruction.
Written by the outgoing orchestrator session after a read-only live
reconciliation. Nothing in the repository was modified when this file was
produced: no directive, no task, no commit, no push, no PR, no merge, no
controller action, no promotion decision, no D-018 correction work.

A brand-new Claude Code session must be able to continue from this file
alone, without the prior conversation.

---

## 1. Repository checkpoint (reconciled live, read-only, 2026-08-19)

- Repo: github.com/martin10101/nyc-buildability (private).
  Primary checkout: `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack`.
  Working worktree used by recent sessions: `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m0t064`.
- origin/main SHA: `3c108944f6b1abf23866351c696e7f09562ea498`
  — this IS the merge commit of PR #238 ("Merge pull request #238 from
  martin10101/task/M0-T075-context-integration").
- M0-T075 identities:
  * first submitted/reviewed SHA: `df2468d3216ffe4e7ec38671548cdb2deaad5651`
  * corrected/attested + ACCEPTED reviewed SHA: `db82e0abb86aa6fe5e2858a29978315a553c881c`
    (content manifest `a0f4aef4a2a42f4c08fe68300c52a4ec875d960a47b2f3c6da8646df3dd395ce`)
  * acceptance-ledger commit: `11ff510e997db50fd58a01a54f53af75e4db6fcb`
  * merge to main: `3c108944…` (PR #238, head-SHA-matched, branch deleted)
- Ledger: **98 accepted tasks**; `M0-T075` present in `state.json accepted_tasks`.
- D-018 (`project-control/directives/D-018-context-vertical-integration-correction/`):
  **70 requirements** total; **63 task-bound** rows (D-018-R006..R068) applicable
  to M0-T075 (verified 63/63 by the independent verifier at db82e0a);
  **7 session-governance sentinel rows** (R001-R005, R069, R070) bound to the
  non-ledger sentinel `D-018-BOOTSTRAP`, verified at directive verification.
- Protected boundaries and owner gates (ABSOLUTE):
  * `tools/agent_supervisor/**` — never modified by these initiatives.
  * Live controller config `C:\Program Files\SupervisorConfig\config.toml`
    (sha256 begins `6aef12a9…`) and
    `C:\SupervisorController\model_selection.toml` (sha256 begins `0e2432c0…`)
    — byte-identical throughout; verified read-only 2026-08-18.
  * limited-auto disabled; branch protection, security policy, CI gates, and
    git history untouched; no live supervisor probe performed.
  * D-013-R060 promotion decision: **PENDING OWNER** — never made.
  * Stage-2 live-controller update bundle: prepared but **NEVER executed**
    (runbook: `C:\Users\MLFLL\Downloads\nyc-zoning\CONTROLLER_UPDATE_RUNBOOK_2026-08-18.md`).
- Current branch/worktree status at reconciliation: wt-m0t064 on `main`,
  HEAD == origin/main == `3c10894…`, `git status --short` EMPTY (clean).
- Availability for the next task: **M0-T076 is UNUSED** (no packet file, no
  branch) and **D-019 is UNUSED** (no directive directory, no branch).
- Open PRs relevant to this work: **none**. The only open PR is the
  long-standing unrelated #64 (M0-T019, apps/web frontend security).

## 2. What D-018 (task M0-T075, PR #238) genuinely implemented

- **Integrated context compiler** (`tools/context_pack.py` + the module set
  `context_pack_{sources,evidence,assembly,render,index,budget,io}.py`):
  one packet under one budget now includes the task packet, the EXACT
  applicable requirement IDs AND texts (directive_refs incl. "ALL" resolved
  deterministically via the registry), reopened authoritative source and
  test excerpts (bounded, deterministic selection), code-graph neighborhoods
  seeded from real changed/allowed paths (prose fields only via a strict
  deterministic extractor with every candidate recorded), Unit C subsystem
  placement, and explicitly ADVISORY Unit D memory entries with honest
  absence/quarantine status, plus inclusion/omission/truncation/query/
  digest/coverage provenance (`meta.integration`).
- **Enforced insufficiency**: missing/unresolved required evidence → bounded
  machine-readable meta + **exit 3**; over-budget split refusal preserved
  (**exit 2**). Public facade + CLI preserved.
- **Canonical orchestrator entry point** `tools/context_orchestrate.py`:
  wraps the SAME compiler (no second packet builder), derives
  `model_routing.Signals` from compiled evidence, writes a bounded
  `dispatch_manifest.json`, records decisions to the external rotated
  `model_routing.jsonl`.
- **Memory-graph transaction** (`tools/memory_graph.py` +
  `repo_index_cache.write_generation_locked`): promotion holds the store's
  single-writer lock across load-current → conflict check → mutation →
  validation → promotion, with explicit `concurrent_writer` + retries and a
  two-writer regression test (BUT see blocker A below — the underlying LOCK
  ACQUISITION itself has a reproduced race).
- **Shared containment rule** `tools/context_paths.py` (canonical
  repo-relative form + real-path/symlink-junction containment) adopted by
  deep views, view seeds/cards, ontology inputs, memory evidence digests,
  compiler --include/contract/excerpt reads (BUT see blocker B — coverage
  has reproduced gaps, notably `--ci-summary`).
- **Retention made real**: generation `prune` invoked on every index build
  and inside the memory transaction (current + rollback kept); telemetry and
  routing JSONL rotated.
- **Projection repair** (`tools/status_projection.py`): deterministic
  input-manifest digest over every material control-plane input + git
  identity; uncommitted edits stale the snapshot; full status map incl.
  `self_check`/`canceled`; generated-current vs committed-snapshot label.
- **Benchmark extension** (`tools/context_benchmark.py`): pre-change G0
  baseline (`project-control/reports/M0-T075-baseline-g0.json`), retained
  42-case index-parity set + distinct parser-version case + lock/orphan
  pass predicates + nearest-rank p95, and an `--e2e` mode invoking the
  actual compiler over five frozen shapes (BUT see blockers C/D — the
  committed e2e result is not reproducible from clean main).
- **CI**: one additive `context-pipeline` job runs the Units B–F suites +
  `tools/test_context_integration.py` on every push/PR (pure +29-line
  insertion; nothing removed or weakened).
- **Automatic supervisor consumption remains OWNER-GATED**: wiring it would
  require protected `tools/agent_supervisor/**` changes; the runbook and
  every dispatch manifest state this explicitly. No automatic integration
  exists or is claimed.
- Honest history record: `project-control/reports/M0-T069-benchmark-scope-correction.md`
  preserves M0-T069's 42/42 as an INDEX-parity result and states its limits;
  M0-T069's records were never reopened.

## 3. Positive independent evidence (still true, reproduced by independent agents)

- The **155 D-018-scope suite tests pass** (integration 11, context_pack 15,
  context_pack_index 8, subsystem_resolver 21, memory_graph 31, repo_views
  26, context_benchmark 19, status_projection 11, repo_index_cache 13),
  plus repo_index_incremental 25 and the A1 suites
  (fingerprint/assembly/baseline) — all green at the accepted SHA and in CI.
- **Exact requirement rows resolve on the real task M0-T066**: the live
  compile carries 24 applicable D-013 requirement IDs with verbatim texts,
  4 source + 3 test excerpts, ontology placement, honest advisory memory.
- **Expanded index benchmark remains byte-identical** across every case
  (superset of the frozen 42; parser-version case included), and the
  committed M0-T069 report is unmodified.
- `modularity_check --check` 0 failures; `validate_directive_compliance`
  exit 0 (18 directives; producer≠verifier separation verified).

## 4. INDEPENDENTLY REPRODUCED PROMOTION BLOCKERS (facts, owner-verified)

These were reproduced outside the producer's own tests and are recorded as
FACTS. They are the reason D-013-R060 promotion must remain pending and the
reason the next task exists.

**A. SingleWriterLock publication/reclaim race (contradicts D-018-R029).**
Two synchronized valid memory writers can BOTH return `promoted` while the
final memory graph contains only ONE node. Mechanism: `SingleWriterLock.
acquire()` (tools/repo_index_cache.py) creates the lock directory via
`mkdir` and only afterwards writes `owner.json`; a second writer that
observes the directory BEFORE `owner.json` exists reads empty metadata,
classifies the lock as stale/dead (aged=True, pid=-1), REMOVES it and enters
concurrently. The in-transaction span then provides no protection because
both writers hold "the lock". The existing two-writer regression test does
not cover this interleave (it forces the race at `load_current`, after
acquisition).

**B. Containment bypass.**
An absolute path supplied through `--ci-summary` is READ AND INCLUDED in the
packet with a successful exit — `--ci-summary` was never routed through the
shared containment rule. Additionally: rejected absolute `--include` values
are repeated in error details (the refusal echoes the caller-supplied
string, which for an absolute input IS a private absolute path in the
packet's omission reason), and an explicitly refused include can still leave
the packet sufficient with exit 0 (a refused explicit request is treated as
an ordinary omission, not an insufficiency).

**C. Clean-main benchmark failure (committed result not reproducible).**
The exact documented e2e command, using
`project-control/reports/M0-T075-baseline-g0.json`, EXITS 2 when run from
clean merged main. Cause: the baseline captured a `git_diff` source from a
dirty control-plane working tree at capture time; clean main has no diff, so
the baseline-included `git_diff` source id is "missing now" and the
no-worse-than-baseline predicate fails. The committed no-worse result is
therefore an artifact of the dirty capture state, not reproducible from a
clean checkout.

**D. Committed-diff failure (diff-base default wrong for reviewers).**
The canonical orchestrator defaults to `--diff-base HEAD`. On a branch where
the work has already been COMMITTED, a reviewer packet sees no diff and
exits 3 (insufficient). Using the frozen parent/G0 base instead includes the
committed change and exits 0. The default therefore breaks the primary
reviewer use-case on committed branches.

**E. Incomplete vertical integration.**
- The compiler REIMPLEMENTS neighborhood/census logic in
  `context_pack_index.py` instead of consuming the actual Unit E view
  functions (`tools/repo_views.py`).
- Graph queries use the alphabetically FIRST FIVE seeds (`MAX_SEEDS = 5`)
  and can miss the task's principal implementation files when control-plane
  or docs paths sort earlier.
- Routing silently emits `False` for undetermined signals such as
  `concurrency_or_performance`, `destructive_operations`,
  `external_side_effects` — false certainty rather than honest unknowns.
- Advisory memory does not carry enough bounded digest content to be useful
  (ids/outcomes only; no bounded note/summary content).

## 5. Owner decisions (standing)

- **D-013-R060 promotion MUST remain pending.** Do not approve, activate, or
  imply it.
- **The controller bundle is a separate owner-present action** and does NOT
  activate context consumption even when executed.
- **No supervisor integration is authorized.** The boundary stays
  owner-gated.
- **The next action is ONE bounded correction task** (D-019 / M0-T076), not
  a rebuild, not a D-013 restart, not a multi-unit program.

## 6. Exact proposed next task (D-019 / M0-T076 — awaiting the owner's master prompt)

Working title: "Context pipeline promotion-blocker correction". Scope, all
within one task / one branch / one PR:

1. **Atomic ownership-token lock**: rework `SingleWriterLock` acquisition/
   reclaim/release so publication is atomic (e.g. create a fully-populated
   temp directory with owner metadata and atomically rename it into place;
   reclaim only a COMPLETE stale lock via the same atomic protocol; release
   verifies ownership token). Add the exact pre-owner.json-observation race
   as a regression test; re-prove the two-writer promotion guarantee end to
   end (blocker A).
2. **Full containment + private-path redaction**: route `--ci-summary` (and
   any remaining external-argument read) through the shared containment
   rule; REDACT caller-supplied absolute strings in every error/omission
   detail (never echo them); decide-and-enforce that an explicitly refused
   `--include` makes the packet insufficient (nonzero), never silently
   sufficient (blocker B).
3. **Frozen G0/explicit diff base**: make the orchestrator/compiler take an
   explicit frozen diff base (task G0/base SHA) for reviewer packets;
   committed-branch reviewer packets must include the committed change and
   exit 0; document and test both committed and uncommitted states
   (blocker D).
4. **Reproducible clean-state e2e benchmark**: re-capture or re-derive the
   baseline so the documented e2e command exits 0 from CLEAN merged main;
   make the no-worse predicate state-independent (compare only
   state-invariant sources or capture baseline from clean state); add the
   e2e benchmark (bounded) to permanent CI execution so reproducibility is
   continuously proven (blocker C).
5. **Actual Unit E consumption + changed-code-first seeds**: consume
   `repo_views` view functions instead of the reimplemented logic (one
   shared implementation); prioritize changed/implementation code paths
   ahead of control-plane/docs paths in seed selection (blocker E).
6. **Honest routing unknowns**: undetermined signals must be represented as
   unknown (and set ambiguity), never silently False (blocker E).
7. **Useful bounded advisory memory**: carry bounded digest content (e.g.
   the digest's bounded note/outcome/files summary) sufficient to be useful,
   still explicitly advisory and quarantine-honest (blocker E).
8. **Honest historical reconciliation**: a committed record stating what the
   M0-T075 e2e "no-worse" result actually demonstrated (dirty-state
   capture), analogous to the M0-T069 scope correction — no reopening of
   accepted records, no disputing what was true.

## 7. MANDATORY adversarial completion protocol (for D-019 and all future completions)

Completion claims are invalid unless ALL of the following hold:

- **Clean-checkout reproduction**: every documented command and benchmark
  result reproduced from a CLEAN clone/checkout of merged main, not from the
  development working tree.
- **Counterexamples hunted for every "every/never/atomic/same" claim**: each
  universal claim gets an explicit attempted counterexample, recorded.
- **Actual call-path verification**: "X consumes Y" requires tracing the real
  call path in code, not the presence of an importable module.
- **Every external argument tested**: each CLI argument that names a file or
  path is probed with absolute/traversal/link inputs.
- **Exact runbook commands**: every runbook line executed verbatim from the
  state a fresh operator would be in.
- **Committed AND uncommitted states**: every state-dependent behavior
  (diff, projection, benchmark) proven in both.
- **Every known observation attacked**: each recorded non-blocking
  observation from prior reviews is either fixed, refuted, or explicitly
  re-accepted with reasoning — never silently carried.
- **Independent-reviewer probes must be NEW**: reviewers must construct
  probes not copied from the producer's tests.
- **No proxy metrics**: byte-identity, test counts, or exit codes never
  substitute for the semantic claim they are meant to evidence.

## 8. Protected and forbidden surfaces (absolute, unchanged)

- `tools/agent_supervisor/**` (all supervisor code and tests)
- Protected controller config (`config.toml`, sha256 prefix `6aef12a9…`)
- `model_selection.toml` (sha256 prefix `0e2432c0…`)
- `apps/`, `services/`, `packages/`, `supabase/` — NYC application logic,
  zoning/calculation logic (hermetic temp-dir test fixtures only, and only
  where genuinely required)
- Branch protection and required CI checks; security policy; dependency
  gates
- limited-auto state (stays disabled)
- Git history (no rewriting, no force-push, no reset/clean)
- Live probes and controller activation (owner-present only)
- D-013-R060 promotion state (owner decision only)

## 9. New-session startup instructions

1. Read THIS ENTIRE FILE first.
2. Reconcile live before anything else (read-only):
   `cd C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t064`
   `git fetch origin && git status --short && git rev-parse HEAD origin/main`
   `python tools/project_control.py status`
   Expect: clean tree, origin/main `3c10894…` (or a NEWER sha — if newer,
   read the intervening merges before acting), 98 accepted, M0-T076/D-019
   unused, no overlapping open PR. If reality diverges from this file, TRUST
   THE REPOSITORY and surface the difference before acting.
3. Then execute ONLY the bounded master prompt supplied by the owner for
   D-019/M0-T076. Do not begin implementation from this handoff alone; this
   file is orientation and scope, not authorization. Capture the owner's
   prompt as directive D-019 verbatim when it arrives (per D-001), create
   M0-T076 with a full claim-time contract, and follow the standard
   lifecycle: G0 → implement → submit at a frozen SHA → fresh independent
   review (with NEW adversarial probes per section 7) → gates → independent
   verification → accept → merge on green.
4. Honor every prohibition in sections 5 and 8 without exception.

— End of handoff —
