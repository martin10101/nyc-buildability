---
name: supervisor-freeze-lane-patterns
description: Defect-lane facts for tools/agent_supervisor — stale activation-checklist vs code, and the fail-closed seam-injection patterns to reuse
metadata:
  type: project
---

Working in the FROZEN supervisor (`tools/agent_supervisor/**`, D-010 defect-only lane,
`.claude/rules/supervisor-freeze.md`).

**The M0-T036 ACTIVATION-CHECKLIST can be STALE relative to the code.** As of HEAD 693df29,
all four "activation-blocking G3 B-rows" (B-1..B-4) were ALREADY fixed and independently
re-gated in V1.1 (frozen c193a52, `M0-T036-V1.1-G3-code-delta-review.md` = PASS), yet the
checklist still listed them as an open box. **Why:** the G3 review that named the B-rows was
at an older frozen SHA (43848bd); V1.1/V1.2.x deltas landed the fixes afterward. **How to
apply:** before implementing any activation-prerequisite, verify each item against current
HEAD (grep the fix + its regression test); report already-fixed items honestly with the
V1.1 delta-review citation instead of faking a reproducing test that cannot fail at baseline.

**Fail-closed seam-injection pattern used throughout the loop** (reuse it for any new wiring):
a new capability is a constructor param defaulting to None/always-safe so every existing
caller/test is unchanged, and only `cli.py` wires the real thing.
- Model availability: `SupervisedLoop(model_available=...)` default `lambda: True`; the CLI
  wires `make_launch_probe(...)` for orchestrator-role only.
- Quota classifier: `probe_model_launch(classify_unavailable=...)` default `lambda: ""` =
  unknown = fail-closed PAUSE (AD-025). `classify_quota_exhaustion` is corpus-gated;
  `QUOTA_EXHAUSTION_SIGNAL_VERIFIED = any(f.verified_live for f in corpus)` — derived, stays
  False until a live exhaustion is captured (bytes never recorded; base CLI = claude 2.1.220).
- Resource sampling: `SupervisedLoop(resource_sampler=None)` no-op default; `_check_resources`
  at cycle entry. Gauges: disk/log measurable stdlib (shutil/os); cpu/memory/process are
  structurally unknown stdlib-only on Windows (psutil NOT admitted) → reported unknown, never
  a fabricated OK, never a per-cycle pause; a sampling OUTAGE of a measurable gauge → conservative pause.

**Suite baseline (M0-T039 freeze):** `python -m unittest` over the 20 modules = 1165 run /
1163 passed / 0 fail / 2 skipped (~80s). The 2 skips are POSIX-only guards. Any change must
keep 0 failures and re-establish >= baseline. `python tools/validate_directive_compliance.py`
must stay exit 0. Journal state has no `delete_state`; clear a durable record by
`set_state(key, <marker with no truthy field>)` (e.g. rotation reason uses `""`).
