**Bounded visual review: REVISE. Overall G3/G4 remain FAIL pending the selector rework.**

Inspected all six actual CI images from run `35038721617`, bound by root to SHA `b4514d9a338a7ced8bd268b85afd55b12c729fd3`.

Two presentation findings:

- **Skip-link positioning:** Both mobile captures show “Skip to workspace” floating over content: coverage text in the closed overview and map metadata in the expanded overview. Focus visibly belongs to the heading or existing-building disclosure, so this is not the intended focused skip-link state. Existing `architect.css:27` uses fixed positioning without `top`/`left` anchors. Anchor it explicitly and verify hiding/reveal after scrolling and moving focus. Screenshots alone cannot establish whether the leak also occurs in the live viewport.
- **Raw status wording:** `professional_review_required` appears prominently throughout the new summary. Render “Professional review required” there while retaining the canonical state in evidence. The generic `CoverageBadge` intentionally displays enum values and is outside the allowed edit paths.

The remaining inspected composition passes: development information comes first; source and evaluated FAR are visibly separate; missing bulk results remain explicit; desktop columns and mobile wrapping remain readable. Existing facts, including Built FAR, remain in the disclosure. The mobile facts table scrolls internally; the screenshots show no page-level horizontal overflow. Report controls, source appendix, complete audit appendix, and zoning evidence remain visible/reachable in the reviewed composition. Actual horizontal-table interaction was not independently exercised.

Image SHA-256 references, under `m5t031-ci-images-v1/`:

| File | SHA-256 |
|---|---|
| `11-development-overview.png` | `fa76fb1a454418e8969e2b99af23d4520ba0c27683f934edf2726947ced213e8` |
| `12-development-report.png` | `638e325da832c7c403ca6f91a5658d830fbd6ad4dee456f21eaae50c81dd9355` |
| `13-development-zoning.png` | `43c57722554f41a02851bd86057d4b0290be0196462d49c85fde3a29b7a4ad09` |
| `6-14-overview-mobile.png` | `197a5afc3754b6c9c5f97477553b0e9e1bc1928f2ffa9fb963a20fcba1466d92` |
| `10-development-mobile-existing-open.png` | `e62a2b2bae400b22ecf43adc5b63f5864625819471cbaf71b78a2b816d6a8a57` |
| `2-02-overview-desktop.png` | `3562665d2a0fea52634ca8d00de99ceb6d0152c4cb41beed57da35a9ead97299` |

No edits, browser process, or repeated full-suite run.
