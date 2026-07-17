---
name: supply-chain-action-pinning-review
description: Verified method for reviewing GitHub Actions SHA-pinning (M0-T012); releases/latest is insufficient, must filter by major line
metadata:
  type: project
---

M0-T012 established the repo's SHA-pinning standard: `uses: actions/<name>@<40-hex> # vX.Y.Z`, secret-scan.yml style.

**Why:** owner directive 2026-07-17 required pinning before any repo/CI secret lands; tag refs are mutable supply-chain surface.

**How to apply (review method for any future pin change):**
- Resolve each tag yourself: `gh api repos/actions/<name>/git/ref/tags/<vX.Y.Z>`; if `object.type == "tag"` (annotated) dereference to the commit SHA — as of 2026-07-17 all four in-use actions tags were lightweight (`type: "commit"`).
- `releases/latest` returns the newest MAJOR (checkout v7, setup-python v6) — NOT valid for the same-major-line rule. Filter the releases list by the in-use major instead.
- The ref lookup path `repos/actions/<name>/...` itself proves the SHA belongs to the official org repo.
- Verified pins at e5f6ea4: checkout v4.3.1 = 34e11487..., setup-node v4.4.0 = 49933ea5..., setup-python v5.6.0 = a26af69b..., upload-artifact v4.6.2 = ea165f8d... (12 refs, 4 distinct pins; secret-scan.yml separately at checkout v4.2.2 = 11bd7190...). Related: [[g5-gate-recording-protocol]].
