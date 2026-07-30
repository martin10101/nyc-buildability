# M0-T028 — Independent directive-compliance verification, pre-merge pass (verbatim reviewer return)

Preservation note (report-preservation rule, `.claude/rules/project-control.md`): the reviewer
returned this report through the agent-return channel; it is saved verbatim below with transport
entity-decoding only (`&lt;` -> `<`, `&gt;` -> `>`). Reviewer: directive-compliance-verifier
(read-only, explicit Fable 5 spawn). Frozen SHA reviewed: e8a7dbfa2145b76f91b8e5272769a1447a940525.
NOTE: this is the PRE-MERGE pass over execution-to-date rows; the FINAL independent directive
verification (verification.json rows) happens at the fresh-session identity per D-004's
two-session boundary.

---

# GATE REPORT — Directive-compliance verification (pre-merge pass), M0-T028 / D-004

**Verdict: PASS** (execution-to-date rows at the frozen pre-merge identity; final acceptance and fresh-session rows PENDING-BY-DESIGN)
**Reviewer:** directive-compliance-verifier (read-only; producer ≠ verifier)
**Reviewed SHA (pinned by me):** `e8a7dbfa2145b76f91b8e5272769a1447a940525` — `git -C .claude/worktrees/M0-T028-readonly-guard rev-parse HEAD` returned exactly this; `status --porcelain` empty. Base verified: sole parent of the frozen commit is `4a4bf2d572edce963a355d9d997a2e05833c1dbf` = local `main` = `origin/main` = merge of PR #120.
**Diff at identity:** exactly 6 files (`.claude/hooks/readonly_agent_guard.py`, `.claude/settings.json`, `.gitignore`, `tools/test_readonly_agent_guard.py`, `project-control/reports/M0-T028-TEAMMATE-PAYLOAD-EVIDENCE.md`, `project-control/reports/M0-T028-producer-report.md`), 762 insertions / 33 deletions.

## Harness results (run by me from the frozen worktree)

| Check | Result |
|---|---|
| `python tools/test_readonly_agent_guard.py` | **131/131 PASS, exit 0** ("ALL CHECKS PASSED") |
| `python tools/test_project_control.py` | **all 14 groups OK, exit 0** |
| `python tools/test_directive_compliance.py` | **55 tests OK, exit 0** |
| `python tools/validate_directive_compliance.py` (+ `--check`, both checkouts) | **exit 0** ("5 directive(s), 5 active; source hashes, ID append-only, producer/verifier separation verified") |
| `git check-ignore -v .claude/settings.local.json` (worktree) | `.gitignore:64:.claude/settings.local.json` — repo file supplies the match |
| PR #121 CI (`gh pr checks 121`) | **0 non-pass lines** — every check pass |

## Scope 1 — Capture fidelity (PASS)

- **source-006-amendment.md** exists at main (added by PR #120 as `A` — no prior file modified in that PR's name-status). SHA-256 recomputed by me: `4f697eb9…d5a2a89a` — matches `manifest.json` line 59. All five prior source digests also recomputed and match (source-001 `cb62b582…`, 002 `bba041d9…`, 003 `8f2bece8…`, 004 `d15911ca…`, 005 `518348c3…`).
- **Append-only:** sorted-key JSON comparison of `requirements.json` at `e5d95b6` (pre-PR-#120) vs current: **all 167 prior rows byte-identical, zero missing/edited**; added rows are exactly contiguous `D-004-R168..R286` (119 rows), every one with `source_ref` into `source-006-amendment.md` and `amendment_sequence: 6`.
- **Manifest:** `version: 6`, `locked_requirement_ids` extended to R286, amendment 5 audit-log entry present.
- Per-ID: **R170 PASS** (capture merged in PR #120 together with the packet correction; capture precedes all implementation), **R218 PASS** (all mandated record items present in source-006/manifest), **R219 PASS** (rows start at next free ID R168; no prior row edited — proven by diff), **R220 PASS** (digests recomputed; validator 0), **R221 PASS** (manifest `affected_tasks` + `index.json` D-004 entry both `["M0-T027","M0-T028"]`; audit-log entry), **R222 PASS** (PR #120 diff = 6 control files only; no product/runtime, no M0-T025, no effort, no handoff rewrite; body carries the correction; checks green), **R223 PASS** (merged 03:43Z, then G0 frozen at 4a4bf2d).

## Scope 2 — Phase-1 packet correction rows (PASS)

Verified against the committed packet at `4a4bf2d` (`project-control/tasks/M0-T028.json`):
- **R203 PASS** (deadlock ratified; corrected pre-G0 — PR #120 merged 03:43:05Z, G0 recorded 03:45:49Z), **R204 PASS** (`"dependencies": []`, line 27), **R205 PASS** (inputs 2–3 = both pilot reports; `dependency_note` names M0-T027 as causal predecessor, NOT an acceptance prerequisite), **R206 PASS** (no replacement dependency; empty array with reasoning), **R207 PASS** (explanation in source-006 Phase 1, manifest notes, AND PR #120 body "The dependency-deadlock correction (Phase 1)"), **R208 PASS** (`owner_review_state` APPROVED committed in the same corrected-packet commit), **R209 PASS** (`producer_agent: backend-engineer` — existing `.claude/agents/backend-engineer.md`; distinct from all four reviewers, each of which exists in the roster), **R210 PASS** (no invented role).

## Scope 3 — Phase-4 evidence rows (PASS)

`M0-T028-TEAMMATE-PAYLOAD-EVIDENCE.md` at the frozen SHA:
- **R238 PASS** — records ACTUAL live payloads: §2.1 baseline (no identity keys), §2.2 named spawn (`agent_type` = spawn name, role in no field), §2.3 unnamed spawn (`agent_type` = role); §3 states H1 REFUTED / H2 CONFIRMED with the identity-substitution mechanism.
- **R239 PASS** — method §1 is live instrumentation of the real hook stdin (primary runtime artifact), not synthetic; instrumentation reverted byte-exact with dirt sweeps recorded.
- **R240 PASS** — my programmatic grep over both frozen reports for usernames/`C:\Users`/`/Users/`/session/prompt/pane ID values found only the sanitization statement itself (producer report line 384). All machine values are `<...>` placeholders.
- **R241 PASS** — §4 items 1–5 reconcile exactly the five required facts (tool-unavailability worked; redirection escaped; synthetic payload worked; cwd resets to primary; worktree assumptions cannot confine).
- **R237 PASS** — diagnosis (35% ledger entry, 03:57) precedes the implementation commit; fix contract derived from evidence §5.

## Scope 4 — Branching rule + Phase-5 rows (PASS)

- **R242 PASS** — diff inspected line-by-line: change is confined to docstring, `pathlib` import, two new helpers (`_known_roster_agents`, `_identity`), and the identity-resolution block in `main()`. **`_MUTATING`, `_REDIRECT`, `_git_argv_mutates` and all command classification are untouched** (no hunks in those regions). H2 narrowest identity fix, inside allowed paths.
- **R243 PASS** — unparseable-payload deny branch unchanged; roster-read failure → empty roster → fail closed; non-string identity coerced (fail closed, not crash-open). "fail-closed: non-JSON payload" / "JSON non-object (array)" pass in my run.
- **R244 PASS** — no removed `check(` lines in the test diff; all 89 pre-existing checks pass unchanged; the new logic only adds governed identities (strictly more denial).
- **R245 PASS** — all read-only allows pass, incl. new teammate-shape allows (pwd, git status/rev-parse, gh pr view, pytest).
- **R246/R247/R248 NOT-TRIGGERED (compliant)** — H2 proven; no detection-only substitute implemented.
- **R249 PASS**, **R250 PASS** (sections 7/8: spawn-name + `agent_id` shape, `agent_id`-only shape — matches the captured payload reality), **R251 PASS**, **R252 PASS**, **R253 PASS** (reproduced in my run), **R254 PASS** (all four hook entries single-string with double-quoted `${CLAUDE_PROJECT_DIR}` path), **R255 PASS** (12 `check_settings_commands` checks incl. "spaced-root script path survives as ONE token" — reproduced), **R256 PASS** (.gitignore line 64 with D-004-R101 comment), **R257 PASS** (I ran `git check-ignore -v` myself: repo `.gitignore:64` supplies the match), **R258 PASS** (index already corrected by PR #120 — `affected_tasks: ["M0-T027","M0-T028"]` at the frozen SHA; task diff on index.json = **0 lines**, producer explicitly did not re-edit; R144 lane satisfied at capture), **R259 PASS at this identity** (four harnesses reproduced green by me; PR #121 CI fully green; secret scan evidenced per-file gitleaks in producer report — merge-time CI re-proof happens at merge), **R260 PASS** (see Scope 5).

## Scope 5 — Prohibition rows (PASS)

- **Effort:** `git diff 4a4bf2d..e8a7dbf | grep -i effort` — hits ONLY inside the two report .md files, documenting the observed payload key and the no-effort-key check; no effort key/setting in any configuration or code file. `.claude/settings.json` at the frozen SHA contains hooks only — no allow rules, no machine paths, no `teammateDefaultModel`, no effort. **R194/R159 PASS.**
- **R178–R193 PASS individually:** the 6-file diff contains no Step-4/5 artifact (R178), no M0-T029 (R179), no Agent Teams adoption artifact (R180), no producer wave/injection (R181), no detection-only substitute (R182), no M0-T025 change — blob `a2af336f` identical at e5d95b6 and e8a7dbf (R183), no M0-T019/PR #64 content (R184; PR #64 remains open, untouched), no second-wave product task (R185), no expansion/PRD (R186), no Mission Control map (R187), no project/control graph (R188), no NYC KG (R189), no Graphify (R190), no M2–M7 product code (R191), no survey (R192), no deployment/hold release (R193).
- **R260 PASS:** protected files blob-identical e5d95b6→e8a7dbf: `AGENT-TEAMS-PILOT-1.md` (`df9e27cb`), `AGENT-TEAMS-PILOT-2-PROBE.md` (`2ab4cdaa`), `M0-T025.json`, `CLAUDE.md`; no agent definitions, rules, or deployment files in the diff.
- **R217 PASS** (pilot reports byte-preserved — blob proof above). **R233 PASS** (producer dispatched as background subagent, consistently recorded in packet `producer_note`, G0 readiness, and producer report; no team artifact anywhere). **R227 PASS** (all holds standing: expansion hold rule unchanged, Graphify WAIT, PR #64 untouched, B-015 open, M0-T027 blocked).
- **Prohibited-action state:** PR #121 OPEN, head = frozen SHA, not merged; main == origin/main == 4a4bf2d; M0-T028 `in_progress` (not accepted; absent from `state.json.accepted_tasks`); B-015 `open`; M0-T027 `blocked`; last checkpoint CP-0033 (no new final checkpoint). Nothing merged/accepted/dispatched/deployed/installed/purchased/closed beyond the authorized PR #120.

## Scope 6 — Deviation disclosures (honestly recorded; no binding violation)

- **(a) Model deviation — recorded and compliant.** Ledger 40% entry records: explicit-Opus spawn resolved to `claude-opus-5`; producer stopped honestly (MODEL-MISMATCH, zero tool uses); re-dispatched on `inherit` (session Fable 5, non-downgrade). Judgment: **R226/R091/R162 bind teammate spawns** ("Opus 4.8 for producer teammates **if a producer teammate is used**"); no producer teammate was used — using one is prohibited while B-015 is open (R233). `ORCHESTRATION_POLICY.md` line 43 sets `model: inherit` for subagent implementation. The two diagnostic teammate probes carried explicit Fable 5 (R160/R161/R234 — Probe B self-reported `claude-fable-5`). **No violation.**
- **(b) Worktree confinement + orchestrator port — honestly disclosed; minor ledger gap.** Disclosed up front in the committed producer report §1 at the frozen SHA (harness refused shared-checkout access in all three forms; work produced in a harness-assigned clean worktree at the identical base `4a4bf2d`; orchestrator ported the diff onto `task/M0-T028-readonly-guard` — commit e8a7dbf, sole parent 4a4bf2d, committed by the orchestrator identity, consistent with ADR-005 integration authority and single-writer R232). **Gap (non-blocking):** the ledger `progress_log` does not yet carry a dedicated entry for this deviation (entries: 35%, 40%, 60% G3 — none mentions the port). Recommend the orchestrator record it via `progress --message` at submit. No binding row is violated: containment exact, same frozen base, R229 worktree/branch exist as contracted.

## Scope 7 — Sentinel clarification + fresh-session boundary (PASS / intact)

- **R211 PASS** (recorded as decision; G0 readiness restates it), **R212 PASS** — no artifact claims the guard denied a tool the teammate could not invoke; the evidence report attributes Step-1 Write denial to tool-unavailability ("No such tool available: Write"); the suite's "deny Write tool" lines are genuine guard subprocess denials on synthetic harness payloads, not live-teammate claims. **R213/R214 PASS at unit level, live proof PENDING-BY-DESIGN (Phase 8)** — producer report AS-3 explicitly says "UNIT-LEVEL ONLY … DEFERRED to the mandatory Phase 8 fresh-session rerun". **R215/R216 PENDING-BY-DESIGN (Phase 8).** My grep across all M0-T028 artifacts for "sentinel passed"/"B-015 closed/resolved" claims: **zero hits**.
- **R224/R268 intact (PASS-so-far):** no freshness simulated; no merged-hook testing claimed in this session; two-session boundary restated in G0 readiness and packet risks. **R267 PASS-so-far**, **R272 PASS-so-far**.
- Incidental live corroboration: during this review the primary checkout's (pre-fix) guard denied my own Bash redirection and `git fetch`, naming `directive-compliance-verifier` — the hook fires for unnamed role spawns (consistent with H1-refuted/H2 mechanism).

## Other execution-to-date rows examined

**R168 PASS** (live reconciliation recorded in source-006 header; head matched e5d95b6), **R169 PASS** (GO captured; manifest owner_approval), **R171 PASS**, **R172 PASS** (no other work in scope of this execution), **R173 PASS**, **R174 PASS** (H2 proven repairable), **R175 PASS**, **R176 IN-PROGRESS** (this review is part of it; merge + rerun pending), **R177 PASS-so-far**, **R195–R197 PASS on control-plane record** (G0 readiness/source-006 capture header), **R198 PASS** (e5d95b6 is the PR #119 merge; no handoff rewrite in any diff), **R199 PASS** (verified settings content), **R200 PASS**, **R201 PASS on record**, **R202 PASS** (advancement beyond e5d95b6 is PR #120 itself), **R225 PASS**, **R228 PASS** (fresh G0 gate record at 4a4bf2d, 03:45:49Z), **R229 PASS**, **R230 PASS** (new branch/worktree named for M0-T028), **R231 PASS** (CLI lifecycle records), **R232 PASS**, **R234 PASS**, **R235 PASS** (sweeps recorded before/after probes; worktree clean now), **R236 PASS-so-far**, **R261 IN-PROGRESS** (G3 PASS recorded at the frozen SHA per 60% entry; this verification is at the same SHA), **R262 PASS** (all reviewers ≠ backend-engineer; I am not the producer), **R263 PASS for this reviewer** (every listed item inspected above), **R264 PASS-so-far** (no corrections applied), **R265 NOT-TRIGGERED**, **R266 PENDING-BY-DESIGN** (merge), **R269–R282 PENDING-BY-DESIGN** (Phases 7–8, fresh session), **R283/R285/R286 PENDING-BY-DESIGN** (return packet), **R284 PASS-so-far** (no stop condition triggered; deviations disclosed, not improvised).

## Defects (non-blocking, for the record)

1. **F-1 (already ledger-recorded by G3, independently reproduced by me):** producer report AS-4 narrative and §2 claim "132 checks (90 pre-existing + 42 new)"; the correct figures are **131 = 89 + 42**. The report's own verbatim suite output (131 PASS lines) and my live run agree; zero failures. Correction properly recorded via the 60% ledger entry without rewriting the frozen report.
2. **Ledger gap:** worktree-port deviation (b) not yet in `progress_log` (lives in producer report §1 at the frozen SHA). Recommend a `progress --message` entry before submit.
3. Cosmetic: the string "effort" appears in the two reports solely as documentation of the observed payload key and of the no-effort-key check — this is not an effort setting and violates nothing; noted so no future scan misreads it.

**Verdict for this pre-merge pass: PASS** at reviewed SHA `e8a7dbfa2145b76f91b8e5272769a1447a940525`. No VIOLATED and no UNVERIFIABLE rows among the execution-to-date requirements; all fresh-session/acceptance rows are PENDING-BY-DESIGN and must not be treated as satisfied until Phase 8. D-004 remains incomplete by design until then.

Key evidence paths (absolute):
- `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\project-control\directives\D-004-agent-teams-runtime-adoption\{source-006-amendment.md, manifest.json, requirements.json, verification.json}`
- `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\project-control\tasks\M0-T028.json`, `...\gates\M0-T028-G0.json`, `...\reports\M0-T028-G0-readiness.md`
- `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\.claude\worktrees\M0-T028-readonly-guard` (frozen identity; reports `project-control/reports/M0-T028-TEAMMATE-PAYLOAD-EVIDENCE.md` and `M0-T028-producer-report.md` at `e8a7dbf`)

---

Orchestrator addendum (recorded at gate time, not part of the reviewer return): defect 2's
requested disclosure entry was recorded at 65% before submit. The C3/C4 bounded delta (d5eb642e)
was applied after this pass and received its own bounded G3/G5 delta reviews (both PASS); this
pre-merge pass therefore binds to e8a7dbf plus those delta reviews. The FINAL directive
verification (verification.json rows at the fresh-session identity) remains pending by design.
