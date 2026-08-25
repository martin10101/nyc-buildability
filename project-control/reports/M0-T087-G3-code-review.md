# GATE REPORT — M0-T087 — G3 independent code review (two rounds)

Reviewer: code-reviewer (read-only). Producer: orchestrator.
Round 1 identity: `96bb98a…` → **PASS with findings; F1/F2 blocking**.
Correction round: consolidated per D-024 §12/§17, committed as `0d7fa80bb3781d1fddc2ab66f8c51aca559206db`.
Delta attestation at `0d7fa80`: **PASS — all five findings cleared or correctly re-scoped**.

## Round 1 (96bb98a) — findings
- **F1 (major, blocking):** `validate()` presence-checked but did not type/non-empty-check six
  load-bearing string fields → silently-empty orientation possible (contradicting AS-1) and an
  uncaught TypeError path in `--status`. Reproduced by the reviewer via runtime probes.
- **F2 (major, blocking):** module/class/report language overstated the sequence guard as
  cross-process mutual exclusion; the reviewer's analysis: `advance()` = load→check→write without a
  spanning lock; two OS processes could both pass the check (last-writer-wins); the two-racers test
  was serialized, not concurrent. Judged immaterial for the serialized single-writer usage (Gate 0
  + one-controller-lease) but the claims required precise scoping before later phases build
  cross-terminal turnover on them. Shared deterministic tmp name compounding noted.
- **F3 (minor):** crash-mid-write invariant asserted, not fault-injected.
- **F4 (minor):** proof's "frozen == live HEAD" claim not time-scoped (true at the parent moment).
- **F5 (nit):** extra-field tolerance; bool accepted as sequence.
Round-1 positives: purely additive (no frozen module touched); authority digest, lineage base,
restrictions verified truthful; 35 tests reproduced; ruff clean; modularity clean; freeze citation
present; producer's turnover-scope honesty confirmed.

## Delta attestation (0d7fa80) — verbatim verdicts
- **F1 PASS (cleared):** `_check_text` enforces non-empty str + C0/C1 rejection across the six
  string fields, next_action values, restrictions items; reviewer's probe: empty/int/None/
  whitespace all rejected; silently-empty orientation and the traceback now impossible; pinned.
- **F2 PASS (correctly re-scoped):** docstrings now state optimistic stale-read detection under
  the serialized single-writer model, "NOT a cross-process lock", cross-process exact-once
  assigned to the Phase D external lease; unique per-writer tmp (`pid-urandom`) + finally cleanup;
  claim now matches behavior.
- **F3 PASS:** genuine fault-injection test (monkeypatched `os.replace` failure → prior record
  byte-identical, tmp removed, seq preserved).
- **F4 PASS:** proof line time-scoped; correction-round bullet explains stale-by-one-by-construction.
- **F5 PASS:** unknown top-level fields fail closed; bool + float sequence rejected; all pinned.
Reviewer re-ran: 50/50 tests (0.33s, Python 3.11.9), ruff clean, `--status` exit 0, live record
validates unchanged; delta verified purely additive with freeze citation on the correction commit.

## OVERALL G3 VERDICT at 0d7fa80: **PASS**
No residual issues; no new findings. Full-suite freeze §4 baseline at the corrected identity is
orchestrator-captured G2 evidence (recorded in `M0-T087-G2-self-check.md` addendum).
