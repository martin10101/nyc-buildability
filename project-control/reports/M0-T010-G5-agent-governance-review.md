<!-- VERBATIM reviewer return (security-reviewer, 2026-07-17), preserved by the orchestrator per the report-preservation rule. Transport entity-decoding only (&gt;/&lt;/&amp; decoded); no other alteration. -->

# G5 Gate Report — M0-T010: 3D/UI Expansion Pack Integration (Security / Agent-Governance Review)

- **Gate:** G5 (security & privacy — agent-authority safety of active execution surfaces)
- **Reviewer:** security-reviewer (independent; did not produce the work; producer: cloud-architect / orchestrator Phase 1)
- **Date:** 2026-07-17
- **Review target:** branch `task/M0-T010-expansion-integration` @ `c0769ae`, worktree `C:\Users\MLFLL\Downloads\nyc zoning\nyc-development-feasibility-claude-pack\.claude\worktrees\M0-T010` (clean; diff vs main = exactly 13 added files, verified by `git diff --stat main...HEAD`)
- **Baseline read from MAIN:** `.claude/rules/project-control.md` (ADR-005 codification + 2026-07-15/16 owner clarifications), `docs/adr/ADR-005-agent-permission-and-gate-workflow.md`, `docs/adr/ADR-004-frontend-hosting-render.md`, `docs/AGENT_OPERATING_SYSTEM.md`, `docs/GATES_AND_CHECKPOINTS.md`, `docs/PROJECT_CONTROL_PROTOCOL.md`, `GENERATIVE_DEVELOPMENT_STRATEGY_REQUIREMENTS.md` §3, `docs/GENERATIVE_STRATEGY_INTEGRATION_PLAN.md`, conformant roster agents (`cloud-architect.md`, `code-reviewer.md`, `security-reviewer.md`, `human-journey-reviewer.md`, `orchestrator.md` — 17 total on main), `project-control/tasks/M0-T010.json`, `project-control/blockers/B-005-*.json`, `.claude/settings.local.json`
- **Read-only discipline honored:** no repo file edits, no git write commands, no gh, no `project_control.py`. Only agent-memory writes under `.claude/agent-memory/security-reviewer/`. Independent re-execution limited to read-only scanners: `python .github/scripts/secret_scan.py` in the worktree → `PASS -- no findings`, exit 0; `python .github/scripts/validate_contracts.py` → `Checked 6 schema file(s); 0 failure(s)`, exit 0 (independently reproduced, matching producer and G3 claims). Note the producer report cites `tools/secret_scan.py`; the actual path is `.github/scripts/secret_scan.py` (cosmetic report inaccuracy, non-blocking).

## Baseline conformance pattern (extracted from main roster, used for Area 2)

Every conformant roster agent carries: frontmatter `permissionMode: default` + `memory: project` + `Skill` in `tools`; producers additionally `isolation: worktree` + body line "Stay within allowed paths" + a "## Ledger and integration protocol (ADR-005)" section ("Do NOT run tools/project_control.py, git push, or gh… RETURN … requested status"); reviewers additionally `Write` (for report drafting) + `skills: run-quality-gate` + a "## Gate reporting protocol (ADR-005)" section ("You are read-only. Do NOT run tools/project_control.py, git write commands, gh, or any write-producing shell command… RETURN … PASS, FAIL, or BLOCKED"). ADR-005 §Decision 6: "All 17 agent definitions … now embed these protocols."

---

## Area 1 — `.claude/rules/3d-ui-expansion.md` conflicts

The file has **no `paths:` frontmatter**, so once on main it attaches to sessions **unconditionally** (contrast `project-control.md`, scoped `paths: - "project-control/**"` — I observed its conditional attachment live this session when reading a `project-control/` file). Every passage below is therefore standing, always-loaded orchestrator instruction, not passive documentation.

**1a. CONFLICT (drives Defect D2).** `.claude/rules/3d-ui-expansion.md:25` (item 13):
> "The main orchestrator must update the existing master plan and continue from the first unblocked task."

Conflicts with:
- Owner directive 2026-07-17 (`project-control/tasks/M0-T010.json`, progress log 08:52Z): "The 19 proposed tasks, 9 contracts, P1-P8, and any MASTER_EXECUTION_PLAN changes are NOT to be applied until owner reviews the complete integration report."
- `docs/AGENT_OPERATING_SYSTEM.md` §2 (plan from evidence via the management loop, not from a standing continuation order) and CLAUDE.md start-of-session routine step 4 (`/replan-project` before assigning new work).
- It is an *unqualified* auto-continuation order. The related pre-existing `CONTINUE_FROM_CURRENT_STATE_PROMPT.md:71` (item 10) at least carries a qualifier ("after the integration report and task-plan update are independently reviewed"); the rule file drops it. Not an authority *theft* (it addresses the orchestrator, which does hold master-plan authority per CLAUDE.md principle 9), but a conflicting-instruction channel that, always-loaded, pushes past the owner-review hold — which currently lives only in a task-packet progress log that falls out of view once M0-T010 closes.

**1b. AMBIGUOUS.** `.claude/rules/3d-ui-expansion.md:23` (item 11):
> "Require visual, mathematical, performance, accessibility, and human-journey gates."

These gate names do not exist in the `docs/GATES_AND_CHECKPOINTS.md` catalog (G0–G7). Reasonably mappable onto G3/G4 evidence requirements, but a future agent could treat them as a parallel gate system. Same class: `docs/3D_AND_UI_EXECUTION_PLAN.md:179` "Reviewer: rules-engineer + professional-review gate" (COMP-002) — "professional-review gate" is not G6 (G6 is legal-rule publication) and is undefined.

**1c. AMBIGUOUS (low).** `.claude/rules/3d-ui-expansion.md:11-17` (item 5, "Use: Three.js + React Three Fiber + Drei … Trimesh …") mandates a technology stack by rules-file fiat, in tension with PRD §31 ("Research official documentation before choosing an endpoint or library behavior") and the ADR discipline. Mitigated: `CONTINUE_FROM_CURRENT_STATE_PROMPT.md:60` permits ADR override ("unless a documented ADR proves a materially better option") and the integration report routes the decision through a 3D-001 ADR (report §2 row 5).

**1d. NO CONFLICT found with:** ADR-005 authority text (the rule file never mentions the control CLI, git, gh, or gate recording); producer/reviewer separation (items 10 and 22 affirmatively require it: "Apply producer/reviewer separation to all visual work"); ADR-004 Render-only (the stack is browser npm libraries + PostGIS/Shapely/Trimesh server-side; no hosting or Vercel statement anywhere in the six files — grep verified); GDS §3 separation of authority (items 8–9: "Never let AI prose directly define geometry", "No shape is accepted without a calculation and provenance trace" — aligned); owner-approval requirements (silent, not contradictory — the only risk is 1a's continuation order skipping the review *pause*, not any claim of approval power). `docs/3D_VISUAL_ACCEPTANCE_STANDARD.md:112-118` actively reinforces governance: "The producer cannot run the final visual acceptance gate." / "The orchestrator alone accepts the task." `docs/COMPETITIVE_FEATURE_EXPANSION.md:325`: "No competitor-derived feature may bypass the established legal and data controls."

---

## Area 2 — Per-agent × per-control matrix

Legend: PASS = control present; MISSING = absent vs baseline; RISK = absent and consequential given current session permissions (see Area 3). File:line refs are to the worktree copies.

| Control | 3d-massing-engineer | product-design-director | visual-quality-reviewer (REVIEWER) | financial-feasibility-engineer | opportunity-search-engineer |
|---|---|---|---|---|---|
| `memory: project` frontmatter | MISSING | MISSING | MISSING | MISSING | MISSING |
| Explicit `permissionMode` | MISSING | MISSING | MISSING | MISSING | MISSING |
| `isolation: worktree` (producers) | MISSING | MISSING | n/a (reviewer) | MISSING | MISSING |
| Allowed/forbidden-path instruction ("Stay within allowed paths") | MISSING | MISSING | MISSING | MISSING | MISSING |
| Write authority (tools) | Read, Write, Edit, Bash, Grep, Glob (:4) | Read, Write, Edit, Grep, Glob (:4) — **no Bash** | Read, Grep, Glob, **Bash** (:4) — no Write/Edit tool, but Bash = arbitrary shell writes | Read, Write, Edit, Bash, Grep, Glob (:4) | Read, Write, Edit, Bash, Grep, Glob (:4) |
| Network authority | No WebFetch; network reachable via Bash | None (no Bash/WebFetch) — least-privileged of the five | No WebFetch; network via Bash | No WebFetch; network via Bash | No WebFetch; network via Bash |
| `Skill` tool / `skills:` block | MISSING | MISSING | MISSING (no `run-quality-gate`) | MISSING | MISSING |
| ADR-005 ledger/gate protocol section | **RISK — absent** | MISSING (no Bash, lower risk) | **RISK — absent** (no "read-only, do not run write-producing commands", no PASS/FAIL/BLOCKED return contract) | **RISK — absent** | **RISK — absent** |
| No self-approval | PASS — :33 "You may not … Approve your own visual work"; :28 "Submit evidence for independent review" | PASS — :36 "You may not: Approve your own design"; :33 "Submit work to the visual-quality-reviewer and human-journey-reviewer" | PARTIAL — description :3 "Never use as the producer of the same UI"; no explicit no-self-gate | PARTIAL — :19 "Submit to independent QA" (implied only) | PARTIAL — :20 "Submit data contracts to independent verification" (implied only) |
| No ledger mutation by reviewer | n/a | n/a | **MISSING** — nothing forbids `tools/project_control.py`/git; has Bash | n/a | n/a |
| Read-only reviewer discipline | n/a | n/a | **AMBIGUOUS/DEFECT D3** — :36 "Do not edit implementation files **during final review**" (temporal qualifier adversarially implies editing is allowed at other times; ADR-005 Decision 3 requires reviewers "stay read-only" unconditionally) | n/a | n/a |
| No production-deploy / credential authority | PASS (no such claims) | PASS | PASS | PASS — positive control :21 "Do not source current market values without an approved data source and provenance" | PASS — positive control :19 "Ensure tenant isolation for saved searches" |
| No ADR/owner-decision override | PASS (no override language in any of the five) | PASS | PASS | PASS | PASS |
| Prompt-injection / secret-handling instructions | None found | None found | None found (":37 Do not approve based only on screenshots supplied by the producer" is a good anti-fabrication control) | None found | None found |

Producer-report/G3 findings C1–C7 **independently confirmed real** (this matrix is my own extraction, not a trust of theirs). One additional finding beyond C1–C7: the temporal qualifier in visual-quality-reviewer (D3 below), and the scripted completion wording in `3d-massing-engineer.md:37-38` ("Geometry implementation is complete and submitted for independent…") which is acceptable (submission, not acceptance) but should adopt the roster's requested-status vocabulary (`awaiting_gate | blocked | needs_split`) in the conformance task.

---

## Area 3 — Discovery / dispatchability on merge

**Concrete harness behavior:**
1. **Agents auto-register.** Files under `.claude/agents/` register as dispatchable subagent types on checkout — no registration step, no allowlist. The day after merge, `3d-massing-engineer`, `product-design-director`, `visual-quality-reviewer`, `financial-feasibility-engineer`, `opportunity-search-engineer` are live Agent-tool targets in every session. `CONTINUE_FROM_CURRENT_STATE_PROMPT.md:27-32` (already on main) even instructs the orchestrator to "Verify that these project subagents are discovered."
2. **The rule auto-loads unconditionally.** `.claude/rules/3d-ui-expansion.md` has no `paths:` frontmatter → always-attached standing context (demonstrated attachment semantics above). Its item 13 then instructs continuation (Area 1a).
3. **Session permission posture removes the safety net.** `.claude/settings.local.json` on main: `"defaultMode": "bypassPermissions"` with blanket allows `Bash`, `Bash(python *)`, `Bash(git *)`, `Bash(gh *)`, `WebFetch`. A dispatched pack agent holding Bash (4 of 5) runs `python tools/project_control.py …`, `git push`, `gh`, and arbitrary network commands **without any prompt**. The only deny rules are `.env` reads; the ask-list covers only destructive git/gh/rm.
4. **The control CLI does not enforce orchestrator-only use.** ADR-005 §Regression proof: "producer can claim/progress/submit" — the CLI's own guards are limited to no-self-100% and no-self-gate/acceptance. ADR-005 compliance is enforced **only** by protocol text embedded in each agent definition (ADR-005 Decision 6) — text the five pack agents do not have.

**What an orchestrator or hook could accidentally do the day after merge:** a fresh session loads item 13 ("update the existing master plan and continue from the first unblocked task"), reads the exec plan (which names the pack agents as producers, e.g. `3D-002: Producer: 3d-massing-engineer`), contracts UI-001/3D-002, and dispatches a pack agent. That agent — no ADR-005 section, no path discipline, no worktree isolation, bypassPermissions — can claim/progress/submit in the ledger itself, commit and push, and reach the network via Bash, all unprompted. The reviewer identity (`visual-quality-reviewer`) can additionally be dispatched to a gate with Bash and no read-only protocol. The owner's separately-noted global auto-setup hook is orthogonal (it reinstalls a generic pack; it does not dispatch agents), and no project `settings.json` hooks exist.

**Does anything in the repo currently prevent dispatch?** **No.** No blocker JSON names the five agents; no rule text prohibits their dispatch; the prohibition exists only in the integration report §4, the G3 report O3, and the M0-T010 progress log — none of which are always-loaded, and all of which fall out of the mandatory reading set once M0-T010 is accepted and closed. This harness has **no agent-type-scoped permission deny**; a machine-visible prohibition can only be prompt-plane (always-loaded rules file + session-start blocker), which is exactly what Disposition A must construct.

---

## Area 4 — Prompt-injection / authority-escalation adversarial read (all six files + merging docs)

- **No gate-power claims, no "you may approve", no "merge when done", no credential/secret-handling instructions, no ADR-override language** in any of the six in-scope files (rule + 5 agents). Grep across the three merging `docs/` pack files for approve/merge/credential/secret/deploy/override/bypass/skip found only *reinforcing* text (quoted in Area 1d).
- **The one real escalation channel is structural, not textual:** always-on rule (item 13) + named-agent execution plan + auto-registered agents + bypassPermissions forms a complete unattended chain from "session start" to "non-conformant agent writing the ledger" (Defects D1+D2). Nothing in the six files *asks* for escalation; the harness *grants* it by default the moment the files land.
- **`visual-quality-reviewer.md:36`** — "Do not edit implementation files during final review" — adversarially reads as permission to edit outside final review (D3).
- **Task-ID scheme collision (C7):** `docs/3D_AND_UI_EXECUTION_PLAN.md` uses `3D-xxx/UI-xxx/COMP-xxx` and its "Continuation rule" (:9-16) instructs the orchestrator to "Add new task IDs." A future agent reading the exec plan as context could create ledger tasks under the pack scheme, bypassing the `M<milestone>-T<n>` convention (`docs/PROJECT_CONTROL_PROTOCOL.md`) and GDS §2.2. Mitigated by the integration report's re-key rule (§1/§2), but that report is not always-loaded — the counter-notice should restate it (LOW).
- **Positive:** the pack contains its own injection-resistant posture for content: rule items 8–9 (no AI-prose geometry, provenance mandatory), `README_ADD_TO_EXISTING_PROJECT.md:45` ("A beautiful but legally disconnected model fails the project gate"), visual standard :112-118 (producer cannot self-accept). Secret scan independently re-run: PASS, no findings; no URLs/exfil targets, no encoded content, no tool-instruction payloads embedded in any pack file.
- **Pre-existing on main (not changed by this merge, noted for completeness):** `CONTINUE_FROM_CURRENT_STATE_PROMPT.md:71` "Continue automatically from the first new unblocked task…" — same risk class as item 13 but qualified by independent review; the counter-notice should cover it too.

---

## Defects

| ID | Severity | Defect | Evidence | Reproduction |
|---|---|---|---|---|
| D1 | **HIGH** | Five auto-registering agent definitions merge without ADR-005 protocol sections while the session runs `bypassPermissions` with blanket `Bash/git/gh/python` allows; the control CLI does not enforce orchestrator-only use. A dispatched pack agent can mutate the ledger, push git, and reach the network unprompted. | Agent files :1-6 (frontmatter `name/description/tools/model` only) vs roster baseline; `.claude/settings.local.json` `"defaultMode": "bypassPermissions"`; ADR-005 §Regression proof ("producer can claim/progress/submit") | Merge branch; in a new session run the Agent tool with `agent_type: 3d-massing-engineer` and any task touching the ledger — no prompt, no embedded prohibition fires |
| D2 | **HIGH** (as the trigger of D1's chain) | Always-loaded, unqualified auto-continuation order: `.claude/rules/3d-ui-expansion.md:25` "The main orchestrator must update the existing master plan and continue from the first unblocked task" — no paths frontmatter, so it attaches to every session and countermands the owner-review hold recorded only in the M0-T010 progress log | Area 1a | Merge; start a fresh session; the rule text is injected before any ledger read; the hold is not |
| D3 | **MEDIUM** | Reviewer identity `visual-quality-reviewer` lacks the read-only gate protocol and its only restraint is temporally qualified ("during final review"), while holding Bash | `visual-quality-reviewer.md:4,36-37` vs ADR-005 Decision 3 and `security-reviewer.md:14-16` | Dispatch it to any G3-style review; nothing forbids `git commit` or `project_control.py gate` |
| D4 | **MEDIUM** | Roster non-conformance aggregate (C1/C2/C3/C6): no `memory: project` (agent-memory write-scope rule in `.claude/rules/project-control.md` has no anchor), no `permissionMode`, producers lack `isolation: worktree` (CLAUDE.md principle 10), no `Skill` tool, no "stay within allowed paths" line | Matrix above; `.claude/rules/project-control.md` agent-memory clarification | Compare any pack agent frontmatter with `cloud-architect.md:1-9` |
| D5 | **LOW** | Undefined gate vocabulary: rule item 11 gate names and exec-plan "professional-review gate" not mapped to the G0–G7 catalog | Area 1b | — |
| D6 | **LOW** | Task-ID scheme `3D-/UI-/COMP-` in an instruction-bearing doc ("Add new task IDs") collides with the ledger convention | Area 4 bullet 4 | — |
| D7 | **INFO** | Producer report cites `tools/secret_scan.py`; actual path `.github/scripts/secret_scan.py` (scan itself re-verified PASS) | This review | — |

No cross-tenant, storage, upload, SSRF, dependency, or log-redaction findings: the diff is 13 text files, zero code, zero dependencies, zero endpoints; secret scan PASS; contracts validator PASS; low-storage footprint ~60 KB (G3-verified, consistent with my diff stat).

---

## Required corrections (all routed to the FOLLOW-UP conformance task — the raw pack files must not be edited inside M0-T010)

For each of the five agent files (preserving domain content):
1. Add frontmatter: `permissionMode: default`, `memory: project`; `isolation: worktree` for the four producers; add `Skill` to tools; for `visual-quality-reviewer` add `Write` + `skills: run-quality-gate`.
2. Embed the verbatim roster protocol sections: producers get "## Ledger and integration protocol (ADR-005)" (per `cloud-architect.md:15-17`); `visual-quality-reviewer` gets "## Gate reporting protocol (ADR-005)" (per `security-reviewer.md:14-16`), including the unconditional "You are read-only… never run write-producing commands" language that removes the "during final review" qualifier's ambiguity (D3).
3. Add the "Stay within allowed paths" / task-packet discipline line to the four producers; align `3d-massing-engineer` completion wording with the requested-status vocabulary.
4. Neutralize D2 in the rule file: either add `paths:` frontmatter scoping `3d-ui-expansion.md` to expansion-related paths, or rewrite item 13 to "…continue from the first unblocked task **after the owner has reviewed the integration report and the orchestrator has contracted the work through the normal G0 process**", and map item 11's gate names to the G0–G7 catalog (D5).
5. State the task-ID re-key rule (pack IDs are workstream labels; ledger IDs are `M<milestone>-T<n>`) somewhere always-authoritative (D6).
6. Recommended, separate from the conformance task (session-hardening, owner decision): revisit `settings.local.json` `bypassPermissions` — it is the amplifier that turns every prompt-level gap into an unprompted capability. At minimum move `Bash(python tools/project_control.py *)`, `Bash(git push*)`, `Bash(gh *)` out of blanket-allow for subagent contexts if the harness configuration permits per-agent distinctions; otherwise record acceptance of the residual risk.

---

## Disposition recommendation: **A**, with the machine-visible prohibition specified below landing in the SAME integration checkpoint as the merge

**Justification:** the six files contain no hostile or authority-claiming text; every dangerous behavior requires the *harness* to grant it, and the harness's only enforcement plane for agent dispatch is prompt-level context. A prohibition that occupies the same always-loaded plane as the risk (a rules file) plus the session-start mandatory reading set (a blocker) is therefore as strong as this harness can make it — and it satisfies the owner's condition ("explicit, machine-visible, cannot be missed"). Disposition B would hold B-005 open for a review-and-edit cycle that changes nothing about the risk model while delaying B-005 closure and the raw-evidence merge the owner explicitly wants preserved.

**Exact contents the machine-visible prohibition must have (all three, none optional):**

1. **Counter-notice rules file on main, outside the pack files** (new file, e.g. `.claude/rules/expansion-agent-dispatch-hold.md`), authored by the orchestrator in the integration commit — this does not touch the raw pack files, preserving ZIP-hash evidence. It must have **NO `paths:` frontmatter** (so it attaches unconditionally, the same plane as `3d-ui-expansion.md`) and must state verbatim-quotable, unambiguous text:
   - "DISPATCH PROHIBITED (owner directive 2026-07-17, G5 M0-T010): the subagents `3d-massing-engineer`, `product-design-director`, `visual-quality-reviewer`, `financial-feasibility-engineer`, `opportunity-search-engineer` MUST NOT be dispatched by any session, agent, skill, or hook until conformance task `<M0-Txxx>` is accepted and blocker `<B-00x>` is closed. Their definitions lack the ADR-005 protocol sections; dispatching them under the current session permissions would allow non-orchestrator ledger writes."
   - "`.claude/rules/3d-ui-expansion.md` item 13 and `CONTINUE_FROM_CURRENT_STATE_PROMPT.md` item 10 are SUSPENDED pending owner review of `docs/3D_UI_EXPANSION_INTEGRATION_REPORT.md`: do not contract or start the 19 proposed tasks, apply P1–P8, or change the master plan on their instruction. This notice supersedes those passages by owner directive 2026-07-17."
   - "Pack task IDs (3D-/UI-/COMP-) are workstream labels only; ledger tasks use `M<milestone>-T<number>`."
2. **Blocker JSON** `project-control/blockers/B-007-expansion-agent-conformance.json` (next free ID; B-001…B-006 exist), same schema as B-005: `blocker_id`, `title` "Dispatch prohibition: 5 expansion agents pending ADR-005 roster conformance", `status: open`, `affects`: the five agent names + the conformance task ID + "any task naming them as producer/reviewer", `detail`: cite C1–C7, D1–D6, and this G5 report path, `exact_human_action`: none (orchestrator-resolvable: conformance task acceptance), `how_it_will_be_tested`: "each of the 5 files carries `permissionMode`/`memory`(+`isolation` for producers)/`Skill` frontmatter and the verbatim ADR-005 protocol section; conformance task accepted; counter-notice rules file then updated or retired by the orchestrator in the same checkpoint." Blockers are mandatory session-start reading (CLAUDE.md routine step 2), giving a second, ledger-plane anchor.
3. **Conformance task packet** (proposed task #1 in report §2) contracted with `allowed_paths` = the five agent files + `.claude/rules/3d-ui-expansion.md`, `required_gates` G0,G2,G3 **+ G5 re-check by security-reviewer** (it edits execution surfaces; G5 is required for "administrative functions" per the gate catalog — code-reviewer alone, as the report proposes, is insufficient). The checkpoint recorded at merge must name the blocker and the task ID.

**Residual risks under A (accepted, with severities):**
- R1 (MEDIUM): the prohibition is prompt-plane only — a hook, a context-truncated session, or an agent that never receives rules-file context could still dispatch; the harness offers no agent-type deny. Mitigation is the dual anchor (always-on rule + session-start blocker); this is the ceiling of what is achievable without editing the pack files or the harness.
- R2 (MEDIUM): `bypassPermissions` remains in force for *all* agents, including roster ones, until correction 6 is decided — independent of this merge.
- R3 (LOW): after conformance closes and the counter-notice is retired, `3d-ui-expansion.md` item 13's continuation order becomes live again; the conformance task must fix it (correction 4), and the G5 re-check must verify it did.
- R4 (LOW): `CONTINUE_FROM_CURRENT_STATE_PROMPT.md` items 3/10 remain on main untouched (pre-existing); covered by the counter-notice text while it stands.

---

## Final verdict

**PASS — with required corrections that are BLOCKING** (per the recorded gate-verdict semantics in `.claude/rules/project-control.md`: recorded as PASS; the corrections block acceptance/next steps).

Blocking conditions for the orchestrator, in order:
1. The merge commit/integration checkpoint MUST include the three-part machine-visible prohibition exactly as specified (counter-notice rules file with no paths frontmatter + B-007 blocker JSON + contracted conformance task with G5 re-check). Merging the raw pack **without** the counter-notice landing in the same checkpoint is NOT safe and would convert D1+D2 into a live escalation chain on the next session start.
2. B-005 closes only alongside item 1, and the conformance task's follow-up G5 must verify corrections 1–5 (and record the owner's decision on correction 6).
3. G3 carry-forwards O1 (CI evidence at merge) and O5 (temp-dir cleanup) remain open and are endorsed here.

The raw pack content itself is clean: no secrets, no hostile instructions, no authority claims, no hosting/ADR-004 conflict, affirmative producer/reviewer-separation and provenance language throughout. The entire risk is the combination of auto-registration, an always-loaded unqualified continuation order, missing ADR-005 protocol text, and the session's `bypassPermissions` posture — all of which the specified prohibition neutralizes at the only enforcement plane this harness provides.

Reviewer memory updated (permitted path): `.claude/agent-memory/security-reviewer/claude-execution-surface-review.md` (+ index line in `MEMORY.md`).
