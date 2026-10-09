# M0-T124 — G4 QA review (VERBATIM reviewer return; saved by the orchestrator, transport entity-decoding only)

Full suite: **2889 passed, 2 skipped** (exit 0) — my third full run at this identity, matching exactly. All checks reproduce. Here is my G4 report.

---

# G4 QA Gate Report — M0-T124 (Fifth Golden Recertification + R347 Presentation)

**Gate:** G4 (independent QA) — READ-ONLY
**Reviewer:** qa-engineer (independent; producer of record = orchestrator)
**Frozen head:** `70fb379`; deliverables at `3cb9e31` (byte-identical — verified)
**Directive regime:** in-regime, `D-024:ALL` (5 applicable rows R328, R330, R345, R346, R347)

## 0. Identity integrity

- `git diff --stat 3cb9e31 70fb379` = control-plane only (G0/G2 gates, G2 self-check, state.json, task json). The two deliverable reports have an **empty diff** between `3cb9e31` and `70fb379` — byte-identical.
- `git log -1 70fb379 -- tools/agent_supervisor/` = **`16e1b3b`** — supervisor material last moved at the M0-T123 hardening commit; this governance task changed **no code** (allowed_paths = two report files). Modularity N/A.

## 1. AS-1/AS-2 — whole suite reproduced (my third full run at this identity)

```
python -m pytest tools/test_agent_supervisor*.py -q
2889 passed, 2 skipped in 216.81s      [exit 0]
python -m pytest tools/test_agent_supervisor*.py --collect-only -q
2891 tests collected      (= 2889 + 2 skips)
```
Reproduces the certified count exactly. **Chain arithmetic:** `2814 (T122, verified) + 56 (T123 base: 45+7+4, attested) + 19 (T123 hardening, attested) = 2889` ✓. Above the ≥1,165 freeze baseline.

## 2. AS-1 anchors (reproduced via git at `70fb379`)

| Anchor | Recorded | Reproduced | Match |
|---|---|---|---|
| Material commit | `16e1b3b` | `16e1b3b1b281706e2dba5da84c853b66514d6a58` | ✓ |
| Supervisor tree | `a72a53b8…` | `a72a53b8c4f560c90dabbf65cb75478fef37ce43` | ✓ |
| Golden blob | `c54fd0d2…` | `c54fd0d2d0e3833e54ba2ec9745ee6e7d9fdb550` | ✓ (unchanged since T119, carried un-weakened) |
| Launch-seam blob | `1a77b904…` | `1a77b904c26935f1cb1bded87498dffa2a42230d` | ✓ (64 tests) |
| Restart blob | unchanged (34) | `d3e23087f0f76a6660b5c19e605fd818fe940b47` | ✓ (unchanged since T122) |

## 3. AS-3 — manifest / verify-controller / doctor / drift / CLI (reproduced READ-ONLY)

Doctor `overall: PASS`. Key rows reproduced:
- `controller_manifest: 121 files verified against 472931279090cd68... including the external config.toml binding` — 121 files / `47293127` / config-bound (this row IS the verify-controller check → **verify-controller PASS corroborated**).
- `approved_models: ['claude-fable-5','claude-opus-4-8']`; OS-ACL **PROTECTED**; `limited-auto: IMPLEMENTED and OFF by default`; `control_response_live_probe VERIFIED … d6f6c29a8ac6b3cf`.

Drift tooth `test_s8_live_version_matches_catalog_fixture` → **1 passed**. CLI identity recomputed: digest `d6f6c29a8ac6b3cf…ed8`, size 217,360,032, `sha256_head+size`, **MATCH True** — no drift, **no new admission event, no repin**. AS-3 satisfied.

## 4. AS-4 — R347 STOP + package correctness (requirement 5)

- **Recovery verb matches the ACTUAL journal state.** Doctor `journal_integrity transitions=18`, `audit_chain 43 verified head 43` — the preserved post-cycle-2 **PAUSED_RECOVERY** state (matches `M0-T107-cycle2-live-journey.md` §4). Section 4 correctly presents **`clear-recovery`** (the PAUSED_RECOVERY→PREFLIGHT exit) and explicitly states "**NOT owner-restart, which is the HALTED surface**." This is the load-bearing correctness: the journal advanced from HALTED (T122) to PAUSED_RECOVERY after the cycle-2 S14 stop, so `clear-recovery` — not the T122 `owner-restart` — is the right verb. ✓
- **Start command verbatim certified shape:** `start --mode limited-auto --owner-enable-bounded-auto --claude-executable …/.local/bin/claude.exe --codex-executable …/npm/codex.cmd --task-packet …/M0-T107.json --config "C:/Program Files/SupervisorConfig/config.toml" --model-selection C:/SupervisorController/model_selection.toml --manifest …/controller_manifest.json` — byte-identical to the T122-certified start; no `--repin-cli-identity`, forward-slash paths, quoted config. ✓
- **R316 consumption + R345 prohibitions restated:** §3 "The R316 one-attempt authorization is CONSUMED"; §4 "PR #241 never merged; autostart, C1 canary, Telegram live send … unchanged"; the objective restates R345. ✓
- **Nothing executed / requested:** §1 "nothing here starts, resumes, or clears anything"; §4 "What remains owner-only and is NOT requested here." **Proof:** the journal readback (transitions 18 / audit 43) is byte-identical to the post-cycle-2 preserved state — had `clear-recovery` or `start` run, both would have grown. AS-4 satisfied.

## 5. Fifth refresh append-only honesty (requirement 6)

Activation-package §10 ("FIFTH refresh at M0-T124") carries the correct anchors (material `16e1b3b`, tree `a72a53b8`, golden `c54fd0d2`/42, launch-seam `1a77b904`/64, restart 34, CLI `d6f6c29a`, 2889/2/0, manifest 121/`47293127`, PAUSED_RECOVERY transitions 18/audit 43, drift green, `clear-recovery` documented, R316 consumed). The prior fourth refresh is **preserved append-only as "## 10-prior"** (M0-T122: material `668c824`, 120 files `7f9991cb`, HALTED audit 33). ✓

## 6. Requirement-by-requirement (QA-reproducible D-024 rows)

- **R328** (disposition grants nothing; journal untouched): journal byte-identical at rest (transitions 18/audit 43, doctor). **PASS**
- **R330** (window closed as bounded: T123 + this recert): consistent with ledger. **PASS**
- **R345** (no restart/clear-recovery/journal-edit/budget-reset/PR#241): journal readback matches post-cycle-2; presentation is text. **PASS**
- **R346** (full process + recert + manifest verification + R276 preflight commitment): 2889/2/0, golden `c54fd0d2`, manifest 121/`47293127`, doctor PASS, drift green, CLI `d6f6c29a`; §4 records the R276-preflight commitment. **PASS**
- **R347** (STOP; package presented for separate owner decision; nothing started): §4 presents `clear-recovery` + certified start; nothing executed. **PASS**

(The ALL-row directive pass is the DCV's authoritative record; the above are the QA-reproducible claims.)

## 7. Findings

No defects. No coverage gaps. Every numeric and cryptographic claim reproduces exactly at the frozen identity; deliverables are byte-identical to `3cb9e31`; the presented recovery verb is correctly state-matched (`clear-recovery` for PAUSED_RECOVERY, not `owner-restart`); and the journal (transitions 18 / audit 43) proves the R347 presentation executed nothing.

VERDICT: PASS
