# M0-T102 — D-024 Amendment 3 unit A: native capability re-baseline (initial owner report, D-024-R190)

Producer: orchestrator (Fable 5), session `session_01HfptKuEs3RDxaxsSHJjc7t`, 2026-08-26 UTC.
Task: M0-T102 (cites `D-024:ALL; D-030:ALL`; discharges D-030 at acceptance). No runtime
implementation was changed by this task (R190/R191 ordering honored).

Companion artifacts (this task's outputs):
- `M0-T102-native-reuse-matrix.json` — machine-readable matrix, 29 areas, **147 requirement IDs
  mapped** (coverage machine-asserted against the resolver-derived applicable sets).
- `M0-T102-docs-snapshot/` — 16/16 official pages, fetch-dated 2026-08-26, masked.
- `tools/agent_supervisor/fixtures/capability_probe_live_2026-08-26.json` — fresh live probe.
- `M0-T102-capture-verification.md` — independent capture verification (PASS, 6/6 checks).

---

## 1. Reconciled repository and campaign identity

Root `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24`; branch `control/D-024-fable-codex-loop`;
reconciliation HEAD `05d03a0` == origin tip, tree clean, `/mcp` = no servers (owner-run);
capture commit `0cc1c62`; evidence commits `85df434`, `e8abe3b`. Ledger: 113 accepted;
M0-T091 accepted/pushed/clean at seam `b2e3b2c` (checkpoint CP-D024-M0-T091); campaign seq 9;
M0-T092..T096 backlog and claim-HELD (R139); M0-T080 is the D-023 lane, disjoint. No conflicting
writer lease/worktree/shell/uncommitted state. READY TO CAPTURE was reported before any write
(R141/R142 discharged).

## 2. Current and target Claude Code versions

- **Installed (live-probed 2026-08-26):** claude `2.1.220`, codex `0.146.0` — byte-identical to the
  2026-08-25 M0-T086 baseline (no installed drift; D-030/D-024-R001 drift-absence proven live).
- **Current official stable:** claude **`2.1.246`** (released 2026-08-25; changelog snapshot with
  verbatim entries 2.1.220→2.1.246). Versions 2.1.244/2.1.242/2.1.230 were never published on the
  page. The upgrade is materially needed: `/goal` background check-ins (2.1.234+) and idle
  check-ins (2.1.236+), `/autocompact` (2.1.221+), `promptCacheTtl`/`subagentPromptCacheTtl`
  (2.1.243+), and three Windows background-session fixes (2.1.246) are absent on 2.1.220.

## 3. Completed native-reuse matrix

`M0-T102-native-reuse-matrix.json`. Decision distribution over the 147 remaining requirements:
**NATIVE WRAPPED 31 · CUSTOM REQUIRED 110 · OPTIONAL ENHANCEMENT 3 · REJECTED/DEFERRED 3.**
No NATIVE REPLACEMENT was awarded: every native adoption still needs D-024 durable state, policy,
verification, or recovery, so the honest maximum is NATIVE WRAPPED (rationale in the matrix).
Headline decisions:

| Native capability | Decision | Key evidence/caveat |
|---|---|---|
| `/goal` | NATIVE WRAPPED (unit E inner continuation, one bounded assignment) | full contract needs 2.1.246; evaluator is a Stop-hook wrapper; 4 goal-clearing error classes documented |
| Background sessions / Agent View | NATIVE WRAPPED — preferred producer host **candidate** | research preview → feature-detected fallback to existing controller; local-only; shutdown kills sessions; Windows fixes only in 2.1.246 |
| `agents --json`, stream-json, forward-subagent-text, hooks events | NATIVE WRAPPED (Codex-side passive observation + event bus) | all 17 required hook events exist (31-event set); forwarding gates 2.1.211/2.1.219 |
| Native worktrees | NATIVE WRAPPED (physical isolation) | logical leases/frozen-identity/branch policy RETAINED; `baseRef` default branches from the DEFAULT branch — pin `"head"` or reset (known hazard) |
| Skills + UserPromptExpansion (`/loop-*`) | NATIVE WRAPPED | `disable-model-invocation: true` confirmed; zero-model-context proof still requires a live fixture, else honest second-terminal fallback |
| Session naming/deterministic IDs/resume | NATIVE WRAPPED | `--session-id` must be UUID; native resume is NOT a seam substitute (R160) |
| Dynamic workflows; native reviews (`/code-review`, `/simplify`…); portability plugin | OPTIONAL ENHANCEMENT | bounded fan-out / gate-evidence supplements / post-golden-run only |
| Cross-session messaging + Remote Control; fallbackModel-as-refusal-policy; top-level-loop list | REJECTED OR DEFERRED | delivery not guaranteed; RC stores transcript server-side while connected (owner security review first); R165/R166 |

## 4. Which unstarted D-024 tasks change (surgical, applied after this task's acceptance)

- **M0-T092 (unit F)**: gains dependencies M0-T103/T104/T105/T106; producer host + session
  identity + event feeds consumed from units C/D/E; scope text updated accordingly. Rows
  R172/R173/R174+R152/R179 restamped to M0-T104/M0-T105/M0-T106/M0-T107 at packet creation.
- **M0-T093 (unit H1, refusal bridge)**: scope unchanged; R165 (fallbackModel prohibition) already bound.
- **M0-T094 (unit G)**: re-scoped to the skills + UserPromptExpansion surface (R158/R159 bound).
- **M0-T095 (unit H2, repair gate + GitHub exact-once)**: scope unchanged.
- **M0-T096 (unit I)**: golden run extended to the amendment's 15-step sequence (R186) and
  upgrade-regression canaries.
- **New packets**: M0-T104 (unit C adapter), M0-T105 (unit D events), M0-T106 (unit E `/goal`),
  M0-T107 (unit J portability plan, post-golden-run, non-blocking), M0-T108 (control-plane fix:
  close the readonly-guard PowerShell write gap — see §11 flags).

## 5. Which accepted components remain untouched

All of them (R144 "do not discard accepted work"): M0-T086 capability baseline; M0-T087
bootstrap/continuity; M0-T088/M0-T089 telemetry (statusLine/subagentStatusLine — explicitly
RETAINED per R162); M0-T090 bounded contracts; M0-T091 runtime supervision (lease_runtime,
runtime_health, runtime_detectors, extension_gate, child_handoff); M0-T097..T101; the D-007 Codex
bridge; the D-010 supervisor (frozen, shadow-only); graph/context-pack system; suite baseline
2707/3/0. Nothing is deleted on documentation claims alone (R181).

## 6. What native features replace custom work (as wrapped primitives)

Process hosting/dispatch of producers (background sessions + daemon restart semantics, replacing a
planned custom spawn/watchdog host in M0-T092's scope — after parity+failure canaries); status
ingestion (`agents --json`, stream-json, hook events — replacing any transcript polling); physical
worktree isolation; session identity/naming/resume primitives; inner turn-continuation for one
bounded assignment (`/goal` — replacing a custom inner prompter); the operator command surface
(skills + UserPromptExpansion — replacing a parallel CLI); the binary updater (official
`claude update`/`install` with documented rollback). Each replacement follows R180: prove native →
one bounded adapter → parity/failure tests → one active backend → separate reviewed removal →
rollback kept only for supervised rollout.

## 7. What remains custom

The full amendment must-remain-custom list (R164), concretely: Codex independent review +
next-task decision; durable campaign sequencing; requirement traceability; frozen Git identities;
exact-once GitHub/external effects; owner gates and pending approvals; safe-seam turnover;
overlap/lease detection; graph + bounded context packs; ambiguous-effect recovery; refusal
classification + the approved Fable-to-4.8 seam policy; quota detect-and-hold; security controls +
MCP default-deny; root-cause replace-not-layer enforcement; the controller state machine, health
bands, and workload supervision policy (110 of 147 requirement rows).

## 8. Revised task sequence (dependency-ordered)

**M0-T102 (A, this task) → M0-T103 (B: upgrade 2.1.220→2.1.246 + dual-version masked probes) →
M0-T104 (C: native runtime adapter) → M0-T105 (D: native event integration) → M0-T106 (E: bounded
/goal) → M0-T092 (F: controller/seams/succession, re-scoped) → M0-T094 (G: operator skills +
UserPromptExpansion) → M0-T093 (H1: refusal bridge) → M0-T095 (H2: repair gate + GitHub
exact-once) → M0-T096 (I: shadow/supervised/crash canaries + golden run) → M0-T107 (J:
portability plan, non-blocking).** M0-T108 (guard fix) can run at any seam as an independent
control-plane task. One cohesive writer task at a time (R188); M0-T092..T096 claims stay HELD
until this conversion is accepted and applied (R139).

## 9. Upgrade and rollback plan (unit B, M0-T103; R167/R168)

Pre-update: record version, binary identity (incl. the dual-install PATH note: `~/.local/bin`
resolves first, npm shim second), supported commands/help, settings, capability fixtures; confirm
official stable (this snapshot); worktree clean + capture pushed; verify no unrelated Claude
session would be disrupted (owner's other sessions checked at execution; background daemon
`claude daemon status`). Update via **official updater only** (`claude update`). Post-update:
record new identity; the running session stays on the old binary → all canaries run as disposable
child launches on the new binary (with `--strict-mcp-config` clean-launch); re-run Bootstrap
Gate 0, MCP default-deny, settings validation, statusLine, skills, hooks, accepted fixtures.
Rollback: `claude install 2.1.220` (documented supported path); any regression is recorded, never
silently worked around; if no supported safe rollback exists → stop for the owner. The new runtime
backend is NOT activated merely because the version command succeeds.

## 10. Test and golden-run plan

Per-unit acceptance-scenario packs using deterministic fixtures, accelerated counters, simulated
failures, disposable branches/worktrees, and real low-risk canaries (R182) — no token-burning
threshold proofs. The 26 required proofs (R183–R185) are allocated across units B–I in the matrix
(`evidence_plan` per area), including: Windows-native + exact installed-version behavior; MCP
default-deny; statusline leak-freedom re-proof post-upgrade; background dispatch lifecycle +
supervisor-restart no-duplicate + unexpected exit; worktree lifecycle; `/goal` six behaviors;
hook order/blocking; UserPromptExpansion zero-context proof or truthful fallback; no polling into
Fable context; no worker token quotas; overlap rejection; seam rotation; handoff boundedness +
successor reconstruction; refusal-vs-quota distinctness; GitHub exact-once + both crash windows;
stale ledger/handoff reconciliation; graph regression; suite stays green (2707/3/0 baseline);
independent security/QA/control-plane/DCV at the same frozen identity; mutation teeth on the
important gates. Golden run (M0-T096) executes the amendment's 15-step sequence from the exact
owner start command; **continuous mode stays disabled after it until you explicitly authorize
activation (R187; §18/R595 unchanged).**

## 11. True owner decisions required

**None to proceed** — the amendment already authorizes the campaign through the golden run, and
this report + amendment are recorded and independently verified (R191), so the campaign continues
automatically. Informational flags (no action needed now):
1. **Guard gap (will be fixed as M0-T108):** `readonly_agent_guard.py` does not intercept
   PowerShell writes; two read-only-typed agents wrote their snapshot files that way (disclosed;
   content reviewed, masked, ratified). Until fixed, the orchestrator treats PowerShell as a write
   surface in dispatch prompts.
2. **Remote Control** stays deferred: while connected, session transcripts are stored on Anthropic
   servers — it will only be proposed after a dedicated security review if you ever want it.
3. Standing items unchanged: PR #241 never merged; FIVE stale pack-repo agent worktrees still
   await your purge; continuous-mode activation remains owner-gated.

---

## Capability-matrix v1 delta record (D-030 discharge evidence)

`capability_matrix_v1.json` re-verified row-by-row against the 2026-08-26 snapshot + fresh probe:
**no contradicted claim; installed versions unchanged.** New facts recorded in the matrix
(`capability_matrix_v1_delta`): official stable 2.1.246; ten previously-unsnapshotted doc pages now
durable; `/goal` check-in and `/autocompact` version gates put key features BEYOND installed
2.1.220; `hooks.live_behavior_fixtures` stays honestly `unknown` pending unit B/D/G live fixtures
on the upgraded binary.
