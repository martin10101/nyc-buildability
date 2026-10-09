# M0-T122 — G4 QA review (VERBATIM reviewer return; saved by the orchestrator, transport entity-decoding only)

All checks reproduce. Every anchor, count, digest, and doctor row matches independently. Here is my G4 report.

---

# G4 QA Gate Report — M0-T122 (Fourth Golden Recertification)

**Task:** M0-T122 — Fourth golden recertification at the post-restart-channel frozen identity + R276 rerun gate
**Gate:** G4 (independent QA) — READ-ONLY
**Reviewer:** qa-engineer (independent; producer of record = orchestrator)
**Frozen head:** `62194d1`; deliverables landed at `acf6505` (byte-identical — verified below)
**Directive regime:** in-regime, `directive_refs D-024:ALL` (10 applicable rows R302, R314–R322)

## 0. Identity / reproduction integrity

- `git diff --stat acf6505 62194d1` = control-plane only (`M0-T122-G2.json`, G2 self-check, `state.json`, `M0-T122.json`). The two deliverable reports (`M0-T122-recertification.md`, `M0-T096-activation-package.md`) have an **empty diff** between `acf6505` and `62194d1` — byte-identical.
- `git log -1 --format=%H 62194d1 -- tools/agent_supervisor/` = **`668c824`** — supervisor material last moved at the M0-T121 fix; this governance task changed **no code** (allowed_paths = two report files only). Modularity check N/A (no handwritten source changed).

## 1. AS-1 / AS-2 — whole suite reproduced (I ran it; ~7 min)

```
python -m pytest tools/test_agent_supervisor*.py -q -p no:cacheprovider
2814 passed, 2 skipped in 195.66s (0:03:15)      [exit 0]
```
Reproduces the recert claim **2,814 passed / 2 skipped / 0 failed** exactly. (My wall-time 195.66s vs the report's 425.8s — environmental, not a claim; counts are identical.) Far above the ≥1,165 freeze baseline (M0-T039 duty), so AS-2 holds.

Golden pack standalone (AS-1 count):
```
python -m pytest tools/test_agent_supervisor_golden_run.py -q
42 passed in 13.71s
```

Environment: `Python 3.11.9, pytest-8.4.2` (supervisor floor).

## 2. Chain arithmetic (requirement 2)

- T119 baseline **2,780 passed** — verified directly from `M0-T119-recertification.md` §3 (line 49: "WHOLE supervisor suite … 2,780 passed, 2 skipped, 0 failed").
- `2,780 + 34` (M0-T121 restart-channel pack, 34 tests) = **2,814** ✓ (matches my run).
- Pre-delta cross-check `2,811 = 2,780 + 31` — the pre-rework restart pack was 31 tests (from my M0-T121 review); the +3 edge-granular rework tests bring it to 34. **Consistent, no inconsistency flagged.**

## 3. Blob / anchor checks (requirement 3) — all at frozen head `62194d1`

| Anchor | Recorded | Reproduced (`git rev-parse 62194d1:…`) | Match |
|---|---|---|---|
| Golden pack blob | `c54fd0d2…fdb550` (== T119 §2 line 29) | `c54fd0d2d0e3833e54ba2ec9745ee6e7d9fdb550` | ✓ byte-identical to T119, carried un-weakened |
| Restart pack blob | `d3e23087…` | `d3e23087f0f76a6660b5c19e605fd818fe940b47` | ✓ |
| `tools/agent_supervisor` tree | `d3db9f3c…` | `d3db9f3c7ee66ff36c44d518e6177c5a39378e4a` | ✓ |
| Material commit | `668c824` | `668c82410c0215659c3af5a1a00a523989473e5d` | ✓ |

## 4. Drift tooth + CLI identity (requirement 4)

```
python -m pytest tools/test_agent_supervisor_event_bus.py -k "s8_live_version_matches_catalog" -v
tools/test_agent_supervisor_event_bus.py::test_s8_live_version_matches_catalog_fixture PASSED
1 passed, 37 deselected in 0.14s
```
CLI identity recomputed via the supervisor's own `process.executable_identity` against the installed `C:/Users/MLFLL/.local/bin/claude.exe`:
```
size   : 217360032
kind   : sha256_head+size
digest : d6f6c29a8ac6b3cf1b76e53cca2faadf784bf5114230c815d55327dbae889ed8
MATCH d6f6c29a...: True
```
Digest is **byte-exact** to the admitted 2.1.251 identity — the "no repin needed / undrifted" claim is independently confirmed.

## 5. AS-3 — manifest / verify-controller / doctor (requirement 5) — reproduced READ-ONLY

I ran `doctor` read-only (did NOT run `record-manifest`, per instruction). `overall: PASS`. Every recert §2 row reproduced:
- `controller_manifest: 120 files verified against 7f9991cbb5a22a40... including the external config.toml binding` — this row IS the verify-controller check; **verify-controller PASS corroborated**, 120 files / `7f9991cb` / config-bound.
- `controller_config: codex allowlist ['gpt-5.6-sol','gpt-5.6-terra']; claude allowlist ['claude-fable-5','claude-opus-4-8']` ✓
- `approved_models: ['claude-fable-5','claude-opus-4-8']` ✓
- `control_response_live_probe: VERIFIED … against sha256_head:d6f6c29a8ac6b3cf` ✓
- OS-ACL posture: **PROTECTED**; `limited-auto: IMPLEMENTED and OFF by default` ✓
- Drift tooth green (above); 2.1.251 identity unchanged.

## 6. AS-4 — R315 hold + cycle-2 handover + protocol (requirement 6)

Recert report §4 records the handover command **verbatim**, and it matches the certified item-3 shape: `--mode limited-auto --owner-enable-bounded-auto`, **NO `--repin-cli-identity`**, forward-slash paths, quoted config path `"C:/Program Files/SupervisorConfig/config.toml"`, `!` prefix, one line. R315 hold recorded (release only after acceptance). The R316–R322 + Amendment-15 protocol (ONE attempt; on any further post-dispatch counted stop → no restart, preserve evidence, separate bounded AD-093 defect citing D-024-R301, touch budget 2/2 at cap; live-journey failure → preserve/report/no-repeat/no-autonomy) is recorded verbatim. §3 carries the R319 disclaimer ("do NOT prove continuous operability") and contains **no operability claim**. The activation-package §10 refresh likewise carries no overclaim. (AS-4's authoritative verification is the DCV's; the verbatim recording and command shape are present and correct.)

## 7. Journal untouched (requirement 7)

Doctor: `journal_integrity … transitions=13`, `audit_chain: 33 records verified; head sequence 33`. The audit-head-33 explanation checks out against `M0-T107-cycle2-start-refusal.md` §4 (verbatim): *"audit chain ok, head sequence 31 → 33 (the refused start's own audited recover_boot + refusal events … transitions still 13"* — a pre-window (campaign seq 34→35) event. The recert window performed only read-only reads plus writes outside the repo (manifest under `%LOCALAPPDATA%`), so the preserved HALTED journal is unchanged (transitions 13 / audit 33 identical). Note: doctor does not print the literal current-state token "HALTED", but transitions=13 + the `recovery_classification` row (`safe_no_auto_resume`, does NOT auto-resume) + the T107 record are mutually consistent with the at-rest HALTED journal — no discrepancy.

## 8. Activation-package §10 fourth refresh (deliverable)

Section 10 ("fourth refresh at M0-T122") carries every anchor for the single certified identity: material `668c824`(+test rework `6432d2d`), tree `d3db9f3c…`, golden `c54fd0d2` (42 tests, byte-identical to T119), restart `d3e23087` (34 tests), CLI `d6f6c29a…` (no repin), manifest 120 files `7f9991cb` config-bound, whole suite 2,814/2/0 with the chain arithmetic. No operability overclaim.

## 9. Requirement-by-requirement (QA-relevant D-024 rows reproduced)

- **R314** (recertification executed): reproduced — 2814/2/0, golden 42, manifest 120/`7f9991cb`, doctor PASS, drift tooth green, CLI `d6f6c29a` exact. **PASS**
- **R315** (hold honored, handover verbatim, released only on acceptance): recorded §4. **PASS**
- **R316/R317** (one-attempt + Amendment-15 on further counted stop): recorded §4 verbatim. **PASS**
- **R319** (no continuous-operability claim): §3 disclaimer present, no claim anywhere. **PASS**
- **R320** (live-journey standard recorded; journal never touched): recorded §3–4; journal transitions 13 / audit 33 unchanged. **PASS**
- **R321/R322** (failure preservation / no-autonomy / no-repeat): recorded §4. **PASS**
- **R302/R318** (bounded window; producer not interrupted): consistent with the ledger (M0-T121 accepted + this recert only). **PASS**

(The full ALL-row directive pass is the DCV's authoritative record; the above are the QA-reproducible claims.)

## 10. Findings

No defects. No coverage gaps. Every numeric and cryptographic claim in the recert report and the activation-package refresh reproduces exactly at the frozen identity; deliverables are byte-identical to the submitted `acf6505`; the preserved journal is demonstrably untouched.

VERDICT: PASS
