# DCV report — M0-T112 (D-024 Amendment 8, unit M: final golden re-certification)

**Overall verdict: PASS.** All six applicable requirement rows SATISFIED against primary repository evidence I reproduced myself. No VIOLATED / UNVERIFIABLE / BLOCKED rows.

**Frozen review identity:** `14d204363c3ad44dff9a96333a9fe0e5662541ca` — confirmed: `git rev-parse HEAD` returns exactly this SHA on branch `control/D-024-fable-codex-loop`.

**Resolver (re-derived by me):** `evaluate_task_refs(M0-T112.json)` → `ok=true`, `applicable_ids=["D-024-R231","D-024-R232","D-024-R246","D-024-R247","D-024-R248","D-024-R249"]`, `cited_ids` identical, `missing_ids=[]`, `invalid_refs=[]`, `unresolved=[]`. Matches the expected set exactly.

**Registry integrity:** `python tools/validate_directive_compliance.py --check` → exit **0** (true exit via `${PIPESTATUS[0]}`; silent success). Confirms source digests match and `locked_requirement_ids` (249 ids, incl. R231–R249) are intact.

## Per-requirement verdicts

| Row | Verdict | Primary evidence I personally verified | Notes |
|---|---|---|---|
| **D-024-R231** — capture verbatim as next amendment + reconcile before further activation work | **SATISFIED** | `source-008-amendment.md` present with `---VERBATIM-BEGIN/END---` block + reconciliation preamble. Manifest `source-008` digest `3c32cf3f…518a14`; I recomputed `sha256` of the file on disk = **identical**. 249 locked req ids. Owner report `D-024-amendment-8-owner-report.md` present. Validator exit 0. | Discharged at capture; artifacts confirmed. |
| **D-024-R232** — both capabilities REQUIRED before continuous-mode activation (hold) | **SATISFIED** | `M0-T110.json` status=**accepted**; `M0-T111.json` status=**accepted** (both capabilities landed). `git diff --name-only a2aec114..14d20436` = **only `project-control/**`** — no `tools/agent_supervisor`, no supervisor mode change → no activation. Supervisor shadow-only posture intact. | Activation deliberately not fired. |
| **D-024-R246** — no silent broadening of M0-T096; safest bounded sequence captured durably | **SATISFIED** | `M0-T096.json` status=**accepted**; its task file **not touched** by the diff (contract unchanged). Bounded sequence captured durably in owner report §2 (M0-T096→T110→T111→T112→T107) and as ledger packets M0-T110/T111/T112 (all exist). Unit diff stays inside `project-control/**` (control-plane records + allowed activation-package refresh). | No production/supervisor code broadened. |
| **D-024-R247** — re-run affected/full golden certification at FINAL frozen identity BEFORE presenting activation package (core row) | **SATISFIED** | Identity anchors independently confirmed: last commit touching `tools/agent_supervisor` = **`8574c58`**; tree obj at HEAD = **`132e698c15a9f9412d53905e45ce0ae0724abe15`**; golden blob = **`d2946392f1c14ba086d63c60f2e125db6863bc10`**, last moved at `635fac5` — **not edited by this unit** (re-run only). I **spot-executed** `python -m pytest tools/test_agent_supervisor_golden_run.py -q` → **40 passed** (19.74s). CI at `615f661` via `gh api …/check-runs`: total=20, non-success=0, conclusions=`["success"]` → **20/20 green**. Activation package NOT presented: banner conditions presentability on M0-T112 ACCEPTANCE; `M0-T112.json` status=`awaiting_gate` (not accepted). | Core executable evidence (golden 40/40 + CI 20/20 + all identity anchors) reproduced by me. The affected-packs 493/493 and whole-suite 2694/2/0 figures are producer claims I did not fully re-execute; they are corroborated by the 20/20 CI whole-suite run on the pushed tip and by the +4 delta reconciliation (four accepted L-pack tests). |
| **D-024-R248** — prohibitions (no activation, no live 4.8 bridge, no PR #241, no Agent SDK, no MCP, no global Claude settings mod, no owner-boundary) | **SATISFIED** | `git diff --name-only a2aec114..14d20436` = only `project-control/**` — no `.claude/**` (no settings), no dependency/lockfile, no MCP config, no supervisor/production code. `gh pr view 241` → state=**OPEN**, mergedAt=**null** (untouched/unmerged). No continuous-mode activation; supervisor shadow-only. | All prohibitions honored within the unit diff. |
| **D-024-R249** — first report five items | **SATISFIED** | `D-024-amendment-8-owner-report.md`: §1 (new amendment required), §2 (bounded sequence), §3 (reused components), §4 (exact official Claude Code mid-turn limitation: ordinary commands queued until turn ends; `/btw` is built-in), §5 (certification to rerun). All five present. | Discharged at capture; artifact confirmed. |

## Exact commands run
- `git rev-parse HEAD` / `--abbrev-ref HEAD`
- `python -c "…directive_registry…evaluate_task_refs(M0-T112.json)…"`
- `git diff --stat a2aec114..14d20436` ; `git diff --name-only a2aec114..14d20436`
- `git log -1 --format=… -- tools/agent_supervisor` ; `git rev-parse HEAD:tools/agent_supervisor`
- `git rev-parse HEAD:tools/test_agent_supervisor_golden_run.py` ; `git log -1 … -- tools/test_agent_supervisor_golden_run.py`
- `git log --oneline a2aec114..14d20436`
- task-status reads of `M0-T110.json`, `M0-T111.json`, `M0-T096.json`, `M0-T112.json`
- manifest digest read + `hashlib.sha256` recompute of `source-008-amendment.md`
- `gh pr view 241 --json state,mergedAt,number`
- `gh api repos/:owner/:repo/commits/615f661a…/check-runs --jq '.total_count,…'`
- `python -m pytest tools/test_agent_supervisor_golden_run.py -q` → 40 passed
- `python tools/validate_directive_compliance.py --check` → exit 0 (`${PIPESTATUS[0]}`)

**Conclusion:** M0-T112 meets every applicable D-024 Amendment-8 requirement at the frozen head `14d20436`. Nothing was activated/merged/dispatched/presented; the R187/R595 activation package remains DEFAULT-OFF and correctly gated behind M0-T112 acceptance. Verdict **PASS**.
