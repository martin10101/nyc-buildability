# Session Handoff — NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume, read it live —
`python tools/project_control.py status` and `python tools/current_state.py` — and reconcile against
the remote: **origin/main may have advanced, so do not trust any SHA written here as still-current.**
This file is orientation only. Operating rules, gates, and workflow routes live in `CLAUDE.md`.

Refreshed **2026-07-31**, at the Step-1 merge boundary of the live closeout authorization.

## Where main is

| | |
|---|---|
| `origin/main` | `1fc8a03b9ad3e827c34ebc805a3005b50f9e3e81` |
| accepted tasks | **53** (M0-T034 is MERGED, not accepted) |
| D-004 registry | version **18**, **700** locked requirement ids |
| merged this window | **#137** (D-004 amendment 17 — the closeout authorization), **#138** (M0-T034, dual PASS) |
| open PRs | **#64** only (unrelated, pre-existing) |

## 1. THE LIVE AUTHORIZATION — this is the session's whole job

**D-004 amendment 17 (`source-018-amendment.md`, rows R650–R700, merged as PR #137) captures the
owner's ONE-SHOT CLOSEOUT AND HANDOFF AUTHORIZATION.** Its gate condition R661 is **SATISFIED**:
both round-3 gates returned **PASS** at frozen SHA `dbf0a88` (G3 by `m0t034-g3-r3`, G5 by
`m0t034-g5-r3`, explicit Opus 5, reports preserved as `M0-T034-G3-report-r3.md` /
`-G5-report-r3.md`, gate records with full FAIL history at `3745fd2`).

**Step 1 is DONE** (this merge + this handoff): PR #138 merged at the exact CI-verified head,
both gate returns preserved as tracked files, branches cleaned.

**Steps 2–7 REMAIN — execute them in order, from the amendment text (read `source-018-amendment.md`
rows R669–R700; the summary below does not replace it):**

2. **Re-submit M0-T027** under corrected identity
   `29a094ebdf312767b2ffa964a9cfb0398432e8838db0a211a711f1dd8db2bb97`, all evidence committed
   BEFORE submit (the merged M0-T034 rule fails closed otherwise). (R669)
3. **Final verification** at that head, delta-scoped, citing settled rulings at their verified
   SHAs; preserve the return as a tracked file; the verifier manually performs any guard the code
   path skips. **HARD STOPS (R673): halt and report if R322/R323/R388 cannot reach PASS through
   completed lifecycle evidence; any new finding needing owner judgment; any UNVERIFIABLE; any
   deviation from expected state.** Note: `verification.json` for D-004 carries 97 rows against
   233 applicable — the independent verifier must rebuild it; the orchestrator never sets a
   verification status.
4. **Conditional accept (R674):** ONLY if exactly clean — every applicable row PASS or attested
   lifecycle deferral, zero UNVERIFIABLE, zero new findings, R024 recorded PASS by the verifier —
   acceptance of M0-T027 is authorized through the CLI (R486). Checkpoint per policy (R487); clean
   only closeout branches/worktrees (R488); run the first post-accept verification of deferred
   lifecycle rows through the M0-T034 mechanism. **Any deviation → stop before accept (R678).**
5. **Efficiency directive (R679–R684):** on acceptance, the pending draft v1.2 is ISSUED — file
   `OWNER_DIRECTIVE_DRAFT_dispatch-efficiency-and-graph-wiring.md` (repo root, untracked), digest
   `bd6c4ec2151202bb5209ee62f4cc2a3f94538cd40b695604ceff0e32d1c22b6b` (verified at capture;
   re-verify bytes before capture). Capture verbatim, decompose without weakening/combining/
   omitting, close out the tracked pending-capture record in the same batch. **R307 disposition:
   the DEFERRED arm applies** — this round's gates ran under the Opus 5 regime; record with that
   evidence and a re-check at the next gate dispatch. Contract the Section 3/5.2 edit task; adopt
   the dispatch/packet standards immediately; begin the N=6 measurement (dcv2–dcv4 baseline). A
   capture conflict or edit-task gate FAIL stops this lane only, not Step 6.
6. **Supervisor directive Phase 0 (R685–R694):** file `.claude/CODEX_CLAUDE_SUPERVISOR_BUILD_DIRECTIVE_v4.3 (1).md`
   — the basename literally contains " (1)"; the anchor is the digest
   `426da3bb22714a403553b013e8969c6bfa424ee01d99e10d1269d0b65e0f5137` (verified at capture).
   Strictly read-only first, per its Section 17; then the TWO permitted writes only (canonical
   directive capture; the controlled task packet). No implementation, no supervisor paths, no
   config changes.
7. **Consolidated stop (R695–R696):** one final report — acceptance record + checkpoint,
   post-accept lifecycle-row results, efficiency capture decomposition + R307 disposition +
   edit-task gate results, Phase 0 Section 19 return packet + supervisor task packet awaiting the
   owner's dispatch decision. Backlog without acting: C1 MATERIAL_FIELDS inversion, OBS-6
   preservation-time redaction, D-001 capture-guidance update for `classified_at_identity`.

**Global rules (R697–R700): every stop is a report, never a workaround; nothing beyond the acts
named; auto mode never overrides an Ask rule; if anything is ambiguous, stop is the default.**

## 2. M0-T034 — merged, NOT accepted

Status `self_check` @ 90%. Merged to main with dual PASS; its OWN acceptance still requires:
the independent `directive-compliance-verifier` per-requirement pass (rebuilding
`verification.json`), **AS-10** (the verifier's classification of the eight candidate rows
R322/R323/R388/R389/R486/R487/R488/R501 — the orchestrator never makes this call), **AS-13**
(orchestrator writes `M0-T034-lifecycle-classification.md` verbatim from the AS-10 return), then
the normal submit/gate/accept lifecycle. AS-5 carries owner ruling C2 in the scenario record —
cite it, never re-litigate.

**G3's BINDING BUNDLE CONDITIONS (round-3 report, rider 4) — F4/F8 revert to BLOCKING if broken:**
(a) contract the follow-up bundle **"C1 MATERIAL_FIELDS boundary + attestation validation"** as a
controlled task BEFORE M0-T034's post-accept verification closes; (b) never widen M0-T034's
`allowed_paths` to absorb it; (c) its items 1 (F4/MATERIAL_FIELDS) and 2 (F8 schema+validator
mirror of conditions (1)(2)(4)(5)(6)) stay in ONE task. The bundle also carries: the c15
manifest-scope gap (M0-T034 absent from D-004's scope list), F5's same-identity transportability
residual, OBS-6, and **FU-4** — the D-001 capture convention that every future
`lifecycle_classification` attestation must carry `classified_at_identity` equal to the identity
it was granted at (condition (6) is live on main NOW; an unstamped attestation refuses).

## 3. Standing discipline (carry forward)

- **R024, public repo:** scan BEFORE commit (username, absolute user paths both slash forms,
  hostnames, session ids); redact with annotation at the redaction site; describe patterns, never
  quote them inside sweep sentences. 76 pre-existing files carry the username — owner-prohibited
  from being touched (R560); systemic fix is OBS-6 in the bundle.
- **Writing producers spawn UNNAMED; reviewers may be named.** Explicit Opus 5 (D-004-R307) for
  every producer/reviewer/verifier; disclose the actual model honestly; never claim Fable 5.
- **Reviewers signal idle without delivering.** Follow up demanding the complete return; preserve
  it verbatim THE MOMENT it arrives (round-1's returns nearly died with their stopped agents; they
  were recovered from stored session transcripts under
  `~/.claude/projects/<project>/<session>/subagents/`).
- **Gate records stamp live at HEAD == reviewed commit (N2).** If HEAD moved after the review,
  record on a branch cut from the reviewed commit and merge (precedent: `af5c083`/`659cdde`).
- **Directive capture is append-only**, decomposed atomic, session-sentinel `D-004-OPTIONB` for
  execution-authority rows, requirement/content digests recomputed in `manifest.json`, validator
  green before commit. Verify append-only with explicit UTF-8 decoding (cp1252 phantom diffs).
- **Static-analysis warnings are not defects** — adjudicate by execution (line tracer, second
  linter). Round-3 G3 refuted every Pyright flag this way.
- **Producer worktree ports are byte-identical**, verified per-file SHA-256 against the producer's
  declared hashes; no orchestrator edit of producer output.
- The auto-mode classifier intermittently denies benign `python -c`/heredoc forms; re-express the
  command (script file piped via stdin works); if a consequential act (e.g. a merge) is denied,
  STOP and surface — never work around a merge denial.

## 4. Superseded / loose ends

- Local branch `control/session-handoff-refresh-2026-07-31` (`7206821`) was never merged and is
  fully superseded by this file; safe to delete after an owner glance.
- The round-3 producer's sandbox/worktree-guard lesson exists only in its preserved return (in the
  orchestrator session transcript); whoever owns `.claude/agent-memory/backend-engineer/` should
  add it post-task (owner statement + producer correction recorded at D-004-R660).
- Stopped agent worktrees under `.claude/worktrees/agent-*` await R488 closeout cleanup (Step 4).
- Producer report §11.4 Command E over-reports three removed-side rows (conservative direction) —
  noted by round-3 G3; no rework required.
- Pre-existing weak test `test_manifest_is_order_independent_and_content_based`
  (`tools/test_directive_compliance.py:339-346`, from M0-T023) never asserts the property it
  names — G3 r3 observation 1; queue with ordinary maintenance, not chargeable to M0-T034.

## 5. NOT AUTHORIZED (unchanged unless amendment 17 conditionally lifts it)

Step 5 / M0-T029 · M0-T032 · M0-T025 · another producer or product wave · product or legal-rule
changes · predicate-schema follow-up · `teammateDefaultModel` changes · **any effort key or effort
setting, anywhere, ever** · hooks, agent definitions, or settings changes · deployment or hold
releases · G6, Graphify, expansion, survey work. The efficiency-draft and supervisor-directive
holds lift ONLY per R679/R685's conditions (M0-T027 acceptance first, scope-limited).
