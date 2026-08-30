<!-- Saved VERBATIM by the orchestrator from the G3 code-reviewer agent-return channel
     (transport entity-decoding only). Review head 702c64c. -->

All records reconcile with primary reality. The supervisor-code change referencing M0-T113 (`broker.py`/`recovery_probes.py`) belongs to the separate M0-T115 seam-fix commit `91664bb` (its message cites the M0-T113 restart only as the reproduced defect); M0-T113's own commits touch only `project-control/reports/**` and control-plane records, so R258 holds. I have completed all verification passes.

---

# G3 GATE REPORT — M0-T113 (D-024 Amendment 9 unit N: R187/R595 limited-auto activation + first-loop operation proof)

**Reviewer:** independent G3 (read-only, code-reviewer role)
**Frozen review head:** `702c64c8131a17570e2b9f8815734816b2aa0776` (branch `control/D-024-fable-codex-loop`) — confirmed HEAD of the ctl24 checkout
**Unit type:** governance/activation (path-free); deliverables are evidence reports, not code. Review = records-vs-reality audit.
**Verdict basis:** every claim reproduced against the runtime audit chain, the read-only status CLI, git, `gh`, and the stored activation artifacts.

## Scope reproduced
- Deliverables read: `project-control/reports/M0-T113-activation-preflight.md` (§1–6), `M0-T113-activation-evidence.md` (R260 + addenda 1–2), `M0-T113-evidence-map.json` (32 rows), `M0-T113-fable-probe.md`, packet `tasks/M0-T113.json`.
- Runtime: `%LOCALAPPDATA%\NYCBuildabilitySupervisor\33dfa57d…7a7ed\audit.jsonl` (+ `.head.json`), status CLI, stored artifacts under `…\ctl24-activation\`.

## Findings

**F1 — INFO — Audit chain intact and fully consistent with the operation claims (RECORD-vs-REALITY item 1: PASS).**
I manually traced all 31 events: every `prev_digest` equals the prior event's `digest` (genesis `0000…` → head `53db08f2…`), and `audit.jsonl.head.json` = `{sequence:31, digest:53db08f2…}`. Status CLI reports `audit_chain_ok: true`, `audit_head_sequence: 31`. The resumed dispatch (seq 20–31, all `cycle:1`) shows: seq20 `preflight_pass` PREFLIGHT→START_CLAUDE; seq21 `claude_unit_completed` checkpoint `M0-T107-ready-2026-08-29-01`, `output_digest 2ac59818…`, `observed_models:["claude-fable-5"]`, `permission_decisions:[]`, `native_tools_guidance_appended:false`, `returncode 0`, `context_tokens 604772`, 143 events; seq26 evidence packet `5539a2be…`, `packet_bytes 46025`; seq27 `codex_review_decision HALT_UNSAFE` by `gpt-5.6-sol`; seq30 finding *"The mandatory fresh, independent repository review was not completed…"*; seq31 `owner_touch_recorded basis S9 synchronous_stop`. All match the reports verbatim.

**F2 — INFO — Journal at rest exactly as claimed (item 1: PASS).** Status CLI: `current_state: HALTED`, `pending_effects: []`, `open_asks: []`, `unsent_outbound: 0`, `mode: none`, `limited_auto_enabled: false`. Exactly 3 `resolved_asks`, all `approval_status: DENIED`, `actionable: false`, with `request_digest` = `5637335f…` / `56cbd282…` / `ae36645d…` — matching the audit denial `input_digest`s (seq12–14) and the addendum-1 echoed digests. This is the M0-T115 read-time reconciliation surfacing the 3 historical denies as resolved/not-actionable. Confirmed.

**F3 — INFO — Addendum-2 confirmation set corroborated (item 2: PASS with one indirect item).**
(1) Budget digest `c1a51d3a…` → audit seq3 `run_budget_started` and seq19 `run_budget_resumed`, `resumes:1`. ✓ (2) Repin → audit seq17 `cli_identity_repinned`, `repinned:["claude"]`, `policy_result owner_repin`. ✓ (4) Zero permission decisions → seq21 `permission_decisions:[]`. ✓ (5) Rotation pending → seq24 `rotation_pending_flagged`, `604772` crossed threshold `400000` (S11.2, in-flight not interrupted). ✓ (6) State at rest → F2. ✓ **(3) Routing tooth `native_preferred` is the only item not persisted in audit/journal/status** — it is a `start`-command stdout claim (fixture `shell_routing_2026-08-29_m0t120_2_1_251.json` present). It is *indirectly* corroborated (empty `permission_decisions` = the worker used native tools instead of brokered shell requests, unlike cycle 1's 3 asks). Not reproducible from persisted runtime state alone; not blocking.

**F4 — INFO — Honesty disclosures verified against primary data (item 3: PASS).**
(a) Bash-mangled attempt 1 (progress_log 01:37:56Z) wrote **nothing** to the audit chain — there are no events between seq16 (2026-08-29T05:33Z) and seq17 (2026-08-30T01:38:23Z); the corrupted `--checkout` path meant the start refused before touching this runtime dir. The disclosed "journal stayed at PREFLIGHT" is correct: the last committed FSM state_transition is seq15 (`owner_cleared_pause` → PREFLIGHT); the seq16 `recover_boot` recorded `next_state PAUSED_RECOVERY` but committed no transition. Disclosed as an orchestrator error, matching reality. (b) `native_tools_guidance_appended:false` present in seq21 with the digest-binding cause honestly stated. (c) The HALT_UNSAFE is framed as a certified refusal (not a success-spin) and quotes the exact seq30 finding. All three disclosures are truthful.

**F5 — INFO — Evidence-map spot-checks (item 4: 8/8 + 6 extra PASS).** All 301 D-024 requirement IDs exist in `requirements.json`; I read the normative text for the 8 required rows and confirmed each map claim matches the requirement AND primary evidence: **R250** (source-009 @ `a87b407`, loop-stops-at-protected-decisions proven live via seq10 S14 + seq30 HALT_UNSAFE); **R254** (first launch `cfc6b16` "launch authorized", seq-33 dispatch `c88c2b9` "R276 rerun unlocked" — both real commits, CI-green per their messages); **R256** (fail-closed live: seq5–7 ASK-never-AUTO, seq10 S14, seq27/30 HALT); **R268** (seq12–14 denies + seq15 clear-recovery + seq16 UNSAFE_OR_DRIFTED restart refusal); **R273** (chain hash-linked intact = no hand-edit); **R276** (seq-30 drift stop; seq-33 resume only after M0-T119 `c88c2b9`); **R285** (seq17 repin; digest `d6f6c29a…`); **R300** (source-015 records the owner's cycle-2 stop protocol verbatim). Also verified R277/R280/R284/R298/R299/R301. Every cited artifact (`a87b407`, `cfc6b16`, `c88c2b9`, `871cab8`, `796e18f`, `f89aa29`, `eafdce4`) exists in git with a corroborating subject.

**F6 — INFO — Prohibitions honored (item 5: PASS).** `gh pr view 241`: `state OPEN`, `closed:false`, `mergedAt:null`, `mergeCommit:null` — **PR #241 unmerged**. Audit chain hash-links unbroken + `audit_chain_ok:true` — **no journal hand-edit**. `wt-m0t107` (at `C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t107`, branch `task/M0-T107-plugin-portability`) HEAD `796e18f33aac…`, `git status --porcelain` empty — **clean at 796e18f**. R258: the only supervisor-code change referencing M0-T113 is M0-T115's separate seam-fix commit `91664bb` (`broker.py`/`recovery_probes.py`, its own R247 recert); M0-T113's own commits touch only `project-control/reports/**` + control-plane records. Confirmed.

**F7 — INFO — Two deliverables internally consistent (item 6: PASS).** Cross-checked run id, budget digest, checkpoint/evidence/session/model/rotation values, manifest lineage, and anchors between preflight §1–6 and evidence addenda — no contradicting numbers or SHAs. On-disk `controller_manifest.json` confirms `manifest_digest 774f9198…`, `FILE_COUNT 119`, `generated_at 2026-08-30T01:20:53Z` (before the 01:41 dispatch), matching addendum 2. Stored `fable_probe_events.json` confirms `init_model:["claude-fable-5"]`, 1 denial, no file write — matching `M0-T113-fable-probe.md`. Resolved provenance question: `d6f6c29a8ac6b3cf` is legitimately both the doctor --live `sha256_head` and the pinned CLI digest — cli.py:1322 derives `sha256_head` as `executable_identity(exe).digest[:16]`, i.e. the same executable-identity digest used for the pin (no conflation).

**F8 — INFO (cosmetic, non-blocking).** (i) Preflight §5 A7 cites CI 20/20 "at `bbb932a`" while the launch is recorded at `cfc6b16`; this is a control-plane commit progression (staging `bbb932a` → launch tip `cfc6b16`), both asserted green — not a contradiction. (ii) Addendum-1's "the journal parked back in PAUSED_RECOVERY" is looser than the committed transition log (which rests at PREFLIGHT per seq15); preflight §6 and the honesty note state PREFLIGHT correctly. (iii) Report shorthand "wt-m0t107" omits that the worktree is a sibling of ctl24, not a child; branch+SHA make it unambiguous. None affect correctness.

## Commands run (reproducible)
- `python -m tools.agent_supervisor status --checkout C:\Users\MLFLL\Downloads\nyc-zoning\ctl24 --json`
- Read `…\33dfa57d…7a7ed\audit.jsonl` (+ `.head.json`); manual prev_digest chain trace (31 events)
- `git rev-parse HEAD` (→ `702c64c…`); `git worktree list`; `git -C …/wt-m0t107 status --porcelain` / `rev-parse HEAD` (→ `796e18f…`, clean)
- `gh pr view 241 --json state,closed,mergedAt,mergeCommit,…` (→ OPEN, unmerged)
- `git cat-file -t` / `git log -1` for `a87b407 cfc6b16 c88c2b9 871cab8 796e18f f89aa29 eafdce4 702c64c` (all exist, subjects corroborate)
- `git show --stat 702c64c`; `git log --oneline --grep=M0-T113` scope scan (identified `91664bb` = M0-T115)
- Python inspection of `requirements.json` (301 IDs), `controller_manifest.json` (`774f9198`, 119 files), `fable_probe_events.json`
- Grep of `tools/agent_supervisor` for `sha256_head`/repin (cli.py:1322 provenance), and source-015 for R300/R301

## Summary
No BLOCKER, MAJOR, or MINOR findings. Every claim in both deliverables — the fail-closed first cycle, the seam-defect discovery, the seq-33 live proof (dispatch, Fable 5 worker, first structured checkpoint with zero ask-stops, one-time repin, certified HALT_UNSAFE), and every honesty disclosure — is corroborated by the hash-linked audit chain, the read-only status CLI, the stored artifacts, git, and `gh`. All prohibitions (PR #241 unmerged, no journal hand-edit, wt-m0t107 clean at 796e18f, R258 supervisor code untouched by this unit) hold. The reports are internally consistent. The single not-directly-persisted claim (routing-tooth `native_preferred`, F3) is indirectly corroborated and non-blocking.

**G3 VERDICT: PASS**
