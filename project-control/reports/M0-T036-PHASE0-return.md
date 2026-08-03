# D-007 Phase 0 — Section 19 return packet (Discovery and control-plane contract; no implementation)

Produced by the orchestrator under D-004-R685–R694 (amendment 17 Step 6, resumed by amendment 18
R713/R714/R716/R717), executing Phase 0 of the captured supervisor build directive
(`D-007-codex-claude-supervisor-bridge/source-001.md`, digest `426da3bb…`). Strictly read-only
reconciliation first; the only writes are Phase 0's two permitted outputs (the D-007 canonical
capture and the M0-T036 contract artifacts, this record among them). Dates: probes run
2026-08-03.

## Section 19 fields

| field | value |
|---|---|
| CURRENT PHASE / MODE | Phase 0 complete; no supervisor exists; no mode active |
| LIVE MAIN SHA | `62a247e` at Phase 0 execution (M0-T035 gate lane and this capture branched from it; the Step 7 report names the final head) |
| CURRENT TASK / STATUS | M0-T036 contracted, `backlog`, NOT claimed — awaiting the owner's dispatch decision (D-004-R717) |
| WORKTREE / BRANCH | capture on `control/D-007-supervisor-capture`; no supervisor worktree created |
| FILES CHANGED | Phase 0 writes only: `D-007-…/source-001.md`, `manifest.json`, `requirements.json`, `verification.json`, `index.json` entry, `tasks/M0-T036.json`, this return |
| TESTS / CI | no implementation → no new tests; `validate_directive_compliance.py --check` exit 0 with D-007 active; CI green required on the capture PR before merge |
| CODEX CLI + MODEL(S) VERIFIED | `codex-cli 0.146.0` (npm `@openai/codex`), meets the `>= 0.146.0` pin. Flags confirmed on the installed binary: `--ephemeral`, `--ignore-user-config`, `--strict-config`, `--output-schema`, `--json`, `-o/--output-last-message`, `-m`, `-s <sandbox>`; both bypass flags present → HARD-DENY list entries are real. **Behavioral:** `-m gpt-5.6-sol` and `-m gpt-5.6-terra` both ACCEPTED (trivial bounded runs, "OK", exit 0). **`--ephemeral` leaves no transcript:** two runs on 2026-08-03; `~/.codex/sessions` gained zero files (no `2026/08` directory; `find -mmin -15` → 0) |
| CLAUDE CLI/SDK CAPABILITIES VERIFIED | Native `claude.exe` 2.1.220 works. **Canonical-executable decision (§13.4): the native install** — the npm shim's bundled exe fails on this Windows ("not compatible with the version of Windows you're running"), so the dual-install ambiguity resolves decisively to `~\.local\bin\claude.exe`, pinned 2.1.220. `--help` confirms: `-p`, `--output-format stream-json`, `--input-format stream-json`, `--session-id`, `--resume`, `--fork-session`, permission modes. `--max-turns` is ABSENT from `--help` (recon claim confirmed read-only); the behavioral acceptance run and the stream-json `canUseTool` protocol probe were **classifier-denied in this session** (nested CLI runs) — recorded as the two OUTSTANDING behavioral verifications, runnable by the owner in one minute (`claude -p "Say OK" --max-turns 1`) or by the M0-T036 producer at dispatch under its granted permissions. NOTE: 2.1.220's help shows an `--effort <level>` flag EXISTS on the CLI — the supervisor must never pass it (D-004-R159 permanent; directive §3.1 already prohibits) |
| SECURITY / CONTROL-PLANE FINDINGS | see "Directive-conflict check" and "ADR-005 reconciliation" below; no conflict requiring a Section 18 stop |
| CONTROLLER / TOOLCHAIN MANIFEST | not yet built (Phase 1); baseline recorded: codex 0.146.0 (npm), claude native 2.1.220, git/gh present per session evidence |
| PROTOCOL / SCHEMA VERSIONS | none yet (Phase 1 deliverable) |
| ISOLATION / DATA-EXPOSURE STATUS | no supervisor process exists; the §13.1/§13.3 controller-isolation and worker-environment decisions are packet risks for the owner at dispatch |
| RESOURCE / USAGE STATUS | thin-client constraint stands (~7 GB free); supervisor runtime state is designed for `%LOCALAPPDATA%`, outside the repo |
| ROTATION PENDING / NEXT-UNIT SIZE | n/a (no run) |
| RECOVERY CLASSIFICATION | n/a (no run) |
| USAGE-LIMIT CLASS / RESET SOURCE | n/a (no run) |
| RESUME-NOT-BEFORE / SCHEDULED TRIGGER | none |
| PENDING EXTERNAL EFFECTS | none |
| QUEUED ASK ITEMS / NOTIFICATION STATUS | the owner-decision list in the M0-T036 packet (below); no notification surface exists yet |
| OWNER-TOUCH COUNT THIS TASK | Phase 0: this consolidated stop is the single owner touch (plus the merge approvals the protected-main workflow always requires) |
| PROPOSED POLICY WIDENINGS | none — Phase 0 proposes no autonomy widening |
| BLOCKERS | none open; the two outstanding claude-side behavioral verifications are dispatch-time items, not blockers |
| OWNER DECISION REQUIRED | M0-T036 dispatch (see packet); ADR-005 amendment approval; audit-anchoring choice; standing-grant approval; controller-location choice |
| EXACT SAFE NEXT ACTION | owner reviews the M0-T036 packet and either dispatches, edits, or holds it |

## SDK-vs-CLI written decision (§8.1)

**Decision: CLI subprocess (`claude -p --output-format stream-json --input-format stream-json`), via the canonical native executable.**
Reasoning: (1) the Claude Agent SDK is NOT installed (verified: `npm ls -g @anthropic-ai/claude-agent-sdk` empty; `pip show claude-agent-sdk` not found), so the §8.1 premise "if the installed SDK provides…" fails at the threshold; (2) adopting the SDK would be a NEW dependency that must pass the repository's admission/security/age/license/lockfile policies (directive §5.1) — a separate owner-visible act, not a Phase 0 default; (3) the installed CLI provides the required primitives (stream-json both directions, session ids, exact resume, fork-session) and its control protocol is the documented headless path for tool-approval mediation on this version. **Revisit trigger:** if the owner elects to admit the SDK dependency, the decision reopens at that admission — recorded here so the CLI choice never hardens silently.

## ADR-005 reconciliation (§4.1/§13.6 ↔ ADR-005)

ADR-005 rule 1 assigns git integration (add/commit/push/merge) and `gh` exclusively to the
**main-session orchestrator**; rule 2 says producers never push. D-007 assigns task-branch pushes
and PR create/update to the **supervisor as deterministic controller actions after a passing
review** — the worker never pushes and holds no push credentials. Reconciliation shape: the
supervisor occupies the ADR-005 orchestrator-side integration role for its task, and the worker
remains an ADR-005 producer.

**An ADR-005 amendment IS required before any supervisor mode that pushes (supervised/limited-auto
with grants) activates** — ADR-005's text names the *main-session orchestrator* as the only
integration principal, and a deterministic controller is a new principal, however
orchestrator-shaped. Phase 0 proposes (does not apply) this amendment text for the owner:

> *ADR-005 amendment (proposed):* "The deterministic Agent Supervisor controller (D-007), when
> operating under an owner-activated mode and an owner-granted standing task grant, MAY perform
> the orchestrator-side integration actions `git push` to the exact authorized non-main task
> branch and PR create/update for that branch, after a passing independent review, subject to
> every ADR-005 prohibition (no merge, no acceptance, no direct/force push to main, no gate
> satisfaction). The worker process never pushes and never holds push credentials. All other
> ADR-005 authority is unchanged."

Until the owner approves that amendment (recommended vehicle: a D-007 amendment row + an ADR-005
edit inside M0-T036's reviewed scope, or at activation), the supervisor's push behavior stays
disabled: replay/shadow modes need no push authority, so Phases 1–4 and the shadow pilot can
proceed without it.

## External audit-anchoring proposal (§13.12)

The local hash chain is mandatory and in scope. For the default-required EXTERNAL anchor, Phase 0
proposes **Option A (recommended):** the controller, at every checkpoint, appends the current
chain-head digest to a dedicated branch (`supervisor-audit-anchor`) of a separate private
repository (or this repository if the owner prefers), pushed with controller-held credentials the
worker never receives. GitHub's commit history is outside every Claude-writable path, timestamped,
and tamper-evident against local rewrites. **Option B:** a controller-owned append-only file under
an ACL-restricted `%LOCALAPPDATA%` location — weaker (same machine, same admin), only acceptable
combined with A later. **Option C:** defer external anchoring beyond V1 — per §13.12 this demands
explicit acceptance by BOTH the owner and the security review, recorded through directive
compliance; Phase 0 does not recommend it. **Owner chooses at dispatch; the packet carries the
choice as an explicit owner decision.**

## Dependency-independence check definition (§4.3)

A unit U is independent of a queued ASK item Q iff ALL of:
1. **Path disjointness:** the canonical target-path set of U (its packet paths + declared file
   set) intersects the affected-path closure of EVERY plausible answer to Q in the empty set;
2. **Interface disjointness:** no module/interface/contract U imports, implements, or tests is
   named in Q or in Q's affected-path closure (the code-graph `query.py` neighborhood is
   admissible ADVISORY input; the recorded check must list the concrete edges checked in source);
3. **Class gate:** Q is not classified architecture, dependency, scope, or security — those
   classes block dependent continuation categorically (directive §4.3(a));
4. **Assumption check:** U's unit definition contains no step whose correctness depends on any
   particular answer to Q (attested per-unit, named in the record);
5. **Durability:** the check's inputs (Q digest, U definition digest, path sets, edges, class)
   and conclusion are journaled digest-bound BEFORE U continues.
Failing any clause ⇒ U is dependent ⇒ park per §4.3(b). The supervisor implements this as a
deterministic function with these five recorded clauses; tests must include a proven-dependent
and a proven-independent fixture pair (§15 tier-policy matrix).

## Directive-conflict check (§17: every active directive)

| directive | conflict? | notes |
|---|---|---|
| D-001 (compliance system) | none | D-007 captured through it; supervisor never writes the registry |
| D-002 / D-003 (waves) | none | no scope overlap |
| D-004 (agent-teams) | **none, with two recorded touchpoints** | (1) effort keys: D-004-R159 PERMANENT prohibition, M0-T028 capsule line 98 ("NO effort key, ever, anywhere") — directive §3.1 independently prohibits them, and `--ignore-user-config` keeps the owner's personal Codex config out; ALIGNED. The CLI's newly-observed `--effort` flag is never passed. (2) D-004's spawn/model rules govern agent-teams spawns; the supervisor's worker is a `claude -p` subprocess, not a teammate spawn — model selection flows through D-007 §3's owner allowlists; the R307 restoration evidence (pinned Fable 5 succeeded 2026-08-03) is recorded at D-006-R032 and awaits the owner's formal discharge ruling |
| D-005 (Graphify) | none | §5.2 forbids installing Graphify or reopening that decision — matches the D-005 WAIT verdict |
| D-006 (dispatch efficiency) | none | D-006 §7 states it does not authorize the supervisor work; D-007 is the separate directive it anticipated |
| Expansion-agent hold (rule file) | none | supervisor work is not expansion planning; the hold is untouched |
| M0-T028 capsule directives | superseded item noted | capsule line 118's "do not accept M0-T027" was superseded by the owner's amendments 17/18 (M0-T027 accepted 2026-08-03 under captured authority); every still-live capsule constraint (effort, worktree-confinement posture) is honored |

**No conflict requires a Section 18 stop.** B-015 is resolved (M0-T028 accepted); the directive's
"do not trust teammate confinement while B-015 is open" baseline is moot but the hardened guard
stays per the dispatch-guard invariant.

## Settled input evidence (§17: recon rounds + delta review)

The two 2026-07-31 reconnaissance rounds and the delta review are embodied in the directive's own
v4.2/v4.3 revision notes and §2.2 "installed-CLI reality" paragraphs (the directive is the
owner's consolidation of them). Phase 0 re-verified every still-verifiable recon claim on the
installed binaries — results above; nothing contradicted the recon. Outstanding: the two
classifier-denied claude-side behavioral runs, listed as dispatch-time items.

## Phase 0 containment statement

No implementation, product, runtime, CI, hook, or deployment change; no supervisor path created;
no configuration modified; the only writes are the D-007 capture and the M0-T036 contract
artifacts (this record among them). The build dispatch is the owner's next and separate decision
(D-004-R717).
