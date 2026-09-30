---
name: massing-b0-input-hardening-boundary
description: massing_model must harden inputs flowing through the FORBIDDEN proposal.py B0 contract at its own boundary, not by editing B0
metadata:
  type: project
---

`services/api/app/scenario/massing_model.py` reads the proposal footprint through the
accepted B0 contract `app.scenario.proposal.validate_proposed_massing`, and `proposal.py`
is FORBIDDEN in most massing packets (its `:250` `{vertex!r}` echo is the wiring packet's
D-OBS-2 root). Consequence for input-hardening:

- `proposal._is_real_number` and `massing_model._is_finite_number` BOTH call
  `math.isfinite`, which raises `OverflowError` on an out-of-float-range int (`10**400`,
  any int ≳10**309), NOT a typed error.
- The LOT ring is a separate arg B0 never sees, so its huge-int / echo hardening lives in
  massing_model directly (`_is_finite_number`, `_preview`).
- The FOOTPRINT huge-int `OverflowError` ORIGINATES inside `proposal.py` during
  `validate_proposed_massing`, so it must be typed by an `except OverflowError` arm on the
  B0 `try/except` in `build_massing_model` — you cannot fix it at `_is_finite_number`
  (B0 runs first) and you cannot edit proposal.py.
- Any B0 error text re-echoed at that boundary must be bounded (`_preview(exc)`), because
  the raw B0 message can itself be caller-length (proposal.py:250).

**Why:** these were the M5-T106 round-2 before-wiring preconditions (G5 MED-1/LOW-1) for
the PKT-E/M5-T107 scene seam that feeds USER geometry in.
**How to apply:** when a future massing packet hardens footprint/lot inputs, split the fix
across BOTH layers — massing_model's own helpers for the lot, and the B0 `try/except`
boundary for anything that overflows or echoes inside forbidden `proposal.py`. Related:
[[MEMORY]].
