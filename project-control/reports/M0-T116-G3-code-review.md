# G3 Independent Code Review — M0-T116 (D-024 Amendment 12, unit P)

**Verdict: PASS — with one MAJOR required-correction (blocking before owner presentation / acceptance).**
The certification itself (the unit's actual product) is byte-verified sound and the zero-code-change claim is true. The MAJOR is a documentation-accuracy defect in the owner-facing activation package, not a certification error.

**Frozen review identity:** `869b313c583cc98107ce6dda96cf2e6973c9babd` — confirmed = `git rev-parse HEAD`.
**Reviewer:** t116-g3-code (read-only; no writes, no git mutations).

---

## Scope 1 — diff touches only project-control/** (PASS)

`git diff --stat 87091a5..869b313` and `git diff --name-only 87091a5..869b313`: 10 files, all under `project-control/**` (gates G0/G2, reports M0-T096-activation-package / M0-T116-recertification / G0-readiness / G2-self-check / evidence-map, M0-T116.json, state.json). `git diff --name-only 87091a5..869b313 | grep -v '^project-control/'` → empty. **Zero code paths. R273 "zero code changes" honored.**

Byte-stability corroboration at span endpoints:
- `87091a5:tools/test_agent_supervisor_golden_run.py` = `869b313:...` = `cf03caaa261da9726c7a12fc1676acb68851bac1` (golden pack byte-identical before/after — confirms the R273 evidence-map claim).
- `87091a5:tools/agent_supervisor` = `869b313:...` = `7487901cea729f5c254f98c8f7dcf859eb64e2c5`.

## Scope 2 — §2 identity claims verified against git (PASS)

- Last commit touching `tools/agent_supervisor`: `git log -1 --format=%H -- tools/agent_supervisor` → **`f89aa29`** ✓
- `git rev-parse HEAD:tools/agent_supervisor` → **`7487901cea729f5c254f98c8f7dcf859eb64e2c5`** ✓
- `git rev-parse HEAD:tools/test_agent_supervisor_golden_run.py` → **`cf03caaa261da9726c7a12fc1676acb68851bac1`** ✓
- Byte-stability across run head `c67830f`, cert tip `07233f5`, HEAD `869b313`: supervisor tree identical (`7487901c…`) and golden blob identical (`cf03caaa…`) at all three ✓

## Scope 3 — §2 identity-composition verified (PASS)

`git log --oneline 8574c58..HEAD -- tools/agent_supervisor tools/test_agent_supervisor_golden_run.py` returns **exactly four** commits, all from accepted units:
- `91664bb` M0-T115 unit O; `d89d740` M0-T115 correction round → accepted **M0-T115**
- `f89aa29` M0-T114 residuals; `a22e34a` M0-T114 pragma → accepted **M0-T114**

Matches the report's composition (M0-T112 system + M0-T115 `91664bb`+`d89d740` + M0-T114 `f89aa29`+`a22e34a`); nothing else touched supervisor code. `git merge-base --is-ancestor 8574c58 HEAD` = YES. Golden blob at `8574c58` = `d2946392…` (the M0-T112-certified version cited in §2). Ledger status confirmed: M0-T114 **accepted**, M0-T115 **accepted**, M0-T116 **awaiting_gate**.
Golden-pack move history: blob at `d89d740` (T115 tip) still `d2946392` (M0-T115 did not touch it) → `f89aa29` moves it to `63b6b78d` (register test) → `a22e34a` moves it to `cf03caaa` (pragma). Confirms §2's "golden pack last moved by M0-T114's register test + the scanner pragma; certified scenarios untouched since M0-T112."

## Scope 4 — collection-reconciliation arithmetic (PASS)

- Baseline chain: 2,696 (M0-T112) + 14 (M0-T115) + 2 (M0-T114) = **2,712 collected** ✓
- Chunk arithmetic: 680+725+689+616 = **2,710 passed**; +2 skipped = **2,712** ✓ (internally consistent across recertification.md §3, evidence-map D-024-R275, and G2-self-check §2)
- +14/+2 attribution spot-checked against the accepted units' own commit messages: `d89d740` states "14 new tests: 6 defect + 7 guards + 1 hardening"; `f89aa29` states "2 defect-named red→green tests." Both match. ✓

## Scope 6 — CI on the certification tip (PASS)

`gh api .../commits/07233f520a1bf1ed29eb54a13612cea544af7527/check-runs` → `{"conclusions":{"success":20},"total":20}`. **20/20 success.** The tip SHA + conclusion are pinned in the M0-T116 `progress_log` (matches). Prior tips `723f1d8`/`29fc1e2` claim (20/20) not independently re-checked — outside this unit's span, not load-bearing.

## Scope 7 — optional spot-execution (PASS)

`python -m pytest tools/test_agent_supervisor_golden_run.py -q` → **41 passed in 18.77s.**

---

## Scope 5 — activation-package refresh is REFRESH-ONLY — PASS on the literal checks, but one MAJOR

`git diff 87091a5..869b313 -- project-control/reports/M0-T096-activation-package.md` shows changes confined to **items 10, 11, and 12** plus the item-12 "Second refresh at M0-T116" paragraph. Verified against the step-5 checklist:
- **Items 10-12 correctly refreshed** to the post-repair identity (`f89aa29`, tree `7487901c…`, golden `cf03caaa`, 41/41, 705/705, 2,710+2 skipped / 2,712) — all figures match my git checks above. ✓
- **R276 resume-gating language intact:** item 12 now states "Resume of the authorized loop is gated on M0-T116 acceptance + the full R276 preflight." ✓
- **No other item's substance changed** (only 10-12 in the diff). ✓
- **Nothing implies activation or resume already happened:** line 3 "ACTIVATION STATE: DEFAULT-OFF. Nothing in this package activates anything" is intact; no activation/resume claimed as done. ✓

### MAJOR-1 — the top banner (Amendment-8 sequencing note, lines 10-16) was left stale and now contradicts item 11 of the same document

The refresh was scoped to items 10-12 and did **not** touch the top-of-file sequencing banner. As of HEAD that banner still reads (lines 10-16):

> **Amendment-8 sequencing (D-024-R232/R247, captured 2026-08-28; refreshed at M0-T112):** … and M0-T112 has re-run the golden certification at the FINAL frozen post-addition identity and refreshed items 10–12 below … This package becomes presentable for the R187/R595 activation decision ONLY once **M0-T112** itself is ACCEPTED through its gates …

This is now factually wrong in three ways, and this unit's entire purpose is to keep the owner-facing record accurate after M0-T112's certification was invalidated (R247):
1. It names **M0-T112** as the current certification "at the FINAL frozen post-addition identity" — that certification was invalidated by the repairs and superseded by M0-T116 at the post-**repair** identity.
2. It gates presentability on "M0-T112 … ACCEPTED." M0-T112 **is** accepted, so the banner logically reads as "already presentable," whereas the true current gate (per item 11 of the same doc and report §4) is **M0-T116 acceptance**.
3. It directly contradicts the freshly-refreshed **item 11**, which lists M0-T116 as "the acceptance the R276 resume waits on." Same document, two different gates.

Practical risk: the owner reads the banner first; it could prompt presentation for the R187/R595 decision before M0-T116 is accepted, resting on an invalidated cert. Bounded because the package activates nothing and presentation stays owner-gated, and items 10-12 are accurate — hence MAJOR, not BLOCKER.

Coupled report defect: recertification.md **§4** asserts "the Amendment-12 sequencing note records that the R276 resume conditions apply." There is **no** Amendment-12 sequencing note — the banner still says Amendment-8. The R276 resume condition is actually recorded in item 12, not a sequencing note. §4 overclaims what was edited (the evidence-map and G2-self-check correctly scope the edit to "items 10-12," so the overclaim is localized to §4's prose).

**Required correction (blocking before the package is presented to the owner / before acceptance):** refresh the top banner to the Amendment-12 / M0-T116 state — correct the presentability gate from "M0-T112 accepted" to "M0-T116 accepted," and stop describing the invalidated M0-T112 run as the current certification — OR reword report §4 and add the sequencing-note update it claims. Either path removes the internal contradiction with item 11.

---

## INFO

- **INFO-1:** `allowed_paths` in tasks/M0-T116.json lists only 3 paths (golden_run.py + recertification.md + activation-package.md), but the producer (orchestrator-as-producer for this governance unit) also authored G0-readiness.md, G2-self-check.md, and the evidence-map. These are the task's own gate-evidence artifacts written under orchestrator control-plane authority; conventional for a governance unit, not a scope violation. Noting for completeness.
- **INFO-2:** G0 (`reviewed_sha c67830f`, administrative PASS) and G2 (`reviewed_sha f102d2d`, self_check PASS) are recorded at earlier run points, as expected for readiness/self-check gates that precede the final submit; the independent G3/G4/G5/DCV wave reviews HEAD `869b313`.

---

## Commands run (read-only)
```
git rev-parse HEAD
git diff --stat 87091a5..869b313 ; git diff --name-only 87091a5..869b313
git diff --name-only 87091a5..869b313 | grep -v '^project-control/'
git log -1 --format=%H -- tools/agent_supervisor
git rev-parse HEAD:tools/agent_supervisor ; git rev-parse HEAD:tools/test_agent_supervisor_golden_run.py
git rev-parse {c67830f,07233f5,869b313,87091a5,8574c58,d89d740,f89aa29,a22e34a}:tools/agent_supervisor (and :...golden_run.py)
git log --oneline 8574c58..HEAD -- tools/agent_supervisor tools/test_agent_supervisor_golden_run.py
git merge-base --is-ancestor 8574c58 HEAD
git diff 87091a5..869b313 -- project-control/reports/M0-T096-activation-package.md
gh api repos/{owner}/{repo}/commits/07233f52…/check-runs
python -m pytest tools/test_agent_supervisor_golden_run.py -q
(Read: recertification.md, evidence-map.json, tasks/M0-T116.json, G2-self-check.md, gates M0-T116-G0/G2.json, activation-package.md head)
```

**Summary:** certification is byte-verified correct — identity, composition, arithmetic, CI 20/20, golden 41/41, zero code changes all confirmed. One MAJOR: the owner-package top banner is stale (points at the invalidated M0-T112 cert and gates presentability on M0-T112, contradicting the refreshed item 11), and report §4 overstates the edit. **PASS with that MAJOR as a required correction before owner presentation / acceptance.**
