# M0-T119 — Third golden re-certification at the post-admission frozen final identity

Task: M0-T119 (unit S; Amendment 13 rows R282/R283/R284 + Amendment 14 rows R293/R296/R297,
instantiating R247). Recorded by: orchestrator (orchestrator-recert-runner), 2026-08-29/30,
campaign seq 32. Supervisor-freeze qualifying evidence: **D-024-R283**.

## 1. Why this re-certification exists (R247/R283/R296)

After the M0-T116 certification, the R276 resume stopped fail-closed on provider CLI drift
(Claude Code auto-updated 2.1.248 → 2.1.251). The owner authorized a deliberate admission
event (Amendment 13) and, mid-window, ordered the shell-routing reconciliation
(Amendment 14). Three units moved `tools/agent_supervisor/**`, invalidating the M0-T116
certification (R247): **M0-T117** (forced `DISABLE_AUTOUPDATER=1` at all four
supervisor-constructed claude env seams + owner machine-scope belt), **M0-T118** (the
2.1.251 measured fixture pack; drift teeth green; +2 hook events recorded), **M0-T120**
(empirical native-routing proof, native-tool worker guidance, pre-dispatch routing drift
tooth gating certified starts). All three were accepted through full four-reviewer waves +
DCV before this unit ran. Per R296 this is the ONE recertification at the ONE final
identity including M0-T120; per R297 it began only after M0-T120's acceptance resolved the
hold (the pre-Amendment-14 partial runs were voided and are not cited here).

## 2. The FINAL frozen post-admission identity (what was certified)

* Certification runs at head **`3a1741e`** (branch `control/D-024-fable-codex-loop`; code
  tree clean during every run; only pre-declared control-plane records change at this seam).
* Supervisor material identity: `tools/agent_supervisor/**` last moved at **`7d8195b`**
  (M0-T120 deliverable); directory tree object
  **`8d34ea53575f2cdf5b2d99029111c9e174339596`**.
* Golden pack: blob **`c54fd0d2d0e3833e54ba2ec9745ee6e7d9fdb550`** — moved from the
  M0-T116-certified `cf03caaa` by M0-T120's reviewed additions ONLY: the routing tooth-bite
  scenario (`test_the_routing_tooth_bites_a_certified_start_without_evidence`) and the
  harness routing-evidence seeding; the 41 previously certified scenarios are carried
  un-weakened (verified by the M0-T120 G3/G4 reviews). Pack is now **42 tests**.
* Identity composition: post-admission identity = M0-T116-certified post-repair system
  (`f89aa29`) + accepted M0-T117 (`d6a2ac8`) + accepted M0-T118 (`d1b05bb`) + accepted
  M0-T120 (`7d8195b`). Nothing else touched supervisor code since `f89aa29` (per-unit
  reviewer diffs + DCV path-scoped identity checks at each acceptance).
* **Version stability through the window:** `claude --version` stamped at certification
  start `2026-08-30T00:29:35Z` and end `2026-08-30T00:34:36Z` — both
  `2.1.251 (Claude Code)`; the machine-scope `DISABLE_AUTOUPDATER=1` belt (owner-set,
  registry-verified three times today) and the code-side forced injection stood guard.

## 3. Re-run evidence (all executed by the orchestrator at the identity above, this seam)

| Pack | Result |
|---|---|
| FULL golden-run pack (42 tests: the 41 certified scenarios + M0-T120's routing tooth-bite) | **42 passed, 0 failed** (15.00s) |
| Affected packs (process, claude-runner-env, recovery-probes, turnover-live-seam, event-bus, capability-probe, native-adapter, operator-channel, adversarial, start-reentry, routing-probe, command-authority, bounded-mode — 13 modules) | **672 passed, 1 skipped, 0 failed** (63.54s) |
| WHOLE supervisor suite (`tools/test_agent_supervisor_*.py`) | **2,780 passed, 2 skipped, 0 failed** (2,782 collected; 198.83s) |

**Baseline reconciliation (freeze rule, exact):** M0-T116 baseline 2,712 collected
→ +14 (M0-T117: env-seam + allowlist tests) → +0 net (M0-T118: pointer/tooth re-points)
→ +56 (M0-T120: 35 routing_probe + 2 recovery_probes + 13 command_authority + 5
bounded_mode + 1 golden) = **2,782 collected**. 2,780 passed + 2 pre-existing platform
skips = 2,782. No test removed, no unexplained drift. (Independent corroboration at the
same identity: the M0-T120 G4 reviewer and the M0-T120 DCV each ran the full suite —
2,782/2,780/2/0 byte-identical counts.)

* **Manifest binding at the final tree:** `record-manifest` re-run from the ctl24 root —
  **119 files** (the certified 117 + `routing_probe.py` + `prompts/claude_native_tools.md`),
  manifest digest **`774f91984bd75c95…`**, external `config.toml` bound, round-trip
  verification passed; `verify-controller` PASS ("including the external config.toml
  binding"); `doctor` (full, non-live) **43/43 PASS**. The stored activation manifest at
  `%LOCALAPPDATA%\NYCBuildabilitySupervisor\ctl24-activation\controller_manifest.json` now
  binds THIS final tree.
* **CI (confirming whole-suite run on the pushed SHA):** the standard 20-check CI runs on
  the pushed certification tip (this report + the activation-package refresh commit); the
  tip SHA and its 20/20 conclusion are pinned in the M0-T119 `progress_log` at the submit
  seam. Prior tips `a0c48b0`, `91d38a4` (M0-T120 wave) were 20/20 green.

## 4. R282 ADMISSION RECORD — Claude Code 2.1.251 is the ADMITTED provider CLI version

Every item of the R282 pass list holds at the frozen identity above, and ONLY on that
basis is the admission recorded here:

| R282 pass-list item | Evidence |
|---|---|
| Fixtures | The 2.1.251 measured pack (M0-T118: hook_event_catalog 33 events with the named +2 delta, interception, guardrail shapes, capability probe, native runtime) + the M0-T120 shell-routing fixture (digest-keyed to the installed binary) |
| Drift teeth | The three version teeth GREEN at 2.1.251 and removal-sensitive for the next drift (M0-T118; re-verified in every subsequent full-suite run) + the NEW pre-dispatch routing tooth gating certified starts (M0-T120) |
| Live probes | doctor --live control-response VERIFIED (`d6f6c29a8ac6b3cf`, seq-30); capability + native-runtime probes measured live (M0-T118); the bounded routing probe measured live under the exact controller construction (M0-T120: native_preferred, Edit brokered+denied) |
| Golden suites | 42/42 at this identity (§3) |
| Gates | G0/G2/G3/G4/G5 PASS for M0-T117, M0-T118, M0-T120 (delta re-attestations where correction rounds ran) |
| Independent reviews | Twelve reviewer engagements across the three units + three DCVs (7/7, 5/5, 8/8 rows PASS) |
| Manifest binding | 119-file manifest `774f9198…` bound + verified at the final tree (§3) |
| Frozen-identity certification | THIS unit at material `7d8195b` / tree `8d34ea53…` / golden blob `c54fd0d2…` |

**ADMITTED: Claude Code `2.1.251` (executable digest `d6f6c29a8ac6b3cf…`; codex-cli
0.146.0 unchanged).** The one-time `--repin-cli-identity` on the next certified start
(R285, owner-authorized) completes the admission at the journal level; per the standing
admission-event discipline (R286/R287) any FUTURE version change is a new deliberate
admission event — recapture → recertify → only then repin.

## 5. Residuals and known characteristics of the certified identity

Carried non-blocking notes from this window's reviews (fixing any later re-triggers R247):
1. The three M0-T116-era notes (seam read-error raw propagation; cli.py reconciliation-
   predicate convergence; telegram queued-digest collision edge) — unchanged.
2. F2 (SEC-MINOR): `powershell -Command "Remove-Item …"` classifies ASK not HARD_DENY
   (wrapper evasion of a bare-form HARD_DENY); still gated, never AUTO; follow-up
   candidate. F1: pipe-to-interpreter ASK not HARD_DENY; same posture.
3. F-LIVE-1: 2.1.251 reports `permissionMode=default` despite `--permission-mode manual`;
   mutating tools remain brokered+denied (verified live); tracking candidate.
4. Mode-invariant regression guard suggestion (G4-MINOR-3/G5-SEC-INFO-3): the routing-gate
   fold hardcodes `== MODE_LIMITED_AUTO`; the "only unattended mode" invariant is asserted
   by test today.
5. Report-hygiene: two stale intermediate count snapshots inside M0-T120-routing-evidence.md
   §3/§4 (superseded by its own §6b finals; adjudicated non-blocking by G4 + DCV).

## 6. Prohibition compliance (R280/R293)

No DISABLE_UPDATES anywhere; the CLI was neither downgraded nor updated (stamps §2); the
broker/classifier/owner gates are byte-untouched across the window (per-unit G5 + DCV
checks); no journal write outside the reviewed evidence key; no PR #241 touch; no
dependency; no `.claude/**` change. This unit wrote only: this report, the
activation-package items-10–12 + banner refresh, and control-plane records. The supervisor
loop remains STOPPED pending the R276 rerun (R284), which starts only after THIS unit is
accepted through its gates.
