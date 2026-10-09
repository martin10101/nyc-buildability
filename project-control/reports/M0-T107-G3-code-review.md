# G3 Independent Code Review — M0-T107 (D-024 Amendment 3 unit J: generic Claude Code plugin portability plan)

> Orchestrator note: reviewer return saved verbatim (transport entity-decoding only: harness-neutralized `&lt;` sequences restored to `<`). Reviewer: independent code-reviewer agent (read-only), returned 2026-09-03.

**Reviewer:** independent G3 (packet-named `code-reviewer`), read-only
**Task:** M0-T107 — governance/planning; requirement D-024-R179; directive_refs D-024:ALL (in-regime)
**Deliverables (2, exactly the packet `allowed_paths`):** `docs/D024_PORTABILITY_PLAN.md`; `project-control/reports/M0-T107-portability-plan.md`
**Reviewed content identity:** candidate HEAD `93a7157f`; deliverable blobs adopted at ancestor `96f1b89b`, byte-identical to task-branch tip `777ef5e4` in `wt-m0t107`.
**Method:** read both files in full; independently re-derived R179 from source; reran all ten Section 6.3 checks plus additional grounding checks myself rather than trusting the producer/orchestrator claims.

## 1. Scope and contract compliance — PASS

- Packet `outputs` and `allowed_paths` are exactly the two deliverable files (packet lines 9–19). The full task-branch diff `ffc77bab..777ef5e4` touches **only** those two files (`ffc77bab..4047c79c` = both files; `4047c79c..777ef5e4` = report only). No forbidden path (`.claude/hooks`, `.claude/settings.json`, `apps`, `packages`, `services`, `supabase`, `project-control/tasks`, `tools/project_control.py`, …) is modified. The plan *references* several of these paths as things that STAY in-repo, but modifies none.
- **Blob identity proven:** plan blob `a0f1790f…` and report blob `0392f0af…` are identical at candidate HEAD and at `wt-m0t107:777ef5e4`. `96f1b89b` is an ancestor of HEAD; the only commit touching either file on the candidate branch is that adoption commit — no post-adoption drift. G0 PASS + G2 PASS already recorded (`03a9b911`); the task is correctly at `awaiting_gate` for G3.
- **Provenance headers accurate** (verified against `wt-m0t107` git log): authoring base `c5c6ff77` (parent of `ffc77bab`); starting state `ffc77bab` (Amendment 49, prior-journey drafts committed unaltered); worker revisions `4047c79c` (D-024-R738); correction pass `777ef5e4` (Section 6 added, Amendment 50). Report Section 6.1's "committed unaltered as 4047c79c" and Section 6.3's "run … at 4047c79c" both match the actual commit graph.

## 2. Requirement D-024-R179 satisfaction — PASS

R179 text (independently read at `requirements.json:6720`, id `D-024-R179`, applicability `task_ids:[M0-T102, M0-T107]`) decomposes into five clauses; each is satisfied:

| R179 clause | Where satisfied (verified) |
|---|---|
| "after the local loop passes its golden run" | Dependency `M0-T096` in packet; plan §8 binds every phase to post-golden-run timing and restates the hard sequencing rule |
| "separate portability plan" | `docs/D024_PORTABILITY_PLAN.md` is a standalone plan; all implementation is PROPOSAL requiring future orchestrator-created tasks (§0.1, §8) |
| "generic plugin w/ reusable skills, agents, hooks, and adapters" | §2–4 map components onto the native plugin set; adapters handled honestly (see §3 below) |
| "keep NYC-specific graph, ledger, security policy, profiles, product rules in this repository" | §5 concrete exclusion table maps each of the five R179 categories to concrete in-repo assets; §6 keeps NYC adapters in-repo behind ports |
| "must not block the local loop's activation" | §0.2, §8 (no phase may be an activation dependency), §11 (explicit non-authorizations) |

The plan's verbatim quotes of R179 ("Keep NYC-specific graph, ledger, security policy, profiles, and product rules in this repository"; "portability work must not block the local loop's activation") match `requirements.json:6720` and `source-003-amendment.md:337` exactly.

## 3. Independent factual verification (I reran every check; did NOT trust report §6.3)

| # | Claim | My independent result |
|---|---|---|
| Supervisor modules | report V1: "111" | **111 at reviewed SHA** (`git ls-tree 4047c79c` and `777ef5e4` = 111; also `ffc77bab` = 111). Report V1 reproduces exactly at the SHA it names. (See Observation OBS-1.) |
| loop-* skills | "9" | 9 — PASS (`loop-ask/codex/emergency-stop/pause/resume/start/status/stop/tasks`) |
| `.claude/hooks/*.py` | "5" | 5 — PASS |
| `.claude/agents/*.md` | "25" | 25 — PASS |
| R179 text @ requirements.json:6720 | verbatim | Verbatim match — PASS |
| capability-rebaseline line 52 | "OPTIONAL ENHANCEMENT … post-golden-run only" | Exact match — PASS |
| source-003-amendment line 337 | unit-J verbatim incl. "must not block…activation" | Exact match — PASS |
| supervisor-freeze.md + plugins-reference.md | both exist | Both exist — PASS |
| native_runtime.py header | "unit C, M0-T104" | Header reads "…D-024 Amendment 3 unit C, M0-T104" — PASS |
| loop-status frontmatter | `disable-model-invocation: true` + M0-T094/R083/R158 | Confirmed — PASS |
| Unit→task map (rebaseline 55–67) | C=T104,D=T105,E=T106,F=T092,G=T094,J=T107 | Confirmed — PASS |
| **Every module/hook named in plan §3** | all exist | All 34 supervisor modules + 5 hooks named in §3 exist in `wt-m0t107` (no MISSING) — PASS |

**Plugin-mechanics grounding (spot-checked against the `plugins-reference.md` snapshot, since §2–4 rest on it):**
- The central design pivot — "**There is no native 'adapters' component type**" — is correct: `grep -i adapter` over the 60 KB snapshot returns **zero** hits. Adapters-as-payload is the right call.
- Skills-directory plugin `<name>@skills-dir` (snapshot §Skills-Directory Plugins, line 808) — PASS.
- `${CLAUDE_PLUGIN_ROOT}` / `${CLAUDE_PLUGIN_DATA}` / `CLAUDE_PLUGIN_OPTION_<KEY>` (lines 392–401, 733) — PASS.
- Shell-field rejection of `${user_config.*}` (line 735) — PASS.
- Keychain "~2 KB total limit" (line 747) — PASS.
- Monitors experimental (lines 54/89) and "unsandboxed at same trust level as hooks" (line 374) — PASS.
- **All eight version gates** the plan cites (v2.1.154/205/207/218/221/238/239/246) are present in the snapshot at the expected features (defaultEnabled/restartOnCrash/user_config-shell/boolean-frontmatter/`"."`-validation/headersHelper/synced-plugins/bare-name). Boolean-frontmatter v2.1.218+ (line 121) supports the plan's "write plain true/false" mitigation.

## 4. Internal consistency and honesty — PASS

- Non-authorization is stated and self-consistent across §0.1, §0.2, §8, §11; the plan creates no ledger task, no dependency, no master-plan change, and forbids any proposed phase from becoming an activation dependency ("any violation is a gate FAIL", §10 risk row). This directly discharges R179's non-blocking and planning-only obligations.
- Freeze discipline is respected: §0.3 mandates COPY-not-modify of `tools/agent_supervisor/**`, consistent with `.claude/rules/supervisor-freeze.md` (exists) and AD-093.
- The mechanism/policy split (§5) is coherent and correctly keeps policy VALUES (rotation ceiling, `approved_models.py` allowlist values, autonomy tiers, holds) in-repo while porting mechanisms — matching R179's five exclusion categories concretely.
- Report §6 (orchestrator-authored) is clearly delimited from the producer's §1–5, correctly attributes authorship, and adjudicates the Codex REVISE as five packet-*verifiability* asks (F1–F5) with **no** identified content defect — an adjudication I independently confirm: I found no content defect in either file, and every checkable claim reproduces.

## 5. Observations (non-defects; no correction required)

- **OBS-1 — "111 modules" is branch-relative, and correctly scoped.** The figure is exact and reproducible at the SHA the report names (`4047c79c`/`777ef5e4` = 111). On the candidate integration branch the same command yields **129**, because additional accepted supervisor modules landed after the task-branch base. This is not a defect: the plan file itself makes **no** module-count claim (§3 calls its table "the seed, not the final word" and defers to a Phase-1 import-closure inventory), and report §6.3 explicitly binds "111" to `wt-m0t107 at 4047c79c`. Flagging only so the number is not later mistaken for a claim about the candidate branch.
- **OBS-2 — minor over-generalization in §4.** The plan says "hook/monitor commands read `CLAUDE_PLUGIN_OPTION_<KEY>` … or a config file instead." For **hooks** this is correct (snapshot 733/739). For **monitors** the snapshot (line 401) states processes do **not** receive that env var and must read a config file (line 402). Immaterial: the plan explicitly **excludes** monitors from the plugin and names the config-file fallback that monitors actually require, so the practical guidance is right.
- I did not re-verify the journey-evidence directory cited in §6.1 (`%LOCALAPPDATA%\…\journey-m0t107-01\`): it is outside the repository and is orchestrator evidence-capture, not a substantive claim in either deliverable. Its accuracy is not load-bearing for the plan's correctness or for R179.

## 6. Conclusion

Both deliverables are in scope, blob-identical at the reviewed identity, and touch no forbidden path. R179 is fully satisfied across all five clauses. Every load-bearing factual claim I re-derived from source reproduces exactly at the SHA it is scoped to; the plan's central design decision (adapters ship as payload because no native adapters component type exists) is correct against the plugins-reference snapshot; all eight cited version gates and the named modules/hooks/skills/agents check out. The plan authorizes nothing and creates no D-024 activation dependency. The two observations are documentation nuances, not defects, and require no correction. No material defect found.

VERDICT: PASS
Reviewed at ctl24 `git rev-parse HEAD` = `93a7157f5c0421988a55b6fddadf667c12f6a977` (deliverable blobs identical to adoption commit `96f1b89b` / task-branch tip `777ef5e4`).
