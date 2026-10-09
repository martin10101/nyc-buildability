<!-- Committed by the orchestrator from the D-091 wave-3 design robot (cloud-architect, 2026-10-02). The ledger, not this file, holds task state. -->
# D-091 wave-3 wiring plan — connect the built dual-review + Linux parts into the loop

Scope: owner directive D-091 (cloud loop + Codex/Claude dual review + combiner), wave 3 =
WIRING the pieces M0-T165..T170 built but left unwired. Design only; no ledger writes, no
edits. Read against `origin/candidate/D-024-mrl-option-b` (merged) + branches
`origin/task/M0-T166-linux-launcher`, `origin/task/M0-T169-review-combiner`.
Server: Ubuntu 4 CPU / 8 GiB, Python 3.12; installed `claude 2.1.287`, `codex 0.157.0`.
Plain words; every claim carries file:line evidence.

The parts exist and are DEFAULT-OFF and UNWIRED on purpose:
- Claude reviewer: `claude_reviewer.py:410` `ClaudeReviewer`, switch `:395` default `False` (`:354`).
- Combiner: `review_combiner.py:475`, switch `:459` default `False` (`:423`); model required, no
  default (`:512`, D-091-R008). A raised reviewer launch exception already becomes a non-PASS
  `unverified_outcome` (`review_combiner.py:108`) — M0-T168 N1 satisfied.
- Linux memory gauge: `resource_sampling.py:284` `linux_memory_gauge_sample`, ceiling
  `:219` `resolve_memory_ceiling_bytes` (70% of /proc/meminfo, `:147`).
- Admission cap: `run_budget.py:793` `admit_review_or_combine` (pure/stateless, `:744`); config
  caps already present `config.example.toml:137-138`.
- Linux launch path: `launch_seam.py:435` `select_launch_path("posix")`, artifacts under
  `tools/agent_supervisor/linux/` (M0-T166 branch).

---

## 1. WIRING — where each piece plugs in, behind default-off switches

**Single review today.** The loop's per-cycle worker review is one injected reviewer:
`loop.py:590` constructor param `reviewer`, called ONCE at `loop.py:2041`
`self.reviewer.review(packet.to_dict(), expected_task_id=..., expected_checkpoint_id=...)`,
returning a `ReviewOutcome` whose `outcome.decision` (a `CodexDecision`) the loop routes on at
`loop.py:2068,2079`. The gate stage reuses this via `ephemeral_review.conduct_ephemeral_review`
(`gate_wave.py:43`).

**Dual review + combiner = a conductor behind the single-reviewer seam (no loop rewrite).**
Add a NEW module `dual_review.py` exposing the SAME `.review(packet, expected_task_id,
expected_checkpoint_id) -> ReviewOutcome` shape the loop already calls. When both switches are
off it is never built and `loop.py:2041` keeps the single Codex reviewer byte-for-byte. When on,
the conductor, at the one frozen head the loop already froze (`loop.py:2006-2012`, packet carries
`git.head`, see `claude_reviewer.py:183`):
1. runs the existing Codex reviewer and a fresh `ClaudeReviewer` on the SAME packet (independence:
   `claude_reviewer.py:235` refuses a packet carrying a peer review; `:204` refuses an unfrozen
   head);
2. feeds both into `ReviewCombiner.combine(...)` (`review_combiner.py:499`);
3. projects the combined verdict (`CombinedReview.verdict`, `review_combiner.py:298`) back into a
   `CodexDecision`-shaped `ReviewOutcome` so the loop's existing routing is unchanged — PASS→the
   worker's decision stands; FAIL→REVISE with the union `blocking_findings`; UNVERIFIED→the
   existing `not outcome.ok` unavailable path (`loop.py:2045`).
- N3 (M0-T169 G5): the conductor is the consumer — it treats the code-computed `verdict` (not model
  text) as authoritative and attaches `CombinedReview.disputed_findings` (`review_combiner.py:308`)
  so the human gate sees them.
- N1 (M0-T169 G5): the conductor resolves the reviewer model AND combiner model against the
  controller allowlists (`config.example.toml:30-34` `[claude] allowed_models`, `:24-28` `[codex]`)
  before building either — `ClaudeReviewer` already takes `allowed_models` (`claude_reviewer.py:424`);
  pass the combiner's model through the same check (the combiner has none today, N1).

**loop.py change is minimal** (it is ~2983 lines, a grandfathered file over HARD_SLOC 1000 —
`modularity_check.py:47`; material growth >50 lines fails CI, `:50`): add one constructor
param and swap the one call site to the injected conductor when present. All real logic lives in
the new `dual_review.py` (keep < WARN 600) and a new `review_slots.py` (below).

**Memory gauge → the existing resource gate.** `loop.py:841-859` `_check_resources` already
samples `self._resource_sampler.sample()` and trips `memory_bytes` against the breaker. Today the
stock sampler emits `memory_bytes` as structural-unknown (`resource_sampling.py:112`), so nothing
pauses on memory. Wiring: on POSIX, have the `ResourceSampler` emit
`linux_memory_gauge_sample()` (`resource_sampling.py:284`) in `sample()`, and at launch set
`max_memory_bytes` to `resolve_memory_ceiling_bytes(MemTotal)` (`:219`) in `cli.py`. No change to
`loop.py` or `circuit_breakers.py` — the unchanged gauge path then enforces the 70% pause
(config note `config.example.toml:109-117`).

**Admission cap → before each review/combine spawn, atomically.** The conductor calls
`admit_review_or_combine(...)` (`run_budget.py:793`) before launching each Codex-review,
Claude-review, or combiner process; `admitted=False` means WAIT, never over-subscribe. BUT the
function is pure/stateless and cannot stop two lanes both seeing a free slot (M0-T170 note 1).
Wiring MUST add an ATOMIC count-check-reserve: a new `review_slots.py` holding a file-lock-backed
counter in the shared runtime dir (`/var/lib/nyc-supervisor/`), reserve-before-spawn /
release-after-exit, fail-closed on an unreadable count. Caps come from immutable config
(`config.example.toml:137-138`), so no model can raise them.

**To the gates without the loop recording a gate (ADR-005).** The combined review stays ADVISORY
input, exactly like one reviewer today. The loop NEVER writes a gate. The orchestrator records
G3/G4/G5 from the combined review by hand; the managed verdict→gate recorder
(`gate_wave.py:15`, `CONTROL_PLANE_ALLOW_SET={gate,submit}` `:73`) stays DEFAULT-OFF / owner-gated
(R595), and G6 always parks for a human (`gate_wave.py:62`). Nothing here enlarges the loop's
control-plane authority.

---

## 2. RECERTIFICATION (design T3) — recapture on Linux after ALL code tasks

Every `tools/agent_supervisor/**` edit invalidates the frozen-identity cert, so recert runs LAST
(design doc header). The installed Linux CLIs differ from the committed Windows baseline, so the
live drift teeth WILL fail until recaptured:
- `test_agent_supervisor_capability_probe.py:188` live-reprobes `claude --version` and asserts it
  equals the committed current fixture "2.1.281 (Claude Code)" — installed is 2.1.287 → FAILS.
- `:224` live-reprobes `codex --version` vs "codex-cli 0.153.4" — installed is 0.157.0 → FAILS.
- The re-baseline invariant `test_current_fixture_records_claude_2_1_281_masked_and_shaped`
  (`:241`) pins those exact strings → must be updated to the new versions (same pattern M0-T159
  used for 2.1.281).

What to recapture, how: run `python -m tools.agent_supervisor.capability_probe` on this box to
freeze a new current fixture (claude 2.1.287 / codex 0.157.0, [HOME]-masked per `:218`); recapture
the shell-routing fixture (bash routing, `routing_probe.py` is platform-neutral) and the
native-runtime-detection fixture on Linux; run the bash shell-routing harness
(`bash tools/agent_supervisor/linux/sh_tests/run_sh_tests.sh`, Linux README); update the
re-baseline invariant test to the new versions; re-bind the controller manifest digest.

Orchestrator-executable HERE (all local, no provider call; cert is agent-executable per design
§7/D-017): the probe recapture, harness run, test update, manifest re-bind, cert report + evidence
map. Owner-typed (NOT agent): creating the root-owned `/etc/nyc-supervisor/config.toml` and the
systemd install (§3). Evidence that CLOSES it: the new fixtures committed, the two live-reprobe
tests GREEN on this box, the updated re-baseline test GREEN, the manifest digest resynced, and a
cert report under `project-control/reports/`. Resolves the two live-reprobe drift teeth + the
version-pinned re-baseline invariant.

---

## 3. COMMISSIONING (design T8) — owner checklist + orchestrator verification

Owner-typed steps (an agent never runs these); orchestrator verifies after each.

1. **Config file.** Copy `config.example.toml` to `/etc/nyc-supervisor/config.toml`, fill owner
   choices (`[claude] allowed_models`, `[codex] allowed_models`, `[approved_models] models`, and —
   when enabling — the combiner model). Make it root-owned, mode 0444, protected parent.
   → Orchestrator verifies: `posix_acl` verdict root-owned/0444 (M0-T165), config loads, manifest binds.
2. **Codex sign-in.** Owner runs `codex` "Sign in with ChatGPT" (or API key) once; credential lands
   in `~/.codex/`, outside the repo (design §3; reviewer passes `--ignore-user-config`).
   → Orchestrator verifies: `codex --version` = 0.157.0 and the read-only reviewer argv builds; the
   live provider round-trip is proven only by the supervised start (step 4).
3. **systemd unit.** Owner substitutes `<...>` in
   `tools/agent_supervisor/linux/nyc-supervisor.service.template`, installs it, `daemon-reload`,
   enable. Template ships with no `[Install]` and `Restart=no` so a stray enable has no target
   (Linux README).
   → Orchestrator verifies: unit carries `DISABLE_AUTOUPDATER=1`, points at the gated start, parses.
4. **Supervised start.** Owner approves the certified-start prompt-digest (supervised mode) and
   starts lane 1 as a canary.
   → Orchestrator verifies: the stored lane-1 canary evidence (gate passed, one clean cycle,
   memory under the 70% ceiling, admission cap honored).

---

## 4. TASK BREAKDOWN — disjoint paths, gates, reviewers, order

All M0-class controller work, cite `D-091`. Producers in isolated worktrees; orchestrator records
gates/merges (ADR-005). Disjoint `allowed_paths` so they can run in parallel where ordered so.

| T | Scope (allowed_paths) | Gates | Reviewers | Order | OD-B needed to ENABLE? |
|---|---|---|---|---|---|
| TW1 Atomic review-slot reservation | `tools/agent_supervisor/review_slots.py` + its test | G0,G2,G3,G4,G5 | code-reviewer, security-reviewer, control-plane-verifier | 1 | no (build + enable independent of model) |
| TW2 Dual-review conductor + loop seam | `tools/agent_supervisor/dual_review.py`, minimal `loop.py` inject, test; resolves models to allowlists (N1), sets verdict authoritative + surfaces disputes (N3), calls TW1 reserve | G0,G2,G3,G4,G5 | code-reviewer, security-reviewer, control-plane-verifier | 2 (after TW1) | YES — combiner refuses until model set |
| TW3 Linux resource wiring | `tools/agent_supervisor/resource_sampling.py` (POSIX sample branch), minimal `cli.py` (set `max_memory_bytes`=resolved ceiling; feed gauge), tests | G0,G2,G3,G4 | code-reviewer, ci-evidence-verifier | parallel to TW1/TW2 | no |
| TW4 Linux recertification | `tools/agent_supervisor/fixtures/**`, `tools/test_agent_supervisor_capability_probe.py`, manifest binding, cert report | G0,G2,G3,G4,G5 | control-plane-verifier, security-reviewer | AFTER TW1,TW2,TW3 | no |
| TW5 Commissioning + certified start | runbook/docs (Linux commissioning checklist), owner-typed start | certification evidence, lane-1 canary | control-plane-verifier (verify stored evidence) | last | YES (enabling the loop uses the combiner) |

Building proceeds with the combiner model UNSET: every switch is default-off and the combiner
refuses fail-closed at runtime until the owner sets a model (`review_combiner.py:512`), so TW1–TW4
can be built, reviewed, and merged now. Only ENABLING (flip `claude.reviewer_enabled`,
`review_combiner.enabled`, set the model) waits on OD-B — a config act at commissioning (TW5).

Modularity: `loop.py` (~2983), `gate_wave.py` (1099), `codex_reviewer.py` (982) are all at/over
HARD_SLOC 1000 (`modularity_check.py:47`) and grandfathered — keep edits to them UNDER the
>50-line/10% material-growth trip (`:50`). New logic goes in `dual_review.py` and `review_slots.py`
(each kept < WARN 600). TW2 touches `loop.py`; no other task does, so paths stay disjoint.

---

## 5. RISKS + smallest set of owner decisions

**Risks**
- 5 lanes / 8 GiB OOM from synchronized review+combine spikes — mitigated by the 70% memory pause
  (TW3) + the atomic cap of 2 concurrent review/combine across lanes (TW1,
  `config.example.toml:137`); if a non-atomic reservation shipped, two lanes could both admit → 3
  running (M0-T170 note 1) — TW1 closes it.
- Combiner/reviewer same provider (Opus reviewer + Opus combiner) — independence ceiling; mitigate
  with distinct Claude models for reviewer vs combiner (`claude_reviewer.py:360`) and the
  code-computed worst-of-two verdict a model can never weaken (`review_combiner.py:103,542`).
- Recert scope creep — any `tools/agent_supervisor/**` edit reinvalidates the cert, so TW4 runs
  strictly last and nothing merges into `agent_supervisor/**` after it without re-running it.
- Codex version churn — pin the newest stable ≥7 days at admission; re-verify flags on the
  installed 0.157.0 binary (M0-T167 already admitted it).
- B-026 honesty — the Linux loop does NOT close the PC-controller blocker; record only a scope note.

**Smallest set of owner decisions**
1. **OD-B (D-091-R008): combiner model.** Approve Opus 5.5 (design default) or Codex-higher-end;
   must be allowlisted and DIFFERENT from the Claude reviewer model. Needed only to ENABLE (TW2/TW5).
2. **OD-C: Codex sign-in** on the server, once, at commissioning (TW5 step 2).
3. **OD-D: B-026 disposition** — keep the PC loop (recommission later) or retire it for the cloud
   loop (the honest path to "resolving" R004).
4. **Root/commissioning acts:** root-own `/etc/nyc-supervisor/config.toml`; install+enable the
   systemd unit; approve the supervised certified-start + ongoing prompt-digest approvals.

(The move itself, R001, is already authorized by D-091.)
