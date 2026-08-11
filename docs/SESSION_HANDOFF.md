# Session Handoff — NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume, read it live —
`python tools/project_control.py status` and `python tools/current_state.py` — and reconcile against
the remote: **origin/main may have advanced, so do not trust any SHA here as still-current.** This
file is orientation only. Rules/gates/workflow routes live in `CLAUDE.md`. Old blocks (1–14) via
`git log -p docs/SESSION_HANDOFF.md`. Keep CURRENT-ONLY: the `context-budget` CI check fails > ~4000 tok.

## SESSION 15 — bounded truth reconciliation (D-011) + real-identity acceptances

Refreshed **2026-08-11 (session 15; `claude-opus-4-8`)**. **Accepted = 75.** Owner directive D-011
(captured verbatim, `project-control/directives/D-011-bounded-truth-reconciliation/`). The ledger wins.

### Integration branch: PR #220 `control/session15-acceptance`
It is the **single reconciled integration branch off current main `7cc1fed`** (supersedes the stale
#217, closed). It carries: D-011 capture; corrected handoff; the item-5 identity repairs; **M0-T055
ACCEPTED**; the M2-T016 measurement + re-DCV; and **M0-T053's code (merged in from #218)**. Its worktree
is `.claude/worktrees/session15-acc`. Do control-plane accept work HERE (current registry + all code +
advanced states coexist). HEAD at handoff ≈ `f38c2ef` (verify live).

### Open PRs
- **#220** control integration (above) — the live acceptance branch.
- **#219** `task/M0-T047-nanoid-lock` — nanoid **3.3.17** override + CI-bot-regenerated lock; **security
  check GREEN** on this branch; owed: G3/G5/DCV records + merge. (Merging #219 to main greens #218/#220's
  `web-dependency-security`.)
- **#218** `task/M0-T053-child-accounting` — M0-T053 product code; **its code is already merged into
  #220**, so #218 is effectively superseded (can be closed once #220 lands, like #217).

### Acceptance chain — ORDER IS FIXED: M0-T055 → M2-T016 → M0-T053 (D-010-R283)
1. **M0-T055 — ACCEPTED ✓** at real identity `f3a6a363` (was empty-set). DCV 21/21 PASS.
2. **M2-T016 — VERIFIED 77/77, NOT yet accepted.** Identity `ac3d45cb` (repaired). Independent re-DCV
   PASS at HEAD after the Phase-2 measurement was produced (`reports/M2-T016-lean-efficiency-measurement.md`).
   **Remaining = mechanical accept only** (recipe below): write the 77-row D-010 `verification.json` row,
   record gates **G0/G2/G3/G4/G5**, re-submit at `ac3d45cb`, accept. Gate reports on file:
   `reports/M2-T016-delta-G3-code-review.md` (G3), backend/`-G5-delta`/human-journey (G5/G3); G0=readiness,
   G2=190 backend tests, G4=green CI on PR #216.
3. **M0-T053 — code VERIFIED SOUND** (R242/R244/R245 PASS; full supervisor suite 1493/2 reproduced),
   identity `e6746f68`. **Blocked ONLY by order** (R283: must accept after M2-T016). After M2-T016
   accepts, re-run its DCV at the new HEAD (R283 flips PASS), record G0/G2/G3/G5 (G3/G5 verbatim on file),
   accept. P1/P2/P3 are pre-**M0-T056**, NOT pre-M0-T053-accept.

### THE ACCEPT MECHANICS RECIPE (proven on M0-T055 this session)
`accept` IS runnable (not a permission wall; owner authorizes each accept — do NOT add the broad
allowlist, D-011 R003). To accept an in-regime task at a repaired identity, work in the #220 worktree
and DO NOT COMMIT until after accept (accept reads the WORKING TREE; `reviewed_sha` must == HEAD, and
the identity is content-stable across uncommitted control-plane files):
1. Refresh the D-010 `verification.json` row (independent DCV verdicts, all PASS) → `reviewed_manifest_sha256`
   = repaired identity, `reviewed_sha` = current HEAD, `producer`=task's producer, `verifier`=directive-compliance-verifier.
2. `progress` awaiting_gate→**rework**→in_progress; write an `M<t>-evidence-map.json` (each applicable req → evidence);
   `submit --report <md> --evidence-map <json> --sha <HEAD>` (re-stamps the producer record at the new identity).
3. Gates must be PASS + independent role (G3/G4/G5 are INDEPENDENT_GATES; G0/G2 may be self_check). Record any
   missing gate with `gate --sha <HEAD>` (require_clean stamps identity at HEAD).
4. `accept` (fail-closed; only writes `accepted` if ALL pass). THEN `git add` the exact control files + commit + push.

### M0-T057 guard (D-011 item 6) — built, on `task/M0-T057-empty-identity-guard` @ `7bc98f5`
Fails closed when allowed_paths bind zero tracked files; opt-in marker `path_free_governance:true` +
`path_free_justification`; wired into the shared `_task_git_identity` (submit/gate/accept) + validator c17.
**BOTH independent reviews = PASS.** Control-plane: grandfather list of 9 recomputed exact, runtime still
fails all 9 closed, robust to #220. Code: 140 tests pass, correctness verified, the Pyright warnings are
PRE-EXISTING (git blame) not introduced, scope clean (6 files, no packet rewritten). **No rework** — next:
record gates G0/G2/G3 + accept (mechanics recipe above). Follow-ups (non-blocking): add an ordering-invariant
test; drain the inert `M0-T055` grandfather entry once #220 merges.

### Path to Codex/R595 (owner's "how many steps") — 6 steps
1 ✅ M0-T055 accepted · 2 🔄 M2-T016 (verified; accept) · 3 ⏳ M0-T053 (accept, after #2) · 4–5 ⏳ **P1/P2/P3
+ P6 supervisor safety fixes** (the real remaining engineering — NOT started; frozen-lane, each needs a gate
wave) · 6 ⏳ build+accept **M0-T056**, then owner flips R595. **Codex model-fallback = RESOLVED** (Codex
already tries its main model first each session, non-sticky — no change needed; the sticky-fallback risk is
Claude-orchestrator-side only). P8: supervisor is Windows-Job-Object-only today.

### Holds (unchanged) + carried rules
- **M0-T056 NOT started, R595 NOT activated, accept allowlist NOT added** (D-011 R001-R003). deployment/G6/
  Graphify/expansion holds; `default_mode=shadow`; LIMITED-AUTO off.
- Task branches from origin/main; producers spawned **UNNAMED** (named → `readonly_agent_guard` fail-closed);
  `project-control/**`+`directives/**` explicit LF; commit exact paths; Tier A merges after green **required**
  checks. Reviewer/orchestrator model `claude-opus-4-8` xhigh. Prose `allowed_paths` = empty-set identity;
  use real pathspecs (M0-T057 now guards this).
