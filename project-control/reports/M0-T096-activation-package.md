# M0-T096 — Owner activation package (D-024 section 20, items 1–14)

**ACTIVATION STATE: DEFAULT-OFF. Nothing in this package activates anything.**
Continuous mode stays DISABLED after the golden run (D-024-R187); live automated
actuation additionally sits behind the R595 owner path. This package is the
section-20 handoff the owner reads AT the activation decision — it grants
nothing by existing. Recorded by the orchestrator at unit-I delivery
(deliverable identity `5ff7f08`; gate/DCV identities in item 11).

**Current sequencing (Amendments 13+14, D-024-R277–R297; supersedes the
Amendment-12 note that stood here through M0-T116):** the Amendment-12 window
completed (M0-T115 + M0-T114 + M0-T116 accepted), but the R276 resume then
STOPPED at preflight step 5 on **provider CLI drift** — Claude Code had
auto-updated 2.1.248 → 2.1.251 after activation. The owner authorized a
**deliberate admission event** (Amendment 13) and, mid-window, the
**shell-routing reconciliation** (Amendment 14): **M0-T117** (forced
`DISABLE_AUTOUPDATER=1` at all four supervisor-constructed claude env seams +
owner machine-scope belt — accepted), **M0-T118** (the 2.1.251 measured
fixture pack; drift teeth green; +2 hook events PreModelSwitch/PostModelSwitch
recorded — accepted), **M0-T120** (empirical native-routing proof under the
exact controller construction; native Read/Grep/Glob/Edit/Write worker
guidance; a pre-dispatch shell-routing drift tooth GATING certified starts —
accepted). **M0-T119 re-ran the golden certification at the ONE post-admission
frozen identity and refreshed items 10–12 below**
(`M0-T119-recertification.md`), recording **Claude Code 2.1.251 as the
ADMITTED provider CLI** per the full R282 pass list. The remaining gate is
the **R276 RESUME, rerun FROM THE BEGINNING (R284)**: only once M0-T119 is
ACCEPTED through its gates AND the complete activation preflight passes again
does the certified start re-run — carrying the authorized ONE-TIME
`--repin-cli-identity` with executable-digest verification (R285). On any
failure the loop stays stopped. Standing forever after (R286/R287): future
Claude Code upgrades are deliberate admission events — update intentionally,
recapture, recertify, only then repin; never silent drift. Nothing in this
package activates or resumes anything by existing.

## 1. What was implemented (plain language)

A supervisor that can run an engineering campaign as a loop: Codex (an external
read-only reviewer process) reads the durable campaign record and selects the
next bounded task; Fable/Claude Code produces the work in a bounded unit;
checkpoints, evidence packets, and independent review run; state advances
durably (SQLite journal + hash-chained audit log, both outside the repository);
the campaign continues to the next unit. Every dangerous surface fails closed:
prompts are digest-bound, effects are exactly-once, session rotation happens
only at safe seams, crashes reconcile instead of repeating, quota exhaustion
and guardrail refusals are classified fail-closed and recorded rather than
worked around. Unit I proved the whole loop end to end: a two-unit golden run
from the exact owner command, crossing one safe session rotation and one
injected controller restart, with injected refusal/quota/fallback/
ambiguous-effect faults — all deterministic and INJECTED (lane 1, Amendment 7);
plus the passive natural-event watcher and its `pending_live_observation`
register (lane 2).

## 2. What was reused from the prior system

Everything below unit I is the accepted prior system, unchanged: the Phase 1–4
supervisor core (journal/audit/state machine/policy/broker/runner/reviewer/
evidence/rotation/recovery/locking), the D-024 units A–H2 (telemetry, bounded
subagent contracts, safe seams + exact-once succession, guardrail-refusal
classification + bounded 4.8 bridge, operator channel, root-cause repair gate +
GitHub-effect discipline), and the Amendment-3 native-runtime adapters. Unit I
added ONLY: the golden-run harness + fault injection (`golden_run.py`), the
watcher/register (`live_observation.py`), the `start` wiring that constructs
the accepted H1 refusal seam (a discovered integration gap), and the 40-test
golden-run pack with its executable prove-first registers.

## 3. Start the agent loop (exact command)

```
python -m tools.agent_supervisor start
```

Run from the repository root. Idempotent; no duration parameter exists. To
DISPATCH, every input is named explicitly (`start` refuses with the exact
missing flags otherwise):

```
python -m tools.agent_supervisor start --mode shadow ^
  --claude-executable <path> --codex-executable <path> ^
  --task-packet project-control/tasks/<id>.json ^
  --config <path>\config.toml --model-selection <path>\model_selection.toml ^
  --manifest <recorded controller_manifest.json>
```

Modes: `shadow` (forwards nothing), `supervised` (every prompt held for your
digest-bound approval), `limited-auto` (REFUSED by name unless the explicit
per-launch `--owner-enable-bounded-auto` is present — and enabling it live is
the R595-gated owner act this package does NOT perform).

## 4. Operator commands (exact)

* Status (no model call): `python -m tools.agent_supervisor status` (`--json`
  verbose) · campaign NEXT: `python -m tools.agent_supervisor.campaign_continuity --status`
* Ask Codex (read-only): `python -m tools.agent_supervisor ask "<question>"
  --codex-executable <path> --config <path> --model-selection <path>` · after a
  timeout: `ask --show <id>` / `ask --resubmit <id> ...`
* Pause / resume: `python -m tools.agent_supervisor pause` / `resume`
* Graceful stop (land the unit, then stop):
  `python -m tools.agent_supervisor graceful-stop --reason "<why>"` · clear:
  `graceful-stop --clear`
* Hard stop / emergency: `python -m tools.agent_supervisor stop` ·
  `emergency-stop` · clear: `stop --clear`
* In the Claude Code terminal: `/loop-start /loop-status /loop-tasks /loop-ask
  /loop-pause /loop-resume /loop-stop /loop-emergency-stop`.

## 5. Pre-model slash interception (installed-version truth)

On the installed CLI the hook path is **UserPromptSubmit** (fixture
`loop_interception_detection_2_1_251.json` — payload inherited from the
2.1.248 measurement with event-set membership re-verified at 2.1.251, per its
`payload_lineage`); UserPromptExpansion's response
contract is UNPROVEN and is passed through unchanged, never faked. The
zero-context proof remains **pending-owner-C1**: until that owner-gated live
canary runs, the SECOND TERMINAL commands in item 4 are the authoritative
zero-context real-time path — this is the documented truthful fallback, not a
gap being hidden.

## 6. Workload sizing + context-health policy (active)

Structural sizing is the primary prevention: vague/oversized assignments are
rejected or split before dispatch; tiny work stays in the main session; healthy
subagents are resumed rather than respawned; more than three concurrent
producers are refused; overlapping write scopes cannot both hold leases.
Context health is watched from OUTSIDE via passive telemetry with explicit
source/confidence labels (unknown is never zero); private bands flag rotation
at the NEXT seam and can never interrupt a running unit. **Workers never
receive token quotas, targets, percentages, or countdowns** — enforced by
`assert_worker_text_clean` and proven by tests (R045/R184).

## 7. Oversized or drifting subagents

Scope drift produces a typed extension REQUEST (approve/deny by the
supervisor, never a silent continuation); unrelated discoveries enter the
backlog without expanding the active contract; blocking discoveries request
the least costly bounded extension. No-progress patterns pause structurally.
`TaskStop` is reserved for emergencies; hard ceilings are catastrophic
backstops, not routine sizing. Verbose child transcripts are summarized under
a hard character bound — never dumped into the parent context.

## 8. The 4.8 bridge and Fable re-entry (fail-safe posture)

A unit that ends without a checkpoint is classified fail-closed: the quota
policy evaluates FIRST (detect-and-hold; weekly-limit evidence only — a bare
429 never qualifies); only a narrowly recognized typed refusal shape enters
the refusal seam, which on this build RECORDS INTENT ONLY and pauses safely.
Live actuation of the continue-with-4.8 choice is double-gated by
`assert_actuation_permitted`: it requires a **measured-live** refusal-shape
corpus (today: `verified_live=false`, documentation-confidence — asserted by
test) AND the R595 owner authorization — both absent, both proven to refuse
independently. Re-entry to Fable 5 is digest-bound with a TWO-attempt cap that
survives restart; two refusals of the same request escalate to the configured
blocked behavior. The next task returns to the pinned model at the seam.

## 9. Root-cause replacement enforcement

The accepted H2 repair gate: every defect fix passes the 8-predicate
RepairRecord gate (wrapper-around-defective-path rejected; stale callers
caught by search/graph; regression test must fail if the fix is removed;
compatibility exceptions need owner + expiry + removal task, and an EXPIRED
exception blocks acceptance) plus the closed 6-question checkpoint with a
never-auto-accept disposition.

## 10. Identity and evidence (FIFTH refresh at M0-T124 — the post-resume-path certified identity)

* **CURRENT (fifth) certified identity:** supervisor material last moved at **`16e1b3b`**
  (accepted M0-T123 `6aada29`+`16e1b3b` — the launch/resume enforcement seam
  `launch_seam.py`: unconditional 400k rotation-ceiling + packet-worktree cwd binding at
  every worker path pre-provider, with the pre-first-dispatch shed and the site-granular
  bypass-sensitive sweep); `tools/agent_supervisor` tree
  **`a72a53b8c4f560c90dabbf65cb75478fef37ce43`**; golden pack blob `c54fd0d2` (42 tests,
  byte-identical since T119); launch-seam pack blob `1a77b904` (64 tests); restart-channel
  pack unchanged (34). **CLI: Claude Code 2.1.251 UNCHANGED** (digest recomputed at recert
  = `d6f6c29a8ac6b3cf…` exactly; codex-cli 0.146.0; no admission event, no repin).
* Fifth-recert evidence (M0-T124): WHOLE suite **2,889 passed, 2 skipped, 0 failed** (TWO
  independent full runs; chain 2,814 + 56 + 19); controller manifest re-recorded **121
  files** digest `47293127…` config-bound; verify-controller PASS; doctor overall PASS
  (journal preserved at PAUSED_RECOVERY, transitions 18, audit 43 verified, OS-ACL
  PROTECTED); drift tooth green. The journal's documented recovery path from the
  preserved S14 stop is `clear-recovery` (PAUSED_RECOVERY → PREFLIGHT); the R316
  one-attempt authorization is CONSUMED — any further live attempt is a NEW owner
  decision (R347; the presented package is in `M0-T124-recertification.md` §4). Full
  detail: `M0-T124-recertification.md`.

## 10-prior. Identity and evidence (fourth refresh at M0-T122 — the post-restart-channel certified identity)

* Branch: `control/D-024-fable-codex-loop`. **FINAL frozen post-restart-channel
  identity:** supervisor material identity last moved at **`668c824`**
  (the M0-T119-certified post-admission system at `7d8195b`, plus accepted
  M0-T121 `668c824`+`6432d2d` — the audited fail-closed operator recovery
  surfaces `owner-restart` / `acknowledge-emergency-stop` /
  `resume-after-answer` closing the complete F-2 edge class, with the
  edge-granular removal-sensitive reachability sweep);
  `tools/agent_supervisor` tree `d3db9f3c7ee66ff36c44d518e6177c5a39378e4a`;
  golden pack blob `c54fd0d2` (**42 tests — byte-identical to the M0-T119
  certification, carried un-weakened**); restart-channel pack blob
  `d3e23087` (**34 tests**).
  **ADMITTED provider CLI: Claude Code 2.1.251 UNCHANGED** (executable digest
  re-computed at recert = `d6f6c29a8ac6b3cf…` exactly; codex-cli 0.146.0
  unchanged; NO repin — the one-time R285 repin is consumed and the identity
  is undrifted).
* Re-certification evidence at that identity (M0-T122): WHOLE supervisor
  suite **2,814 passed, 2 skipped, 0 failed** (exact chain: 2,780 M0-T119
  baseline + 34 M0-T121; pre-delta cross-check 2,811 = 2,780+31 measured the
  same session); drift tooth `test_s8` green at 2.1.251. Controller manifest
  re-recorded at the final tree: **120 files**, digest `7f9991cb…`, config
  bound, round-trip verified; verify-controller PASS; doctor overall PASS
  (journal HALTED at rest, audit chain 33 verified, OS-ACL PROTECTED). The
  restored HALTED restart path is the NEW certified `owner-restart` operator
  surface (M0-T121). Full detail: `M0-T122-recertification.md` (prior cycles:
  `M0-T119-recertification.md`, `M0-T116-recertification.md`,
  `M0-T112-recertification.md`). CI on the pushed certification tip is the
  confirming whole-suite run (20/20; SHA pinned in the M0-T122 progress_log).
* PR/check links: the campaign branch pushes run the standard 20-check CI; the
  supervisor-bridge job is the whole-suite confirmation.

## 11. Independent review verdicts (third refresh at M0-T119)

Each unit carries its own 4-reviewer wave (G3 code-reviewer, G4 qa-engineer,
G5 security-reviewer, DCV directive-compliance-verifier) against ONE frozen
identity: unit I (`M0-T096-*`), unit K (`M0-T110-*`, DCV 13/13), unit L
(`M0-T111-*`, DCV 10/10), the first re-certification (`M0-T112-*`, DCV 6/6),
the seam repair (`M0-T115-*`, DCV 3/3 — one G3 BLOCKER correction round, four
delta-PASS attestations), the residual fixes (`M0-T114-*`, DCV 3/3), the
second re-certification (`M0-T116-*`), the autoupdater control (`M0-T117-*`,
DCV 7/7 — one consolidated G3-FAIL round closed two uncovered claude launch
seams, then three delta-PASS attestations), the 2.1.251 fixture recapture
(`M0-T118-*`, DCV 5/5, zero-blocking wave), the shell-routing unit
(`M0-T120-*`, DCV 8/8, zero-blocking wave; the limited-auto mode-scoping of
the routing gate was independently adjudicated as satisfying R295 by G3, G5,
AND the DCV), and the third re-certification itself (`M0-T119-*`, recorded at
its gate wave — the acceptance the R276 RERUN waits on). A later identity
change invalidates the affected verdicts (rework→resubmit; R247 re-triggers
re-certification).

## 12. Golden-run evidence (the observed complete loop)

`test_the_two_unit_golden_run_crosses_a_rotation_with_no_human_step`: ONE
invocation of the exact `start` command (item 3 shape, limited-auto with the
explicit per-launch enable inside a disposable checkout) ran unit A (a REAL
git commit on the non-protected task branch), crossed the context threshold,
rotated at the safe seam, verified the READY successor, ran unit B (second
real commit) — three launches, zero human continuation, exactly-once forwards,
no pending effects. `..._injected_controller_restart_continues_without_
duplicate_work`: the SAME command re-run after a controller death resumed
exactly-once (unit A never re-ran). Injected refusal, quota, fallback and
ambiguous-effect scenarios each held fail-closed. Full detail:
`project-control/reports/M0-T096-golden-run-evidence.md` §4. **All INJECTED
(lane 1). The natural-event lane stays `pending_live_observation`** — it gates
ONLY the automatic 4.8 bridge's live actuation (item 8), nothing else (R228).
**Refreshed at M0-T112:** the identical 40-test pack was re-run 40/40 at the
FINAL frozen post-addition identity (item 10) — the observed complete loop,
rotation crossing, restart resume, and fail-closed fault scenarios all hold
with the accepted Codex-channel and Telegram-sink additions in place
(`M0-T112-recertification.md` §3).
**Second refresh at M0-T116:** after the first live limited-auto run exposed
and the certified process repaired the deny→restart seam defect (M0-T115) and
the carried residuals (M0-T114), the pack (now 41 tests) was re-run **41/41**
at the post-repair identity — the certified scenarios are byte-unchanged and
all hold; the live run's fail-closed stop itself validated the design (ASK
never AUTO; a missing checkpoint never read as success). Resume of the
authorized loop is gated on M0-T116 acceptance + the full R276 preflight
(`M0-T116-recertification.md`).
**Third refresh at M0-T119:** after the R276 resume stopped fail-closed on
the 2.1.248→2.1.251 provider-CLI drift, the owner-authorized admission window
landed (M0-T117 autoupdater control, M0-T118 fixture recapture, M0-T120
shell-routing unit — all accepted), and the pack (now **42 tests**, the 41
certified scenarios plus M0-T120's routing tooth-bite) was re-run **42/42**
at the post-admission identity. The loop's observed complete run, rotation
crossing, restart resume, and fail-closed fault scenarios all hold on the
ADMITTED 2.1.251 CLI under the new drift-proof controls — and the certified
start is now additionally gated by the pre-dispatch shell-routing tooth
(a certified start without current routing evidence for the pinned executable
digest refuses UNSAFE_OR_DRIFTED before any provider contact). The measured
routing fixture shows the 2.1.251 worker prefers NATIVE tools (Grep/Read/Edit,
zero shell) under the exact controller construction. The resume rerun is
gated on M0-T119 acceptance + the full R276 preflight, and its certified
start carries the one-time `--repin-cli-identity`
(`M0-T119-recertification.md`).

## 13. Clean-session launch (proven shape)

Launch Claude Code with its primary cwd AT the repository root
(`C:\Users\MLFLL\Downloads\nyc-zoning\ctl24`): `cd <repo-root> && claude`.
Bootstrap Gate 0 (R125–R128) must pass before any write: primary cwd IS the
worktree root and `/mcp` reports NO servers (this session's effective MCP list:
empty — verified at unit-I claim, `M0-T096-G0-readiness.md`). An added
directory or absolute path does NOT satisfy the gate.

## 14. Host-restart behavior + remaining owner steps

* **Host restart:** the autostart mechanism is BUILT and owner-gated: 
  `autostart-plan` shows the exact one wake task + logon task (fixed launcher,
  fixed argv — a model can never change the command); `install-autostart`
  refuses without your plan digest. Until you install it, the truthful
  statement is: **the loop is NOT fully unattended across a reboot; the same
  one-command `start` resumes the exact campaign after logon** — reported as
  an activation consideration, not hidden (R031/R032). Software can never
  power the machine on; a logon task resumes at next sign-in.
* **Remaining owner-only steps (each a separate explicit act):**
  1. R187/R595 continuous-mode activation decision (this package's subject).
  2. `install-autostart --confirm-plan-digest <digest>` if unattended
     host-restart resume is wanted.
  3. The pending-owner-C1 live interception canary (zero-context proof).
  4. The natural-event graduation path: when a genuine Fable 5 refusal/quota/
     model-turnover event is observed by the passive watcher, review the
     `pending_live_observation` register row, compare with the injected proof
     (R227), and — only then, and only by your act — graduate the refusal-shape
     corpus via its fixture `upgrade_procedure`. Until then the 4.8 bridge
     stays shadow-only fail-safe.
  5. Controller-config OS-ACL hardening (`harden_controller_config.ps1`, UAC)
     if the manifest-detection posture is deemed insufficient at activation.

**No genuine blocker exists for the golden-run readiness claim itself; every
item above is an owner decision, not undocumented manual repair.**
